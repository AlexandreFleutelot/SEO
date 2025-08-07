# -*- coding: utf-8 -*-
"""
5_🔬_Études_de_Cas.py

Interface pour créer et gérer les études de cas SEO comparatives.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import time

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.case_studies.case_manager import CaseStudyManager
from src.case_studies.llm_source_extractor import LLMSourceExtractor
from src.case_studies.models import LLMProvider, CaseStatus

st.set_page_config(page_title="Études de Cas", page_icon="🔬", layout="wide")

# CSS personnalisé
st.markdown("""
<style>
    .case-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #3b82f6;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .case-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1e40af;
        margin-bottom: 0.5rem;
    }
    
    .case-question {
        font-style: italic;
        color: #475569;
        margin-bottom: 1rem;
    }
    
    .case-meta {
        font-size: 0.9rem;
        color: #64748b;
    }
    
    .wizard-step {
        background: #f1f5f9;
        padding: 1rem;
        border-radius: 10px;
        border: 2px dashed #cbd5e1;
        margin: 0.5rem 0;
    }
    
    .progress-container {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .source-item {
        background: white;
        padding: 0.75rem;
        margin: 0.25rem 0;
        border-radius: 8px;
        border-left: 3px solid #22c55e;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔬 Études de Cas SEO")

# Initialiser le gestionnaire
@st.cache_resource
def init_case_manager():
    return CaseStudyManager()

@st.cache_resource  
def init_source_extractor():
    return LLMSourceExtractor()

case_manager = init_case_manager()
source_extractor = init_source_extractor()

def display_existing_cases():
    """Affiche la liste des études de cas existantes."""
    st.subheader("📋 Mes Études de Cas")
    
    # Chargement des études
    cases = case_manager.list_case_studies()
    
    if not cases:
        st.info("📭 Aucune étude de cas créée. Utilisez l'onglet 'Nouvelle Étude' pour commencer.")
        return
    
    # Filtres
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Rechercher", placeholder="Titre, question, domaine...")
    
    with col2:
        status_filter = st.selectbox(
            "Statut", 
            ["Tous", "Brouillon", "En cours", "Terminé", "Erreur"]
        )
    
    with col3:
        sort_by = st.selectbox(
            "Trier par",
            ["Plus récent", "Plus ancien", "Titre", "Progression"]
        )
    
    # Appliquer les filtres
    filtered_cases = cases
    
    if search_term:
        filtered_cases = [
            c for c in filtered_cases 
            if search_term.lower() in c['title'].lower() 
            or search_term.lower() in c['research_question'].lower()
        ]
    
    if status_filter != "Tous":
        status_map = {
            "Brouillon": "draft",
            "En cours": "analyzing", 
            "Terminé": "completed",
            "Erreur": "error"
        }
        filtered_cases = [c for c in filtered_cases if c['status'] == status_map.get(status_filter)]
    
    # Affichage des études
    for i, case in enumerate(filtered_cases):
        with st.container():
            st.markdown('<div class="case-card">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f'<div class="case-title">{case["title"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="case-question">❓ {case["research_question"]}</div>', unsafe_allow_html=True)
                
                # Progression
                progress = case['progress']
                st.progress(progress / 100, text=f"Progression: {progress:.1f}%")
                
                st.markdown(f'''
                <div class="case-meta">
                    📅 Créé: {case["created_date"].strftime("%d/%m/%Y %H:%M")} | 
                    🔄 MAJ: {case["updated_date"].strftime("%d/%m/%Y %H:%M")} | 
                    📊 Sources: {case["sources_analyzed"]}/{case["total_sources"]}
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                # Badge de statut
                status_colors = {
                    "draft": "🟡",
                    "analyzing": "🔵", 
                    "completed": "🟢",
                    "error": "🔴"
                }
                status_icon = status_colors.get(case['status'], "⚪")
                st.write(f"{status_icon} {case['status'].title()}")
            
            with col3:
                # Actions
                if st.button("👀 Voir", key=f"view_{case['id']}", use_container_width=True):
                    st.session_state.selected_case_id = case['id']
                    display_case_details(case['id'])
                
                if st.button("▶️ Continuer", key=f"continue_{case['id']}", use_container_width=True):
                    st.session_state.continue_case_id = case['id']
                    continue_case_analysis(case['id'])
            
            st.markdown('</div>', unsafe_allow_html=True)


def display_case_creation_wizard():
    """Affiche l'assistant de création d'étude de cas."""
    st.subheader("🧙‍♂️ Assistant de Création d'Étude")
    
    with st.form("case_creation_form"):
        st.markdown('<div class="wizard-step">', unsafe_allow_html=True)
        st.write("**Étape 1: Définition de l'étude**")
        
        case_title = st.text_input(
            "📝 Titre de l'étude",
            placeholder="Ex: Analyse concurrentielle assurance-vie 2025"
        )
        
        research_question = st.text_area(
            "❓ Question de recherche",
            placeholder="Ex: Quels sont les avantages d'une assurance-vie selon les experts du secteur ?",
            height=100
        )
        
        case_description = st.text_area(
            "📋 Description (optionnel)",
            placeholder="Contexte, objectifs, contraintes particulières...",
            height=80
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="wizard-step">', unsafe_allow_html=True)
        st.write("**Étape 2: Configuration LLM**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            llm_providers = st.multiselect(
                "🤖 Moteurs LLM à utiliser",
                ["OpenAI (GPT-4)", "Anthropic (Claude)", "Google (Gemini)"],
                default=["OpenAI (GPT-4)"],
                help="Plus de moteurs = plus de sources diversifiées"
            )
        
        with col2:
            max_sources = st.slider(
                "📊 Sources max par moteur",
                min_value=5,
                max_value=20,
                value=10,
                help="Nombre maximum de sources à extraire par LLM"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="wizard-step">', unsafe_allow_html=True)
        st.write("**Étape 3: Options avancées**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            auto_analyze = st.checkbox(
                "🚀 Analyse automatique",
                value=True,
                help="Analyser automatiquement toutes les sources trouvées"
            )
        
        with col2:
            verify_urls = st.checkbox(
                "✅ Vérifier l'accessibilité",
                value=True,
                help="Vérifier que les URLs sont accessibles"
            )
        
        with col3:
            include_keywords = st.checkbox(
                "🔍 Analyse des mots-clés",
                value=False,
                help="Analyser les mots-clés et mentions de marque"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Bouton de création
        submitted = st.form_submit_button("🚀 Créer l'Étude de Cas", use_container_width=True, type="primary")
        
        if submitted:
            if not case_title or not research_question:
                st.error("❌ Le titre et la question de recherche sont obligatoires")
            else:
                create_new_case_study(
                    case_title, research_question, case_description,
                    llm_providers, max_sources, auto_analyze, verify_urls, include_keywords
                )


def create_new_case_study(title, question, description, llm_providers, max_sources, 
                         auto_analyze, verify_urls, include_keywords):
    """Crée une nouvelle étude de cas et lance l'analyse."""
    
    # Mapper les noms d'affichage vers les enums
    provider_mapping = {
        "OpenAI (GPT-4)": LLMProvider.OPENAI,
        "Anthropic (Claude)": LLMProvider.ANTHROPIC,
        "Google (Gemini)": LLMProvider.GOOGLE
    }
    
    selected_providers = [provider_mapping[p] for p in llm_providers if p in provider_mapping]
    
    try:
        # Créer l'étude
        case_study = case_manager.create_case_study(
            title=title,
            research_question=question,
            description=description,
            llm_providers=selected_providers
        )
        
        case_study.max_sources_per_llm = max_sources
        
        st.success(f"✅ Étude de cas créée: {case_study.id}")
        
        if auto_analyze:
            st.info("🚀 Lancement de l'analyse automatique...")
            
            # Mettre à jour le statut
            case_study.update_status(CaseStatus.ANALYZING)
            case_manager.update_case_study(case_study)
            
            # Conteneur pour les logs en temps réel
            progress_container = st.container()
            
            with progress_container:
                st.markdown('<div class="progress-container">', unsafe_allow_html=True)
                
                # Phase 1: Extraction des sources
                st.write("🔍 **Phase 1: Extraction des sources LLM**")
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.write("Interrogation des moteurs LLM...")
                
                # Extraire les sources
                llm_responses = source_extractor.extract_sources_multi_llm(
                    research_question=question,
                    providers=selected_providers,
                    max_sources_per_provider=max_sources
                )
                
                progress_bar.progress(30)
                
                # Ajouter les réponses à l'étude
                for response in llm_responses:
                    case_study.add_llm_response(response)
                
                status_text.write(f"✅ {len(llm_responses)} réponses LLM obtenues, {case_study.total_sources_found} sources trouvées")
                
                # Phase 2: Vérification des URLs (si demandé)
                if verify_urls:
                    progress_bar.progress(50)
                    status_text.write("🔍 Vérification de l'accessibilité des URLs...")
                    
                    all_sources = []
                    for response in llm_responses:
                        all_sources.extend(response.sources)
                    
                    verified_sources = source_extractor.verify_urls_accessibility(all_sources)
                    status_text.write(f"✅ {len(verified_sources)} URLs vérifiées")
                
                progress_bar.progress(70)
                
                # Sauvegarder les modifications
                case_manager.update_case_study(case_study)
                
                progress_bar.progress(100)
                status_text.write("🎉 Extraction terminée! Prêt pour l'analyse SEO des sources.")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Afficher un résumé des sources
                display_sources_summary(llm_responses)
                
                # Proposer l'analyse SEO
                st.divider()
                if st.button("📊 Lancer l'Analyse SEO des Sources", use_container_width=True, type="primary"):
                    launch_seo_analysis(case_study.id)
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la création: {str(e)}")
        st.exception(e)


def display_sources_summary(llm_responses):
    """Affiche un résumé des sources extraites."""
    st.subheader("📋 Sources Extraites")
    
    for i, response in enumerate(llm_responses):
        with st.expander(f"🤖 {response.provider.value} - {len(response.sources)} sources"):
            
            st.write(f"**Modèle:** {response.model_name}")
            st.write(f"**Temps de réponse:** {response.response_time_ms}ms")
            st.write(f"**Tokens utilisés:** {response.tokens_used}")
            
            st.write("**Sources trouvées:**")
            
            for j, source in enumerate(response.sources[:10], 1):  # Limiter l'affichage
                reliability_color = "🟢" if source.reliability_score > 0.7 else "🟡" if source.reliability_score > 0.5 else "🔴"
                
                st.markdown(f'''
                <div class="source-item">
                    <strong>{j}. {source.domain}</strong> {reliability_color}<br>
                    <small>{source.url[:80]}{"..." if len(source.url) > 80 else ""}</small><br>
                    <em>Fiabilité: {source.reliability_score:.2f} | Confiance extraction: {source.extraction_confidence:.2f}</em>
                </div>
                ''', unsafe_allow_html=True)


def launch_seo_analysis(case_id):
    """Lance l'analyse SEO des sources d'une étude de cas."""
    try:
        # Charger l'étude de cas
        case_study = case_manager.load_case_study(case_id)
        if not case_study:
            st.error("❌ Étude de cas introuvable")
            return
        
        # Collecter toutes les sources à analyser
        all_sources = []
        for response in case_study.llm_responses:
            all_sources.extend(response.sources)
        
        if not all_sources:
            st.warning("⚠️ Aucune source à analyser")
            return
        
        st.info(f"🚀 Lancement de l'analyse SEO de {len(all_sources)} sources...")
        
        # Import des modules d'analyse comparative
        from src.case_studies.comparative_analyzer import ComparativeAnalyzer
        from src.case_studies.case_report_generator import CaseReportGenerator
        
        analyzer = ComparativeAnalyzer()
        report_generator = CaseReportGenerator()
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        
        def update_progress(current, total, url):
            progress = current / total
            progress_bar.progress(progress)
            status_placeholder.write(f"📊 Analyse en cours ({current}/{total}): {url[:50]}...")
        
        # Lancer l'analyse batch
        batch_results = analyzer.analyze_sources_batch(
            all_sources, 
            progress_callback=update_progress
        )
        
        progress_bar.progress(1.0)
        status_placeholder.write("✅ Analyse SEO terminée!")
        
        # Afficher les résultats
        st.success(f"🎉 Analyse terminée: {len(batch_results['successful_analyses'])} sources analysées avec succès")
        
        if batch_results['failed_analyses']:
            st.warning(f"⚠️ {len(batch_results['failed_analyses'])} sources ont échoué")
        
        # Générer les insights concurrentiels
        with st.spinner("🔍 Génération des insights concurrentiels..."):
            competitor_insights = analyzer.generate_competitor_insights(batch_results['successful_analyses'])
            gap_analysis = analyzer.perform_gap_analysis(case_study, competitor_insights)
        
        # Afficher les résultats de l'analyse comparative
        display_competitive_analysis_results(case_study, competitor_insights, gap_analysis, batch_results)
        
        # Mettre à jour le statut de l'étude
        case_study.update_status(CaseStatus.COMPLETED)
        case_study.sources_analyzed = len(batch_results['successful_analyses'])
        case_manager.update_case_study(case_study)
        
        # Proposer la génération de rapport
        st.divider()
        if st.button("📋 Générer le Rapport Complet", use_container_width=True, type="primary"):
            generate_case_report(case_study, competitor_insights, gap_analysis, batch_results)
            
    except Exception as e:
        st.error(f"❌ Erreur lors de l'analyse: {str(e)}")
        st.exception(e)


def display_case_statistics():
    """Affiche les statistiques des études de cas."""
    st.subheader("📊 Statistiques Générales")
    
    stats = case_manager.get_case_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Total Études", stats['total_cases'])
    
    with col2:
        st.metric("🔄 Actives", stats['active_cases'])
    
    with col3:
        st.metric("✅ Terminées", stats['completed_cases'])
    
    with col4:
        st.metric("📊 Sources Analysées", stats['total_sources_analyzed'])
    
    if stats['most_recent_case']:
        st.subheader("🆕 Dernière Étude")
        recent = stats['most_recent_case']
        st.info(f"**{recent['title']}** - {recent['updated_date'].strftime('%d/%m/%Y')}")


def display_case_details(case_id):
    """Affiche les détails d'une étude de cas."""
    st.subheader(f"🔬 Détails de l'Étude")
    
    case = case_manager.load_case_study(case_id)
    
    if not case:
        st.error("❌ Étude de cas introuvable")
        return
    
    st.write(f"**Titre:** {case.title}")
    st.write(f"**Question:** {case.research_question}")
    st.write(f"**Statut:** {case.status.value}")
    st.write(f"**Sources trouvées:** {case.total_sources_found}")
    st.write(f"**Sources analysées:** {case.sources_analyzed}")
    
    if case.llm_responses:
        st.subheader("🤖 Réponses LLM")
        for response in case.llm_responses:
            st.write(f"- {response.provider.value}: {len(response.sources)} sources")


def display_competitive_analysis_results(case_study, competitor_insights, gap_analysis, batch_results):
    """Affiche les résultats de l'analyse comparative."""
    st.subheader("🏆 Résultats de l'Analyse Comparative")
    
    # Métriques de synthèse
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Concurrents analysés", len(competitor_insights))
    
    with col2:
        avg_score = sum(i.seo_score for i in competitor_insights) / len(competitor_insights) if competitor_insights else 0
        st.metric("📊 Score moyen", f"{avg_score:.1f}/100")
    
    with col3:
        st.metric("🚀 Opportunités", len(gap_analysis.content_opportunities))
    
    with col4:
        st.metric("⚡ Priorités", len(gap_analysis.optimization_priorities))
    
    # Tableau de performance des concurrents
    if competitor_insights:
        st.subheader("📈 Classement des Concurrents")
        
        perf_data = []
        for i, insight in enumerate(competitor_insights):
            perf_data.append({
                'Rang': i + 1,
                'Domaine': insight.domain,
                'Score SEO': f"{insight.seo_score:.1f}/100",
                'Forces': len(insight.strengths),
                'Faiblesses': len(insight.weaknesses),
                'Mots-clés': len(insight.target_keywords)
            })
        
        import pandas as pd
        df = pd.DataFrame(perf_data)
        st.dataframe(df, use_container_width=True)
        
        # Détails du leader
        if competitor_insights:
            leader = competitor_insights[0]
            st.subheader(f"👑 Leader du Marché: {leader.domain}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🚀 Forces principales:**")
                for strength in leader.strengths[:3]:
                    st.write(f"• {strength}")
            
            with col2:
                st.write("**⚠️ Points d'amélioration:**")
                for weakness in leader.weaknesses[:3]:
                    st.write(f"• {weakness}")
    
    # Analyse des gaps
    st.subheader("🎯 Analyse des Opportunités")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📋 Sujets manquants:**")
        for topic in gap_analysis.missing_topics[:5]:
            st.write(f"• {topic}")
        
        st.write("**🔍 Mots-clés sous-exploités:**")
        for keyword in gap_analysis.underrepresented_keywords[:5]:
            st.write(f"• {keyword}")
    
    with col2:
        st.write("**💡 Opportunités de contenu:**")
        for opportunity in gap_analysis.content_opportunities[:5]:
            st.write(f"• {opportunity}")
        
        st.write("**⚡ Priorités d'optimisation:**")
        for priority in gap_analysis.optimization_priorities[:5]:
            st.write(f"• {priority}")


def generate_case_report(case_study, competitor_insights, gap_analysis, batch_results):
    """Génère et affiche le rapport complet d'étude de cas."""
    try:
        from src.case_studies.case_report_generator import CaseReportGenerator
        
        report_generator = CaseReportGenerator()
        
        with st.spinner("📋 Génération du rapport complet..."):
            # Générer le rapport
            report = report_generator.generate_complete_report(
                case_study, competitor_insights, gap_analysis, batch_results
            )
            
            # Générer les graphiques
            charts = report_generator.generate_visual_charts(competitor_insights, gap_analysis)
        
        st.success("✅ Rapport généré avec succès!")
        
        # Afficher le résumé exécutif
        st.subheader("📋 Résumé Exécutif")
        st.markdown(report.executive_summary)
        
        # Afficher les graphiques
        if charts:
            st.subheader("📊 Visualisations")
            
            for chart_name, fig in charts.items():
                st.plotly_chart(fig, use_container_width=True)
        
        # Afficher les découvertes clés
        if report.key_findings:
            st.subheader("🔍 Découvertes Clés")
            for finding in report.key_findings:
                st.write(f"• {finding}")
        
        # Afficher les recommandations
        if report.recommendations:
            st.subheader("💡 Recommandations")
            for recommendation in report.recommendations:
                st.write(f"• {recommendation}")
        
        # Options d'export
        st.subheader("📤 Options d'Export")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export JSON", use_container_width=True):
                if 'json' in report.file_paths:
                    st.success(f"✅ Rapport JSON sauvegardé: {report.file_paths['json']}")
                else:
                    st.error("❌ Erreur export JSON")
        
        with col2:
            if st.button("📊 Export Excel", use_container_width=True):
                excel_path = report_generator.export_to_excel(report, case_study.id)
                if excel_path:
                    st.success(f"✅ Rapport Excel sauvegardé: {excel_path}")
                else:
                    st.error("❌ Erreur export Excel")
        
        with col3:
            if st.button("🔄 Régénérer", use_container_width=True):
                st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erreur génération rapport: {str(e)}")
        st.exception(e)


def continue_case_analysis(case_id):
    """Continue l'analyse d'une étude de cas existante."""
    case = case_manager.load_case_study(case_id)
    if not case:
        st.error("❌ Étude de cas introuvable")
        return
    
    st.info(f"🔄 Continuation de l'analyse: {case.title}")
    
    # Si l'étude a des sources mais pas d'analyse SEO
    if case.llm_responses and case.sources_analyzed == 0:
        st.write("📊 Des sources sont disponibles pour l'analyse SEO")
        if st.button("🚀 Lancer l'Analyse SEO", use_container_width=True):
            launch_seo_analysis(case_id)
    else:
        st.write("Fonctionnalité de continuation en développement...")


# Navigation principale
tab1, tab2, tab3 = st.tabs(["📋 Mes Études", "➕ Nouvelle Étude", "📊 Statistiques"])

with tab1:
    display_existing_cases()

with tab2:
    display_case_creation_wizard()

with tab3:
    display_case_statistics()


# Afficher les détails si une étude est sélectionnée
if hasattr(st.session_state, 'selected_case_id'):
    display_case_details(st.session_state.selected_case_id)


# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem;">
    💡 <strong>Études de Cas SEO:</strong> Analysez la concurrence en interrogeant plusieurs LLM pour identifier les meilleures sources,
    <br>puis comparez automatiquement leurs performances SEO pour découvrir des opportunités d'optimisation.
</div>
""", unsafe_allow_html=True)