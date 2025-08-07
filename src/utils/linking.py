# -*- coding: utf-8 -*-
"""
category_3_linking.py

Ce module contient les fonctions pour analyser le maillage interne et les ancres
d'une page web (Catégorie 3 de la grille d'évaluation).

Dépendances :
pip install beautifulsoup4
"""
from urllib.parse import urlparse, urljoin
from collections import Counter
from bs4 import BeautifulSoup

def analyze_internal_linking(soup, base_url):
    """
    Critère 3.1 & 3.2: Analyse les liens internes et leurs textes d'ancrage.
    """
    internal_links = []
    domain = urlparse(base_url).netloc
    
    # On se concentre sur les liens dans le contenu principal
    main_content = soup.find('main') or soup.find('article') or soup.body
    
    for a_tag in main_content.find_all('a', href=True):
        href = a_tag['href']
        # Ignore les liens d'ancrage sur la même page
        if href.startswith('#'):
            continue
            
        absolute_url = urljoin(base_url, href)
        link_domain = urlparse(absolute_url).netloc
        
        if domain == link_domain:
            internal_links.append({
                'text': a_tag.get_text(strip=True),
                'url': absolute_url
            })
    
    anchor_texts = [link['text'] for link in internal_links if link['text']]
    anchor_distribution = dict(Counter(anchor_texts))
    
    # Détection des ancres non descriptives
    non_descriptive_anchors = [
        text for text in anchor_texts if text.lower() in 
        ['cliquez ici', 'en savoir plus', 'lire la suite', 'ici', 'ce lien']
    ]

    return {
        'internal_link_count': len(internal_links),
        'anchor_text_diversity': len(anchor_distribution),
        'non_descriptive_anchor_count': len(non_descriptive_anchors),
        'anchor_text_distribution': {k: v for k, v in sorted(anchor_distribution.items(), key=lambda item: item[1], reverse=True)[:5]}
    }

if __name__ == '__main__':
    import requests
    URL = "https://www.meilleurtaux.com/credit-immobilier.html"
    print(f"Analyse de la Catégorie 3 pour : {URL}")
    
    try:
        response = requests.get(URL)
        response.raise_for_status()
        main_soup = BeautifulSoup(response.content, 'html.parser')

        print("\n--- 3.1 & 3.2 Maillage Interne et Ancres ---")
        print(analyze_internal_linking(main_soup, URL))

    except requests.RequestException as e:
        print(f"Erreur: {e}")
