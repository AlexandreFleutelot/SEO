# -*- coding: utf-8 -*-
"""
category_4_performance.py

Ce module contient les fonctions pour analyser la performance technique
d'une page web via l'API Google PageSpeed Insights (Catégorie 4).

Dépendances :
pip install requests
"""
import requests

def analyze_core_web_vitals(url, api_key, strategy='DESKTOP'):
    """
    Critère 4.1 & 4.2: Interroge l'API PageSpeed Insights.
    Nécessite une clé API de la Google Cloud Platform.
    Stratégie peut être 'DESKTOP' ou 'MOBILE'.
    """
    if not api_key:
        return {
            'error': "Clé API Google PageSpeed non fournie.",
            'LCP': None, 'INP': None, 'CLS': None, 'mobile_friendly': None
        }

    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={api_key}&strategy={strategy}"
    
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        results = response.json()
        
        metrics = results.get('loadingExperience', {}).get('metrics', {})
        
        lcp = metrics.get('LARGEST_CONTENTFUL_PAINT_MS', {}).get('percentile')
        inp = metrics.get('INTERACTION_TO_NEXT_PAINT', {}).get('percentile')
        cls = metrics.get('CUMULATIVE_LAYOUT_SHIFT_SCORE', {}).get('percentile')
        
        # Le test de compatibilité mobile est dans les audits
        mobile_audit = results.get('lighthouseResult', {}).get('audits', {}).get('is-on-https', {})
        mobile_friendly = mobile_audit.get('score') == 1 if mobile_audit else None

        return {
            'LCP_ms': lcp,
            'INP_ms': inp,
            'CLS_score': cls / 100.0 if cls is not None else None, # L'API retourne le score * 100
            'mobile_friendly_score': mobile_friendly
        }
        
    except requests.RequestException as e:
        return {'error': str(e)}
    except KeyError:
        return {'error': "La réponse de l'API n'a pas le format attendu."}

if __name__ == '__main__':
    # REMPLACEZ PAR VOTRE URL ET VOTRE CLÉ API
    URL_TO_TEST = "https://www.google.com"
    # Pour obtenir une clé : https://developers.google.com/speed/docs/insights/v5/get-started
    PAGESPEED_API_KEY = "" # LAISSER VIDE POUR NE PAS EXECUTER L'APPEL

    print(f"Analyse de la Catégorie 4 pour : {URL_TO_TEST}")
    
    if not PAGESPEED_API_KEY:
        print("\nAVERTISSEMENT: Aucune clé API PageSpeed n'a été fournie.")
        print("La fonction `analyze_core_web_vitals` ne sera pas exécutée.")
    else:
        print("\n--- Analyse Desktop ---")
        print(analyze_core_web_vitals(URL_TO_TEST, PAGESPEED_API_KEY, 'DESKTOP'))
        
        print("\n--- Analyse Mobile ---")
        print(analyze_core_web_vitals(URL_TO_TEST, PAGESPEED_API_KEY, 'MOBILE'))

