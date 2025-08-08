# -*- coding: utf-8 -*-
"""
Modules d'analyse SEO simplifiés et humanisés
"""

from .contenu import analyser_contenu_complet
from .structure import analyser_structure_complete  
from .performance import analyser_performance_complete
from .utils import calculer_score_global, generer_recommandations

__all__ = [
    'analyser_contenu_complet',
    'analyser_structure_complete', 
    'analyser_performance_complete',
    'calculer_score_global',
    'generer_recommandations'
]