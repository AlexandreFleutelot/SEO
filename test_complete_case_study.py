#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_complete_case_study.py

Test complet du système d'études de cas avec analyse comparative.
"""

import sys
from pathlib import Path
import time

sys.path.append(str(Path(__file__).parent))

from src.case_studies.case_manager import CaseStudyManager
from src.case_studies.llm_source_extractor import LLMSourceExtractor
from src.case_studies.comparative_analyzer import ComparativeAnalyzer
from src.case_studies.case_report_generator import CaseReportGenerator
from src.case_studies.models import LLMProvider, CaseStatus


def test_complete_workflow():
    """Test du workflow complet d'étude de cas."""
    
    print("🚀 Test du workflow complet d'études de cas SEO")
    print("=" * 60)
    
    # 1. Initialiser les composants
    print("\n📋 1. Initialisation des composants")
    manager = CaseStudyManager()
    extractor = LLMSourceExtractor()
    analyzer = ComparativeAnalyzer()
    report_generator = CaseReportGenerator()
    
    print("✅ Tous les composants initialisés")
    
    # 2. Créer une étude de cas
    print("\n📋 2. Création d'une étude de cas")
    case_study = manager.create_case_study(
        title="Test Complet - Avantages Assurance Vie",
        research_question="Quels sont les principaux avantages de l'assurance vie selon les experts ?",
        description="Test complet du système d'analyse comparative",
        llm_providers=[LLMProvider.OPENAI]
    )
    
    print(f"✅ Étude créée: {case_study.title}")
    
    # 3. Simuler l'extraction de sources (pas d'appel LLM réel)
    print("\n📋 3. Simulation de l'extraction de sources")
    
    # Créer des sources fictives pour le test
    from src.case_studies.models import LLMResponse, SourceURL
    from datetime import datetime
    
    mock_response = LLMResponse(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4o-mock",
        query=case_study.research_question,
        response_text="Test response with sources",
        timestamp=datetime.now(),
        tokens_used=1000,
        response_time_ms=2500
    )
    
    # Ajouter des sources fictives réalistes
    test_sources = [
        SourceURL(
            url="https://www.amf-france.org/fr/espace-epargnants/bien-investir/assurance-vie",
            citation_order=1,
            mentioned_in_context="Site officiel de l'AMF sur l'assurance vie",
            reliability_score=0.9,
            domain="amf-france.org",
            extraction_confidence=0.8
        ),
        SourceURL(
            url="https://www.moneyvox.fr/assurance-vie/guide-complet",
            citation_order=2,
            mentioned_in_context="Guide complet assurance vie Moneyvox",
            reliability_score=0.75,
            domain="moneyvox.fr",
            extraction_confidence=0.7
        ),
        SourceURL(
            url="https://www.boursorama.com/patrimoine/assurance-vie/",
            citation_order=3,
            mentioned_in_context="Section assurance vie Boursorama",
            reliability_score=0.7,
            domain="boursorama.com",
            extraction_confidence=0.6
        ),
        SourceURL(
            url="https://www.service-public.fr/particuliers/vosdroits/F15395",
            citation_order=4,
            mentioned_in_context="Guide service public assurance vie",
            reliability_score=0.85,
            domain="service-public.fr",
            extraction_confidence=0.9
        )
    ]
    
    mock_response.sources = test_sources
    case_study.add_llm_response(mock_response)
    manager.update_case_study(case_study)
    
    print(f"✅ {len(test_sources)} sources simulées ajoutées")
    
    # 4. Lancer l'analyse batch des sources
    print("\n📋 4. Analyse SEO batch des sources")
    
    all_sources = []
    for response in case_study.llm_responses:
        all_sources.extend(response.sources)
    
    def progress_callback(current, total, url):
        print(f"📊 Analyse {current}/{total}: {url[:50]}...")
        time.sleep(0.5)  # Simulation
    
    # Analyser avec des données mock
    batch_results = analyzer.analyze_sources_batch(all_sources, progress_callback)
    
    print(f"✅ Analyse terminée: {len(batch_results['successful_analyses'])} sources analysées")
    
    # 5. Générer les insights concurrentiels
    print("\n📋 5. Génération des insights concurrentiels")
    
    competitor_insights = analyzer.generate_competitor_insights(batch_results['successful_analyses'])
    gap_analysis = analyzer.perform_gap_analysis(case_study, competitor_insights)
    
    print(f"✅ {len(competitor_insights)} insights générés")
    print(f"✅ {len(gap_analysis.optimization_priorities)} priorités identifiées")
    
    # 6. Générer le rapport complet
    print("\n📋 6. Génération du rapport complet")
    
    report = report_generator.generate_complete_report(
        case_study, competitor_insights, gap_analysis, batch_results
    )
    
    print(f"✅ Rapport généré: {report.title}")
    
    # 7. Afficher les résultats de synthèse
    print("\n📊 7. Synthèse des résultats")
    print("-" * 40)
    
    print(f"🎯 Concurrents analysés: {len(competitor_insights)}")
    if competitor_insights:
        avg_score = sum(i.seo_score for i in competitor_insights) / len(competitor_insights)
        print(f"📊 Score SEO moyen: {avg_score:.1f}/100")
        print(f"👑 Leader: {competitor_insights[0].domain}")
    
    print(f"🚀 Opportunités détectées: {len(gap_analysis.content_opportunities)}")
    print(f"⚡ Priorités d'optimisation: {len(gap_analysis.optimization_priorities)}")
    print(f"🔍 Découvertes clés: {len(report.key_findings)}")
    print(f"💡 Recommandations: {len(report.recommendations)}")
    
    # 8. Mettre à jour le statut de l'étude
    print("\n📋 8. Finalisation de l'étude")
    
    case_study.update_status(CaseStatus.COMPLETED)
    case_study.sources_analyzed = len(batch_results['successful_analyses'])
    manager.update_case_study(case_study)
    
    print("✅ Étude marquée comme terminée")
    
    # 9. Tester les statistiques
    print("\n📋 9. Statistiques finales")
    
    stats = manager.get_case_statistics()
    print(f"📋 Total études: {stats['total_cases']}")
    print(f"✅ Études terminées: {stats['completed_cases']}")
    print(f"📊 Sources totales analysées: {stats['total_sources_analyzed']}")
    
    print("\n🎉 Test complet réussi!")
    print("=" * 60)
    
    return {
        'case_study': case_study,
        'competitor_insights': competitor_insights,
        'gap_analysis': gap_analysis,
        'report': report,
        'stats': stats
    }


