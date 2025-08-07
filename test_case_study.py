#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_case_study.py

Script de test pour le système d'études de cas.
"""

from src.case_studies.case_manager import CaseStudyManager
from src.case_studies.llm_source_extractor import LLMSourceExtractor
from src.case_studies.models import LLMProvider, SourceURL

def test_case_study_creation():
    """Test de création d'une étude de cas."""
    
    print("🧪 Test du système d'études de cas")
    print("-" * 50)
    
    # Initialiser le gestionnaire
    manager = CaseStudyManager()
    
    # Créer une étude de cas de test
    case_study = manager.create_case_study(
        title="Test - Avantages Assurance Vie",
        research_question="Quels sont les principaux avantages de l'assurance vie ?",
        description="Étude test pour valider le système d'extraction de sources",
        llm_providers=[LLMProvider.OPENAI]
    )
    
    print(f"✅ Étude créée avec ID: {case_study.id}")
    
    # Tester la liste des études
    cases = manager.list_case_studies()
    print(f"📋 {len(cases)} études trouvées")
    
    # Tester l'extracteur de sources (sans réellement appeler les LLM)
    extractor = LLMSourceExtractor()
    print(f"🤖 Extracteur initialisé - OpenAI: {'✅' if extractor.openai_client else '❌'}")
    print(f"🤖 Extracteur initialisé - Anthropic: {'✅' if extractor.anthropic_client else '❌'}")
    
    # Statistiques
    stats = manager.get_case_statistics()
    print(f"📊 Statistiques:")
    print(f"   - Total: {stats['total_cases']}")
    print(f"   - Actives: {stats['active_cases']}")
    print(f"   - Terminées: {stats['completed_cases']}")
    
    print("\n✅ Test de base réussi!")
    return case_study.id

def test_url_extraction():
    """Test d'extraction d'URL depuis du texte."""
    
    print("\n🔍 Test d'extraction d'URLs avec nouvelles améliorations")
    print("-" * 50)
    
    extractor = LLMSourceExtractor()
    
    # Texte de test avec diverses URLs dans le nouveau format
    test_text = """
    Voici les sources fiables sur l'assurance vie:
    
    Source: AMF France - URL: https://www.amf-france.org/fr/espace-epargnants/bien-investir/assurance-vie
    Source: MoneyVox Guide - URL: https://www.moneyvox.fr/assurance-vie/guide-complet
    Source: Service Public - URL: https://www.service-public.fr/particuliers/vosdroits/F15395
    Source: Boursorama Patrimoine - URL: https://www.boursorama.com/patrimoine/assurance-vie/
    Source: Les Echos Finance - URL: https://www.lesechos.fr/finance-marches/banques/assurance-vie-guide-2024
    Source: ACPR Banque France - URL: https://acpr.banque-france.fr/assurance-vie-reglementation
    Source: Capital Magazine - URL: https://www.capital.fr/votre-argent/assurance-vie-avantages-fiscaux
    """
    
    # Extraire les URLs
    sources = extractor._extract_urls_from_response(test_text)
    
    print(f"📄 Texte testé: {len(test_text)} caractères")
    print(f"🔗 URLs extraites avant validation: {len(sources)}")
    
    # Test de validation avancée
    validated_sources = extractor._advanced_url_validation(sources)
    
    print(f"✅ URLs conservées après validation: {len(validated_sources)}")
    
    for i, source in enumerate(validated_sources, 1):
        print(f"{i}. {source.domain} - Confiance: {source.extraction_confidence:.2f}")
        print(f"   URL: {source.url}")
        print(f"   Fiabilité: {source.reliability_score:.2f}")
        print(f"   Contexte: {source.mentioned_in_context[:80]}...")
        print()
    
    return validated_sources


def test_follow_up_extraction():
    """Test de l'extraction avec requêtes de suivi."""
    
    print("\n🔄 Test d'extraction avec suivi automatique")
    print("-" * 50)
    
    # Test du prompt de suivi
    extractor = LLMSourceExtractor()
    
    # Simuler une extraction avec peu de sources initiales
    test_question = "Quels sont les avantages de l'assurance vie en 2024 ?"
    
    # Test du prompt de suivi
    follow_up_prompt = extractor.extraction_prompts["follow_up_sources"].format(
        count=3, 
        question=test_question
    )
    
    print("📋 Prompt de suivi généré:")
    print(follow_up_prompt[:200] + "...")
    
    # Test de validation avancée
    print("\n🔍 Test de validation avancée:")
    
    test_urls = [
        "https://www.amf-france.org/fr/assurance-vie-guide",
        "https://google.com/search?q=assurance+vie",  # Devrait être filtré
        "https://facebook.com/page-assurance",  # Devrait être filtré
        "www.moneyvox.fr",  # Devrait être normalisé
        "https://a.co/short",  # Devrait être filtré (trop court)
        "https://www.capital.fr/argent/assurance-vie-guide-complet",
    ]
    
    mock_sources = []
    for i, url in enumerate(test_urls):
        source = SourceURL(
            url=url,
            citation_order=i+1,
            mentioned_in_context=f"Source {i+1} dans le contexte",
            extraction_confidence=0.7
        )
        mock_sources.append(source)
    
    # Appliquer la validation avancée
    validated = extractor._advanced_url_validation(mock_sources)
    
    print(f"URLs testées: {len(test_urls)}")
    print(f"URLs conservées: {len(validated)}")
    
    for source in validated:
        print(f"✅ Conservé: {source.url}")
    
    return validated

if __name__ == "__main__":
    print("🚀 TEST DU SYSTÈME D'EXTRACTION AMÉLIORÉ")
    print("=" * 60)
    
    case_id = test_case_study_creation()
    sources = test_url_extraction()
    validated_sources = test_follow_up_extraction()
    
    print(f"\n🎉 Tests terminés!")
    print("=" * 60)
    print(f"📋 Étude créée: {case_id}")
    print(f"🔗 {len(sources)} URLs extraites du test d'extraction")
    print(f"✅ {len(validated_sources)} URLs validées dans le test de suivi")
    print(f"\n💡 Améliorations implémentées:")
    print(f"   • Prompts explicites avec demande d'URLs complètes")
    print(f"   • Extraction avec requêtes de suivi automatiques")
    print(f"   • Validation avancée des URLs extraites")
    print(f"   • Filtrage des URLs de recherche et réseaux sociaux")
    print(f"   • Déduplication croisée entre providers")
    print(f"   • Scoring de fiabilité basé sur le domaine")
    print(f"   • Support des réponses JSON structurées")