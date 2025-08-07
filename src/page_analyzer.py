# -*- coding: utf-8 -*-
"""
page_analyzer.py

Ce script est l'orchestrateur principal de l'outil d'analyse SEO.
Il importe les fonctions d'analyse des différents modules de catégories
et génère un rapport complet pour une URL donnée.

Pour que ce script fonctionne, assurez-vous que les fichiers suivants
sont dans le répertoire utils:
- content.py
- structure.py
- linking.py
- performance.py
- aio.py

Dépendances à installer :
pip install requests beautifulsoup4 spacy datefinder

Modèle de langue pour le français :
python -m spacy download fr_core_news_sm
"""

import requests
import json
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Importation des fonctions d'analyse depuis les modules de catégories ---
from .utils.content import (
    get_main_text,
    analyze_richness_and_coverage,
    analyze_style_clarity,
    analyze_sources_reliability,
    analyze_freshness
)
from .utils.structure import (
    analyze_hn_structure,
    analyze_metadata,
    analyze_images_optimization,
    analyze_structured_data,
    analyze_crawlability
)
from .utils.linking import analyze_internal_linking
from .utils.performance import analyze_core_web_vitals
from .utils.aio import (
    analyze_atomicity_direct_answer,
    analyze_quantifiable_data,
    analyze_expertise_signals,
    analyze_multimodal_interoperability
)
from .utils.llm_analysis import analyze_llm_content
from .utils.enhanced_content import analyze_enhanced_content
from .utils.enhanced_structure import analyze_enhanced_structure
from .utils.scoring import generate_score_report
from .utils.page_storage import save_page_content, cleanup_old_pages


def analyze_full_page(url, pagespeed_api_key=None):
    """
    Orchestre l'analyse complète d'une page web en appelant toutes les fonctions
    des modules de catégories.
    
    Args:
        url (str): L'URL de la page à analyser.
        pagespeed_api_key (str, optional): La clé API pour Google PageSpeed Insights.
                                           Si None, cette analyse sera ignorée.

    Returns:
        dict: Un dictionnaire contenant le rapport d'analyse complet.
    """
    print(f"🚀 Démarrage de l'analyse complète pour : {url}")
    
    final_report = {'url': url, 'analysis_results': {}}

    # --- Étape 1: Récupération du contenu de la page ---
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Sauvegarder la page téléchargée
        try:
            save_page_content(url, response.text, dict(response.headers))
        except Exception as e:
            print(f"⚠️ Erreur lors de la sauvegarde de la page: {e}")
        
        # Créer une copie de la soup pour l'analyse textuelle afin de ne pas affecter les autres analyses
        text_soup = BeautifulSoup(str(soup), 'html.parser')
        main_text = get_main_text(text_soup)
        print("✅ Contenu de la page récupéré avec succès.")
    except requests.RequestException as e:
        print(f"❌ Erreur critique : Impossible de récupérer la page. {e}")
        final_report['error'] = str(e)
        return final_report

    # --- Étape 2: Lancement des analyses par catégorie ---
    
    # Catégorie 1: Contenu & Sémantique
    try:
        final_report['analysis_results']['category_1_content'] = {
            '1.1_richness_coverage': analyze_richness_and_coverage(main_text),
            '1.2_style_clarity': analyze_style_clarity(soup),
            '1.3_sources_reliability': analyze_sources_reliability(soup, url),
            '1.4_freshness': analyze_freshness(soup)
        }
        print("📊 Catégorie 1 (Contenu) analysée.")
    except Exception as e:
        final_report['analysis_results']['category_1_content'] = {'error': str(e)}

    # Catégorie 2: Structure
    try:
        final_report['analysis_results']['category_2_structure'] = {
            '2.1_hn_structure': analyze_hn_structure(soup),
            '2.2_metadata': analyze_metadata(soup),
            '2.3_images_optimization': analyze_images_optimization(soup),
            '2.4_structured_data': analyze_structured_data(soup),
            '2.5_crawlability': analyze_crawlability(url)
        }
        print("🏗️  Catégorie 2 (Structure) analysée.")
    except Exception as e:
        final_report['analysis_results']['category_2_structure'] = {'error': str(e)}

    # Catégorie 3: Maillage & Liens
    try:
        final_report['analysis_results']['category_3_linking'] = {
            '3.1_3.2_internal_linking': analyze_internal_linking(soup, url)
        }
        print("🔗 Catégorie 3 (Maillage) analysée.")
    except Exception as e:
        final_report['analysis_results']['category_3_linking'] = {'error': str(e)}

    # Catégorie 4: Performance Technique
    try:
        print("⏱️  Analyse de la Catégorie 4 (Performance) en cours (peut prendre du temps)...")
        final_report['analysis_results']['category_4_performance'] = {
            '4.1_4.2_desktop_performance': analyze_core_web_vitals(url, pagespeed_api_key, 'DESKTOP'),
            '4.1_4.2_mobile_performance': analyze_core_web_vitals(url, pagespeed_api_key, 'MOBILE')
        }
        print("⚡ Catégorie 4 (Performance) analysée.")
    except Exception as e:
        final_report['analysis_results']['category_4_performance'] = {'error': str(e)}

    # Catégorie 5: Optimisation AIO
    try:
        final_report['analysis_results']['category_5_aio'] = {
            '5.1_atomicity_direct_answer': analyze_atomicity_direct_answer(soup),
            '5.2_quantifiable_data': analyze_quantifiable_data(main_text),
            '5.3_expertise_signals': analyze_expertise_signals(soup),
            '5.4_multimodal_interoperability': analyze_multimodal_interoperability(soup)
        }
        print("🤖 Catégorie 5 (AIO) analysée.")
    except Exception as e:
        final_report['analysis_results']['category_5_aio'] = {'error': str(e)}

    # --- CATÉGORIE 6 : AI-POWERED CONTENT ANALYSIS ---
    try:
        print("🧠 Analyse de la Catégorie 6 (AI Content Analysis) en cours...")
        final_report['analysis_results']['category_6_llm_analysis'] = analyze_llm_content(soup, main_text, url)
        print("🧠 Catégorie 6 (AI Content Analysis) analysée.")
    except Exception as e:
        final_report['analysis_results']['category_6_llm_analysis'] = {'error': str(e)}
        print(f"⚠️  Erreur lors de l'analyse LLM: {str(e)}")

    # --- ANALYSES AMÉLIORÉES ---
    try:
        print("🔍 Analyses de contenu améliorées en cours...")
        final_report['analysis_results']['enhanced_content_analysis'] = analyze_enhanced_content(soup, main_text)
        print("🔍 Analyses de contenu améliorées terminées.")
    except Exception as e:
        final_report['analysis_results']['enhanced_content_analysis'] = {'error': str(e)}
        print(f"⚠️  Erreur lors de l'analyse de contenu améliorée: {str(e)}")

    try:
        print("🏗️  Analyses de structure améliorées en cours...")
        final_report['analysis_results']['enhanced_structure_analysis'] = analyze_enhanced_structure(url, soup)
        print("🏗️  Analyses de structure améliorées terminées.")
    except Exception as e:
        final_report['analysis_results']['enhanced_structure_analysis'] = {'error': str(e)}
        print(f"⚠️  Erreur lors de l'analyse de structure améliorée: {str(e)}")

    print("\n🎉 Analyse complète terminée !")
    return final_report


