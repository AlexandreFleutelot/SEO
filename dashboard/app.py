# -*- coding: utf-8 -*-
"""
app.py

Dashboard SEO interactif avec Streamlit.
Interface principale pour visualiser les analyses SEO.
"""

import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from dashboard.utils.data_loader import SEODataLoader, get_mock_data_for_demo
from dashboard.components.charts import (
    create_score_gauge, create_category_radar, create_comparison_bar_chart,
    create_trend_line_chart, create_performance_waterfall,
    create_enhanced_insights_chart, create_recommendations_priority_chart,
    display_score_card
)
from dashboard.style import inject_dashboard_styles
import pandas as pd
from datetime import datetime
import json


# Configuration de la page
st.set_page_config(
    page_title="Dashboard SEO",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injecter les styles CSS centralisés
inject_dashboard_styles()


@st.cache_data
def load_data(_last_modified: float):
    """Charge les données avec cache Streamlit basé sur l'horodatage."""
    loader = SEODataLoader()
    reports = loader.get_available_reports()
    return loader, reports


def main():
    """Fonction principale du dashboard."""

    # Header principal
    st.markdown('<h1 class="main-header">🔍 Dashboard SEO</h1>', unsafe_allow_html=True)

    # Chargement des données avec détection des changements
    try:
        temp_loader = SEODataLoader()
        last_modified = temp_loader.get_reports_last_modified()
        loader, reports = load_data(last_modified)

        if not reports:
            st.warning("🚨 Aucun rapport SEO disponible. Lancez d'abord une analyse avec `uv run python -m src.page_analyzer`")
            st.info("💡 En attendant, voici un aperçu du dashboard avec des données de démonstration :")
            show_demo_dashboard()
            return

        # Sélections sur la page principale
        col1, col2 = st.columns(2)
        with col1:
            # Sélection du domaine
            domains = sorted(list(set(r['domain'] for r in reports)))
            selected_domains = st.multiselect(
                "Choisir un ou plusieurs domaines",
                options=domains,
                default=domains if domains else [],
                key="domain_filter"
            )

        # Filtrer les rapports par domaine
        if not selected_domains:
            reports_for_selection = reports
        else:
            reports_for_selection = [r for r in reports if r['domain'] in selected_domains]

        with col2:
            # Sélection du rapport principal
            selected_reports = st.multiselect(
                "Choisir un ou plusieurs rapports",
                options=reports_for_selection,
                default=reports_for_selection[:1],
                format_func=lambda x: f"{x['url']} ({x['created_date'].strftime('%d/%m/%Y %H:%M')})",
                key="main_report"
            )

        st.divider()

        # Sidebar pour les options et informations
        with st.sidebar:
            st.header("📊 Configuration")
            # Options d'affichage
            st.subheader("🎨 Options d'affichage")
            show_detailed_metrics = st.checkbox("Métriques détaillées", value=True)
            show_recommendations = st.checkbox("Recommandations", value=True)
            show_enhanced_analysis = st.checkbox("Analyses améliorées", value=True)

            st.divider()

            # Bouton de rafraîchissement
            if st.button("🔄 Rafraîchir", use_container_width=True):
                st.cache_data.clear()
                st.rerun()

            st.divider()

            # Informations sur le rapport (si un seul est sélectionné)
            if len(selected_reports) == 1:
                st.subheader("📋 Informations")
                report_info = selected_reports[0]
                st.write(f"**URL:** {report_info['url']}")
                st.write(f"**Domaine:** {report_info['domain']}")
                st.write(f"**Date:** {report_info['created_date'].strftime('%d/%m/%Y à %H:%M')}")
                st.write(f"**Scores disponibles:** {'✅' if report_info['has_scores'] else '❌'}")

        # Contenu principal
        if not selected_reports:
            st.info("💡 Sélectionnez un ou plusieurs rapports pour commencer.")
            return

        if len(selected_reports) == 1:
            selected_report = selected_reports[0]
            if not selected_report['has_scores']:
                st.error("❌ Pas de rapport de scores disponible pour cette analyse.")
                st.info("💡 Relancez l'analyse pour générer automatiquement les scores.")
                return

            score_report = loader.load_score_report(selected_report['id'])
            raw_report = loader.load_raw_report(selected_report['id'])

            if not score_report:
                st.error("❌ Impossible de charger le rapport de scores.")
                return

            display_main_dashboard(loader, score_report, raw_report, show_detailed_metrics,
                                 show_recommendations, show_enhanced_analysis)
        else: # len(selected_reports) > 1
             display_comparison_section(loader, selected_reports)


    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données : {str(e)}")
        st.info("💡 Vérifiez que les rapports sont bien générés dans le dossier reports/")


def display_main_dashboard(loader, score_report, raw_report, show_detailed_metrics,
                          show_recommendations, show_enhanced_analysis):
    """Affiche le dashboard principal."""

    global_analysis = score_report.get("global_analysis", {})
    category_scores = score_report.get("category_scores", {})

    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        display_score_card(
            "Score Global",
            global_analysis.get("global_score", 0),
            f"Niveau: {global_analysis.get('performance_level', 'N/A')}"
        )

    with col2:
        content_score = category_scores.get("content_semantics", {}).get("score", 0)
        display_score_card(
            "Contenu & Sémantique",
            content_score,
            "Qualité du contenu"
        )

    with col3:
        perf_score = category_scores.get("performance", {}).get("score", 0)
        display_score_card(
            "Performance",
            perf_score,
            "Core Web Vitals"
        )

    with col4:
        llm_score = category_scores.get("llm_analysis", {}).get("score", 0)
        display_score_card(
            "Analyse IA",
            llm_score,
            "Optimisation LLM"
        )

    # Graphiques principaux
    st.divider()

    # Tabs pour organiser le contenu
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Vue d'ensemble", "⚡ Performance", "🧠 Analyses IA", "📋 Recommandations"])

    with tab1:
        col1, col2 = st.columns([1, 1])

        with col1:
            # Score global en gauge
            global_score = global_analysis.get("global_score", 0)
            fig_gauge = create_score_gauge(global_score, "Score SEO Global")
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col2:
            # Radar des catégories
            scores_dict = {}
            for category, data in category_scores.items():
                if isinstance(data, dict) and "score" in data:
                    scores_dict[category] = data["score"]

            fig_radar = create_category_radar(scores_dict)
            st.plotly_chart(fig_radar, use_container_width=True)

        # Forces et faiblesses
        if show_detailed_metrics:
            st.subheader("💪 Forces et Faiblesses")

            col1, col2 = st.columns(2)

            with col1:
                st.write("**🎯 Points forts:**")
                strengths = global_analysis.get("strengths", [])
                if strengths:
                    for strength in strengths:
                        category_name = strength.replace("category_", "").replace("_", " ").title()
                        st.markdown(f'<span class="improvement-badge">✅ {category_name}</span>', unsafe_allow_html=True)
                else:
                    st.write("Aucun point fort identifié")

            with col2:
                st.write("**⚠️ Points à améliorer:**")
                weaknesses = global_analysis.get("weaknesses", [])
                if weaknesses:
                    for weakness in weaknesses:
                        category_name = weakness.replace("category_", "").replace("_", " ").title()
                        st.markdown(f'<span class="warning-badge">⚠️ {category_name}</span>', unsafe_allow_html=True)
                else:
                    st.write("Aucun point faible majeur")

    with tab2:
        display_performance_tab(loader, raw_report)

    with tab3:
        if show_enhanced_analysis:
            display_enhanced_analysis_tab(loader, raw_report)
        else:
            st.info("💡 Activez les 'Analyses améliorées' dans la sidebar pour voir cette section.")

    with tab4:
        if show_recommendations:
            display_recommendations_tab(loader, raw_report)
        else:
            st.info("💡 Activez les 'Recommandations' dans la sidebar pour voir cette section.")


def display_performance_tab(loader, raw_report):
    """Affiche l'onglet Performance."""
    st.subheader("⚡ Métriques de Performance")

    if not raw_report:
        st.warning("Données de performance non disponibles")
        return

    performance_metrics = loader.get_performance_metrics(raw_report.get('url', '').split('/')[-1])

    if not performance_metrics:
        st.warning("❌ Aucune donnée de performance Core Web Vitals disponible")
        st.info("💡 Vérifiez que la clé API Google PageSpeed est configurée dans le fichier .env")
        return

    # Graphique des Core Web Vitals
    desktop_scores = performance_metrics.get("desktop", {})
    mobile_scores = performance_metrics.get("mobile", {})

    if desktop_scores or mobile_scores:
        fig_perf = create_performance_waterfall(desktop_scores, mobile_scores)
        st.plotly_chart(fig_perf, use_container_width=True)

    # Détails des métriques
    col1, col2 = st.columns(2)

    with col1:
        st.write("**🖥️ Desktop Performance**")
        if desktop_scores:
            lcp = desktop_scores.get('LCP', 0)
            inp = desktop_scores.get('INP', 0)
            cls = desktop_scores.get('CLS', 0)

            st.metric("LCP (Largest Contentful Paint)", f"{lcp:.0f} ms",
                     delta="Bon" if lcp <= 2500 else "À améliorer" if lcp <= 4000 else "Critique")
            st.metric("INP (Interaction to Next Paint)", f"{inp:.0f} ms",
                     delta="Bon" if inp <= 200 else "À améliorer" if inp <= 500 else "Critique")
            st.metric("CLS (Cumulative Layout Shift)", f"{cls:.3f}",
                     delta="Bon" if cls <= 0.1 else "À améliorer" if cls <= 0.25 else "Critique")
        else:
            st.write("Données non disponibles")

    with col2:
        st.write("**📱 Mobile Performance**")
        if mobile_scores:
            lcp = mobile_scores.get('LCP', 0)
            inp = mobile_scores.get('INP', 0)
            cls = mobile_scores.get('CLS', 0)

            st.metric("LCP (Largest Contentful Paint)", f"{lcp:.0f} ms",
                     delta="Bon" if lcp <= 2500 else "À améliorer" if lcp <= 4000 else "Critique")
            st.metric("INP (Interaction to Next Paint)", f"{inp:.0f} ms",
                     delta="Bon" if inp <= 200 else "À améliorer" if inp <= 500 else "Critique")
            st.metric("CLS (Cumulative Layout Shift)", f"{cls:.3f}",
                     delta="Bon" if cls <= 0.1 else "À améliorer" if cls <= 0.25 else "Critique")
        else:
            st.write("Données non disponibles")


def display_enhanced_analysis_tab(loader, raw_report):
    """Affiche l'onglet des analyses améliorées."""
    st.subheader("🧠 Analyses Améliorées (LLM/GEO)")

    if not raw_report:
        st.warning("Données d'analyse améliorée non disponibles")
        return

    insights = loader.get_enhanced_insights(raw_report.get('url', '').split('/')[-1])

    if not insights:
        st.warning("❌ Aucune analyse améliorée disponible")
        return

    # Graphique des insights
    fig_insights = create_enhanced_insights_chart(insights)
    st.plotly_chart(fig_insights, use_container_width=True)

    # Détails des analyses
    col1, col2 = st.columns(2)

    with col1:
        st.write("**📝 Analyses de Contenu**")
        content = insights.get("content", {})

        if content.get("informational_density_score") is not None:
            st.metric("Densité Informationnelle", f"{content['informational_density_score']:.1f}/100")

        if content.get("naturalness_score") is not None:
            st.metric("Authenticité du Contenu", f"{content['naturalness_score']:.1f}/100",
                     delta=content.get("content_authenticity", ""))

        if content.get("data_originality_score") is not None:
            st.metric("Données Originales", f"{content['data_originality_score']:.1f}/100")

    with col2:
        st.write("**🏗️ Analyses de Structure**")
        structure = insights.get("structure", {})

        if structure.get("ssr_compatibility_score") is not None:
            st.metric("Compatibilité SSR", f"{structure['ssr_compatibility_score']:.1f}/100")

        if structure.get("freshness_score") is not None:
            st.metric("Fraîcheur Temporelle", f"{structure['freshness_score']:.1f}/100",
                     delta=structure.get("freshness_level", ""))

        if structure.get("structured_data_quality_score") is not None:
            st.metric("Données Structurées", f"{structure['structured_data_quality_score']:.1f}/100")


def display_recommendations_tab(loader, raw_report):
    """Affiche l'onglet des recommandations."""
    st.subheader("📋 Recommandations d'Optimisation")

    if not raw_report:
        st.warning("Recommandations non disponibles")
        return

    recommendations = loader.extract_recommendations(raw_report.get('url', '').split('/')[-1])

    if not recommendations:
        st.info("💡 Aucune recommandation spécifique disponible")
        return

    # Graphique de répartition des recommandations
    fig_recs = create_recommendations_priority_chart(recommendations)
    st.plotly_chart(fig_recs, use_container_width=True)

    # Liste détaillée des recommandations
    st.subheader("📝 Recommandations détaillées")

    for category, recs in recommendations.items():
        if recs:
            category_name = category.replace('_', ' ').replace('6.', 'Catégorie ').title()

            with st.expander(f"🎯 {category_name} ({len(recs)} recommandations)"):
                for i, rec in enumerate(recs, 1):
                    # Déterminer la priorité basée sur les mots-clés
                    priority = "Moyenne"
                    if any(word in rec.lower() for word in ["urgent", "critique", "important"]):
                        priority = "Critique"
                    elif any(word in rec.lower() for word in ["améliorer", "optimiser", "ajouter"]):
                        priority = "Élevée"
                    elif any(word in rec.lower() for word in ["considérer", "envisager"]):
                        priority = "Faible"

                    # Badge de priorité
                    if priority == "Critique":
                        badge_class = "critical-badge"
                        icon = "🔴"
                    elif priority == "Élevée":
                        badge_class = "warning-badge"
                        icon = "🟡"
                    else:
                        badge_class = "improvement-badge"
                        icon = "🟢"

                    st.markdown(f"""
                    <div style="margin: 0.5rem 0; padding: 0.75rem; border-left: 4px solid #3b82f6; background: #f8fafc;">
                        <span class="{badge_class}">{icon} {priority}</span>
                        <p style="margin: 0.5rem 0 0 0; font-size: 0.95rem;">{rec}</p>
                    </div>
                    """, unsafe_allow_html=True)


def display_comparison_section(loader, selected_reports_to_compare):
    """Affiche la section de comparaison entre rapports."""
    st.header("📊 Comparaison de Rapports")

    if len(selected_reports_to_compare) < 2:
        st.info("💡 Sélectionnez au moins 2 rapports pour voir la comparaison.")
        return

    # Préparer les données de comparaison
    report_ids = [r['id'] for r in selected_reports_to_compare]
    comparison_df = loader.get_reports_comparison_data(report_ids)

    if comparison_df.empty:
        st.warning("❌ Impossible de charger les données de comparaison.")
        return

    # Graphique de comparaison
    fig_comparison = create_comparison_bar_chart(comparison_df)
    st.plotly_chart(fig_comparison, use_container_width=True)

    # Tableau de comparaison détaillé
    with st.expander("📋 Tableau de comparaison détaillé"):
        # Préparer le DataFrame pour l'affichage
        display_df = comparison_df.copy()

        # Renommer les colonnes pour l'affichage
        column_mapping = {
            'domain': 'Domaine',
            'global_score': 'Score Global',
            'performance_level': 'Niveau',
            'content_semantics_score': 'Contenu',
            'technical_structure_score': 'Structure',
            'internal_linking_score': 'Maillage',
            'performance_score': 'Performance',
            'aio_optimization_score': 'AIO',
            'llm_analysis_score': 'IA'
        }

        # Sélectionner et renommer les colonnes
        cols_to_show = [col for col in column_mapping.keys() if col in display_df.columns]
        display_df = display_df[cols_to_show].rename(columns=column_mapping)

        # Formatter les scores numériques
        numeric_cols = [col for col in display_df.columns if col not in ['Domaine', 'Niveau']]
        for col in numeric_cols:
            if col in display_df.columns:
                display_df[col] = display_df[col].round(1)

        st.dataframe(display_df, use_container_width=True)


def show_demo_dashboard():
    """Affiche un dashboard de démonstration avec des données factices."""
    st.info("👋 Bienvenue sur le Dashboard SEO ! Voici un aperçu avec des données de démonstration.")

    demo_data = get_mock_data_for_demo()

    # Métriques de démo
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Score Global", "73.8/100", delta="2.3")

    with col2:
        st.metric("Contenu", "85.2/100", delta="1.1")

    with col3:
        st.metric("Performance", "45.3/100", delta="-3.2")

    with col4:
        st.metric("Analyse IA", "71.2/100", delta="4.7")

    # Graphiques de démo
    tab1, tab2 = st.tabs(["📊 Vue d'ensemble", "📋 Recommandations"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            fig_gauge = create_score_gauge(73.8, "Score SEO Global")
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col2:
            fig_radar = create_category_radar(demo_data["demo_scores"])
            st.plotly_chart(fig_radar, use_container_width=True)

    with tab2:
        st.subheader("📝 Recommandations Prioritaires")

        for i, rec in enumerate(demo_data["demo_recommendations"], 1):
            st.markdown(f"""
            <div style="margin: 0.5rem 0; padding: 0.75rem; border-left: 4px solid #3b82f6; background: #f8fafc;">
                <span class="improvement-badge">💡 Recommandation {i}</span>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.95rem;">{rec}</p>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.success("🚀 Lancez votre première analyse SEO avec `uv run python -m src.page_analyzer` pour voir vos vraies données !")


if __name__ == "__main__":
    main()