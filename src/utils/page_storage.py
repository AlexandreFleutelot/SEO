# -*- coding: utf-8 -*-
"""
Stockage et cache des pages web analysées
Ce module gère la sauvegarde des contenus de pages pour debug et cache
"""

import json
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from ..config import PAGES_STORAGE_DIR


def save_page_content(url: str, html_content: str) -> str:
    """
    Sauvegarde le contenu d'une page web pour cache/debug
    
    Args:
        url: URL de la page
        html_content: Contenu HTML brut
        
    Returns:
        str: Chemin du fichier sauvegardé
    """
    # Créer le nom de fichier sécurisé
    nom_fichier = creer_nom_fichier_page(url)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Fichier HTML
    fichier_html = PAGES_STORAGE_DIR / f"{nom_fichier}_{timestamp}.html"
    
    # Fichier métadonnées
    fichier_meta = PAGES_STORAGE_DIR / f"{nom_fichier}_{timestamp}_metadata.json"
    
    # Sauvegarder le contenu HTML
    with open(fichier_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Sauvegarder les métadonnées
    metadonnees = {
        'url': url,
        'domaine': urlparse(url).netloc,
        'date_sauvegarde': datetime.now().isoformat(),
        'taille_contenu': len(html_content),
        'fichier_html': fichier_html.name
    }
    
    with open(fichier_meta, 'w', encoding='utf-8') as f:
        json.dump(metadonnees, f, indent=2, ensure_ascii=False)
    
    return str(fichier_html)


def creer_nom_fichier_page(url: str) -> str:
    """
    Crée un nom de fichier sécurisé à partir d'une URL
    
    Args:
        url: URL à convertir
        
    Returns:
        str: Nom de fichier nettoyé
    """
    import re
    
    # Supprimer le protocole
    nom = url.replace('https://', '').replace('http://', '')
    
    # Remplacer les caractères spéciaux par des underscores
    nom = re.sub(r'[^\w\-_.]', '_', nom)
    
    # Supprimer les underscores multiples
    nom = re.sub(r'_+', '_', nom)
    
    # Limiter la longueur
    if len(nom) > 100:
        nom = nom[:100]
    
    # Supprimer les underscores en début/fin
    nom = nom.strip('_')
    
    return nom if nom else 'page_inconnue'


def get_saved_pages() -> list:
    """
    Récupère la liste des pages sauvegardées
    
    Returns:
        list: Liste des pages avec métadonnées
    """
    pages = []
    
    # Chercher tous les fichiers de métadonnées
    for fichier_meta in PAGES_STORAGE_DIR.glob("*_metadata.json"):
        try:
            with open(fichier_meta, 'r', encoding='utf-8') as f:
                metadonnees = json.load(f)
                
            # Vérifier que le fichier HTML existe toujours
            fichier_html = PAGES_STORAGE_DIR / metadonnees.get('fichier_html', '')
            if fichier_html.exists():
                metadonnees['chemin_complet'] = str(fichier_html)
                pages.append(metadonnees)
                
        except (json.JSONDecodeError, IOError):
            # Ignorer les fichiers corrompus
            continue
    
    # Trier par date de sauvegarde (plus récent en premier)
    pages.sort(key=lambda x: x.get('date_sauvegarde', ''), reverse=True)
    
    return pages


def delete_saved_page(nom_fichier: str) -> bool:
    """
    Supprime une page sauvegardée (HTML + métadonnées)
    
    Args:
        nom_fichier: Nom du fichier à supprimer (sans extension)
        
    Returns:
        bool: True si suppression réussie
    """
    try:
        # Supprimer le fichier HTML
        fichier_html = PAGES_STORAGE_DIR / f"{nom_fichier}.html"
        if fichier_html.exists():
            fichier_html.unlink()
        
        # Supprimer le fichier de métadonnées
        fichier_meta = PAGES_STORAGE_DIR / f"{nom_fichier}_metadata.json"
        if fichier_meta.exists():
            fichier_meta.unlink()
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de la suppression de {nom_fichier}: {e}")
        return False


def get_storage_stats() -> dict:
    """
    Récupère les statistiques du stockage
    
    Returns:
        dict: Statistiques du cache
    """
    pages = get_saved_pages()
    
    # Calculer la taille totale
    taille_totale = 0
    for page in pages:
        fichier_html = Path(page.get('chemin_complet', ''))
        if fichier_html.exists():
            taille_totale += fichier_html.stat().st_size
    
    # Grouper par domaine
    domaines = {}
    for page in pages:
        domaine = page.get('domaine', 'inconnu')
        if domaine not in domaines:
            domaines[domaine] = 0
        domaines[domaine] += 1
    
    return {
        'nombre_pages': len(pages),
        'taille_totale_mb': round(taille_totale / (1024 * 1024), 2),
        'domaines': domaines,
        'page_plus_recente': pages[0].get('date_sauvegarde') if pages else None,
        'page_plus_ancienne': pages[-1].get('date_sauvegarde') if pages else None
    }