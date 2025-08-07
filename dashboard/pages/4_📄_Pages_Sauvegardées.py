# -*- coding: utf-8 -*-
"""
4_📄_Pages_Sauvegardées.py

Page pour consulter et gérer les pages HTML sauvegardées.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import os

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.page_storage import get_saved_pages, get_storage_stats, cleanup_old_pages

st.set_page_config(page_title="Pages Sauvegardées", page_icon="📄", layout="wide")

# CSS personnalisé
st.markdown("""
<style>
    .page-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    
    .stats-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
    
    .page-url {
        color: #3b82f6;
        font-weight: 500;
        word-break: break-all;
    }
    
    .page-meta {
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    .storage-stat {
        text-align: center;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("📄 Pages Sauvegardées")

# Chargement des données
@st.cache_data
def load_page_data():
    pages = get_saved_pages()
    stats = get_storage_stats()
    return pages, stats

try:
    pages, stats = load_page_data()
    
    # Statistiques de stockage
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    st.subheader("📊 Statistiques de Stockage")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="storage-stat">', unsafe_allow_html=True)
        st.metric("📄 Pages totales", stats['total_pages'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="storage-stat">', unsafe_allow_html=True)
        st.metric("💾 Taille totale", f"{stats['total_size_mb']} MB")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="storage-stat">', unsafe_allow_html=True)
        if stats['oldest_date']:
            st.metric("📅 Plus ancienne", stats['oldest_date'])
        else:
            st.metric("📅 Plus ancienne", "N/A")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="storage-stat">', unsafe_allow_html=True)
        if stats['newest_date']:
            st.metric("🆕 Plus récente", stats['newest_date'])
        else:
            st.metric("🆕 Plus récente", "N/A")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if not pages:
        st.info("📭 Aucune page sauvegardée. Les pages seront automatiquement sauvegardées lors des prochaines analyses.")
        st.stop()
    
    # Options de gestion
    with st.sidebar:
        st.header("🛠️ Gestion des Pages")
        
        # Filtres
        st.subheader("🔍 Filtres")
        
        # Filtre par domaine
        domains = list(set(page['domain'] for page in pages))
        selected_domain = st.selectbox(
            "Filtrer par domaine",
            ["Tous"] + sorted(domains)
        )
        
        # Filtre par date
        date_filter = st.selectbox(
            "Période",
            ["Toutes", "Aujourd'hui", "7 derniers jours", "30 derniers jours"]
        )
        
        st.divider()
        
        # Actions de nettoyage
        st.subheader("🧹 Nettoyage")
        
        if st.button("🗑️ Nettoyer (30+ jours)", use_container_width=True):
            try:
                cleanup_old_pages(max_pages=1000, max_days=30)
                st.success("✅ Nettoyage effectué !")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur: {e}")
        
        if st.button("🗑️ Conserver 25 plus récentes", use_container_width=True):
            try:
                cleanup_old_pages(max_pages=25, max_days=365)
                st.success("✅ Nettoyage effectué !")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur: {e}")
        
        st.divider()
        
        # Informations
        st.subheader("ℹ️ Informations")
        st.write("Les pages sont automatiquement sauvegardées lors des analyses SEO.")
        st.write("💡 **Conseils:**")
        st.write("• Nettoyez régulièrement pour économiser l'espace")
        st.write("• Les pages récentes sont utiles pour les comparaisons")
    
    # Appliquer les filtres
    filtered_pages = pages
    
    # Filtre par domaine
    if selected_domain != "Tous":
        filtered_pages = [p for p in filtered_pages if p['domain'] == selected_domain]
    
    # Filtre par date
    if date_filter != "Toutes":
        now = datetime.now()
        
        if date_filter == "Aujourd'hui":
            cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_filter == "7 derniers jours":
            cutoff = now - timedelta(days=7)
        elif date_filter == "30 derniers jours":
            cutoff = now - timedelta(days=30)
        else:
            cutoff = None
        
        if cutoff:
            filtered_pages = [
                p for p in filtered_pages 
                if datetime.fromisoformat(p['download_date'].replace('Z', '+00:00')) >= cutoff
            ]
    
    # Affichage de la liste
    st.header(f"📋 Pages Disponibles ({len(filtered_pages)})")
    
    if not filtered_pages:
        st.info("🔍 Aucune page ne correspond aux filtres sélectionnés.")
    else:
        # Pagination
        pages_per_page = 10
        total_pages = len(filtered_pages)
        total_page_numbers = (total_pages + pages_per_page - 1) // pages_per_page
        
        if total_page_numbers > 1:
            page_number = st.selectbox(
                "Page",
                range(1, total_page_numbers + 1),
                format_func=lambda x: f"Page {x} / {total_page_numbers}"
            )
            
            start_idx = (page_number - 1) * pages_per_page
            end_idx = min(start_idx + pages_per_page, total_pages)
            current_page_items = filtered_pages[start_idx:end_idx]
        else:
            current_page_items = filtered_pages
        
        # Afficher les pages
        for i, page in enumerate(current_page_items):
            with st.container():
                st.markdown('<div class="page-card">', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f'<div class="page-url">{page["url"]}</div>', unsafe_allow_html=True)
                    
                    # Métadonnées
                    download_date = datetime.fromisoformat(page['download_date'].replace('Z', '+00:00'))
                    age_hours = (datetime.now() - download_date).total_seconds() / 3600
                    
                    if age_hours < 1:
                        age_str = f"{int(age_hours * 60)} min"
                    elif age_hours < 24:
                        age_str = f"{int(age_hours)} h"
                    else:
                        age_str = f"{int(age_hours / 24)} j"
                    
                    st.markdown(f'''
                    <div class="page-meta">
                        📅 {download_date.strftime("%d/%m/%Y %H:%M")} ({age_str}) | 
                        🌐 {page["domain"]} | 
                        📦 {page["html_size_kb"]} KB | 
                        🔗 {page["content_hash"][:8]}
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col2:
                    # Bouton pour voir le contenu
                    if st.button("👁️ Voir", key=f"view_{i}"):
                        # Lire et afficher le contenu HTML
                        try:
                            with open(page['html_path'], 'r', encoding='utf-8') as f:
                                html_content = f.read()
                            
                            # Créer un expander pour afficher le HTML
                            with st.expander(f"📄 Contenu HTML - {page['domain']}", expanded=True):
                                # Afficher les métadonnées
                                st.json({
                                    "URL": page["url"],
                                    "Taille": f"{page['html_size_kb']} KB",
                                    "Date": page["download_date"],
                                    "Hash": page["content_hash"]
                                })
                                
                                # Afficher un aperçu du HTML
                                st.code(html_content[:2000] + "..." if len(html_content) > 2000 else html_content, language="html")
                                
                                if len(html_content) > 2000:
                                    st.info(f"💡 Aperçu des premiers 2000 caractères (total: {len(html_content)} caractères)")
                        
                        except Exception as e:
                            st.error(f"❌ Erreur lors de la lecture du fichier: {e}")
                
                with col3:
                    # Bouton pour supprimer
                    if st.button("🗑️ Suppr.", key=f"delete_{i}"):
                        try:
                            # Supprimer les fichiers
                            os.remove(page['html_path'])
                            os.remove(page['metadata_path'])
                            st.success("✅ Page supprimée !")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur: {e}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                if i < len(current_page_items) - 1:
                    st.divider()

except Exception as e:
    st.error(f"❌ Erreur lors du chargement des pages: {str(e)}")
    st.exception(e)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem;">
    💡 <strong>Fonctionnement:</strong> Les pages sont automatiquement sauvegardées lors des analyses SEO.
    <br>
    🔄 Elles sont conservées pour permettre les comparaisons, le debug et l'historique des analyses.
    <br>
    🧹 Un nettoyage automatique supprime les pages de plus de 30 jours et limite le nombre total à 50.
</div>
""", unsafe_allow_html=True)