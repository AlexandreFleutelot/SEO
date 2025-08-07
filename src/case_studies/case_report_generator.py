# -*- coding: utf-8 -*-
"""
case_report_generator.py

Générateur de rapports pour les études de cas SEO.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from .models import CaseStudy, CaseStudyReport, CompetitorInsight, GapAnalysis


class CaseReportGenerator:
    """Générateur de rapports complets pour les études de cas."""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.reports_dir = self.base_path / "data" / "case_studies" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_complete_report(
        self,
        case_study: CaseStudy,
        competitor_insights: List[CompetitorInsight],
        gap_analysis: GapAnalysis,
        batch_results: Dict[str, Any]
    ) -> CaseStudyReport:
        """Génère un rapport complet d'étude de cas."""
        
        print(f"📊 Génération du rapport pour: {case_study.title}")
        
        # Créer le rapport de base
        report = CaseStudyReport(
            case_study_id=case_study.id,
            title=f"Rapport d'Analyse: {case_study.title}",
            executive_summary=self._generate_executive_summary(
                case_study, competitor_insights, gap_analysis
            )
        )
        
        # Ajouter les découvertes clés
        self._add_key_findings(report, competitor_insights, gap_analysis, batch_results)
        
        # Ajouter les recommandations
        self._add_recommendations(report, gap_analysis, competitor_insights)
        
        # Créer la matrice de performance
        report.performance_matrix = self._create_performance_matrix(competitor_insights)
        
        # Analyser les clusters de mots-clés
        report.keyword_clusters = self._analyze_keyword_clusters(competitor_insights)
        
        # Créer le paysage concurrentiel
        report.competitive_landscape = self._create_competitive_landscape(
            competitor_insights, gap_analysis
        )
        
        # Identifier les opportunités marché
        report.market_opportunities = self._identify_market_opportunities(
            gap_analysis, competitor_insights
        )
        
        # Sauvegarder le rapport
        self._save_report(report, case_study.id)
        
        print(f"✅ Rapport généré et sauvegardé pour {case_study.title}")
        
        return report
    
    def _generate_executive_summary(
        self,
        case_study: CaseStudy,
        competitor_insights: List[CompetitorInsight],
        gap_analysis: GapAnalysis
    ) -> str:
        """Génère le résumé exécutif du rapport."""
        
        # Calculs de base
        total_competitors = len(competitor_insights)
        avg_score = sum(i.seo_score for i in competitor_insights) / total_competitors if competitor_insights else 0
        
        best_performer = competitor_insights[0] if competitor_insights else None
        market_leader = best_performer.domain if best_performer else "Non identifié"
        
        opportunity_count = len(gap_analysis.content_opportunities)
        priority_count = len(gap_analysis.optimization_priorities)
        
        summary = f"""
Cette étude de cas analyse {total_competitors} concurrents principaux dans le secteur de la question :
"{case_study.research_question}"

## Résultats Clés

**Performance Marché :**
- Score SEO moyen du secteur : {avg_score:.1f}/100
- Leader du marché : {market_leader}
- Score du leader : {best_performer.seo_score:.1f}/100 si best_performer else "N/A"

**Opportunités Identifiées :**
- {opportunity_count} opportunités de contenu détectées
- {priority_count} priorités d'optimisation définies
- {len(gap_analysis.missing_topics)} sujets manquants sur le marché

**Recommandations Principales :**
Les analyses révèlent plusieurs axes d'amélioration stratégiques pour se positionner 
efficacement face à la concurrence, avec un potentiel d'optimisation significatif 
sur les aspects de contenu et de structure SEO.

*Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*
        """.strip()
        
        return summary
    
    def _add_key_findings(
        self,
        report: CaseStudyReport,
        competitor_insights: List[CompetitorInsight],
        gap_analysis: GapAnalysis,
        batch_results: Dict[str, Any]
    ):
        """Ajoute les découvertes clés au rapport."""
        
        # Analyse de la performance globale
        if competitor_insights:
            avg_score = sum(i.seo_score for i in competitor_insights) / len(competitor_insights)
            report.add_finding(
                f"Score SEO moyen du secteur: {avg_score:.1f}/100",
                "high" if avg_score < 70 else "medium"
            )
            
            # Écart entre leader et suivants
            if len(competitor_insights) > 1:
                score_gap = competitor_insights[0].seo_score - competitor_insights[-1].seo_score
                report.add_finding(
                    f"Écart de performance: {score_gap:.1f} points entre leader et dernier",
                    "high" if score_gap > 30 else "medium"
                )
        
        # Analyse des contenus manquants
        if gap_analysis.missing_topics:
            report.add_finding(
                f"{len(gap_analysis.missing_topics)} sujets clés absents du marché",
                "high"
            )
        
        # Analyse des mots-clés
        if gap_analysis.underrepresented_keywords:
            report.add_finding(
                f"{len(gap_analysis.underrepresented_keywords)} mots-clés sous-exploités",
                "medium"
            )
        
        # Analyse des taux de succès
        stats = batch_results.get('summary_stats', {})
        if stats.get('total_analyzed', 0) > 0:
            success_rate = (len(batch_results.get('successful_analyses', [])) / 
                          stats['total_analyzed']) * 100
            report.add_finding(
                f"Taux de réussite d'analyse: {success_rate:.1f}%",
                "low"
            )
    
    def _add_recommendations(
        self,
        report: CaseStudyReport,
        gap_analysis: GapAnalysis,
        competitor_insights: List[CompetitorInsight]
    ):
        """Ajoute les recommandations stratégiques."""
        
        # Recommandations basées sur les gaps
        for priority in gap_analysis.optimization_priorities[:5]:
            impact = "high" if "HAUTE" in priority else "medium" if "MOYENNE" in priority else "low"
            report.add_recommendation(priority.replace("HAUTE:", "").replace("MOYENNE:", "").replace("TECHNIQUE:", "").strip(), impact)
        
        # Recommandations basées sur les leaders
        if competitor_insights:
            best_performer = competitor_insights[0]
            for strength in best_performer.strengths[:2]:
                report.add_recommendation(
                    f"Adopter la stratégie du leader: {strength}",
                    "high"
                )
        
        # Recommandations d'opportunités de contenu
        for opportunity in gap_analysis.content_opportunities[:3]:
            report.add_recommendation(
                f"Saisir l'opportunité: {opportunity}",
                "medium"
            )
    
    def _create_performance_matrix(
        self,
        competitor_insights: List[CompetitorInsight]
    ) -> Dict[str, Dict[str, float]]:
        """Crée la matrice de performance des concurrents."""
        
        matrix = {}
        
        for insight in competitor_insights:
            matrix[insight.domain] = {
                'seo_score': insight.seo_score,
                'content_strength': len(insight.strengths),
                'weaknesses_count': len(insight.weaknesses),
                'keyword_coverage': len(insight.target_keywords),
                'authority_level': insight.authority_indicators.get('external_sources', 0),
                'market_position': insight.position_rank
            }
        
        return matrix
    
    def _analyze_keyword_clusters(
        self,
        competitor_insights: List[CompetitorInsight]
    ) -> Dict[str, List[str]]:
        """Analyse les clusters de mots-clés par thématique."""
        
        # Collecter tous les mots-clés
        all_keywords = []
        for insight in competitor_insights:
            all_keywords.extend(insight.target_keywords)
        
        # Groupement simple par similarité (première approche)
        clusters = {
            'assurance': [kw for kw in all_keywords if any(term in kw.lower() for term in ['assurance', 'assureur'])],
            'finance': [kw for kw in all_keywords if any(term in kw.lower() for term in ['finance', 'financier', 'placement'])],
            'avantages': [kw for kw in all_keywords if any(term in kw.lower() for term in ['avantage', 'bénéfice', 'intérêt'])],
            'produits': [kw for kw in all_keywords if any(term in kw.lower() for term in ['produit', 'contrat', 'offre'])],
            'autres': [kw for kw in all_keywords if not any(
                any(term in kw.lower() for term in cluster_terms) 
                for cluster_terms in [
                    ['assurance', 'assureur'],
                    ['finance', 'financier', 'placement'],
                    ['avantage', 'bénéfice', 'intérêt'],
                    ['produit', 'contrat', 'offre']
                ]
            )]
        }
        
        # Nettoyer les clusters vides
        clusters = {k: list(set(v)) for k, v in clusters.items() if v}
        
        return clusters
    
    def _create_competitive_landscape(
        self,
        competitor_insights: List[CompetitorInsight],
        gap_analysis: GapAnalysis
    ) -> Dict[str, Any]:
        """Crée une vue d'ensemble du paysage concurrentiel."""
        
        landscape = {
            'market_segments': {},
            'positioning_map': {},
            'competitive_intensity': {},
            'market_gaps': gap_analysis.market_positioning
        }
        
        # Segmenter les concurrents par performance
        if competitor_insights:
            high_performers = [i for i in competitor_insights if i.seo_score >= 80]
            medium_performers = [i for i in competitor_insights if 60 <= i.seo_score < 80]
            low_performers = [i for i in competitor_insights if i.seo_score < 60]
            
            landscape['market_segments'] = {
                'leaders': len(high_performers),
                'challengers': len(medium_performers),
                'followers': len(low_performers)
            }
            
            # Carte de positionnement (score vs autorité)
            for insight in competitor_insights:
                authority_score = insight.authority_indicators.get('external_sources', 0)
                landscape['positioning_map'][insight.domain] = {
                    'seo_score': insight.seo_score,
                    'authority_score': min(authority_score * 5, 100),  # Normaliser sur 100
                    'category': 'leader' if insight.seo_score >= 80 else 'challenger' if insight.seo_score >= 60 else 'follower'
                }
        
        return landscape
    
    def _identify_market_opportunities(
        self,
        gap_analysis: GapAnalysis,
        competitor_insights: List[CompetitorInsight]
    ) -> List[str]:
        """Identifie les opportunités de marché."""
        
        opportunities = []
        
        # Opportunités basées sur les gaps
        for topic in gap_analysis.missing_topics:
            opportunities.append(f"Créer du contenu leader sur: {topic}")
        
        # Opportunités basées sur les mots-clés sous-exploités
        for keyword in gap_analysis.underrepresented_keywords[:3]:
            opportunities.append(f"Se positionner sur le mot-clé: {keyword}")
        
        # Opportunités basées sur les faiblesses communes
        if competitor_insights:
            common_weaknesses = {}
            for insight in competitor_insights:
                for weakness in insight.weaknesses:
                    common_weaknesses[weakness] = common_weaknesses.get(weakness, 0) + 1
            
            # Faiblesses partagées par plus de 50% des concurrents
            threshold = len(competitor_insights) * 0.5
            for weakness, count in common_weaknesses.items():
                if count >= threshold:
                    opportunities.append(f"Exploiter la faiblesse commune: {weakness}")
        
        return opportunities[:10]  # Limiter à 10 opportunités principales
    
    def _save_report(self, report: CaseStudyReport, case_id: str):
        """Sauvegarde le rapport en différents formats."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"case_report_{case_id}_{timestamp}"
        
        # Sauvegarder en JSON
        json_path = self.reports_dir / f"{base_filename}.json"
        report_dict = {
            'case_study_id': report.case_study_id,
            'title': report.title,
            'executive_summary': report.executive_summary,
            'generated_date': report.generated_date.isoformat(),
            'key_findings': report.key_findings,
            'recommendations': report.recommendations,
            'competitive_landscape': report.competitive_landscape,
            'market_opportunities': report.market_opportunities,
            'performance_matrix': report.performance_matrix,
            'keyword_clusters': report.keyword_clusters,
            'sentiment_breakdown': report.sentiment_breakdown
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False, default=str)
        
        report.file_paths['json'] = str(json_path)
        
        print(f"💾 Rapport sauvegardé: {json_path}")
    
    def generate_visual_charts(
        self,
        competitor_insights: List[CompetitorInsight],
        gap_analysis: GapAnalysis
    ) -> Dict[str, go.Figure]:
        """Génère les graphiques visuels pour le rapport."""
        
        charts = {}
        
        if not competitor_insights:
            return charts
        
        # 1. Graphique de performance globale
        fig_performance = go.Figure()
        
        domains = [insight.domain for insight in competitor_insights]
        scores = [insight.seo_score for insight in competitor_insights]
        colors = ['#1f77b4' if i == 0 else '#ff7f0e' if i < 3 else '#2ca02c' 
                 for i in range(len(competitor_insights))]
        
        fig_performance.add_trace(go.Bar(
            x=domains,
            y=scores,
            marker_color=colors,
            name='Score SEO'
        ))
        
        fig_performance.update_layout(
            title='Performance SEO des Concurrents',
            xaxis_title='Concurrent',
            yaxis_title='Score SEO (/100)',
            showlegend=False
        )
        
        charts['performance_comparison'] = fig_performance
        
        # 2. Matrice de positionnement
        if len(competitor_insights) > 1:
            fig_positioning = go.Figure()
            
            seo_scores = [i.seo_score for i in competitor_insights]
            authority_scores = [i.authority_indicators.get('external_sources', 0) * 5 for i in competitor_insights]
            
            fig_positioning.add_trace(go.Scatter(
                x=authority_scores,
                y=seo_scores,
                mode='markers+text',
                text=[i.domain[:10] + '...' if len(i.domain) > 10 else i.domain for i in competitor_insights],
                textposition='top center',
                marker=dict(
                    size=10,
                    color=seo_scores,
                    colorscale='Viridis',
                    showscale=True
                )
            ))
            
            fig_positioning.update_layout(
                title='Matrice de Positionnement',
                xaxis_title='Autorité (Nb sources * 5)',
                yaxis_title='Score SEO'
            )
            
            charts['positioning_matrix'] = fig_positioning
        
        # 3. Distribution des mots-clés
        all_keywords = []
        for insight in competitor_insights:
            all_keywords.extend(insight.target_keywords)
        
        if all_keywords:
            keyword_counts = {}
            for kw in all_keywords:
                keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
            
            # Top 10 des mots-clés les plus mentionnés
            top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            if top_keywords:
                fig_keywords = go.Figure()
                
                keywords, counts = zip(*top_keywords)
                
                fig_keywords.add_trace(go.Bar(
                    y=keywords,
                    x=counts,
                    orientation='h',
                    marker_color='#2ca02c'
                ))
                
                fig_keywords.update_layout(
                    title='Mots-clés les Plus Mentionnés',
                    xaxis_title='Fréquence',
                    yaxis_title='Mot-clé'
                )
                
                charts['keyword_frequency'] = fig_keywords
        
        return charts
    
    def export_to_excel(self, report: CaseStudyReport, case_id: str) -> str:
        """Exporte le rapport vers Excel (nécessite openpyxl)."""
        try:
            import pandas as pd
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_path = self.reports_dir / f"case_report_{case_id}_{timestamp}.xlsx"
            
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                # Feuille résumé
                summary_data = {
                    'Métrique': ['Titre', 'Date de génération', 'Nombre de découvertes', 'Nombre de recommandations'],
                    'Valeur': [
                        report.title,
                        report.generated_date.strftime('%d/%m/%Y %H:%M'),
                        len(report.key_findings),
                        len(report.recommendations)
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Résumé', index=False)
                
                # Feuille découvertes
                if report.key_findings:
                    findings_df = pd.DataFrame({'Découvertes Clés': report.key_findings})
                    findings_df.to_excel(writer, sheet_name='Découvertes', index=False)
                
                # Feuille recommandations
                if report.recommendations:
                    reco_df = pd.DataFrame({'Recommandations': report.recommendations})
                    reco_df.to_excel(writer, sheet_name='Recommandations', index=False)
                
                # Feuille performance
                if report.performance_matrix:
                    perf_df = pd.DataFrame(report.performance_matrix).T
                    perf_df.to_excel(writer, sheet_name='Performance', index=True)
            
            report.file_paths['excel'] = str(excel_path)
            print(f"📊 Rapport Excel exporté: {excel_path}")
            
            return str(excel_path)
            
        except ImportError:
            print("⚠️ pandas non disponible pour l'export Excel")
            return ""
        except Exception as e:
            print(f"❌ Erreur export Excel: {e}")
            return ""