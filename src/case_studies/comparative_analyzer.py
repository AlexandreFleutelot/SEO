# -*- coding: utf-8 -*-
"""
comparative_analyzer.py

Analyseur comparatif pour les études de cas SEO.
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# Ajouter le path pour les imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from page_analyzer import PageAnalyzer
except ImportError:
    # Fallback pour les tests - créer une classe mock
    class PageAnalyzer:
        def analyze_page(self, url):
            return {
                'analysis_id': f'mock_{hash(url)}',
                'scores': {
                    'content_score': 75.0,
                    'structure_score': 80.0,
                    'linking_score': 70.0,
                    'performance_score': 65.0,
                    'overall_score': 72.5
                },
                'raw_analysis': {
                    'content': {'word_count': 1500, 'external_links': []},
                    'structure': {'headings': [], 'title': 'Mock Title', 'meta_description': 'Mock description'}
                }
            }
from .models import CaseStudy, CompetitorInsight, GapAnalysis, SourceURL


class ComparativeAnalyzer:
    """Analyseur comparatif pour les études de cas SEO."""
    
    def __init__(self):
        self.page_analyzer = PageAnalyzer()
        self.analysis_cache = {}
    
    def analyze_sources_batch(
        self, 
        sources: List[SourceURL], 
        progress_callback=None
    ) -> Dict[str, Any]:
        """Analyse un lot de sources en batch."""
        
        results = {
            'successful_analyses': [],
            'failed_analyses': [],
            'summary_stats': {},
            'comparative_scores': {}
        }
        
        total_sources = len(sources)
        print(f"🚀 Début de l'analyse batch de {total_sources} sources")
        
        for i, source in enumerate(sources):
            try:
                if progress_callback:
                    progress_callback(i + 1, total_sources, source.url)
                
                # Vérifier le cache
                cache_key = f"{source.domain}_{hash(source.url)}"
                if cache_key in self.analysis_cache:
                    print(f"📋 Cache hit pour {source.domain}")
                    analysis = self.analysis_cache[cache_key]
                else:
                    # Analyser la page
                    print(f"🔍 Analyse de {source.domain}...")
                    analysis = self.page_analyzer.analyze_page(source.url)
                    
                    if analysis:
                        self.analysis_cache[cache_key] = analysis
                        print(f"✅ {source.domain} analysé avec succès")
                    else:
                        print(f"❌ Échec de l'analyse de {source.domain}")
                        continue
                
                # Enrichir avec les données de source
                analysis['case_study_metadata'] = {
                    'source_url': source.url,
                    'domain': source.domain,
                    'reliability_score': source.reliability_score,
                    'extraction_confidence': source.extraction_confidence,
                    'citation_order': source.citation_order
                }
                
                # Marquer la source comme analysée
                source.is_analyzed = True
                source.analysis_id = analysis.get('analysis_id')
                
                results['successful_analyses'].append(analysis)
                
            except Exception as e:
                error_info = {
                    'url': source.url,
                    'domain': source.domain,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                results['failed_analyses'].append(error_info)
                print(f"❌ Erreur lors de l'analyse de {source.domain}: {e}")
        
        # Calculer les statistiques de synthèse
        results['summary_stats'] = self._calculate_batch_stats(results['successful_analyses'])
        
        # Calculer les scores comparatifs
        results['comparative_scores'] = self._calculate_comparative_scores(results['successful_analyses'])
        
        print(f"📊 Analyse batch terminée: {len(results['successful_analyses'])}/{total_sources} réussies")
        
        return results
    
    def generate_competitor_insights(self, analyses: List[Dict[str, Any]]) -> List[CompetitorInsight]:
        """Génère des insights concurrentiels à partir des analyses."""
        
        insights = []
        
        # Trier par score SEO global
        sorted_analyses = sorted(
            analyses, 
            key=lambda x: x.get('scores', {}).get('overall_score', 0), 
            reverse=True
        )
        
        for rank, analysis in enumerate(sorted_analyses, 1):
            try:
                metadata = analysis.get('case_study_metadata', {})
                scores = analysis.get('scores', {})
                raw_data = analysis.get('raw_analysis', {})
                
                # Identifier les forces
                strengths = self._identify_strengths(scores, raw_data)
                
                # Identifier les faiblesses  
                weaknesses = self._identify_weaknesses(scores, raw_data)
                
                # Extraire l'approche de contenu
                content_approach = self._analyze_content_approach(raw_data)
                
                # Extraire les mots-clés cibles
                target_keywords = self._extract_target_keywords(raw_data)
                
                insight = CompetitorInsight(
                    domain=metadata.get('domain', ''),
                    url=metadata.get('source_url', ''),
                    seo_score=scores.get('overall_score', 0),
                    position_rank=rank,
                    strengths=strengths,
                    weaknesses=weaknesses,
                    content_approach=content_approach,
                    target_keywords=target_keywords,
                    authority_indicators=self._extract_authority_indicators(raw_data)
                )
                
                insights.append(insight)
                
            except Exception as e:
                print(f"⚠️ Erreur génération insight: {e}")
                continue
        
        return insights
    
    def perform_gap_analysis(
        self, 
        case_study: CaseStudy, 
        competitor_insights: List[CompetitorInsight]
    ) -> GapAnalysis:
        """Effectue une analyse des gaps concurrentiels."""
        
        # Analyser les topics manquants
        all_content_approaches = [insight.content_approach for insight in competitor_insights]
        missing_topics = self._identify_missing_topics(all_content_approaches)
        
        # Analyser les mots-clés sous-représentés
        all_keywords = []
        for insight in competitor_insights:
            all_keywords.extend(insight.target_keywords)
        
        underrepresented_keywords = self._find_underrepresented_keywords(all_keywords)
        
        # Identifier les opportunités de contenu
        content_opportunities = self._identify_content_opportunities(competitor_insights)
        
        # Identifier les avantages concurrentiels
        competitive_advantages = self._identify_competitive_advantages(competitor_insights)
        
        # Définir les priorités d'optimisation
        optimization_priorities = self._define_optimization_priorities(
            missing_topics, 
            underrepresented_keywords,
            competitor_insights
        )
        
        # Analyser le positionnement marché
        market_positioning = self._analyze_market_positioning(competitor_insights)
        
        return GapAnalysis(
            missing_topics=missing_topics,
            underrepresented_keywords=underrepresented_keywords,
            content_opportunities=content_opportunities,
            competitive_advantages=competitive_advantages,
            optimization_priorities=optimization_priorities,
            market_positioning=market_positioning
        )
    
    def _calculate_batch_stats(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcule les statistiques de synthèse du batch."""
        if not analyses:
            return {}
        
        all_scores = [a.get('scores', {}) for a in analyses]
        
        stats = {
            'total_analyzed': len(analyses),
            'average_scores': {},
            'best_performers': {},
            'worst_performers': {},
            'score_distribution': {}
        }
        
        # Calculer les moyennes par catégorie
        score_categories = ['content_score', 'structure_score', 'linking_score', 'performance_score', 'overall_score']
        
        for category in score_categories:
            values = [scores.get(category, 0) for scores in all_scores]
            if values:
                stats['average_scores'][category] = sum(values) / len(values)
                stats['best_performers'][category] = max(values)
                stats['worst_performers'][category] = min(values)
        
        return stats
    
    def _calculate_comparative_scores(self, analyses: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Calcule les scores comparatifs normalisés."""
        comparative_scores = {}
        
        for analysis in analyses:
            domain = analysis.get('case_study_metadata', {}).get('domain', 'unknown')
            scores = analysis.get('scores', {})
            
            comparative_scores[domain] = {
                'content_score': scores.get('content_score', 0),
                'structure_score': scores.get('structure_score', 0),
                'linking_score': scores.get('linking_score', 0),
                'performance_score': scores.get('performance_score', 0),
                'overall_score': scores.get('overall_score', 0),
                'reliability_weight': analysis.get('case_study_metadata', {}).get('reliability_score', 0.5)
            }
        
        return comparative_scores
    
    def _identify_strengths(self, scores: Dict[str, float], raw_data: Dict[str, Any]) -> List[str]:
        """Identifie les forces d'un concurrent."""
        strengths = []
        
        # Scores élevés (> 80)
        high_scores = {k: v for k, v in scores.items() if v > 80}
        for category, score in high_scores.items():
            strengths.append(f"Excellence en {category.replace('_', ' ')}: {score:.1f}/100")
        
        # Analyse du contenu
        content = raw_data.get('content', {})
        if content.get('word_count', 0) > 2000:
            strengths.append("Contenu très détaillé et complet")
        
        if len(content.get('external_links', [])) > 10:
            strengths.append("Nombreuses sources externes de qualité")
        
        # Analyse de la structure
        structure = raw_data.get('structure', {})
        if len(structure.get('headings', [])) > 5:
            strengths.append("Structure de contenu bien organisée")
        
        return strengths[:5]  # Limiter à 5 forces principales
    
    def _identify_weaknesses(self, scores: Dict[str, float], raw_data: Dict[str, Any]) -> List[str]:
        """Identifie les faiblesses d'un concurrent."""
        weaknesses = []
        
        # Scores faibles (< 60)
        low_scores = {k: v for k, v in scores.items() if v < 60}
        for category, score in low_scores.items():
            weaknesses.append(f"Faiblesse en {category.replace('_', ' ')}: {score:.1f}/100")
        
        # Analyse spécifique
        content = raw_data.get('content', {})
        if content.get('word_count', 0) < 500:
            weaknesses.append("Contenu trop court, manque de profondeur")
        
        structure = raw_data.get('structure', {})
        if not structure.get('meta_description'):
            weaknesses.append("Meta description manquante")
        
        return weaknesses[:5]  # Limiter à 5 faiblesses principales
    
    def _analyze_content_approach(self, raw_data: Dict[str, Any]) -> str:
        """Analyse l'approche de contenu d'un concurrent."""
        content = raw_data.get('content', {})
        
        word_count = content.get('word_count', 0)
        has_lists = len(content.get('lists', [])) > 0
        has_images = len(raw_data.get('structure', {}).get('images', [])) > 0
        
        if word_count > 2000:
            approach = "Contenu long-forme détaillé"
        elif word_count > 1000:
            approach = "Contenu de taille moyenne"
        else:
            approach = "Contenu concis"
        
        if has_lists and has_images:
            approach += " avec éléments visuels et listes structurées"
        elif has_lists:
            approach += " avec listes structurées"
        elif has_images:
            approach += " avec support visuel"
        
        return approach
    
    def _extract_target_keywords(self, raw_data: Dict[str, Any]) -> List[str]:
        """Extrait les mots-clés cibles probables."""
        keywords = []
        
        # Mots-clés du titre
        structure = raw_data.get('structure', {})
        title = structure.get('title', '').lower()
        if title:
            # Extraire les mots significatifs (> 3 caractères, pas de mots vides)
            title_words = [w for w in title.split() if len(w) > 3 and w not in ['dans', 'avec', 'pour', 'cette', 'sont']]
            keywords.extend(title_words[:5])
        
        # Mots-clés des headings
        headings = structure.get('headings', [])
        for heading in headings[:3]:  # Premiers headings seulement
            heading_text = heading.get('text', '').lower()
            heading_words = [w for w in heading_text.split() if len(w) > 3]
            keywords.extend(heading_words[:3])
        
        # Nettoyer et dédupliquer
        keywords = list(set([k.strip('.,!?:;') for k in keywords if k]))
        
        return keywords[:10]  # Limiter à 10 mots-clés
    
    def _extract_authority_indicators(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les indicateurs d'autorité."""
        indicators = {}
        
        content = raw_data.get('content', {})
        structure = raw_data.get('structure', {})
        
        # Nombre de sources externes
        indicators['external_sources'] = len(content.get('external_links', []))
        
        # Longueur du contenu
        indicators['content_depth'] = content.get('word_count', 0)
        
        # Structure organisée
        indicators['content_structure'] = len(structure.get('headings', []))
        
        # Présence de schema markup
        indicators['structured_data'] = bool(structure.get('schema_markup'))
        
        return indicators
    
    def _identify_missing_topics(self, content_approaches: List[str]) -> List[str]:
        """Identifie les topics manquants dans le paysage concurrentiel."""
        # Analyse simple basée sur les approches de contenu
        common_topics = ['avantages', 'inconvénients', 'comparaison', 'guide', 'conseils']
        mentioned_topics = []
        
        for approach in content_approaches:
            approach_lower = approach.lower()
            for topic in common_topics:
                if topic in approach_lower:
                    mentioned_topics.append(topic)
        
        missing = [topic for topic in common_topics if topic not in mentioned_topics]
        return missing
    
    def _find_underrepresented_keywords(self, all_keywords: List[str]) -> List[str]:
        """Trouve les mots-clés sous-représentés."""
        keyword_counts = {}
        for keyword in all_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Mots-clés mentionnés seulement 1-2 fois
        underrepresented = [k for k, count in keyword_counts.items() if count <= 2]
        
        return underrepresented[:10]
    
    def _identify_content_opportunities(self, insights: List[CompetitorInsight]) -> List[str]:
        """Identifie les opportunités de contenu."""
        opportunities = []
        
        # Analyser les faiblesses communes
        common_weaknesses = {}
        for insight in insights:
            for weakness in insight.weaknesses:
                common_weaknesses[weakness] = common_weaknesses.get(weakness, 0) + 1
        
        # Les faiblesses les plus communes sont des opportunités
        for weakness, count in common_weaknesses.items():
            if count >= len(insights) * 0.5:  # Plus de 50% des concurrents
                opportunities.append(f"Améliorer: {weakness}")
        
        return opportunities[:5]
    
    def _identify_competitive_advantages(self, insights: List[CompetitorInsight]) -> List[str]:
        """Identifie les avantages concurrentiels potentiels."""
        advantages = []
        
        if insights:
            best_performer = insights[0]  # Premier = meilleur score
            advantages.extend([f"S'inspirer de: {strength}" for strength in best_performer.strengths[:3]])
        
        return advantages
    
    def _define_optimization_priorities(
        self, 
        missing_topics: List[str],
        underrepresented_keywords: List[str], 
        insights: List[CompetitorInsight]
    ) -> List[str]:
        """Définit les priorités d'optimisation."""
        priorities = []
        
        # Topics manquants = haute priorité
        priorities.extend([f"HAUTE: Créer du contenu sur '{topic}'" for topic in missing_topics[:3]])
        
        # Mots-clés sous-représentés = priorité moyenne
        priorities.extend([f"MOYENNE: Optimiser pour '{keyword}'" for keyword in underrepresented_keywords[:3]])
        
        # Faiblesses communes = priorité technique
        if insights:
            avg_content_score = sum(i.seo_score for i in insights) / len(insights)
            if avg_content_score < 70:
                priorities.append("TECHNIQUE: Améliorer la qualité générale du contenu")
        
        return priorities
    
    def _analyze_market_positioning(self, insights: List[CompetitorInsight]) -> Dict[str, Any]:
        """Analyse le positionnement marché."""
        if not insights:
            return {}
        
        positioning = {
            'market_leader': insights[0].domain if insights else None,
            'average_score': sum(i.seo_score for i in insights) / len(insights),
            'score_range': {
                'min': min(i.seo_score for i in insights),
                'max': max(i.seo_score for i in insights)
            },
            'content_approaches': list(set(i.content_approach for i in insights)),
            'opportunity_score': 100 - (sum(i.seo_score for i in insights) / len(insights))
        }
        
        return positioning