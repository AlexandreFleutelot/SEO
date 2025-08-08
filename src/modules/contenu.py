# -*- coding: utf-8 -*-
"""
Analyse du contenu et de la sémantique des pages web
Ce module évalue la qualité, la richesse et la pertinence du contenu
"""

import re
import spacy
import datefinder
import statistics
from collections import Counter
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Dict, List, Any, Optional

from ..config import MAX_TEXT_LENGTH, USER_MESSAGES

# Chargement du modèle français pour l'analyse linguistique
try:
    nlp = spacy.load("fr_core_news_sm")
    print("✅ Modèle français chargé avec succès")
except OSError:
    print("❌ Modèle français non trouvé. Installez-le avec: python -m spacy download fr_core_news_sm")
    nlp = None


def extraire_texte_principal(soup: BeautifulSoup) -> str:
    """
    Extrait le texte principal de la page en ignorant navigation, footer, etc.
    
    Args:
        soup: Objet BeautifulSoup de la page
        
    Returns:
        str: Texte principal nettoyé
    """
    # Supprimer les éléments non pertinents
    elements_inutiles = ['nav', 'footer', 'header', 'aside', 'script', 'style', 'meta']
    for element in soup(elements_inutiles):
        element.decompose()
    
    # Extraire le texte du body
    if soup.body:
        return soup.body.get_text(separator=' ', strip=True)
    return soup.get_text(separator=' ', strip=True)


def analyser_richesse_contenu(texte: str) -> Dict[str, Any]:
    """
    Analyse la richesse du contenu : longueur, entités, diversité vocabulaire
    
    Args:
        texte: Texte à analyser
        
    Returns:
        dict: Métriques de richesse du contenu
    """
    if not nlp:
        return {'erreur': 'Modèle linguistique non disponible'}
    
    # Compter les mots
    mots = texte.split()
    nombre_mots = len(mots)
    
    # Limiter la taille pour l'analyse NLP
    texte_limite = texte[:MAX_TEXT_LENGTH] if len(texte) > MAX_TEXT_LENGTH else texte
    
    try:
        # Analyse avec spaCy
        document = nlp(texte_limite)
        
        # Extraire les entités nommées
        entites = [entite.label_ for entite in document.ents]
        repartition_entites = dict(Counter(entites))
        
        # Analyser les mots-clés importants
        mots_importants = [token.text.lower() for token in document 
                          if not token.is_stop and not token.is_punct 
                          and len(token.text) > 3]
        
        diversite_vocabulaire = len(set(mots_importants)) / len(mots_importants) if mots_importants else 0
        
        return {
            'nombre_mots': nombre_mots,
            'nombre_entites': len(entites),
            'repartition_entites': repartition_entites,
            'diversite_vocabulaire': round(diversite_vocabulaire, 2),
            'mots_cles_principaux': Counter(mots_importants).most_common(10)
        }
        
    except Exception as e:
        return {'erreur': f'Erreur lors de l\'analyse: {str(e)}'}


def analyser_style_lisibilite(soup: BeautifulSoup, texte: str) -> Dict[str, Any]:
    """
    Analyse le style et la lisibilité : phrases, listes, tableaux
    
    Args:
        soup: Objet BeautifulSoup
        texte: Texte principal
        
    Returns:
        dict: Métriques de lisibilité
    """
    if not nlp:
        return {'erreur': 'Modèle linguistique non disponible'}
    
    try:
        # Limiter le texte pour l'analyse
        texte_limite = texte[:MAX_TEXT_LENGTH] if len(texte) > MAX_TEXT_LENGTH else texte
        document = nlp(texte_limite)
        
        # Analyser les phrases
        phrases = list(document.sents)
        longueurs_phrases = [len(phrase.text.split()) for phrase in phrases]
        
        longueur_moyenne_phrase = statistics.mean(longueurs_phrases) if longueurs_phrases else 0
        
        # Compter les éléments structurants
        listes = soup.find_all(['ul', 'ol'])
        tableaux = soup.find_all('table')
        titres = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        return {
            'nombre_phrases': len(phrases),
            'longueur_moyenne_phrase': round(longueur_moyenne_phrase, 1),
            'nombre_listes': len(listes),
            'nombre_tableaux': len(tableaux),
            'nombre_titres': len(titres),
            'lisibilite_score': calculer_score_lisibilite(longueur_moyenne_phrase, len(listes), len(tableaux))
        }
        
    except Exception as e:
        return {'erreur': f'Erreur lors de l\'analyse du style: {str(e)}'}


