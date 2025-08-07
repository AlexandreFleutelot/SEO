# -*- coding: utf-8 -*-
"""
page_storage.py

Utilitaires pour la sauvegarde et la gestion des pages HTML téléchargées.
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse
import hashlib
import re


def sanitize_filename(url: str) -> str:
    """
    Convertit une URL en nom de fichier sécurisé.
    
    Args:
        url (str): URL à convertir
        
    Returns:
        str: Nom de fichier sécurisé
    """
    # Parse l'URL
    parsed = urlparse(url)
    
    # Créer un nom basé sur le domaine et le chemin
    domain = parsed.netloc.replace('www.', '')
    path = parsed.path.strip('/')
    
    # Remplacer les caractères problématiques
    safe_chars = re.sub(r'[^\w\-_.]', '_', f"{domain}_{path}")
    
    # Limiter la longueur et nettoyer
    safe_chars = safe_chars.replace('__', '_').strip('_')[:100]
    
    return safe_chars


def save_page_content(url: str, html_content: str, response_headers: dict = None) -> str:
    """
    Sauvegarde le contenu HTML d'une page avec ses métadonnées.
    
    Args:
        url (str): URL de la page
        html_content (str): Contenu HTML brut
        response_headers (dict, optional): Headers de la réponse HTTP
        
    Returns:
        str: Chemin du fichier sauvegardé
    """
    # Créer le dossier s'il n'existe pas
    pages_dir = Path("data/pages")
    pages_dir.mkdir(parents=True, exist_ok=True)
    
    # Générer le nom de fichier
    safe_filename = sanitize_filename(url)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Nom de fichier avec horodatage
    html_filename = f"{safe_filename}_{timestamp}.html"
    metadata_filename = f"{safe_filename}_{timestamp}_metadata.json"
    
    html_path = pages_dir / html_filename
    metadata_path = pages_dir / metadata_filename
    
    # Sauvegarder le HTML
    try:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Sauvegarder les métadonnées
        metadata = {
            "url": url,
            "download_date": datetime.now().isoformat(),
            "html_file": html_filename,
            "html_size_bytes": len(html_content.encode('utf-8')),
            "html_size_kb": round(len(html_content.encode('utf-8')) / 1024, 2),
            "content_hash": hashlib.md5(html_content.encode('utf-8')).hexdigest(),
            "response_headers": response_headers or {},
            "domain": urlparse(url).netloc,
            "path": urlparse(url).path
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Page sauvegardée: {html_path}")
        print(f"📋 Métadonnées: {metadata_path}")
        
        return str(html_path)
        
    except Exception as e:
        print(f"⚠️ Erreur lors de la sauvegarde de la page: {e}")
        return ""


def get_saved_pages() -> list:
    """
    Récupère la liste des pages sauvegardées avec leurs métadonnées.
    
    Returns:
        list: Liste des pages sauvegardées avec leurs métadonnées
    """
    pages_dir = Path("data/pages")
    
    if not pages_dir.exists():
        return []
    
    saved_pages = []
    
    # Parcourir tous les fichiers metadata
    for metadata_file in pages_dir.glob("*_metadata.json"):
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Vérifier que le fichier HTML existe encore
            html_path = pages_dir / metadata['html_file']
            if html_path.exists():
                metadata['html_path'] = str(html_path)
                metadata['metadata_path'] = str(metadata_file)
                saved_pages.append(metadata)
                
        except Exception as e:
            print(f"⚠️ Erreur lors de la lecture de {metadata_file}: {e}")
    
    # Trier par date de téléchargement (plus récent en premier)
    saved_pages.sort(key=lambda x: x['download_date'], reverse=True)
    
    return saved_pages


def cleanup_old_pages(max_pages: int = 100, max_days: int = 30):
    """
    Nettoie les anciennes pages sauvegardées.
    
    Args:
        max_pages (int): Nombre maximum de pages à conserver
        max_days (int): Âge maximum des pages en jours
    """
    pages_dir = Path("data/pages")
    
    if not pages_dir.exists():
        return
    
    saved_pages = get_saved_pages()
    
    # Nettoyer par nombre
    if len(saved_pages) > max_pages:
        pages_to_delete = saved_pages[max_pages:]
        for page in pages_to_delete:
            try:
                os.remove(page['html_path'])
                os.remove(page['metadata_path'])
                print(f"🗑️ Supprimé: {page['html_file']} (limite de {max_pages} pages)")
            except Exception as e:
                print(f"⚠️ Erreur lors de la suppression: {e}")
    
    # Nettoyer par âge
    cutoff_date = datetime.now() - timedelta(days=max_days)
    
    for page in saved_pages:
        try:
            download_date = datetime.fromisoformat(page['download_date'].replace('Z', '+00:00'))
            if download_date < cutoff_date:
                os.remove(page['html_path'])
                os.remove(page['metadata_path'])
                print(f"🗑️ Supprimé: {page['html_file']} (plus de {max_days} jours)")
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage par âge: {e}")


def find_page_by_url(url: str, tolerance_hours: int = 24) -> dict:
    """
    Trouve une page sauvegardée correspondant à l'URL donnée.
    
    Args:
        url (str): URL à chercher
        tolerance_hours (int): Tolérance en heures pour considérer une page comme récente
        
    Returns:
        dict: Métadonnées de la page trouvée ou None
    """
    saved_pages = get_saved_pages()
    
    for page in saved_pages:
        if page['url'] == url:
            # Vérifier si la page est assez récente
            download_date = datetime.fromisoformat(page['download_date'].replace('Z', '+00:00'))
            age_hours = (datetime.now() - download_date).total_seconds() / 3600
            
            if age_hours <= tolerance_hours:
                return page
    
    return None


def get_storage_stats() -> dict:
    """
    Retourne des statistiques sur le stockage des pages.
    
    Returns:
        dict: Statistiques de stockage
    """
    pages_dir = Path("data/pages")
    
    if not pages_dir.exists():
        return {
            "total_pages": 0,
            "total_size_mb": 0,
            "oldest_date": None,
            "newest_date": None
        }
    
    saved_pages = get_saved_pages()
    
    if not saved_pages:
        return {
            "total_pages": 0,
            "total_size_mb": 0,
            "oldest_date": None,
            "newest_date": None
        }
    
    total_size = sum(page.get('html_size_bytes', 0) for page in saved_pages)
    
    dates = [datetime.fromisoformat(page['download_date'].replace('Z', '+00:00')) for page in saved_pages]
    
    return {
        "total_pages": len(saved_pages),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "oldest_date": min(dates).strftime('%d/%m/%Y %H:%M'),
        "newest_date": max(dates).strftime('%d/%m/%Y %H:%M'),
        "average_size_kb": round(total_size / len(saved_pages) / 1024, 2)
    }