# -*- coding: utf-8 -*-
"""
category_1_content.py

Ce module contient les fonctions pour analyser la qualité du contenu et la sémantique
d'une page web (Catégorie 1 de la grille d'évaluation).

Dépendances :
pip install beautifulsoup4 spacy textstat datefinder

Modèle spaCy à télécharger :
python -m spacy download fr_core_news_sm
"""
import re
from collections import Counter
import spacy
import datefinder
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Charger le modèle NLP une seule fois pour la performance
try:
    nlp = spacy.load("fr_core_news_sm")
except OSError:
    print("Modèle 'fr_core_news_sm' non trouvé. Veuillez l'installer.")
    # On peut continuer sans, mais certaines fonctions échoueront.
    nlp = None

def get_main_text(soup):
    """Extrait le texte principal en ignorant les balises de navigation, footer, etc."""
    for tag in soup(['nav', 'footer', 'header', 'aside', 'script', 'style']):
        tag.decompose()
    return soup.body.get_text(separator=' ', strip=True) if soup.body else ""

def analyze_richness_and_coverage(text):
    """
    Critère 1.1: Analyse la richesse, la longueur et les entités du texte.
    """
    if not nlp:
        return {'error': 'Modèle spaCy non chargé.'}
        
    word_count = len(text.split())
    doc = nlp(text[:nlp.max_length]) # Limiter la longueur pour la performance
    
    entities = [ent.label_ for ent in doc.ents]
    entity_distribution = dict(Counter(entities))

    return {
        'word_count': word_count,
        'entity_count': len(entities),
        'entity_distribution': entity_distribution
    }

def analyze_style_clarity(soup):
    """
    Critère 1.2: Analyse la clarté et la structure du texte (listes, tableaux...).
    """
    text = get_main_text(BeautifulSoup(str(soup), 'html.parser'))
    if not nlp:
        return {'error': 'Modèle spaCy non chargé.'}

    doc = nlp(text[:nlp.max_length])
    sentences = list(doc.sents)
    
    sentence_lengths = [len(sent) for sent in sentences]
    avg_sentence_length = sum(sentence_lengths) / len(sentences) if sentences else 0

    return {
        'sentence_count': len(sentences),
        'avg_sentence_length_words': avg_sentence_length,
        'list_count': len(soup.find_all(['ul', 'ol'])),
        'table_count': len(soup.find_all('table'))
    }

def analyze_sources_reliability(soup, base_url):
    """
    Critère 1.3: Analyse les liens sortants vers des sources externes.
    """
    domain = urlparse(base_url).netloc
    external_links = []
    for a in soup.find_all('a', href=True):
        link_domain = urlparse(a['href']).netloc
        if link_domain and link_domain != domain:
            external_links.append(a['href'])
    
    # Heuristique simple pour les citations textuelles
    citations = re.findall(r'\(source ?:|selon|d\'après', get_main_text(soup), re.IGNORECASE)

    return {
        'external_link_count': len(external_links),
        'external_links': external_links[:10], # Limiter pour la lisibilité
        'textual_citation_count': len(citations)
    }

def analyze_freshness(soup):
    """
    Critère 1.4: Tente d'extraire la date de publication ou de mise à jour.
    """
    text_content = soup.get_text()
    
    # Recherche de dates avec datefinder
    found_dates = list(datefinder.find_dates(text_content))
    
    # Recherche spécifique dans les balises meta
    meta_date = soup.find('meta', property='article:published_time') or \
                soup.find('meta', property='article:modified_time') or \
                soup.find('meta', attrs={'name': 'date'})
    
    publication_date = meta_date['content'] if meta_date else None
    
    # Heuristique pour trouver l'année dans le H1 ou le titre
    h1_text = soup.h1.get_text() if soup.h1 else ""
    title_text = soup.title.get_text() if soup.title else ""
    year_in_title = re.search(r'(20[2-9]\d)', h1_text + " " + title_text)

    return {
        'publication_date_meta': publication_date,
        'detected_dates_in_text': sorted([d.isoformat() for d in found_dates], reverse=True)[:5],
        'year_in_title_h1': year_in_title.group(0) if year_in_title else None
    }

if __name__ == '__main__':
    import requests
    URL = "https://www.meilleurtaux.com/credit-immobilier/simulation.html"
    print(f"Analyse de la Catégorie 1 pour : {URL}")
    
    try:
        response = requests.get(URL)
        response.raise_for_status()
        main_soup = BeautifulSoup(response.content, 'html.parser')
        main_text = get_main_text(BeautifulSoup(str(main_soup), 'html.parser'))

        print("\n--- 1.1 Richesse et Couverture ---")
        print(analyze_richness_and_coverage(main_text))
        
        print("\n--- 1.2 Style et Clarté ---")
        print(analyze_style_clarity(main_soup))

        print("\n--- 1.3 Sources et Fiabilité ---")
        print(analyze_sources_reliability(main_soup, URL))

        print("\n--- 1.4 Fraîcheur ---")
        print(analyze_freshness(main_soup))

    except requests.RequestException as e:
        print(f"Erreur: {e}")

