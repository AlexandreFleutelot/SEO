# -*- coding: utf-8 -*-
"""
case_manager.py

Gestionnaire principal des études de cas SEO.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .models import CaseStudy, CaseStatus, LLMProvider, CaseStudyReport


class CaseStudyManager:
    """Gestionnaire des études de cas SEO."""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.cases_dir = self.base_path / "data" / "case_studies"
        self.cases_dir.mkdir(parents=True, exist_ok=True)
        
        # Sous-dossiers pour l'organisation
        self.active_dir = self.cases_dir / "active"
        self.completed_dir = self.cases_dir / "completed"
        self.reports_dir = self.cases_dir / "reports"
        
        for directory in [self.active_dir, self.completed_dir, self.reports_dir]:
            directory.mkdir(exist_ok=True)
    
    def create_case_study(
        self, 
        title: str, 
        research_question: str,
        description: str = "",
        llm_providers: List[LLMProvider] = None
    ) -> CaseStudy:
        """Crée une nouvelle étude de cas."""
        
        if llm_providers is None:
            llm_providers = [LLMProvider.OPENAI]
        
        case_id = str(uuid.uuid4())
        case_study = CaseStudy(
            id=case_id,
            title=title,
            research_question=research_question,
            description=description,
            llm_providers=llm_providers,
            status=CaseStatus.DRAFT
        )
        
        # Sauvegarder immédiatement
        self._save_case_study(case_study)
        
        print(f"✅ Nouvelle étude de cas créée: {title}")
        print(f"📋 ID: {case_id}")
        print(f"❓ Question: {research_question}")
        
        return case_study
    
    def load_case_study(self, case_id: str) -> Optional[CaseStudy]:
        """Charge une étude de cas par son ID."""
        
        # Chercher dans les dossiers actifs et terminés
        for directory in [self.active_dir, self.completed_dir]:
            case_file = directory / f"{case_id}.json"
            if case_file.exists():
                try:
                    with open(case_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    return self._deserialize_case_study(data)
                except Exception as e:
                    print(f"❌ Erreur lors du chargement de l'étude {case_id}: {e}")
                    return None
        
        return None
    
    def list_case_studies(self, status_filter: CaseStatus = None) -> List[Dict[str, Any]]:
        """Liste toutes les études de cas avec métadonnées."""
        cases = []
        
        # Scanner les dossiers
        for directory in [self.active_dir, self.completed_dir]:
            for case_file in directory.glob("*.json"):
                try:
                    with open(case_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Filtrer par statut si demandé
                    if status_filter and data.get('status') != status_filter.value:
                        continue
                    
                    # Extraire les métadonnées
                    cases.append({
                        'id': data.get('id'),
                        'title': data.get('title'),
                        'research_question': data.get('research_question'),
                        'status': data.get('status'),
                        'created_date': datetime.fromisoformat(data.get('created_date')),
                        'updated_date': datetime.fromisoformat(data.get('updated_date')),
                        'total_sources': data.get('total_sources_found', 0),
                        'sources_analyzed': data.get('sources_analyzed', 0),
                        'progress': data.get('sources_analyzed', 0) / max(data.get('total_sources_found', 1), 1) * 100
                    })
                    
                except Exception as e:
                    print(f"⚠️ Erreur lors de la lecture de {case_file}: {e}")
                    continue
        
        # Trier par date de mise à jour (plus récent en premier)
        cases.sort(key=lambda x: x['updated_date'], reverse=True)
        return cases
    
    def update_case_study(self, case_study: CaseStudy) -> bool:
        """Met à jour une étude de cas."""
        try:
            case_study.updated_date = datetime.now()
            self._save_case_study(case_study)
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour: {e}")
            return False
    
    def delete_case_study(self, case_id: str) -> bool:
        """Supprime une étude de cas."""
        try:
            for directory in [self.active_dir, self.completed_dir]:
                case_file = directory / f"{case_id}.json"
                if case_file.exists():
                    case_file.unlink()
                    print(f"🗑️ Étude de cas {case_id} supprimée")
                    return True
            return False
        except Exception as e:
            print(f"❌ Erreur lors de la suppression: {e}")
            return False
    
    def archive_case_study(self, case_id: str) -> bool:
        """Archive une étude de cas terminée."""
        try:
            active_file = self.active_dir / f"{case_id}.json"
            completed_file = self.completed_dir / f"{case_id}.json"
            
            if active_file.exists():
                # Déplacer vers les complétés
                active_file.rename(completed_file)
                print(f"📦 Étude de cas {case_id} archivée")
                return True
            return False
        except Exception as e:
            print(f"❌ Erreur lors de l'archivage: {e}")
            return False
    
    def get_case_statistics(self) -> Dict[str, Any]:
        """Retourne des statistiques sur les études de cas."""
        all_cases = self.list_case_studies()
        
        if not all_cases:
            return {
                'total_cases': 0,
                'active_cases': 0,
                'completed_cases': 0,
                'total_sources_analyzed': 0,
                'average_sources_per_case': 0,
                'most_recent_case': None
            }
        
        stats = {
            'total_cases': len(all_cases),
            'active_cases': len([c for c in all_cases if c['status'] != CaseStatus.COMPLETED.value]),
            'completed_cases': len([c for c in all_cases if c['status'] == CaseStatus.COMPLETED.value]),
            'total_sources_analyzed': sum(c['sources_analyzed'] for c in all_cases),
            'average_sources_per_case': sum(c['total_sources'] for c in all_cases) / len(all_cases),
            'most_recent_case': all_cases[0] if all_cases else None
        }
        
        return stats
    
    def _save_case_study(self, case_study: CaseStudy) -> None:
        """Sauvegarde une étude de cas."""
        # Déterminer le dossier selon le statut
        if case_study.status == CaseStatus.COMPLETED:
            target_dir = self.completed_dir
        else:
            target_dir = self.active_dir
        
        case_file = target_dir / f"{case_study.id}.json"
        
        # Sérialiser et sauvegarder
        data = self._serialize_case_study(case_study)
        with open(case_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    def _serialize_case_study(self, case_study: CaseStudy) -> Dict[str, Any]:
        """Sérialise une étude de cas en dictionnaire."""
        data = {
            'id': case_study.id,
            'title': case_study.title,
            'research_question': case_study.research_question,
            'description': case_study.description,
            'status': case_study.status.value,
            'created_date': case_study.created_date.isoformat(),
            'updated_date': case_study.updated_date.isoformat(),
            'llm_providers': [provider.value for provider in case_study.llm_providers],
            'max_sources_per_llm': case_study.max_sources_per_llm,
            'total_sources_found': case_study.total_sources_found,
            'sources_analyzed': case_study.sources_analyzed,
            'analysis_duration_minutes': case_study.analysis_duration_minutes,
            'cost_estimate_usd': case_study.cost_estimate_usd,
            'llm_responses': [],
            'analyzed_sources': [],
            'competitor_insights': [],
            'comparative_scores': case_study.comparative_scores,
            'keyword_analysis': case_study.keyword_analysis,
            'sentiment_analysis': case_study.sentiment_analysis
        }
        
        # Sérialiser les réponses LLM (simplifié pour éviter la complexité)
        for response in case_study.llm_responses:
            data['llm_responses'].append({
                'provider': response.provider.value,
                'model_name': response.model_name,
                'query': response.query,
                'response_text': response.response_text,
                'timestamp': response.timestamp.isoformat(),
                'tokens_used': response.tokens_used,
                'sources_count': len(response.sources)
            })
        
        return data
    
    def _deserialize_case_study(self, data: Dict[str, Any]) -> CaseStudy:
        """Désérialise un dictionnaire en étude de cas."""
        case_study = CaseStudy(
            id=data['id'],
            title=data['title'],
            research_question=data['research_question'],
            description=data.get('description', ''),
            status=CaseStatus(data['status']),
            created_date=datetime.fromisoformat(data['created_date']),
            updated_date=datetime.fromisoformat(data['updated_date']),
            llm_providers=[LLMProvider(p) for p in data.get('llm_providers', ['openai'])],
            max_sources_per_llm=data.get('max_sources_per_llm', 10),
            total_sources_found=data.get('total_sources_found', 0),
            sources_analyzed=data.get('sources_analyzed', 0),
            analysis_duration_minutes=data.get('analysis_duration_minutes', 0.0),
            cost_estimate_usd=data.get('cost_estimate_usd', 0.0),
            comparative_scores=data.get('comparative_scores', {}),
            keyword_analysis=data.get('keyword_analysis', {}),
            sentiment_analysis=data.get('sentiment_analysis', {})
        )
        
        return case_study