# -*- coding: utf-8 -*-
"""
Styles CSS centralisés pour le dashboard SEO
Tous les styles Streamlit regroupés dans un seul endroit
"""

# Styles principaux du dashboard
DASHBOARD_CSS = """
<style>
    /* === HEADER ET NAVIGATION === */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
        border-bottom: 3px solid #3b82f6;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .page-title {
        color: #1f2937;
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    /* === CONTENEURS ET SECTIONS === */
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .section-container {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .analysis-form {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    }
    
    /* === BADGES ET STATUTS === */
    .status-ready {
        background: #dcfce7;
        color: #166534;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 500;
        display: inline-block;
    }
    
    .status-warning {
        background: #fef3c7;
        color: #92400e;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 500;
        display: inline-block;
    }
    
    .status-info {
        background: #dbeafe;
        color: #1e40af;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 500;
        display: inline-block;
    }
    
    .status-error {
        background: #fee2e2;
        color: #991b1b;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 500;
        display: inline-block;
    }
    
    .improvement-badge {
        background-color: #dcfce7;
        color: #166534;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        display: inline-block;
        margin: 0.25rem;
    }
    
    .warning-badge {
        background-color: #fef3c7;
        color: #92400e;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        display: inline-block;
        margin: 0.25rem;
    }
    
    .critical-badge {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        display: inline-block;
        margin: 0.25rem;
    }
    
    /* === CARTES ET CONTENUS === */
    .page-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
        transition: all 0.2s ease;
    }
    
    .page-card:hover {
        background: #f1f5f9;
        border-left-color: #2563eb;
    }
    
    .page-url {
        color: #3b82f6;
        font-weight: 500;
        word-break: break-all;
        font-size: 0.95rem;
    }
    
    .page-meta {
        color: #64748b;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
    
    /* === RECOMMANDATIONS === */
    .recommendation-card {
        margin: 0.5rem 0;
        padding: 0.75rem;
        border-left: 4px solid #3b82f6;
        background: #f8fafc;
        border-radius: 0 8px 8px 0;
    }
    
    .recommendation-priority {
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .recommendation-text {
        margin: 0.5rem 0 0 0;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    
    /* === STATISTIQUES === */
    .stats-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
    
    .storage-stat {
        text-align: center;
        padding: 1rem;
    }
    
    /* === COMPARAISONS === */
    .section-header {
        color: #1f2937;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* === OVERRIDES STREAMLIT === */
    div.stTabs > div > div > div > div {
        padding-top: 1rem;
    }
    
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 8px;
    }
    
    .stMultiSelect > div > div {
        background-color: white;
        border-radius: 8px;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* === RESPONSIVE === */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .metric-container {
            padding: 0.75rem;
        }
        
        .section-container {
            padding: 1rem;
        }
    }
    
    /* === ANIMATIONS === */
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .slide-in {
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-10px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* === UTILITAIRES === */
    .text-center { text-align: center; }
    .text-left { text-align: left; }
    .text-right { text-align: right; }
    
    .mb-1 { margin-bottom: 0.5rem; }
    .mb-2 { margin-bottom: 1rem; }
    .mb-3 { margin-bottom: 1.5rem; }
    
    .mt-1 { margin-top: 0.5rem; }
    .mt-2 { margin-top: 1rem; }
    .mt-3 { margin-top: 1.5rem; }
    
    .p-1 { padding: 0.5rem; }
    .p-2 { padding: 1rem; }
    .p-3 { padding: 1.5rem; }
    
    .font-small { font-size: 0.875rem; }
    .font-large { font-size: 1.125rem; }
    .font-bold { font-weight: 600; }
    
    .text-blue { color: #3b82f6; }
    .text-green { color: #22c55e; }
    .text-red { color: #ef4444; }
    .text-yellow { color: #eab308; }
    .text-gray { color: #64748b; }
    
    /* === FOOTER === */
    .dashboard-footer {
        text-align: center;
        color: #64748b;
        padding: 1rem;
        background: #f8fafc;
        border-radius: 8px;
        margin-top: 2rem;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    .dashboard-footer strong {
        color: #1f2937;
    }
</style>
"""


def inject_dashboard_styles():
    """Injecte les styles CSS dans une page Streamlit"""
    import streamlit as st
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)


def get_status_badge(status: str, text: str) -> str:
    """Génère un badge de statut HTML"""
    class_mapping = {
        'success': 'status-ready',
        'warning': 'status-warning', 
        'info': 'status-info',
        'error': 'status-error'
    }
    
    css_class = class_mapping.get(status, 'status-info')
    return f'<div class="{css_class}">{text}</div>'


def get_recommendation_card(priority: str, text: str, icon: str = "💡") -> str:
    """Génère une carte de recommandation HTML"""
    priority_colors = {
        'critique': '#ef4444',
        'élevée': '#f97316', 
        'moyenne': '#eab308',
        'faible': '#22c55e'
    }
    
    color = priority_colors.get(priority.lower(), '#3b82f6')
    
    return f"""
    <div class="recommendation-card" style="border-left-color: {color};">
        <div class="recommendation-priority" style="color: {color};">
            {icon} {priority.upper()}
        </div>
        <p class="recommendation-text">{text}</p>
    </div>
    """


def get_metric_card(title: str, value: str, subtitle: str = "") -> str:
    """Génère une carte de métrique HTML"""
    subtitle_html = f'<div style="font-size: 0.85rem; opacity: 0.8; margin-top: 0.25rem;">{subtitle}</div>' if subtitle else ""
    
    return f"""
    <div class="metric-container">
        <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.25rem;">{title}</div>
        <div style="font-size: 1.8rem; font-weight: bold;">{value}</div>
        {subtitle_html}
    </div>
    """