# -*- coding: utf-8 -*-
"""
Analyse de la structure technique des pages web
Ce module évalue l'organisation, les balises et l'optimisation technique
"""

import json
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional

from ...config import USER_MESSAGES


def analyser_structure_titres(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Analyse la hiérarchie des titres (H1-H6)
    
    Args:
        soup: Objet BeautifulSoup de la page
        
    Returns:
        dict: Informations sur la structure des titres
    """
    # Trouver tous les titres
    titres_par_niveau = {}
    for niveau in range(1, 7):
        titres = soup.find_all(f'h{niveau}')
        if titres:
            titres_par_niveau[f'h{niveau}'] = [titre.get_text(strip=True) for titre in titres]
    
    # Analyser la structure
    h1_elements = soup.find_all('h1')
    nombre_h1 = len(h1_elements)
    
    # Vérifier la hiérarchie logique
    hierarchie_correcte = True
    niveaux_utilises = []
    
    for niveau in range(1, 7):
        if soup.find_all(f'h{niveau}'):
            niveaux_utilises.append(niveau)
    
    # Vérifier s'il y a des sauts dans la hiérarchie
    for i in range(1, len(niveaux_utilises)):
        if niveaux_utilises[i] - niveaux_utilises[i-1] > 1:
            hierarchie_correcte = False
            break
    
    # Score basé sur la qualité de la structure
    score_structure = 50  # Score de base
    
    if nombre_h1 == 1:
        score_structure += 25  # Un seul H1 = bon
    elif nombre_h1 == 0:
        score_structure -= 30  # Pas de H1 = mauvais
    elif nombre_h1 > 1:
        score_structure -= 15  # Plusieurs H1 = problématique
    
    if hierarchie_correcte:
        score_structure += 15
    
    if len(niveaux_utilises) > 1:
        score_structure += 10  # Utilisation de plusieurs niveaux
    
    return {
        'nombre_h1': nombre_h1,
        'titres_par_niveau': titres_par_niveau,
        'hierarchie_correcte': hierarchie_correcte,
        'niveaux_utilises': niveaux_utilises,
        'score_structure_titres': max(0, min(100, score_structure)),
        'titre_principal': h1_elements[0].get_text(strip=True) if h1_elements else None
    }


def analyser_meta_donnees(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Analyse les métadonnées essentielles de la page
    
    Args:
        soup: Objet BeautifulSoup de la page
        
    Returns:
        dict: Informations sur les métadonnées
    """
    # Titre de la page
    titre_element = soup.find('title')
    titre = titre_element.get_text(strip=True) if titre_element else ""
    longueur_titre = len(titre)
    
    # Meta description
    meta_desc = soup.find('meta', {'name': 'description'})
    description = meta_desc.get('content', '') if meta_desc else ""
    longueur_description = len(description)
    
    # Autres métadonnées importantes
    meta_keywords = soup.find('meta', {'name': 'keywords'})
    keywords = meta_keywords.get('content', '') if meta_keywords else ""
    
    # Open Graph et Twitter Cards
    og_tags = soup.find_all('meta', {'property': re.compile(r'^og:')})
    twitter_tags = soup.find_all('meta', {'name': re.compile(r'^twitter:')})
    
    # Canonical
    canonical = soup.find('link', {'rel': 'canonical'})
    url_canonical = canonical.get('href') if canonical else None
    
    # Meta robots
    meta_robots = soup.find('meta', {'name': 'robots'})
    robots = meta_robots.get('content', '') if meta_robots else ""
    
    # Calculer le score des métadonnées
    score_meta = 0
    
    # Score pour le titre
    if 30 <= longueur_titre <= 60:
        score_meta += 25
    elif 20 <= longueur_titre <= 70:
        score_meta += 15
    elif longueur_titre > 0:
        score_meta += 5
    
    # Score pour la description
    if 150 <= longueur_description <= 160:
        score_meta += 25
    elif 120 <= longueur_description <= 180:
        score_meta += 20
    elif 100 <= longueur_description <= 200:
        score_meta += 10
    elif longueur_description > 0:
        score_meta += 5
    
    # Bonus pour les autres éléments
    if og_tags:
        score_meta += 10
    if twitter_tags:
        score_meta += 5
    if url_canonical:
        score_meta += 10
    if robots and 'noindex' not in robots.lower():
        score_meta += 5
    
    return {
        'titre': titre,
        'longueur_titre': longueur_titre,
        'description': description,
        'longueur_description': longueur_description,
        'keywords': keywords,
        'url_canonical': url_canonical,
        'robots': robots,
        'nombre_og_tags': len(og_tags),
        'nombre_twitter_tags': len(twitter_tags),
        'score_metadonnees': min(100, score_meta),
        'qualite_titre': evaluer_qualite_meta(longueur_titre, 30, 60),
        'qualite_description': evaluer_qualite_meta(longueur_description, 150, 160)
    }


def evaluer_qualite_meta(longueur: int, optimal_min: int, optimal_max: int) -> str:
    """Évalue la qualité d'une métadonnée basée sur sa longueur"""
    if longueur == 0:
        return "manquant"
    elif optimal_min <= longueur <= optimal_max:
        return "optimal"
    elif longueur < optimal_min:
        return "trop court"
    else:
        return "trop long"


def analyser_images(soup: BeautifulSoup, url_base: str) -> Dict[str, Any]:
    """
    Analyse l'optimisation des images
    
    Args:
        soup: Objet BeautifulSoup de la page
        url_base: URL de base pour résoudre les liens relatifs
        
    Returns:
        dict: Informations sur les images
    """
    images = soup.find_all('img')
    nombre_total_images = len(images)
    
    if nombre_total_images == 0:
        return {
            'nombre_total_images': 0,
            'avec_alt': 0,
            'sans_alt': 0,
            'couverture_alt_pourcentage': 0,
            'score_images': 50,  # Score neutre si pas d'images
            'problemes': []
        }
    
    # Analyser chaque image
    avec_alt = 0
    sans_alt = 0
    alt_vides = 0
    images_problematiques = []
    
    for img in images:
        alt_text = img.get('alt', '')
        src = img.get('src', '')
        
        if alt_text:
            avec_alt += 1
            if len(alt_text.strip()) == 0:
                alt_vides += 1
        else:
            sans_alt += 1
            images_problematiques.append({
                'src': src,
                'probleme': 'Alt manquant'
            })
        
        # Vérifier d'autres attributs importants
        if not img.get('width') or not img.get('height'):
            if len(images_problematiques) < 5:  # Limiter les exemples
                images_problematiques.append({
                    'src': src,
                    'probleme': 'Dimensions manquantes'
                })
    
    # Calculer le pourcentage de couverture alt
    couverture_alt = (avec_alt / nombre_total_images * 100) if nombre_total_images > 0 else 0
    
    # Calculer le score des images
    score_images = 0
    
    if couverture_alt >= 95:
        score_images = 100
    elif couverture_alt >= 80:
        score_images = 85
    elif couverture_alt >= 60:
        score_images = 70
    elif couverture_alt >= 40:
        score_images = 50
    else:
        score_images = 30
    
    # Pénalité pour alt vides
    if alt_vides > 0:
        score_images -= min(20, alt_vides * 5)
    
    return {
        'nombre_total_images': nombre_total_images,
        'avec_alt': avec_alt,
        'sans_alt': sans_alt,
        'alt_vides': alt_vides,
        'couverture_alt_pourcentage': round(couverture_alt, 1),
        'score_images': max(0, score_images),
        'images_problematiques': images_problematiques[:5]  # Limiter les exemples
    }


def analyser_donnees_structurees(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Analyse les données structurées (JSON-LD, microdata)
    
    Args:
        soup: Objet BeautifulSoup de la page
        
    Returns:
        dict: Informations sur les données structurées
    """
    # JSON-LD
    json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
    schemas_json_ld = []
    
    for script in json_ld_scripts:
        try:
            data = json.loads(script.get_text())
            if '@type' in data:
                schemas_json_ld.append(data['@type'])
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and '@type' in item:
                        schemas_json_ld.append(item['@type'])
        except:
            continue
    
    # Microdata
    microdata_items = soup.find_all(attrs={'itemtype': True})
    schemas_microdata = []
    
    for item in microdata_items:
        itemtype = item.get('itemtype', '')
        if itemtype:
            # Extraire le type du schema.org
            if 'schema.org' in itemtype:
                schema_type = itemtype.split('/')[-1]
                schemas_microdata.append(schema_type)
    
    # Score basé sur la présence de données structurées
    score_schema = 0
    
    if json_ld_scripts:
        score_schema += 50
    if microdata_items:
        score_schema += 30
    
    # Bonus pour des types importants
    types_importants = ['Organization', 'LocalBusiness', 'Article', 'Product', 'WebSite']
    for type_important in types_importants:
        if type_important in schemas_json_ld or type_important in schemas_microdata:
            score_schema += 10
    
    return {
        'json_ld_present': len(json_ld_scripts) > 0,
        'nombre_json_ld': len(json_ld_scripts),
        'schemas_json_ld': list(set(schemas_json_ld)),
        'microdata_present': len(microdata_items) > 0,
        'nombre_microdata': len(microdata_items),
        'schemas_microdata': list(set(schemas_microdata)),
        'score_donnees_structurees': min(100, score_schema),
        'types_detectes': list(set(schemas_json_ld + schemas_microdata))
    }


def analyser_crawlabilite(soup: BeautifulSoup, url_base: str) -> Dict[str, Any]:
    """
    Analyse la crawlabilité de la page
    
    Args:
        soup: Objet BeautifulSoup de la page
        url_base: URL de base
        
    Returns:
        dict: Informations sur la crawlabilité
    """
    # Liens internes
    liens_internes = []
    domaine_base = urlparse(url_base).netloc
    
    for lien in soup.find_all('a', href=True):
        href = lien['href']
        
        # Résoudre les liens relatifs
        if href.startswith('/'):
            url_complete = urljoin(url_base, href)
        elif href.startswith('http'):
            url_complete = href
        else:
            url_complete = urljoin(url_base, href)
        
        # Vérifier si c'est un lien interne
        domaine_lien = urlparse(url_complete).netloc
        if domaine_lien == domaine_base:
            liens_internes.append({
                'url': url_complete,
                'texte_ancre': lien.get_text(strip=True)[:50],
                'title': lien.get('title', '')
            })
    
    # Vérifier le fichier robots.txt (simulation)
    # En réalité, il faudrait faire une requête HTTP
    
    # Meta robots
    meta_robots = soup.find('meta', {'name': 'robots'})
    robots_content = meta_robots.get('content', '').lower() if meta_robots else ""
    
    # Analyser les directives robots
    noindex = 'noindex' in robots_content
    nofollow = 'nofollow' in robots_content
    
    # Plan du site (sitemap)
    sitemap_links = soup.find_all('link', {'rel': 'sitemap'})
    
    # Score de crawlabilité
    score_crawl = 70  # Score de base
    
    if noindex:
        score_crawl -= 50  # Pénalité majeure
    if nofollow:
        score_crawl -= 20
    
    if len(liens_internes) > 5:
        score_crawl += 15  # Bonus pour navigation interne
    
    if sitemap_links:
        score_crawl += 15
    
    return {
        'nombre_liens_internes': len(liens_internes),
        'exemples_liens_internes': liens_internes[:5],
        'meta_robots': robots_content,
        'noindex': noindex,
        'nofollow': nofollow,
        'sitemap_declare': len(sitemap_links) > 0,
        'score_crawlabilite': max(0, min(100, score_crawl)),
        'problemes_crawl': generer_problemes_crawl(noindex, nofollow, len(liens_internes))
    }


def generer_problemes_crawl(noindex: bool, nofollow: bool, nb_liens: int) -> List[str]:
    """Génère une liste des problèmes de crawlabilité détectés"""
    problemes = []
    
    if noindex:
        problemes.append("Page marquée noindex - non indexable par les moteurs")
    if nofollow:
        problemes.append("Page marquée nofollow - liens non suivis")
    if nb_liens < 3:
        problemes.append("Peu de liens internes - navigation limitée")
    
    return problemes


def analyser_structure_complete(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """
    Fonction principale qui effectue toutes les analyses de structure
    
    Args:
        soup: Objet BeautifulSoup de la page
        url: URL de la page
        
    Returns:
        dict: Toutes les analyses de structure
    """
    print("🏗️ Analyse de la structure technique...")
    
    # Effectuer toutes les analyses
    analyses = {
        'structure_titres': analyser_structure_titres(soup),
        'metadonnees': analyser_meta_donnees(soup),
        'images': analyser_images(soup, url),
        'donnees_structurees': analyser_donnees_structurees(soup),
        'crawlabilite': analyser_crawlabilite(soup, url)
    }
    
    print("✅ Analyse de la structure terminée")
    return analyses