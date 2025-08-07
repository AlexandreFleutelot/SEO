# -*- coding: utf-8 -*-
"""
category_2_structure.py

Ce module contient les fonctions pour analyser la structure technique
d'une page web (Catégorie 2 de la grille d'évaluation).

Dépendances :
pip install beautifulsoup4 requests
"""
import json
import requests
from bs4 import BeautifulSoup

def analyze_hn_structure(soup):
    """
    Critère 2.1: Analyse la structure des balises Hn (H1 à H6).
    """
    headings = {}
    for i in range(1, 7):
        tag = f'h{i}'
        headings[tag] = [h.get_text(strip=True) for h in soup.find_all(tag)]

    h1_count = len(headings.get('h1', []))
    
    # Vérification simple de la hiérarchie
    issues = []
    last_level = 0
    for i in range(1, 7):
        tag = f'h{i}'
        if headings[tag]:
            if i > last_level + 1 and last_level > 0:
                issues.append(f"Saut de niveau détecté : de h{last_level} à h{i}")
            last_level = i

    return {
        'h1_count': h1_count,
        'headings_by_level': {k: v for k, v in headings.items() if v},
        'hierarchy_issues': issues
    }

def analyze_metadata(soup):
    """
    Critère 2.2: Analyse les métadonnées de la page (title, meta description).
    """
    title = soup.find('title').get_text(strip=True) if soup.find('title') else None
    description = soup.find('meta', attrs={'name': 'description'})
    description_content = description['content'] if description else None
    
    return {
        'title': title,
        'title_length': len(title) if title else 0,
        'meta_description': description_content,
        'meta_description_length': len(description_content) if description_content else 0
    }

def analyze_images_optimization(soup):
    """
    Critère 2.3: Analyse les images de la page (alt, légendes).
    """
    images = soup.find_all('img')
    total_images = len(images)
    images_with_alt = 0
    images_with_figcaption = 0

    for img in images:
        if img.get('alt', '').strip():
            images_with_alt += 1
        # Vérifie si l'image est dans une balise <figure> avec une <figcaption>
        if img.find_parent('figure') and img.find_parent('figure').find('figcaption'):
            images_with_figcaption += 1
            
    return {
        'total_images': total_images,
        'images_with_alt': images_with_alt,
        'alt_coverage_percentage': (images_with_alt / total_images * 100) if total_images > 0 else 100,
        'images_with_figcaption': images_with_figcaption
    }

def analyze_structured_data(soup):
    """
    Critère 2.4: Détecte la présence de données structurées (Schema.org en JSON-LD).
    """
    schemas = []
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and '@type' in data:
                schemas.append(data.get('@type'))
            elif isinstance(data, list):
                 for item in data:
                     if isinstance(item, dict) and '@type' in item:
                         schemas.append(item.get('@type'))
        except json.JSONDecodeError:
            continue # Ignorer les JSON invalides
            
    return {
        'schema_count': len(schemas),
        'schema_types': list(set(schemas)) # Types uniques
    }

def analyze_crawlability(url):
    """
    Critère 2.5: Vérifie la présence de sitemap et robots.txt (basique).
    Cette fonction est simplifiée et ne parse pas le contenu des fichiers.
    """
    from urllib.parse import urlparse, urljoin
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    robots_url = urljoin(base_url, "robots.txt")
    sitemap_url = urljoin(base_url, "sitemap.xml")
    
    robots_status = "not_found"
    sitemap_status = "not_found"
    
    try:
        if requests.head(robots_url, timeout=5).status_code == 200:
            robots_status = "found"
    except requests.RequestException:
        robots_status = "error"
        
    try:
        if requests.head(sitemap_url, timeout=5).status_code == 200:
            sitemap_status = "found"
    except requests.RequestException:
        sitemap_status = "error"

    return {
        'robots_txt_status': robots_status,
        'sitemap_xml_status': sitemap_status
    }


if __name__ == '__main__':
    URL = "https://www.meilleurtaux.com/credit-immobilier.html"
    print(f"Analyse de la Catégorie 2 pour : {URL}")
    
    try:
        response = requests.get(URL)
        response.raise_for_status()
        main_soup = BeautifulSoup(response.content, 'html.parser')

        print("\n--- 2.1 Structure Hn ---")
        print(analyze_hn_structure(main_soup))
        
        print("\n--- 2.2 Métadonnées ---")
        print(analyze_metadata(main_soup))

        print("\n--- 2.3 Optimisation des Images ---")
        print(analyze_images_optimization(main_soup))

        print("\n--- 2.4 Données Structurées ---")
        print(analyze_structured_data(main_soup))

        print("\n--- 2.5 Crawlabilité ---")
        print(analyze_crawlability(URL))

    except requests.RequestException as e:
        print(f"Erreur: {e}")