def calculer_score_lisibilite(longueur_phrase: float, nb_listes: int, nb_tableaux: int) -> int:
    """Calcule un score de lisibilité simple"""
    score = 50  # Score de base
    
    # Pénaliser les phrases trop longues
    if longueur_phrase > 25:
        score -= 20
    elif longueur_phrase > 20:
        score -= 10
    elif longueur_phrase < 15:
        score += 10
    
    # Bonus pour les éléments structurants
    score += min(nb_listes * 5, 20)  # Max +20 pour les listes
    score += min(nb_tableaux * 3, 15)  # Max +15 pour les tableaux
    
    return max(0, min(100, score))


def analyser_sources_credibilite(soup: BeautifulSoup, url_base: str) -> Dict[str, Any]:
    """
    Analyse les sources externes et la crédibilité
    
    Args:
        soup: Objet BeautifulSoup
        url_base: URL de base de la page
        
    Returns:
        dict: Informations sur les sources
    """
    domaine_principal = urlparse(url_base).netloc
    liens_externes = []
    
    # Chercher tous les liens externes
    for lien in soup.find_all('a', href=True):
        href = lien['href']
        if href.startswith('http'):
            domaine_lien = urlparse(href).netloc
            if domaine_lien and domaine_lien != domaine_principal:
                liens_externes.append({
                    'url': href,
                    'texte': lien.get_text(strip=True)[:50],  # Limiter le texte
                    'domaine': domaine_lien
                })
    
    # Chercher des citations textuelles
    texte = extraire_texte_principal(soup)
    patterns_citations = [
        r'\(source\s*:\s*[^)]+\)',
        r'selon\s+[^,]{3,30}',
        r'd\'après\s+[^,]{3,30}',
        r'étude\s+[^,]{3,30}',
        r'rapport\s+[^,]{3,30}'
    ]
    
    citations_trouvees = []
    for pattern in patterns_citations:
        citations_trouvees.extend(re.findall(pattern, texte, re.IGNORECASE))
    
    # Analyser la qualité des sources
    domaines_fiables = ['gouv.fr', 'insee.fr', 'legifrance.gouv.fr', 'banque-france.fr',
                       'who.int', 'europa.eu', '.edu', '.org']
    
    sources_fiables = 0
    for lien in liens_externes:
        if any(domaine in lien['domaine'] for domaine in domaines_fiables):
            sources_fiables += 1
    
    return {
        'nombre_liens_externes': len(liens_externes),
        'liens_externes': liens_externes[:10],  # Limiter pour l'affichage
        'citations_textuelles': len(citations_trouvees),
        'exemples_citations': citations_trouvees[:5],
        'sources_fiables': sources_fiables,
        'score_credibilite': calculer_score_credibilite(sources_fiables, len(citations_trouvees))
    }


def calculer_score_credibilite(sources_fiables: int, citations: int) -> int:
    """Calcule un score de crédibilité basé sur les sources"""
    score = 30  # Score de base
    
    # Bonus pour sources fiables
    score += min(sources_fiables * 15, 40)
    
    # Bonus pour citations
    score += min(citations * 10, 30)
    
    return min(100, score)


