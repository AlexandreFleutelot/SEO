# -*- coding: utf-8 -*-
"""
1_🔍_Analyse_Détaillée.py

Page d'analyse détaillée pour un rapport spécifique.
"""

import streamlit as st
import sys
from pathlib import Path
import json

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import SEODataLoader
from dashboard.components.charts import create_score_gauge, display_score_card
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Analyse Détaillée", page_icon="🔍", layout="wide")

st.title("🔍 Analyse Détaillée")

# Chargement des données
@st.cache_data
def load_data(_last_modified: float):
    loader = SEODataLoader()
    reports = loader.get_available_reports()
    return loader, reports

# Charger avec détection des changements
temp_loader = SEODataLoader()
last_modified = temp_loader.get_reports_last_modified()
loader, reports = load_data(last_modified)

if not reports:
    st.warning("Aucun rapport disponible. Lancez d'abord une analyse.")
    st.stop()

# Sélection du rapport avec design amélioré
st.subheader("🎯 Sélection du Rapport à Analyser")

col1, col2 = st.columns([3, 1])

with col1:
    selected_report = st.selectbox(
        "Choisissez le rapport à analyser en détail",
        options=reports,
        format_func=lambda x: f"🌐 {x['domain']} • {x['created_date'].strftime('%d/%m/%Y à %H:%M')}",
        help="Sélectionnez un rapport pour accéder à l'analyse détaillée de toutes ses métriques SEO"
    )

with col2:
    if st.button("🔄 Rafraîchir", use_container_width=True, help="Actualiser les données"):
        st.cache_data.clear()
        st.rerun()

if not selected_report:
    st.stop()

st.divider()

# Chargement des données détaillées
raw_report = loader.load_raw_report(selected_report['id'])
score_report = loader.load_score_report(selected_report['id'])

if not raw_report or not score_report:
    st.error("Impossible de charger les données du rapport.")
    st.stop()

# Affichage des informations générales
st.header("📋 Informations Générales")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("URL", raw_report.get('url', 'N/A'))
with col2:
    st.metric("Date d'analyse", selected_report['created_date'].strftime('%d/%m/%Y à %H:%M'))
with col3:
    global_score = score_report.get('global_analysis', {}).get('global_score', 0)
    st.metric("Score Global", f"{global_score:.1f}/100")

st.divider()

# Tabs pour les différentes catégories d'analyse
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📝 Contenu", "🏗️ Structure", "🔗 Maillage", 
    "⚡ Performance", "🤖 AIO", "🧠 IA Avancée"
])