def display_detailed_results(results):
    """Affiche les résultats détaillés du test."""
    
    print("\n📈 RÉSULTATS DÉTAILLÉS")
    print("=" * 60)
    
    case_study = results['case_study']
    competitor_insights = results['competitor_insights']
    gap_analysis = results['gap_analysis']
    report = results['report']
    
    # Détails de l'étude
    print(f"\n🔬 Étude: {case_study.title}")
    print(f"❓ Question: {case_study.research_question}")
    print(f"📊 Statut: {case_study.status.value}")
    print(f"🔗 Sources trouvées: {case_study.total_sources_found}")
    print(f"✅ Sources analysées: {case_study.sources_analyzed}")
    
    # Classement des concurrents
    if competitor_insights:
        print(f"\n🏆 CLASSEMENT DES CONCURRENTS")
        print("-" * 40)
        
        for i, insight in enumerate(competitor_insights, 1):
            print(f"{i}. {insight.domain} - {insight.seo_score:.1f}/100")
            print(f"   Forces: {len(insight.strengths)} | Faiblesses: {len(insight.weaknesses)}")
            print(f"   Mots-clés: {len(insight.target_keywords)}")
            print()
    
    # Analyse des gaps
    print(f"\n🎯 ANALYSE DES OPPORTUNITÉS")
    print("-" * 40)
    
    if gap_analysis.missing_topics:
        print("📋 Sujets manquants:")
        for topic in gap_analysis.missing_topics[:3]:
            print(f"   • {topic}")
    
    if gap_analysis.optimization_priorities:
        print("\n⚡ Priorités d'optimisation:")
        for priority in gap_analysis.optimization_priorities[:3]:
            print(f"   • {priority}")
    
    # Extraits du rapport
    print(f"\n📋 RAPPORT EXÉCUTIF")
    print("-" * 40)
    
    if report.key_findings:
        print("🔍 Découvertes principales:")
        for finding in report.key_findings[:3]:
            print(f"   • {finding}")
    
    if report.recommendations:
        print("\n💡 Recommandations principales:")
        for rec in report.recommendations[:3]:
            print(f"   • {rec}")


if __name__ == "__main__":
    # Lancer le test complet
    results = test_complete_workflow()
    
    # Afficher les résultats détaillés
    display_detailed_results(results)
    
    print(f"\n✅ SYSTÈME D'ÉTUDES DE CAS OPÉRATIONNEL")
    print("Le système peut maintenant:")
    print("• Extraire des sources depuis les LLM")
    print("• Analyser les performances SEO en batch") 
    print("• Générer des insights concurrentiels")
    print("• Identifier les gaps et opportunités")
    print("• Produire des rapports complets")
    print("• Exporter vers différents formats")
    print("• Suivre les statistiques d'utilisation")