# --- Exemple d'utilisation du script ---
def main():
    """Fonction principale pour l'analyse SEO."""
    # --- CONFIGURATION ---
    # URL de la page que vous souhaitez analyser (depuis l'environnement ou par défaut)
    TARGET_URL = os.getenv('ANALYSIS_URL', "https://www.meilleurtaux.com/credit-immobilier/actualites/2025-aout/ete-favorable-emprunteurs-immobiliers.html")
    
    # Configuration des options d'analyse
    ENABLE_LLM_ANALYSIS = os.getenv('ENABLE_LLM_ANALYSIS', 'true').lower() == 'true'
    ENABLE_ENHANCED_ANALYSIS = os.getenv('ENABLE_ENHANCED_ANALYSIS', 'true').lower() == 'true'
    
    # (Optionnel) Clé API Google PageSpeed Insights chargée depuis .env
    # Pour en obtenir une, suivez les instructions sur :
    # https://developers.google.com/speed/docs/insights/v5/get-started
    # Si vous n'en mettez pas dans .env, l'analyse de performance sera ignorée.
    PAGESPEED_API_KEY = os.getenv('PAGESPEED_API_KEY') 
    
    print(f"🎯 URL à analyser: {TARGET_URL}")
    print(f"🧠 Analyse LLM: {'✅ Activée' if ENABLE_LLM_ANALYSIS else '❌ Désactivée'}")
    print(f"🔬 Analyse améliorée: {'✅ Activée' if ENABLE_ENHANCED_ANALYSIS else '❌ Désactivée'}")
    print(f"⚡ API PageSpeed: {'✅ Configurée' if PAGESPEED_API_KEY else '❌ Non configurée'}")
    print("-" * 60)

    # --- Lancement de l'analyse ---
    full_report = analyze_full_page(TARGET_URL, PAGESPEED_API_KEY)
    
    # --- Affichage du rapport ---
    print("\n--- RAPPORT D'ANALYSE SEO & AIO COMPLET ---")
    # Utiliser json.dumps pour un affichage propre et lisible du dictionnaire
    print(json.dumps(full_report, indent=4, ensure_ascii=False))
    
    # (Optionnel) Sauvegarder le rapport dans un fichier JSON
    try:
        report_filename = f"reports/raw/report_{TARGET_URL.split('//')[1].replace('/', '_')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(full_report, f, indent=4, ensure_ascii=False)
        print(f"\n✅ Rapport raw sauvegardé dans le fichier : {report_filename}")
        
        # Générer automatiquement le rapport de scores
        try:
            print("📊 Génération du rapport de scores...")
            score_report = generate_score_report(report_filename)
            
            # Afficher un résumé des scores
            global_analysis = score_report["global_analysis"]
            print(f"\n🎯 Score Global SEO: {global_analysis['global_score']}/100")
            print(f"📊 Niveau de Performance: {global_analysis['performance_level']}")
            
            if global_analysis['strengths']:
                print(f"💪 Forces: {', '.join(global_analysis['strengths'])}")
            if global_analysis['weaknesses']:
                print(f"⚠️  Faiblesses: {', '.join(global_analysis['weaknesses'])}")
                
        except Exception as e:
            print(f"⚠️  Erreur lors de la génération des scores : {e}")
            
    except Exception as e:
        print(f"\n❌ Erreur lors de la sauvegarde du rapport : {e}")
    
    # Nettoyage automatique des anciennes pages (optionnel)
    try:
        print("🧹 Nettoyage des anciennes pages...")
        cleanup_old_pages(max_pages=50, max_days=30)
    except Exception as e:
        print(f"⚠️ Erreur lors du nettoyage: {e}")


if __name__ == '__main__':
    main()
