# -*- coding: utf-8 -*-
"""
data_loader.py

Utilitaires pour charger et traiter les données des rapports SEO.
Conçu pour être facilement adapté vers une API backend.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd


class SEODataLoader:
    """Chargeur de données pour les rapports SEO."""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.reports_raw_path = self.base_path / "reports" / "raw"
        self.reports_scores_path = self.base_path / "reports" / "scores"
    
    def get_reports_last_modified(self) -> float:
        """Retourne l'horodatage de la dernière modification des rapports."""
        max_mtime = 0
        
        # Vérifier les fichiers raw
        if self.reports_raw_path.exists():
            for file_path in self.reports_raw_path.glob("*.json"):
                mtime = file_path.stat().st_mtime
                max_mtime = max(max_mtime, mtime)
        
        # Vérifier les fichiers scores
        if self.reports_scores_path.exists():
            for file_path in self.reports_scores_path.glob("*.json"):
                mtime = file_path.stat().st_mtime
                max_mtime = max(max_mtime, mtime)
        
        return max_mtime
    
    def get_available_reports(self) -> List[Dict[str, Any]]:
        """Retourne la liste des rapports disponibles."""
        reports = []
        
        if not self.reports_raw_path.exists():
            return reports
        
        for raw_file in self.reports_raw_path.glob("report_*.json"):
            try:
                with open(raw_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Chercher le rapport de scores correspondant
                score_file = self.reports_scores_path / raw_file.name.replace("report_", "scores_")
                has_scores = score_file.exists()
                
                # Extraire les métadonnées
                url = data.get("url", "Unknown")
                domain = self._extract_domain(url)
                
                # Date de création du fichier
                created_date = datetime.fromtimestamp(raw_file.stat().st_mtime)
                
                reports.append({
                    "id": raw_file.stem,
                    "url": url,
                    "domain": domain,
                    "created_date": created_date,
                    "has_scores": has_scores,
                    "raw_file": str(raw_file),
                    "score_file": str(score_file) if has_scores else None
                })
                
            except Exception as e:
                print(f"Erreur lors du chargement de {raw_file}: {e}")
                continue
        
        # Trier par date de création (plus récent en premier)
        reports.sort(key=lambda x: x["created_date"], reverse=True)
        return reports
    
    def load_raw_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Charge un rapport raw complet."""
        raw_file = self.reports_raw_path / f"{report_id}.json"
        
        if not raw_file.exists():
            return None
        
        try:
            with open(raw_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement du rapport raw {report_id}: {e}")
            return None
    
    def load_score_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Charge un rapport de scores."""
        score_file = self.reports_scores_path / f"{report_id.replace('report_', 'scores_')}.json"
        
        if not score_file.exists():
            return None
        
        try:
            with open(score_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement du rapport de scores {report_id}: {e}")
            return None
    
    def get_reports_comparison_data(self, report_ids: List[str]) -> pd.DataFrame:
        """Prépare les données pour la comparaison entre rapports."""
        comparison_data = []
        
        for report_id in report_ids:
            score_report = self.load_score_report(report_id)
            if not score_report:
                continue
            
            # Extraire les scores principaux
            global_analysis = score_report.get("global_analysis", {})
            category_scores = score_report.get("category_scores", {})
            
            row_data = {
                "report_id": report_id,
                "url": score_report.get("url", ""),
                "domain": self._extract_domain(score_report.get("url", "")),
                "analysis_date": score_report.get("analysis_date", ""),
                "global_score": global_analysis.get("global_score", 0),
                "performance_level": global_analysis.get("performance_level", ""),
            }
            
            # Ajouter les scores par catégorie
            for category, data in category_scores.items():
                if isinstance(data, dict) and "score" in data:
                    row_data[f"{category}_score"] = data["score"]
            
            comparison_data.append(row_data)
        
        return pd.DataFrame(comparison_data)
    
    def get_category_trends(self, report_ids: List[str]) -> Dict[str, List[float]]:
        """Analyse les tendances des scores par catégorie."""
        trends = {
            "content_semantics": [],
            "technical_structure": [],
            "internal_linking": [],
            "performance": [],
            "aio_optimization": [],
            "llm_analysis": []
        }
        
        for report_id in sorted(report_ids):  # Trier pour avoir un ordre chronologique
            score_report = self.load_score_report(report_id)
            if not score_report:
                continue
            
            category_scores = score_report.get("category_scores", {})
            
            for category in trends.keys():
                if category in category_scores and "score" in category_scores[category]:
                    trends[category].append(category_scores[category]["score"])
                else:
                    trends[category].append(0)
        
        return trends
    
    def extract_recommendations(self, report_id: str) -> Dict[str, List[str]]:
        """Extrait toutes les recommandations d'un rapport."""
        raw_report = self.load_raw_report(report_id)
        if not raw_report:
            return {}
        
        recommendations = {}
        
        # Recommandations des analyses LLM
        llm_analysis = raw_report.get("analysis_results", {}).get("category_6_llm_analysis", {})
        for key, analysis in llm_analysis.items():
            if isinstance(analysis, dict) and "recommendations" in analysis:
                recommendations[key] = analysis["recommendations"]
        
        # Recommandations des analyses améliorées
        enhanced_structure = raw_report.get("analysis_results", {}).get("enhanced_structure_analysis", {})
        for key, analysis in enhanced_structure.items():
            if isinstance(analysis, dict) and "recommendations" in analysis:
                recommendations[f"enhanced_{key}"] = analysis["recommendations"]
        
        return recommendations
    
    def get_performance_metrics(self, report_id: str) -> Dict[str, Any]:
        """Extrait les métriques de performance détaillées."""
        raw_report = self.load_raw_report(report_id)
        if not raw_report:
            return {}
        
        performance = raw_report.get("analysis_results", {}).get("category_4_performance", {})
        
        metrics = {}
        
        # Desktop performance
        desktop = performance.get("4.1_4.2_desktop_performance", {})
        if not desktop.get("error"):
            metrics["desktop"] = {
                "LCP": desktop.get("LCP_ms"),
                "INP": desktop.get("INP_ms"),
                "CLS": desktop.get("CLS_score")
            }
        
        # Mobile performance
        mobile = performance.get("4.1_4.2_mobile_performance", {})
        if not mobile.get("error"):
            metrics["mobile"] = {
                "LCP": mobile.get("LCP_ms"),
                "INP": mobile.get("INP_ms"),
                "CLS": mobile.get("CLS_score")
            }
        
        return metrics
    
    def get_enhanced_insights(self, report_id: str) -> Dict[str, Any]:
        """Extrait les insights des analyses améliorées."""
        raw_report = self.load_raw_report(report_id)
        if not raw_report:
            return {}
        
        enhanced_content = raw_report.get("analysis_results", {}).get("enhanced_content_analysis", {})
        enhanced_structure = raw_report.get("analysis_results", {}).get("enhanced_structure_analysis", {})
        
        insights = {}
        
        # Insights contenu
        if enhanced_content:
            insights["content"] = {
                "informational_density_score": enhanced_content.get("1.1_informational_density", {}).get("informational_density_score"),
                "naturalness_score": enhanced_content.get("1.3_ai_generated_detection", {}).get("naturalness_score"),
                "content_authenticity": enhanced_content.get("1.3_ai_generated_detection", {}).get("content_authenticity"),
                "data_originality_score": enhanced_content.get("1.4_original_data", {}).get("data_originality_score"),
                "nap_consistency_score": enhanced_content.get("1.5_nap_consistency", {}).get("nap_consistency_score")
            }
        
        # Insights structure
        if enhanced_structure:
            insights["structure"] = {
                "ssr_compatibility_score": enhanced_structure.get("2.1_ssr_javascript", {}).get("ssr_compatibility_score"),
                "freshness_score": enhanced_structure.get("2.2_year_metadata", {}).get("freshness_score"),
                "freshness_level": enhanced_structure.get("2.2_year_metadata", {}).get("freshness_level"),
                "structured_data_quality_score": enhanced_structure.get("2.3_structured_data_relevance", {}).get("structured_data_quality_score"),
                "llms_txt_status": enhanced_structure.get("2.4_llms_txt_status", {}).get("status")
            }
        
        return insights
    
    def _extract_domain(self, url: str) -> str:
        """Extrait le domaine d'une URL."""
        if not url:
            return "Unknown"
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return "Unknown"


def get_mock_data_for_demo():
    """Génère des données de démonstration si aucun rapport n'est disponible."""
    return {
        "demo_scores": {
            "content_semantics": 85.2,
            "technical_structure": 72.1,
            "internal_linking": 68.5,
            "performance": 45.3,
            "aio_optimization": 38.7,
            "llm_analysis": 71.2
        },
        "demo_trends": {
            "dates": ["2025-01-01", "2025-01-15", "2025-02-01", "2025-02-15"],
            "scores": [65.2, 68.1, 71.5, 73.8]
        },
        "demo_recommendations": [
            "Ajouter l'année 2025 dans le titre et la meta description",
            "Implémenter des données structurées Schema.org",
            "Optimiser les Core Web Vitals (LCP > 2.5s)",
            "Améliorer le maillage interne avec des ancres descriptives",
            "Intégrer plus de données originales et d'études internes"
        ]
    }


if __name__ == "__main__":
    # Test du chargeur
    loader = SEODataLoader()
    reports = loader.get_available_reports()
    
    print(f"Rapports disponibles: {len(reports)}")
    for report in reports[:3]:  # Afficher les 3 premiers
        print(f"- {report['domain']} ({report['created_date'].strftime('%Y-%m-%d %H:%M')})")