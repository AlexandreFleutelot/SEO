# -*- coding: utf-8 -*-
"""
2_📊_Comparaisons.py

Page de comparaison et d'analyse des tendances entre plusieurs rapports.
Interface consolidée avec comparaison de sites et évolution temporelle par page.
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

# CSS personnalisé pour les sections
st.markdown("""
<style>
    .comparison-section {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
    }
    
    .section-header {
        color: #1f2937;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .status-ready {
        background: #dcfce7;
        color: #166534;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 500;
    }
    
    .status-warning {
        background: #fef3c7;
        color: #92400e;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 500;
    }
    
    .status-info {
        background: #dbeafe;
        color: #1e40af;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

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

# Header avec actions globales
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### 🎛️ Centre de Comparaisons SEO")
    st.caption("Analysez et comparez vos données SEO sous différents angles")

with col2:
    if st.button("🔄 Rafraîchir toutes les données", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.divider()

# ==================== SECTION 1: COMPARAISON ENTRE SITES ====================
with st.expander("🌐 **Comparaison entre Sites et Analyses Détaillées**", expanded=True):
    st.markdown('<div class="section-header">🌐 Comparaison Multi-Sites avec Analyses Approfondies</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        multi_site_reports = st.multiselect(
            "Sélectionnez les sites/pages à comparer",
            options=reports,
            default=reports[:min(4, len(reports))],
            format_func=lambda x: f"🌐 {x['domain']} • {x['created_date'].strftime('%d/%m/%Y à %H:%M')}",
            key="multi_site_selection",
            help="Choisissez 2 à 6 sites pour une comparaison optimale avec analyses détaillées"
        )
    
    with col2:
        if multi_site_reports:
            if len(multi_site_reports) >= 2:
                st.markdown('<div class="status-ready">✅ Prêt - {} sites</div>'.format(len(multi_site_reports)), unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-warning">⚠️ Minimum 2 sites</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-info">🔍 Sélectionnez des sites</div>', unsafe_allow_html=True)
    
    # Affichage de la comparaison multi-sites
    if len(multi_site_reports) >= 2:
        # Préparer les données de comparaison
        report_ids = [r['id'] for r in multi_site_reports]
        comparison_df = loader.get_reports_comparison_data(report_ids)
        
        if not comparison_df.empty:
            # === MÉTRIQUES GÉNÉRALES ===
            st.markdown("#### 📊 Vue d'Ensemble")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_global = comparison_df['global_score'].mean()
                st.metric("📈 Score moyen", f"{avg_global:.1f}/100")
            
            with col2:
                best_site = comparison_df.loc[comparison_df['global_score'].idxmax(), 'domain']
                max_score = comparison_df['global_score'].max()
                st.metric("🏆 Meilleur site", best_site, delta=f"{max_score:.1f}/100")
            
            with col3:
                score_range = comparison_df['global_score'].max() - comparison_df['global_score'].min()
                st.metric("📊 Écart de performance", f"{score_range:.1f} points")
            
            # === GRAPHIQUE PRINCIPAL ===
            st.markdown("#### 📈 Comparaison Graphique")
            fig_comparison = create_comparison_bar_chart(comparison_df)
            st.plotly_chart(fig_comparison, use_container_width=True)
            
            # === TABLEAU DE SYNTHÈSE DÉTAILLÉ ===
            st.markdown("#### 📋 Tableau de Synthèse Détaillé")
            
            # Préparer le tableau d'affichage avec tous les scores
            display_columns = ['domain', 'global_score'] + [col for col in comparison_df.columns if col.endswith('_score') and col != 'global_score']
            display_df = comparison_df[display_columns].copy()
            
            # Renommer les colonnes pour l'affichage
            column_rename = {
                'domain': 'Site/Domaine',
                'global_score': 'Score Global',
                'content_semantics_score': 'Contenu & Sémantique',
                'technical_structure_score': 'Structure Technique',
                'internal_linking_score': 'Maillage Interne',
                'performance_score': 'Performance',
                'aio_optimization_score': 'Optimisation AIO',
                'llm_analysis_score': 'Analyse IA'
            }
            
            display_df = display_df.rename(columns=column_rename)
            
            # Formater les scores numériques
            numeric_cols = [col for col in display_df.columns if col != 'Site/Domaine']
            for col in numeric_cols:
                display_df[col] = display_df[col].round(1)
            
            # Styliser le tableau avec mise en surbrillance des meilleurs scores
            def highlight_best(s):
                if s.name == 'Site/Domaine':
                    return [''] * len(s)
                max_val = s.max()
                return ['background-color: #dcfce7; font-weight: bold' if v == max_val else '' for v in s]
            
            styled_df = display_df.style.apply(highlight_best, axis=0)
            st.dataframe(styled_df, use_container_width=True)
            
            # === ANALYSE PAR CATÉGORIE ===
            st.markdown("#### 📊 Performance par Catégorie")
            
            score_columns = [col for col in comparison_df.columns if col.endswith('_score') and col != 'global_score']
            
            # Créer un DataFrame pour l'analyse des catégories
            category_analysis = []
            for col in score_columns:
                if col in comparison_df.columns:
                    category_name = col.replace('_score', '').replace('_', ' ').title()
                    category_analysis.append({
                        'Catégorie': category_name,
                        'Score Moyen': comparison_df[col].mean(),
                        'Meilleur Score': comparison_df[col].max(),
                        'Plus Faible': comparison_df[col].min(),
                        'Écart': comparison_df[col].max() - comparison_df[col].min(),
                        'Leader': comparison_df.loc[comparison_df[col].idxmax(), 'domain']
                    })
            
            category_df = pd.DataFrame(category_analysis)
            
            # Afficher le tableau des catégories
            st.dataframe(
                category_df.style.format({
                    'Score Moyen': '{:.1f}',
                    'Meilleur Score': '{:.1f}',
                    'Plus Faible': '{:.1f}',
                    'Écart': '{:.1f}'
                }).highlight_max(subset=['Score Moyen', 'Meilleur Score'], color='#dcfce7'),
                use_container_width=True
            )
            
            # === HEATMAP DES PERFORMANCES ===
            st.markdown("#### 🔥 Matrice de Performance")
            
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
                colorbar=dict(title="Score (/100)")
            ))
            
            fig_heatmap.update_layout(
                title="Matrice de Performance par Site et Catégorie SEO",
                height=max(400, len(heatmap_data) * 60)
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
        else:
            st.error("❌ Impossible de charger les données de comparaison.")

st.divider()

# ==================== SECTION 2: ÉVOLUTION TEMPORELLE PAR PAGE ====================
with st.expander("📈 **Évolution Temporelle par Page**", expanded=True):
    st.markdown('<div class="section-header">📈 Suivi de l\'Évolution d\'une Page Spécifique</div>', unsafe_allow_html=True)
    
    # Regrouper les rapports par URL exacte (et non par domaine)
    pages_by_url = {}
    for report in reports:
        url = report.get('url', 'URL inconnue')
        if url not in pages_by_url:
            pages_by_url[url] = []
        pages_by_url[url].append(report)
    
    # Filtrer les URLs avec plusieurs rapports
    pages_with_history = {k: v for k, v in pages_by_url.items() if len(v) >= 2}
    
    if pages_with_history:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_url = st.selectbox(
                "Choisissez la page à analyser dans le temps",
                options=list(pages_with_history.keys()),
                format_func=lambda x: f"📊 {x[:80]}{'...' if len(x) > 80 else ''} ({len(pages_with_history[x])} analyses)",
                key="temporal_url_selection",
                help="Sélectionnez une page qui a été analysée plusieurs fois pour voir son évolution"
            )
        
        with col2:
            if selected_url:
                page_reports = pages_with_history[selected_url]
                st.markdown('<div class="status-ready">✅ {} analyses</div>'.format(len(page_reports)), unsafe_allow_html=True)
                # Calculer la période
                sorted_dates = sorted([r['created_date'] for r in page_reports])
                date_range = sorted_dates[-1] - sorted_dates[0]
                st.caption(f"📅 Période: {date_range.days} jours")
        
        # Affichage de l'évolution temporelle
        if selected_url:
            st.markdown("#### 📈 Évolution de la Page")
            temporal_reports = pages_with_history[selected_url]
            
            # Trier les rapports par date
            sorted_reports = sorted(temporal_reports, key=lambda x: x['created_date'])
            
            # Préparer les données temporelles avec toutes les catégories
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
                    
                    # Ajouter tous les scores de catégorie
                    for category, data in category_scores.items():
                        if isinstance(data, dict) and 'score' in data:
                            row[f"{category}_score"] = data['score']
                    
                    temporal_data.append(row)
            
            temporal_df = pd.DataFrame(temporal_data)
            
            if not temporal_df.empty and len(temporal_df) >= 2:
                # === MÉTRIQUES D'ÉVOLUTION ===
                col1, col2, col3, col4 = st.columns(4)
                
                first_score = temporal_df.iloc[0]['global_score']
                last_score = temporal_df.iloc[-1]['global_score']
                evolution = last_score - first_score
                
                with col1:
                    st.metric("📊 Score initial", f"{first_score:.1f}/100")
                
                with col2:
                    st.metric("📊 Score actuel", f"{last_score:.1f}/100", delta=f"{evolution:+.1f}")
                
                with col3:
                    period_days = (temporal_df.iloc[-1]['date'] - temporal_df.iloc[0]['date']).days
                    st.metric("📅 Période", f"{period_days} jours")
                
                with col4:
                    trend = "📈 Progression" if evolution > 1 else "📉 Régression" if evolution < -1 else "➡️ Stable"
                    st.metric("📊 Tendance", trend)
                
                # === GRAPHIQUE D'ÉVOLUTION GLOBALE ===
                st.markdown("#### 📈 Évolution du Score Global")
                
                fig_temporal = go.Figure()
                fig_temporal.add_trace(go.Scatter(
                    x=temporal_df['date'],
                    y=temporal_df['global_score'],
                    mode='lines+markers',
                    name='Score Global',
                    line=dict(color='#3b82f6', width=3),
                    marker=dict(size=8)
                ))
                
                fig_temporal.update_layout(
                    title=f"Évolution du Score Global SEO",
                    xaxis_title="Date d'analyse",
                    yaxis_title="Score Global (/100)",
                    height=400,
                    yaxis=dict(range=[0, 100])
                )
                
                st.plotly_chart(fig_temporal, use_container_width=True)
                
                # === ÉVOLUTION PAR CATÉGORIE ===
                st.markdown("#### 📊 Évolution par Catégorie SEO")
                
                score_columns = [col for col in temporal_df.columns if col.endswith('_score') and col != 'global_score']
                
                if score_columns:
                    fig_categories = go.Figure()
                    
                    colors = ['#3b82f6', '#ef4444', '#22c55e', '#eab308', '#8b5cf6', '#f97316', '#06b6d4']
                    
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
                        title="Évolution des Scores par Catégorie SEO",
                        xaxis_title="Date d'analyse",
                        yaxis_title="Score (/100)",
                        height=500,
                        yaxis=dict(range=[0, 100]),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig_categories, use_container_width=True)
                
                # === TABLEAU D'ÉVOLUTION DÉTAILLÉ ===
                st.markdown("#### 📋 Évolution Détaillée par Catégorie")
                
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
                            'Évolution (pts)': change,
                            'Évolution (%)': change_pct,
                            'Tendance': '📈' if change > 1 else '📉' if change < -1 else '➡️'
                        })
                
                evolution_df = pd.DataFrame(evolution_data)
                
                # Styliser le tableau d'évolution
                def color_evolution(val):
                    if isinstance(val, (int, float)):
                        if val > 1:
                            return 'background-color: #dcfce7; color: #166534'  # Vert pour amélioration
                        elif val < -1:
                            return 'background-color: #fee2e2; color: #991b1b'  # Rouge pour dégradation
                    return ''
                
                styled_evolution_df = evolution_df.style.format({
                    'Score Initial': '{:.1f}',
                    'Score Final': '{:.1f}',
                    'Évolution (pts)': '{:+.1f}',
                    'Évolution (%)': '{:+.1f}%'
                }).applymap(color_evolution, subset=['Évolution (pts)', 'Évolution (%)'])
                
                st.dataframe(styled_evolution_df, use_container_width=True)
                
            else:
                st.info("Pas assez de données pour afficher l'évolution de cette page.")
    else:
        st.info("🔍 Aucune page n'a été analysée plusieurs fois. Relancez des analyses sur les mêmes pages à différents moments pour voir leur évolution.")

# Footer avec conseils améliorés
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem; background: #f8fafc; border-radius: 8px;">
    💡 <strong>Guide d'utilisation des comparaisons:</strong>
    <br><br>
    🌐 <strong>Comparaison Multi-Sites:</strong> Comparez différents sites/pages entre eux avec tableau de synthèse, graphiques et matrice de performance
    <br><br>
    📈 <strong>Évolution Temporelle:</strong> Suivez les améliorations SEO d'une page spécifique dans le temps avec analyses détaillées par catégorie
    <br><br>
    🎯 <strong>Conseils:</strong> Analysez la même page plusieurs fois pour voir son évolution • Comparez avec la concurrence • Identifiez les axes d'amélioration prioritaires
</div>
""", unsafe_allow_html=True)