with tab1:
    st.subheader("📝 Analyse du Contenu")
    
    content_data = raw_report.get('analysis_results', {}).get('category_1_content', {})
    
    # Métriques de base
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        richness = content_data.get('1.1_richness_coverage', {})
        word_count = richness.get('word_count', 0)
        st.metric("Nombre de mots", word_count)
    
    with col2:
        entity_count = richness.get('entity_count', 0)
        st.metric("Entités détectées", entity_count)
    
    with col3:
        style = content_data.get('1.2_style_clarity', {})
        avg_length = style.get('avg_sentence_length_words', 0)
        st.metric("Longueur moyenne des phrases", f"{avg_length:.1f} mots")
    
    with col4:
        list_count = style.get('list_count', 0)
        st.metric("Listes structurées", list_count)
    
    # Distribution des entités
    if richness.get('entity_distribution'):
        st.subheader("Distribution des entités")
        
        entity_dist = richness['entity_distribution']
        fig = go.Figure(data=[go.Bar(
            x=list(entity_dist.keys()),
            y=list(entity_dist.values()),
            marker_color=['#3b82f6', '#ef4444', '#22c55e', '#eab308']
        )])
        
        fig.update_layout(
            title="Répartition des types d'entités",
            xaxis_title="Types d'entités",
            yaxis_title="Nombre",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Liens externes
    sources = content_data.get('1.3_sources_reliability', {})
    if sources.get('external_links'):
        st.subheader("Liens externes")
        for i, link in enumerate(sources['external_links'][:5], 1):
            st.write(f"{i}. {link}")

with tab2:
    st.subheader("🏗️ Analyse de la Structure")
    
    structure_data = raw_report.get('analysis_results', {}).get('category_2_structure', {})
    
    # Structure des titres
    hn_structure = structure_data.get('2.1_hn_structure', {})
    st.subheader("Structure des titres")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Nombre de H1", hn_structure.get('h1_count', 0))
        
        headings = hn_structure.get('headings_by_level', {})
        for level, titles in headings.items():
            if titles:
                st.write(f"**{level.upper()}** ({len(titles)})")
                for title in titles[:3]:  # Limiter à 3 pour l'affichage
                    st.write(f"• {title}")
                if len(titles) > 3:
                    st.write(f"... et {len(titles) - 3} autres")
    
    with col2:
        # Métadonnées
        metadata = structure_data.get('2.2_metadata', {})
        st.write("**Métadonnées:**")
        st.write(f"Titre: {metadata.get('title_length', 0)} caractères")
        st.write(f"Description: {metadata.get('meta_description_length', 0)} caractères")
        
        # Images
        images = structure_data.get('2.3_images_optimization', {})
        st.write(f"**Images:** {images.get('total_images', 0)} total")
        st.write(f"Alt text: {images.get('alt_coverage_percentage', 0):.1f}% couverture")

with tab3:
    st.subheader("🔗 Analyse du Maillage")
    
    linking_data = raw_report.get('analysis_results', {}).get('category_3_linking', {})
    internal_linking = linking_data.get('3.1_3.2_internal_linking', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Liens internes", internal_linking.get('internal_link_count', 0))
        st.metric("Diversité des ancres", internal_linking.get('anchor_text_diversity', 0))
    
    with col2:
        st.metric("Ancres non descriptives", internal_linking.get('non_descriptive_anchor_count', 0))
    
    # Distribution des textes d'ancrage
    anchor_dist = internal_linking.get('anchor_text_distribution', {})
    if anchor_dist:
        st.subheader("Top 10 des textes d'ancrage")
        
        # Trier par fréquence
        sorted_anchors = sorted(anchor_dist.items(), key=lambda x: x[1], reverse=True)[:10]
        
        fig = go.Figure(data=[go.Bar(
            x=[item[1] for item in sorted_anchors],
            y=[item[0] for item in sorted_anchors],
            orientation='h',
            marker_color='#3b82f6'
        )])
        
        fig.update_layout(
            title="Fréquence des textes d'ancrage",
            xaxis_title="Nombre d'occurrences",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("⚡ Analyse des Performances")
    
    performance_data = raw_report.get('analysis_results', {}).get('category_4_performance', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🖥️ Desktop**")
        desktop = performance_data.get('4.1_4.2_desktop_performance', {})
        
        if not desktop.get('error'):
            st.metric("LCP", f"{desktop.get('LCP_ms', 0):.0f} ms")
            st.metric("INP", f"{desktop.get('INP_ms', 0):.0f} ms")
            st.metric("CLS", f"{desktop.get('CLS_score', 0):.3f}")
        else:
            st.write("Données non disponibles")
            st.write(f"Erreur: {desktop.get('error', 'Inconnue')}")
    
    with col2:
        st.write("**📱 Mobile**")
        mobile = performance_data.get('4.1_4.2_mobile_performance', {})
        
        if not mobile.get('error'):
            st.metric("LCP", f"{mobile.get('LCP_ms', 0):.0f} ms")
            st.metric("INP", f"{mobile.get('INP_ms', 0):.0f} ms")
            st.metric("CLS", f"{mobile.get('CLS_score', 0):.3f}")
        else:
            st.write("Données non disponibles")
            st.write(f"Erreur: {mobile.get('error', 'Inconnue')}")

with tab5:
    st.subheader("🤖 Optimisation AIO")
    
    aio_data = raw_report.get('analysis_results', {}).get('category_5_aio', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        atomicity = aio_data.get('5.1_atomicity_direct_answer', {})
        st.metric("Paires Q&A potentielles", atomicity.get('potential_qa_pairs', 0))
        st.metric("Blocs de résumé", atomicity.get('summary_block_count', 0))
    
    with col2:
        quantifiable = aio_data.get('5.2_quantifiable_data', {})
        st.metric("Pourcentages", quantifiable.get('percentage_count', 0))
        st.metric("Mentions monétaires", quantifiable.get('currency_mention_count', 0))
        st.metric("Dates numériques", quantifiable.get('numeric_date_count', 0))
    
    # Signaux d'expertise
    expertise = aio_data.get('5.3_expertise_signals', {})
    multimodal = aio_data.get('5.4_multimodal_interoperability', {})
    
    st.subheader("Signaux d'autorité")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Schéma auteur:** {'✅' if expertise.get('author_schema_present') else '❌'}")
        st.write(f"**Page à propos:** {'✅' if expertise.get('about_page_linked') else '❌'}")
    
    with col2:
        st.write(f"**Vidéos intégrées:** {multimodal.get('video_embed_count', 0)}")
        st.write(f"**Liens API potentiels:** {multimodal.get('potential_api_link_count', 0)}")

with tab6:
    st.subheader("🧠 Analyses IA Avancées")
    
    # Analyse LLM classique
    llm_data = raw_report.get('analysis_results', {}).get('category_6_llm_analysis', {})
    
    if not any(analysis.get('error') for analysis in llm_data.values()):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Qualité E-A-T")
            eat = llm_data.get('6.1_content_quality_eat', {})
            if not eat.get('error'):
                st.metric("Score E-A-T global", f"{eat.get('overall_eat_score', 0)}/10")
                st.metric("Expertise", f"{eat.get('expertise_score', 0)}/10")
                st.metric("Autorité", f"{eat.get('authoritativeness_score', 0)}/10")
                st.metric("Confiance", f"{eat.get('trustworthiness_score', 0)}/10")
        
        with col2:
            st.subheader("Intention de recherche")
            intent = llm_data.get('6.2_search_intent', {})
            if not intent.get('error'):
                st.write(f"**Intention primaire:** {intent.get('primary_intent', 'N/A')}")
                st.write(f"**Score de satisfaction:** {intent.get('intent_fulfillment_score', 0)}/10")
                st.write(f"**Alignement requête:** {intent.get('query_alignment_score', 0)}/10")
                
                keywords = intent.get('target_keywords_identified', [])
                if keywords:
                    st.write("**Mots-clés identifiés:**")
                    for kw in keywords:
                        st.write(f"• {kw}")
    
    # Analyses améliorées
    enhanced_content = raw_report.get('analysis_results', {}).get('enhanced_content_analysis', {})
    enhanced_structure = raw_report.get('analysis_results', {}).get('enhanced_structure_analysis', {})
    
    if enhanced_content or enhanced_structure:
        st.divider()
        st.subheader("🔬 Analyses Améliorées")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if enhanced_content:
                st.write("**Contenu Amélioré:**")
                
                density = enhanced_content.get('1.1_informational_density', {})
                st.metric("Densité informationnelle", f"{density.get('informational_density_score', 0):.1f}/100")
                
                ai_detection = enhanced_content.get('1.3_ai_generated_detection', {})
                st.metric("Naturalité", f"{ai_detection.get('naturalness_score', 0):.1f}/100")
                st.write(f"Authenticité: {ai_detection.get('content_authenticity', 'N/A')}")
        
        with col2:
            if enhanced_structure:
                st.write("**Structure Améliorée:**")
                
                ssr = enhanced_structure.get('2.1_ssr_javascript', {})
                st.metric("Compatibilité SSR", f"{ssr.get('ssr_compatibility_score', 0):.1f}/100")
                
                year_meta = enhanced_structure.get('2.2_year_metadata', {})
                st.metric("Fraîcheur temporelle", f"{year_meta.get('freshness_score', 0):.1f}/100")
                st.write(f"Niveau: {year_meta.get('freshness_level', 'N/A')}")

# Section JSON brut (optionnelle)
with st.expander("🔍 Données JSON brutes"):
    st.json(raw_report)