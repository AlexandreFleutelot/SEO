# -*- coding: utf-8 -*-
"""
category_5_aio.py

Ce module contient les fonctions pour analyser les critères spécifiques
à l'optimisation pour les IA (AIO) (Catégorie 5).

Dépendances :
pip install beautifulsoup4
"""
import re
from bs4 import BeautifulSoup

def analyze_atomicity_direct_answer(soup):
    """
    Critère 5.1: Détecte les structures de type "Réponse-Directe".
    """
    qa_pairs = 0
    # Heuristique : cherche un Hn suivi immédiatement d'un seul paragraphe court
    for h_tag in soup.find_all(['h2', 'h3', 'h4']):
        next_sibling = h_tag.find_next_sibling()
        if next_sibling and next_sibling.name == 'p' and len(next_sibling.get_text(strip=True).split()) < 60:
            qa_pairs += 1
            
    summary_blocks = len(soup.find_all('blockquote')) + \
                     len(soup.find_all(class_=re.compile("summary|key-takeaway", re.I)))

    return {
        'potential_qa_pairs': qa_pairs,
        'summary_block_count': summary_blocks
    }

def analyze_quantifiable_data(text):
    """
    Critère 5.2: Détecte la présence de données chiffrées et factuelles.
    """
    percentages = len(re.findall(r'\d+%', text))
    currencies = len(re.findall(r'€|\$', text))
    # Recherche de dates au format numérique (ex: 2023, 12/05/2024)
    numeric_dates = len(re.findall(r'\b(19|20)\d{2}\b|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text))
    
    return {
        'percentage_count': percentages,
        'currency_mention_count': currencies,
        'numeric_date_count': numeric_dates
    }

def analyze_expertise_signals(soup):
    """
    Critère 5.3: Recherche les signaux d'expertise (bio auteur, page à propos).
    """
    # Recherche de schémas "Person" qui peuvent indiquer un auteur
    author_schema_present = False
    for script in soup.find_all('script', type='application/ld+json'):
        if '"@type":"Person"' in script.string or '"@type": "Author"' in script.string:
            author_schema_present = True
            break
            
    # Recherche d'un lien vers une page "à propos"
    about_page_linked = bool(soup.find('a', href=re.compile("a-propos|about|qui-sommes-nous", re.I)))

    return {
        'author_schema_present': author_schema_present,
        'about_page_linked': about_page_linked
    }

def analyze_multimodal_interoperability(soup):
    """
    Critère 5.4: Détecte la présence de contenu multimodal.
    """
    video_count = len(soup.find_all(['video', 'iframe[src*="youtube.com"]', 'iframe[src*="vimeo.com"]']))
    
    # Heuristique très simple pour les API (ne détectera que les liens évidents)
    api_links = len(soup.find_all('a', href=re.compile("/api/|/v\d/")))
    
    return {
        'video_embed_count': video_count,
        'potential_api_link_count': api_links
    }


if __name__ == '__main__':
    import requests
    from utils.content import get_main_text # Réutiliser la fonction du module 1

    URL = "https://www.meilleurtaux.com/credit-immobilier.html"
    print(f"Analyse de la Catégorie 5 pour : {URL}")
    
    try:
        response = requests.get(URL)
        response.raise_for_status()
        main_soup = BeautifulSoup(response.content, 'html.parser')
        main_text = get_main_text(BeautifulSoup(str(main_soup), 'html.parser'))

        print("\n--- 5.1 Atomicité et Réponse-Directe ---")
        print(analyze_atomicity_direct_answer(main_soup))
        
        print("\n--- 5.2 Données Quantifiables ---")
        print(analyze_quantifiable_data(main_text))

        print("\n--- 5.3 Signaux d'Expertise ---")
        print(analyze_expertise_signals(main_soup))

        print("\n--- 5.4 Multimodalité ---")
        print(analyze_multimodal_interoperability(main_soup))

    except requests.RequestException as e:
        print(f"Erreur: {e}")
