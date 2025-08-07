# -*- coding: utf-8 -*-
"""
2_📊_Comparaisons.py

Page de comparaison et d'analyse des tendances entre plusieurs rapports.
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import SEODataLoader
from dashboard.components.charts import create_comparison_bar_chart, create_trend_line_chart

st.set_page_config(page_title="Comparaisons", page_icon="📊", layout="wide")

st.title("📊 Comparaisons et Tendances")

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

if len(reports) < 2:
    st.info("Il faut au moins 2 rapports pour effectuer des comparaisons.")
    st.stop()

# Sidebar pour les options
with st.sidebar:
    st.header("🎛️ Options de Comparaison")
    
    # Type de comparaison
    comparison_type = st.selectbox(
        "Type de comparaison",
        ["Sites différents", "Évolution temporelle", "Analyse détaillée"]
    )
    
    st.divider()
    
    # Initialiser les variables
    selected_domain = None
    
    if comparison_type == "Sites différents":
        st.subheader("Sélection des sites")
        selected_reports = st.multiselect(
            "Choisir les rapports à comparer",
            options=reports,
            default=reports[:min(4, len(reports))],
            format_func=lambda x: f"{x['domain']} ({x['created_date'].strftime('%d/%m/%Y')})"
        )
        
    elif comparison_type == "Évolution temporelle":
        st.subheader("Sélection du domaine")
        
        # Regrouper les rapports par domaine
        domains = {}
        for report in reports:
            domain = report['domain']
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(report)
        
        # Filtrer les domaines avec plusieurs rapports
        domains_with_history = {k: v for k, v in domains.items() if len(v) >= 2}
        
        if not domains_with_history:
            st.warning("Aucun domaine n'a plusieurs rapports pour l'évolution temporelle.")
            st.stop()
        
        selected_domain = st.selectbox(
            "Choisir un domaine",
            options=list(domains_with_history.keys())
        )
        
        selected_reports = domains_with_history[selected_domain]
        
    else:  # Analyse détaillée
        st.subheader("Sélection pour analyse")
        selected_reports = st.multiselect(
            "Choisir 2-3 rapports pour l'analyse détaillée",
            options=reports,
            default=reports[:2],
            format_func=lambda x: f"{x['domain']} ({x['created_date'].strftime('%d/%m/%Y')})",
            max_selections=3
        )
    
    st.divider()
    
    # Bouton de rafraîchissement
    if st.button("🔄 Rafraîchir", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Les fonctions d'affichage seront appelées plus tard, après leur définition


def display_multi_site_comparison(loader, selected_reports):
    """Affiche la comparaison entre plusieurs sites."""
    
    if len(selected_reports) < 2:
        st.info("Sélectionnez au moins 2 sites pour la comparaison.")
        return
    
    st.header(f"🔍 Comparaison de {len(selected_reports)} Sites")
    
    # Préparer les données de comparaison
    report_ids = [r['id'] for r in selected_reports]
    comparison_df = loader.get_reports_comparison_data(report_ids)
    
    if comparison_df.empty:
        st.error("Impossible de charger les données de comparaison.")
        return
    
    # Vue d'ensemble
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_global = comparison_df['global_score'].mean()
        best_site = comparison_df.loc[comparison_df['global_score'].idxmax(), 'domain']
        st.metric("Score moyen", f"{avg_global:.1f}/100")
        
    with col2:
        max_score = comparison_df['global_score'].max()
        st.metric("Meilleur score", f"{max_score:.1f}/100", delta=f"({best_site})")
        
    with col3:
        score_range = comparison_df['global_score'].max() - comparison_df['global_score'].min()
        st.metric("Écart de performance", f"{score_range:.1f} points")
    
    # Graphique principal de comparaison
    fig_comparison = create_comparison_bar_chart(comparison_df)
    st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Analyse par catégorie
    st.subheader("📊 Analyse par Catégorie")
    
    score_columns = [col for col in comparison_df.columns if col.endswith('_score') and col != 'global_score']
    
    # Créer un DataFrame pour l'analyse des catégories
    category_analysis = []
    for col in score_columns:
        if col in comparison_df.columns:
            category_name = col.replace('_score', '').replace('_', ' ').title()
            category_analysis.append({
                'Catégorie': category_name,
                'Score Moyen': comparison_df[col].mean(),
                'Meilleur': comparison_df[col].max(),
                'Plus Faible': comparison_df[col].min(),
                'Écart': comparison_df[col].max() - comparison_df[col].min(),
                'Leader': comparison_df.loc[comparison_df[col].idxmax(), 'domain']
            })
    
    category_df = pd.DataFrame(category_analysis)
    
    # Tableau des performances par catégorie
    st.dataframe(
        category_df.style.format({
            'Score Moyen': '{:.1f}',
            'Meilleur': '{:.1f}',
            'Plus Faible': '{:.1f}',
            'Écart': '{:.1f}'
        }),
        use_container_width=True
    )
    
    # Heatmap des scores
    st.subheader("🔥 Heatmap des Performances")
    
    # Préparer les données pour la heatmap
    heatmap_data = comparison_df.set_index('domain')[score_columns]
    heatmap_data.columns = [col.replace('_score', '').replace('_', ' ').title() for col in heatmap_data.columns]
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='RdYlGn',
        text=heatmap_data.round(1).values,
        texttemplate="%{text}",
        textfont={"size": 12},
        colorbar=dict(title="Score")
    ))
    
    fig_heatmap.update_layout(
        title="Matrice de Performance par Site et Catégorie",
        height=400
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)


def display_temporal_evolution(loader, selected_reports, domain):
    """Affiche l'évolution temporelle d'un domaine."""
    
    st.header(f"📈 Évolution de {domain}")
    
    if len(selected_reports) < 2:
        st.info("Il faut au moins 2 rapports pour voir l'évolution.")
        return
    
    # Trier les rapports par date
    sorted_reports = sorted(selected_reports, key=lambda x: x['created_date'])
    
    # Préparer les données temporelles
    dates = [r['created_date'] for r in sorted_reports]
    report_ids = [r['id'] for r in sorted_reports]
    
    # Charger les scores pour chaque rapport
    temporal_data = []
    for report in sorted_reports:
        score_report = loader.load_score_report(report['id'])
        if score_report:
            global_analysis = score_report.get('global_analysis', {})
            category_scores = score_report.get('category_scores', {})
            
            row = {
                'date': report['created_date'],
                'global_score': global_analysis.get('global_score', 0)
            }
            
            for category, data in category_scores.items():
                if isinstance(data, dict) and 'score' in data:
                    row[f"{category}_score"] = data['score']
            
            temporal_data.append(row)
    
    temporal_df = pd.DataFrame(temporal_data)
    
    if temporal_df.empty:
        st.error("Impossible de charger les données temporelles.")
        return
    
    # Métriques d'évolution
    col1, col2, col3, col4 = st.columns(4)
    
    first_score = temporal_df.iloc[0]['global_score']
    last_score = temporal_df.iloc[-1]['global_score']
    evolution = last_score - first_score
    
    with col1:
        st.metric("Score initial", f"{first_score:.1f}/100")
    
    with col2:
        st.metric("Score actuel", f"{last_score:.1f}/100", delta=f"{evolution:+.1f}")
    
    with col3:
        period_days = (dates[-1] - dates[0]).days
        st.metric("Période d'analyse", f"{period_days} jours")
    
    with col4:
        trend = "📈 Progression" if evolution > 1 else "📉 Régression" if evolution < -1 else "➡️ Stable"
        st.metric("Tendance", trend)
    
    # Graphique d'évolution globale
    fig_global = go.Figure()
    
    fig_global.add_trace(go.Scatter(
        x=temporal_df['date'],
        y=temporal_df['global_score'],
        mode='lines+markers',
        name='Score Global',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=8)
    ))
    
    fig_global.update_layout(
        title="Évolution du Score Global SEO",
        xaxis_title="Date",
        yaxis_title="Score Global (/100)",
        height=400,
        yaxis=dict(range=[0, 100])
    )
    
    st.plotly_chart(fig_global, use_container_width=True)
    
    # Évolution par catégorie
    st.subheader("📊 Évolution par Catégorie")
    
    score_columns = [col for col in temporal_df.columns if col.endswith('_score') and col != 'global_score']
    
    fig_categories = go.Figure()
    
    colors = ['#3b82f6', '#ef4444', '#22c55e', '#eab308', '#8b5cf6', '#f97316']
    
    for i, col in enumerate(score_columns):
        category_name = col.replace('_score', '').replace('_', ' ').title()
        
        fig_categories.add_trace(go.Scatter(
            x=temporal_df['date'],
            y=temporal_df[col],
            mode='lines+markers',
            name=category_name,
            line=dict(color=colors[i % len(colors)], width=2),
            marker=dict(size=6)
        ))
    
    fig_categories.update_layout(
        title="Évolution des Scores par Catégorie",
        xaxis_title="Date",
        yaxis_title="Score (/100)",
        height=500,
        yaxis=dict(range=[0, 100])
    )
    
    st.plotly_chart(fig_categories, use_container_width=True)
    
    # Tableau d'évolution détaillé
    st.subheader("📋 Évolution Détaillée")
    
    # Calculer les changements
    evolution_data = []
    for col in ['global_score'] + score_columns:
        if col in temporal_df.columns and len(temporal_df) >= 2:
            first_val = temporal_df.iloc[0][col]
            last_val = temporal_df.iloc[-1][col]
            change = last_val - first_val
            change_pct = (change / first_val * 100) if first_val > 0 else 0
            
            category_name = col.replace('_score', '').replace('_', ' ').title()
            if col == 'global_score':
                category_name = 'Score Global'
            
            evolution_data.append({
                'Catégorie': category_name,
                'Score Initial': first_val,
                'Score Final': last_val,
                'Évolution': change,
                'Évolution (%)': change_pct,
                'Tendance': '📈' if change > 1 else '📉' if change < -1 else '➡️'
            })
    
    evolution_df = pd.DataFrame(evolution_data)
    
    st.dataframe(
        evolution_df.style.format({
            'Score Initial': '{:.1f}',
            'Score Final': '{:.1f}',
            'Évolution': '{:+.1f}',
            'Évolution (%)': '{:+.1f}%'
        }),
        use_container_width=True
    )


def display_detailed_analysis(loader, selected_reports):
    """Affiche une analyse détaillée comparative."""
    
    if len(selected_reports) < 2:
        st.info("Sélectionnez au moins 2 rapports pour l'analyse détaillée.")
        return
    
    st.header(f"🔬 Analyse Détaillée Comparative")
    
    # Vue d'ensemble rapide
    report_ids = [r['id'] for r in selected_reports]
    comparison_df = loader.get_reports_comparison_data(report_ids)
    
    if comparison_df.empty:
        st.error("Impossible de charger les données de comparaison.")
        return
    
    # Tableau de comparaison principal
    st.subheader("📊 Scores Comparatifs")
    
    # Préparer le tableau d'affichage
    display_columns = ['domain', 'global_score'] + [col for col in comparison_df.columns if col.endswith('_score') and col != 'global_score']
    display_df = comparison_df[display_columns].copy()
    
    # Renommer les colonnes
    column_rename = {
        'domain': 'Domaine',
        'global_score': 'Global',
        'content_semantics_score': 'Contenu',
        'technical_structure_score': 'Structure',
        'internal_linking_score': 'Maillage',
        'performance_score': 'Performance',
        'aio_optimization_score': 'AIO',
        'llm_analysis_score': 'IA'
    }
    
    display_df = display_df.rename(columns=column_rename)
    
    # Formater les scores numériques
    numeric_cols = [col for col in display_df.columns if col != 'Domaine']
    for col in numeric_cols:
        display_df[col] = display_df[col].round(1)
    
    # Styliser le tableau
    def highlight_best(s):
        if s.name == 'Domaine':
            return [''] * len(s)
        
        max_val = s.max()
        return ['background-color: #dcfce7' if v == max_val else '' for v in s]
    
    styled_df = display_df.style.apply(highlight_best, axis=0)
    st.dataframe(styled_df, use_container_width=True)
    
    # Analyses spécifiques par rapport
    st.divider()
    st.subheader("🔍 Analyses Spécifiques")
    
    tabs = st.tabs([f"📄 {report['domain']}" for report in selected_reports])
    
    for i, (tab, report) in enumerate(zip(tabs, selected_reports)):
        with tab:
            display_specific_report_analysis(loader, report)


def display_specific_report_analysis(loader, report):
    """Affiche l'analyse spécifique d'un rapport."""
    
    raw_report = loader.load_raw_report(report['id'])
    enhanced_insights = loader.get_enhanced_insights(report['id'])
    recommendations = loader.extract_recommendations(report['id'])
    
    if not raw_report:
        st.error("Impossible de charger les données du rapport.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📋 Informations générales:**")
        st.write(f"URL: {raw_report.get('url', 'N/A')}")
        st.write(f"Date: {report['created_date'].strftime('%d/%m/%Y à %H:%M')}")
        
        # Métriques de contenu
        content_data = raw_report.get('analysis_results', {}).get('category_1_content', {})
        if content_data:
            richness = content_data.get('1.1_richness_coverage', {})
            st.write(f"Mots: {richness.get('word_count', 0)}")
            st.write(f"Entités: {richness.get('entity_count', 0)}")
    
    with col2:
        st.write("**🧠 Insights avancés:**")
        
        if enhanced_insights.get('content'):
            content = enhanced_insights['content']
            if content.get('naturalness_score'):
                st.write(f"Authenticité: {content['naturalness_score']:.1f}/100")
                st.write(f"Type: {content.get('content_authenticity', 'N/A')}")
        
        if enhanced_insights.get('structure'):
            structure = enhanced_insights['structure']
            if structure.get('ssr_compatibility_score'):
                st.write(f"Compatibilité SSR: {structure['ssr_compatibility_score']:.1f}/100")
    
    # Top 3 recommandations
    if recommendations:
        st.write("**🎯 Top 3 Recommandations:**")
        
        all_recs = []
        for category_recs in recommendations.values():
            all_recs.extend(category_recs)
        
        for i, rec in enumerate(all_recs[:3], 1):
            st.write(f"{i}. {rec}")


# Fonction principale appelée lors du chargement de la page
if len(selected_reports) > 0:
    if comparison_type == "Sites différents":
        display_multi_site_comparison(loader, selected_reports)
    elif comparison_type == "Évolution temporelle":
        # Utiliser selected_domain défini dans la sidebar
        display_temporal_evolution(loader, selected_reports, selected_domain or "Inconnu")
    else:  # Analyse détaillée
        display_detailed_analysis(loader, selected_reports)
else:
    st.info("Sélectionnez des rapports dans la sidebar pour commencer l'analyse comparative.")