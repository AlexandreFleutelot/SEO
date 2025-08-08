# -*- coding: utf-8 -*-
"""
Modules d'analyse SEO simplifiés et humanisés
Structure organisée en dossiers logiques :
- seo/ : modules d'analyse SEO 
- core/ : utilitaires de base
- llm/ : analyse avec LLM (Large Language Models)
"""

# Modules d'analyse SEO
from .seo.contenu import analyser_contenu_complet
from .seo.structure import analyser_structure_complete  
from .seo.performance import analyser_performance_complete

# Utilitaires de base
from .core.utils import calculer_score_global, generer_recommandations

# Analyse avec LLM
from .llm.multi_llm_analyzer import analyser_question_multi_llm, MultiLLMAnalyzer

__all__ = [
    'analyser_contenu_complet',
    'analyser_structure_complete', 
    'analyser_performance_complete',
    'calculer_score_global',
    'generer_recommandations',
    'analyser_question_multi_llm',
    'MultiLLMAnalyzer'
]