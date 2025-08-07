# -*- coding: utf-8 -*-
"""
3_➕_Nouvelle_Analyse.py

Page pour lancer de nouvelles analyses SEO directement depuis le dashboard.
"""

import streamlit as st
import sys
from pathlib import Path
import subprocess
import time
import os
from datetime import datetime
import validators

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent.parent))

from dashboard.utils.data_loader import SEODataLoader

st.set_page_config(page_title="Nouvelle Analyse", page_icon="➕", layout="wide")

# CSS personnalisé
st.markdown("""
<style>
    .analysis-form {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
    
    .status-running {
        background-color: #dbeafe;
        color: #1e40af;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #3b82f6;
    }
    
    .status-success {
        background-color: #dcfce7;
        color: #166534;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #22c55e;
    }
    
    .status-error {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ef4444;
    }
    
    .quick-urls {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

st.title("➕ Nouvelle Analyse SEO")

# Section principale - Formulaire d'analyse
st.markdown('<div class="analysis-form">', unsafe_allow_html=True)
st.header("🚀 Lancer une Nouvelle Analyse")

with st.form("new_analysis_form"):
    # URL à analyser
    url_input = st.text_input(
        "🌐 URL à analyser",
        placeholder="https://example.com/page-to-analyze",
        help="Entrez l'URL complète de la page à analyser"
    )
    
    # Options avancées
    col1, col2 = st.columns(2)
    
    with col1:
        enable_llm = st.checkbox(
            "🧠 Analyse IA avancée", 
            value=True,
            help="Active l'analyse LLM pour les métriques E-A-T et optimisation GEO"
        )
        
        pagespeed_analysis = st.checkbox(
            "⚡ Analyse Performance", 
            value=True,
            help="Active l'analyse des Core Web Vitals via Google PageSpeed"
        )
    
    with col2:
        enhanced_analysis = st.checkbox(
            "🔬 Analyses améliorées", 
            value=True,
            help="Active les analyses de naturalité, SSR, et données originales"
        )
        
        auto_refresh = st.checkbox(
            "🔄 Rafraîchir automatiquement", 
            value=True,
            help="Rafraîchit automatiquement la page après analyse"
        )
    
    # Bouton de soumission
    submit_button = st.form_submit_button(
        "🚀 Lancer l'Analyse",
        use_container_width=True,
        type="primary"
    )

st.markdown('</div>', unsafe_allow_html=True)

# URLs rapides suggérées
with st.expander("⚡ URLs Rapides Suggérées"):
    st.markdown('<div class="quick-urls">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**🏦 Finance**")
        quick_urls_finance = [
            "https://www.meilleurtaux.com",
            "https://www.boursorama.com",
            "https://www.credit-agricole.fr"
        ]
        for url in quick_urls_finance:
            if st.button(f"📊 {url.split('//')[1].split('.')[1]}", key=f"finance_{url}"):
                st.session_state.quick_url = url
                st.rerun()
    
    with col2:
        st.write("**🛒 E-commerce**")
        quick_urls_ecommerce = [
            "https://www.amazon.fr",
            "https://www.fnac.com",
            "https://www.cdiscount.com"
        ]
        for url in quick_urls_ecommerce:
            if st.button(f"🛍️ {url.split('//')[1].split('.')[1]}", key=f"ecommerce_{url}"):
                st.session_state.quick_url = url
                st.rerun()
    
    with col3:
        st.write("**📰 Actualités**")
        quick_urls_news = [
            "https://www.lemonde.fr",
            "https://www.lefigaro.fr",
            "https://www.liberation.fr"
        ]
        for url in quick_urls_news:
            if st.button(f"📰 {url.split('//')[1].split('.')[1]}", key=f"news_{url}"):
                st.session_state.quick_url = url
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Gestion de l'URL rapide sélectionnée
if hasattr(st.session_state, 'quick_url'):
    url_input = st.session_state.quick_url
    del st.session_state.quick_url
    st.rerun()

# Traitement du formulaire
if submit_button:
    if not url_input:
        st.error("❌ Veuillez entrer une URL à analyser")
    elif not validators.url(url_input):
        st.error("❌ L'URL entrée n'est pas valide. Vérifiez le format (https://example.com)")
    else:
        # Lancer l'analyse
        st.success(f"✅ Analyse lancée pour: {url_input}")
        
        # Barre de progression
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Préparer la commande
            project_root = Path(__file__).parent.parent.parent
            
            # Préparer les variables d'environnement
            env = os.environ.copy()
            env['ANALYSIS_URL'] = url_input
            env['ENABLE_LLM_ANALYSIS'] = 'true' if enable_llm else 'false'
            env['ENABLE_ENHANCED_ANALYSIS'] = 'true' if enhanced_analysis else 'false'
            
            # Mettre à jour la barre de progression
            progress_bar.progress(10)
            status_text.markdown('<div class="status-running">🔄 Initialisation de l\'analyse...</div>', unsafe_allow_html=True)
            
            # Lancer l'analyse
            cmd = [
                "uv", "run", "python", "-m", "src.page_analyzer"
            ]
            
            progress_bar.progress(20)
            status_text.markdown('<div class="status-running">📄 Récupération du contenu de la page...</div>', unsafe_allow_html=True)
            
            # Exécuter la commande d'analyse
            process = subprocess.run(
                cmd,
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
                env=env
            )
            
            progress_bar.progress(50)
            status_text.markdown('<div class="status-running">🔍 Analyse du contenu et de la structure...</div>', unsafe_allow_html=True)
            
            time.sleep(1)  # Simulation du traitement
            progress_bar.progress(70)
            
            if enable_llm:
                status_text.markdown('<div class="status-running">🧠 Analyse IA en cours...</div>', unsafe_allow_html=True)
                time.sleep(2)
                progress_bar.progress(85)
            
            if pagespeed_analysis:
                status_text.markdown('<div class="status-running">⚡ Analyse des performances...</div>', unsafe_allow_html=True)
                time.sleep(1)
                progress_bar.progress(95)
            
            status_text.markdown('<div class="status-running">📊 Génération des scores et recommandations...</div>', unsafe_allow_html=True)
            progress_bar.progress(100)
            
            if process.returncode == 0:
                status_text.markdown('<div class="status-success">✅ Analyse terminée avec succès!</div>', unsafe_allow_html=True)
                
                # Afficher les résultats
                st.success("🎉 Analyse SEO terminée!")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("🌐 URL analysée", url_input.split('//')[-1][:30] + "..." if len(url_input) > 30 else url_input)
                
                with col2:
                    st.metric("📅 Date d'analyse", datetime.now().strftime("%d/%m/%Y %H:%M"))
                
                with col3:
                    if process.stdout:
                        # Essayer d'extraire le score global des logs
                        if "Score global" in process.stdout:
                            score_line = [line for line in process.stdout.split('\n') if 'Score global' in line]
                            if score_line:
                                score = score_line[0].split(':')[-1].strip()
                                st.metric("📊 Score Global", score)
                        else:
                            st.metric("✅ Status", "Terminé")
                
                # Options post-analyse
                st.divider()
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📊 Voir dans le Dashboard", use_container_width=True, type="primary"):
                        # Vider tous les caches avant de changer de page
                        st.cache_data.clear()
                        st.switch_page("dashboard/app.py")
                
                with col2:
                    if st.button("🔍 Analyse Détaillée", use_container_width=True):
                        # Vider tous les caches avant de changer de page
                        st.cache_data.clear()
                        st.switch_page("pages/1_🔍_Analyse_Détaillée.py")
                
                with col3:
                    if st.button("➕ Nouvelle Analyse", use_container_width=True):
                        # Vider le cache et rafraîchir
                        st.cache_data.clear()
                        st.rerun()
                
                # Logs détaillés (repliable)
                if process.stdout or process.stderr:
                    with st.expander("📋 Logs détaillés de l'analyse"):
                        if process.stdout:
                            st.text("STDOUT:")
                            st.code(process.stdout, language="text")
                        if process.stderr:
                            st.text("STDERR:")
                            st.code(process.stderr, language="text")
                
                # Auto-refresh si activé
                if auto_refresh:
                    st.cache_data.clear()  # Vider le cache avant de rafraîchir
                    time.sleep(3)
                    st.rerun()
                    
            else:
                status_text.markdown('<div class="status-error">❌ Erreur lors de l\'analyse</div>', unsafe_allow_html=True)
                st.error(f"❌ L'analyse a échoué avec le code d'erreur: {process.returncode}")
                
                if process.stderr:
                    st.error(f"Erreur: {process.stderr}")
                
                with st.expander("🔍 Détails de l'erreur"):
                    st.code(process.stderr if process.stderr else "Aucun détail disponible", language="text")
                
        except subprocess.TimeoutExpired:
            status_text.markdown('<div class="status-error">⏱️ Timeout - L\'analyse a pris trop de temps</div>', unsafe_allow_html=True)
            st.error("⏱️ L'analyse a dépassé le délai maximum (5 minutes)")
            st.info("💡 Essayez avec une page plus simple ou vérifiez votre connexion internet")
            
        except Exception as e:
            status_text.markdown('<div class="status-error">❌ Erreur inattendue</div>', unsafe_allow_html=True)
            st.error(f"❌ Erreur inattendue: {str(e)}")
            
            with st.expander("🔍 Détails techniques"):
                st.exception(e)

# Historique des analyses récentes
st.divider()
st.header("📈 Analyses Récentes")

# Charger les rapports existants avec détection des changements
try:
    loader = SEODataLoader()
    reports = loader.get_available_reports()
    
    if reports:
        # Afficher les 5 dernières analyses
        recent_reports = sorted(reports, key=lambda x: x['created_date'], reverse=True)[:5]
        
        for i, report in enumerate(recent_reports):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{report['domain']}**")
                    st.caption(report['url'][:60] + "..." if len(report['url']) > 60 else report['url'])
                
                with col2:
                    st.write(f"📅 {report['created_date'].strftime('%d/%m/%Y %H:%M')}")
                
                with col3:
                    if report['has_scores']:
                        score_report = loader.load_score_report(report['id'])
                        if score_report:
                            global_score = score_report.get('global_analysis', {}).get('global_score', 0)
                            st.metric("Score", f"{global_score:.1f}/100")
                        else:
                            st.write("Score: N/A")
                    else:
                        st.write("⏳ En cours...")
                
                with col4:
                    if st.button("👀", key=f"view_{i}", help="Voir l'analyse"):
                        # Rediriger vers l'analyse détaillée
                        st.session_state.selected_report_id = report['id']
                        st.switch_page("pages/1_🔍_Analyse_Détaillée.py")
                
                if i < len(recent_reports) - 1:
                    st.divider()
    else:
        st.info("📝 Aucune analyse disponible. Lancez votre première analyse ci-dessus!")
        
except Exception as e:
    st.error(f"❌ Erreur lors du chargement de l'historique: {str(e)}")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem;">
    💡 <strong>Astuce:</strong> Les analyses peuvent prendre 2-5 minutes selon la complexité de la page et les options activées.
    <br>
    🔄 Les résultats sont automatiquement sauvegardés et disponibles dans les autres onglets du dashboard.
</div>
""", unsafe_allow_html=True)