def analyser_fraicheur_contenu(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Analyse la fraîcheur et l'actualité du contenu
    
    Args:
        soup: Objet BeautifulSoup
        
    Returns:
        dict: Informations sur la fraîcheur
    """
    # Chercher des dates dans le HTML et le texte
    dates_trouvees = []
    
    # Balises méta pour dates
    meta_dates = soup.find_all('meta', {'name': re.compile(r'date|time', re.I)})
    for meta in meta_dates:
        if 'content' in meta.attrs:
            dates_trouvees.append(meta['content'])
    
    # Balises time
    time_elements = soup.find_all('time')
    for time_elem in time_elements:
        if 'datetime' in time_elem.attrs:
            dates_trouvees.append(time_elem['datetime'])
        dates_trouvees.append(time_elem.get_text(strip=True))
    
    # Recherche dans le texte
    texte_complet = soup.get_text()
    try:
        dates_dans_texte = list(datefinder.find_dates(texte_complet))
        dates_trouvees.extend([date.isoformat() for date in dates_dans_texte[:5]])
    except:
        pass
    
    # Analyser les dates trouvées
    date_plus_recente = None
    if dates_trouvees:
        try:
            dates_valides = []
            for date_str in dates_trouvees:
                try:
                    if isinstance(date_str, str):
                        # Essayer de parser différents formats
                        for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%dT%H:%M:%S']:
                            try:
                                date_obj = datetime.strptime(date_str, fmt)
                                dates_valides.append(date_obj)
                                break
                            except:
                                continue
                except:
                    continue
            
            if dates_valides:
                date_plus_recente = max(dates_valides)
        except:
            pass
    
    # Calculer l'âge du contenu
    jours_depuis_maj = None
    niveau_fraicheur = "inconnu"
    
    if date_plus_recente:
        jours_depuis_maj = (datetime.now() - date_plus_recente).days
        
        if jours_depuis_maj < 30:
            niveau_fraicheur = "très récent"
        elif jours_depuis_maj < 90:
            niveau_fraicheur = "récent"
        elif jours_depuis_maj < 365:
            niveau_fraicheur = "moyennement récent"
        else:
            niveau_fraicheur = "ancien"
    
    return {
        'dates_trouvees': len(dates_trouvees),
        'date_plus_recente': date_plus_recente.isoformat() if date_plus_recente else None,
        'jours_depuis_maj': jours_depuis_maj,
        'niveau_fraicheur': niveau_fraicheur,
        'score_fraicheur': calculer_score_fraicheur(jours_depuis_maj)
    }


def calculer_score_fraicheur(jours: Optional[int]) -> int:
    """Calcule un score de fraîcheur basé sur l'âge du contenu"""
    if jours is None:
        return 50  # Score neutre si date inconnue
    
    if jours < 30:
        return 100
    elif jours < 90:
        return 80
    elif jours < 180:
        return 60
    elif jours < 365:
        return 40
    else:
        return 20


def detecter_contenu_ia(texte: str) -> Dict[str, Any]:
    """
    Détecte si le contenu semble généré par IA (analyse simplifiée)
    
    Args:
        texte: Texte à analyser
        
    Returns:
        dict: Indicateurs de contenu IA
    """
    if not nlp:
        return {'erreur': 'Modèle linguistique non disponible'}
    
    # Indicateurs de contenu IA
    indicateurs_ia = [
        'en tant qu\'IA', 'en tant que modèle', 'je suis une IA',
        'basé sur mes connaissances', 'selon les informations disponibles',
        'il est important de noter', 'en conclusion', 'pour résumer'
    ]
    
    # Phrases répétitives ou génériques
    phrases_generiques = [
        'cet article explore', 'nous allons examiner', 'il convient de souligner',
        'dans cet article nous', 'nous avons vu que', 'en définitive'
    ]
    
    texte_lower = texte.lower()
    
    # Compter les occurrences
    score_ia = 0
    for indicateur in indicateurs_ia:
        if indicateur in texte_lower:
            score_ia += 10
    
    for phrase in phrases_generiques:
        score_ia += texte_lower.count(phrase) * 5
    
    # Analyse de la variation linguistique
    if nlp and len(texte) > 1000:
        try:
            doc = nlp(texte[:MAX_TEXT_LENGTH])
            phrases = [sent.text for sent in doc.sents]
            
            # Calculer la similarité entre phrases (version simplifiée)
            if len(phrases) > 10:
                longueurs = [len(phrase.split()) for phrase in phrases]
                variance_longueurs = statistics.variance(longueurs) if len(longueurs) > 1 else 0
                
                # Faible variance = phrases trop similaires = possible IA
                if variance_longueurs < 5:
                    score_ia += 15
        except:
            pass
    
    # Normaliser le score
    score_ia = min(100, score_ia)
    
    # Déterminer le niveau d'authenticité
    if score_ia < 20:
        authenticite = "probablement humain"
    elif score_ia < 40:
        authenticite = "possiblement humain"
    elif score_ia < 60:
        authenticite = "incertain"
    else:
        authenticite = "possiblement IA"
    
    return {
        'score_ia': score_ia,
        'score_naturel': 100 - score_ia,
        'authenticite_contenu': authenticite,
        'indicateurs_detectes': score_ia > 30
    }


def analyser_contenu_complet(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """
    Fonction principale qui effectue toutes les analyses de contenu
    
    Args:
        soup: Objet BeautifulSoup de la page
        url: URL de la page
        
    Returns:
        dict: Toutes les analyses de contenu
    """
    texte_principal = extraire_texte_principal(soup)
    
    if not texte_principal:
        return {'erreur': 'Aucun contenu textuel trouvé sur la page'}
    
    print(f"📝 Analyse du contenu ({len(texte_principal)} caractères)")
    
    # Effectuer toutes les analyses
    analyses = {
        'richesse_couverture': analyser_richesse_contenu(texte_principal),
        'style_clarte': analyser_style_lisibilite(soup, texte_principal),
        'sources_fiabilite': analyser_sources_credibilite(soup, url),
        'fraicheur': analyser_fraicheur_contenu(soup),
        'detection_ia': detecter_contenu_ia(texte_principal),
        'longueur_texte': len(texte_principal),
        'nb_mots_total': len(texte_principal.split())
    }
    
    print("✅ Analyse du contenu terminée")
    return analyses