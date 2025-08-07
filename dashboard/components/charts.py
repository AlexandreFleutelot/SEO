# -*- coding: utf-8 -*-
"""
charts.py

Composants de visualisation pour le dashboard SEO.
Utilise Plotly pour des graphiques interactifs.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any, Optional
import streamlit as st


def create_score_gauge(score: float, title: str, color_scheme: str = "RdYlGn") -> go.Figure:
    """Crée un gauge pour afficher un score."""
    
    # Déterminer la couleur basée sur le score
    if score >= 80:
        color = "#22c55e"  # Vert
    elif score >= 60:
        color = "#eab308"  # Jaune
    elif score >= 40:
        color = "#f97316"  # Orange
    else:
        color = "#ef4444"  # Rouge
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 16}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 40], 'color': "#fee2e2"},
                {'range': [40, 60], 'color': "#fed7aa"},
                {'range': [60, 80], 'color': "#fef3c7"},
                {'range': [80, 100], 'color': "#dcfce7"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def create_category_radar(scores: Dict[str, float]) -> go.Figure:
    """Crée un graphique radar pour les scores par catégorie."""
    
    categories = [
        "Contenu & Sémantique",
        "Structure Technique", 
        "Maillage Interne",
        "Performance",
        "Optimisation AIO",
        "Analyse LLM"
    ]
    
    category_keys = [
        "content_semantics",
        "technical_structure",
        "internal_linking", 
        "performance",
        "aio_optimization",
        "llm_analysis"
    ]
    
    values = [scores.get(key, 0) for key in category_keys]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Scores SEO',
        line_color='#3b82f6',
        fillcolor='rgba(59, 130, 246, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title="Vue d'ensemble des performances SEO",
        height=500
    )
    
    return fig


def create_comparison_bar_chart(comparison_df: pd.DataFrame) -> go.Figure:
    """Crée un graphique en barres pour comparer plusieurs sites."""
    
    if comparison_df.empty:
        return go.Figure().add_annotation(
            text="Aucune donnée de comparaison disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font_size=16
        )
    
    fig = go.Figure()
    
    score_columns = [col for col in comparison_df.columns if col.endswith('_score')]
    
    for col in score_columns:
        category_name = col.replace('_score', '').replace('_', ' ').title()
        
        fig.add_trace(go.Bar(
            name=category_name,
            x=comparison_df['domain'],
            y=comparison_df[col],
            text=comparison_df[col].round(1),
            textposition='auto',
        ))
    
    fig.update_layout(
        barmode='group',
        title="Comparaison des scores par catégorie",
        xaxis_title="Sites web",
        yaxis_title="Score (/100)",
        height=500,
        xaxis_tickangle=-45
    )
    
    return fig


def create_trend_line_chart(trends_data: Dict[str, List[float]], dates: List[str]) -> go.Figure:
    """Crée un graphique linéaire pour les tendances temporelles."""
    
    fig = go.Figure()
    
    colors = ['#3b82f6', '#ef4444', '#22c55e', '#eab308', '#8b5cf6', '#f97316']
    
    for i, (category, scores) in enumerate(trends_data.items()):
        if scores:  # Seulement si on a des données
            category_name = category.replace('_', ' ').title()
            
            fig.add_trace(go.Scatter(
                x=dates[:len(scores)],
                y=scores,
                mode='lines+markers',
                name=category_name,
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=8)
            ))
    
    fig.update_layout(
        title="Évolution des scores dans le temps",
        xaxis_title="Date",
        yaxis_title="Score (/100)",
        height=400,
        hovermode='x unified'
    )
    
    return fig


def create_performance_waterfall(desktop_scores: Dict[str, float], mobile_scores: Dict[str, float]) -> go.Figure:
    """Crée un graphique waterfall pour les métriques de performance."""
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Desktop Performance', 'Mobile Performance'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Desktop
    if desktop_scores:
        metrics = ['LCP', 'INP', 'CLS']
        values_desktop = [desktop_scores.get(metric, 0) for metric in metrics]
        
        fig.add_trace(go.Bar(
            name="Desktop",
            x=metrics,
            y=values_desktop,
            marker_color='#3b82f6',
            text=[f"{v:.0f}ms" if i < 2 else f"{v:.3f}" for i, v in enumerate(values_desktop)],
            textposition='auto'
        ), row=1, col=1)
    
    # Mobile
    if mobile_scores:
        metrics = ['LCP', 'INP', 'CLS']
        values_mobile = [mobile_scores.get(metric, 0) for metric in metrics]
        
        fig.add_trace(go.Bar(
            name="Mobile",
            x=metrics,
            y=values_mobile,
            marker_color='#ef4444',
            text=[f"{v:.0f}ms" if i < 2 else f"{v:.3f}" for i, v in enumerate(values_mobile)],
            textposition='auto'
        ), row=1, col=2)
    
    fig.update_layout(
        title="Core Web Vitals - Desktop vs Mobile",
        height=400,
        showlegend=False
    )
    
    return fig


def create_enhanced_insights_chart(insights: Dict[str, Any]) -> go.Figure:
    """Crée une visualisation pour les insights des analyses améliorées."""
    
    content_insights = insights.get("content", {})
    structure_insights = insights.get("structure", {})
    
    # Préparer les données pour le graphique
    categories = []
    scores = []
    colors = []
    
    # Insights de contenu
    if content_insights.get("informational_density_score") is not None:
        categories.append("Densité Informationnelle")
        scores.append(content_insights["informational_density_score"])
        colors.append('#3b82f6')
    
    if content_insights.get("naturalness_score") is not None:
        categories.append("Authenticité Contenu")
        scores.append(content_insights["naturalness_score"])
        colors.append('#22c55e')
    
    if content_insights.get("data_originality_score") is not None:
        categories.append("Données Originales")
        scores.append(content_insights["data_originality_score"])
        colors.append('#8b5cf6')
    
    if content_insights.get("nap_consistency_score") is not None:
        categories.append("Cohérence NAP")
        scores.append(content_insights["nap_consistency_score"])
        colors.append('#eab308')
    
    # Insights de structure
    if structure_insights.get("ssr_compatibility_score") is not None:
        categories.append("Compatibilité SSR")
        scores.append(structure_insights["ssr_compatibility_score"])
        colors.append('#f97316')
    
    if structure_insights.get("freshness_score") is not None:
        categories.append("Fraîcheur Temporelle")
        scores.append(structure_insights["freshness_score"])
        colors.append('#06b6d4')
    
    if structure_insights.get("structured_data_quality_score") is not None:
        categories.append("Données Structurées")
        scores.append(structure_insights["structured_data_quality_score"])
        colors.append('#84cc16')
    
    if not categories:
        return go.Figure().add_annotation(
            text="Aucun insight amélioré disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font_size=16
        )
    
    fig = go.Figure(go.Bar(
        x=categories,
        y=scores,
        marker_color=colors,
        text=[f"{s:.1f}" for s in scores],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Analyses Améliorées - Scores LLM/GEO",
        xaxis_title="Critères d'analyse",
        yaxis_title="Score (/100)",
        height=400,
        xaxis_tickangle=-45
    )
    
    return fig


def create_recommendations_priority_chart(recommendations: Dict[str, List[str]]) -> go.Figure:
    """Crée une visualisation des recommandations par priorité."""
    
    if not recommendations:
        return go.Figure().add_annotation(
            text="Aucune recommandation disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font_size=16
        )
    
    # Compter les recommandations par catégorie
    category_counts = {}
    priority_keywords = {
        "Critique": ["urgent", "critique", "important", "immédiat"],
        "Élevée": ["améliorer", "optimiser", "ajouter", "implémenter"],
        "Moyenne": ["considérer", "envisager", "suggérer", "recommander"],
        "Faible": ["optionnel", "futur", "éventuel"]
    }
    
    priority_counts = {"Critique": 0, "Élevée": 0, "Moyenne": 0, "Faible": 0}
    
    for category, recs in recommendations.items():
        category_counts[category] = len(recs)
        
        for rec in recs:
            rec_lower = rec.lower()
            classified = False
            
            for priority, keywords in priority_keywords.items():
                if any(keyword in rec_lower for keyword in keywords):
                    priority_counts[priority] += 1
                    classified = True
                    break
            
            if not classified:
                priority_counts["Moyenne"] += 1  # Par défaut
    
    # Graphique en secteurs pour les priorités
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Recommandations par Priorité', 'Recommandations par Catégorie'),
        specs=[[{"type": "pie"}, {"type": "pie"}]]
    )
    
    # Priorités
    fig.add_trace(go.Pie(
        labels=list(priority_counts.keys()),
        values=list(priority_counts.values()),
        name="Priorité",
        marker_colors=['#ef4444', '#f97316', '#eab308', '#22c55e']
    ), row=1, col=1)
    
    # Catégories
    fig.add_trace(go.Pie(
        labels=[cat.replace('_', ' ').title() for cat in category_counts.keys()],
        values=list(category_counts.values()),
        name="Catégorie"
    ), row=1, col=2)
    
    fig.update_layout(
        height=400,
        showlegend=True
    )
    
    return fig


def display_score_card(title: str, score: float, description: str = "", delta: Optional[float] = None):
    """Affiche une carte de score avec Streamlit."""
    
    # Déterminer la couleur
    if score >= 80:
        color = "normal"
        icon = "✅"
    elif score >= 60:
        color = "normal" 
        icon = "⚠️"
    else:
        color = "inverse"
        icon = "❌"
    
    # Formatage du delta
    delta_str = f"{delta:+.1f}" if delta is not None else None
    
    # Affichage avec metric
    st.metric(
        label=f"{icon} {title}",
        value=f"{score:.1f}/100",
        delta=delta_str
    )
    
    if description:
        st.caption(description)