# -*- coding: utf-8 -*-
"""
Analyse des performances et Core Web Vitals
Ce module évalue la vitesse et les métriques de performance utilisateur
"""

import requests
import json
import time
from typing import Dict, Any, Optional
from urllib.parse import urlencode

from ...config import GOOGLE_PAGESPEED_API_KEY, REQUEST_TIMEOUT, has_api_key


def analyser_core_web_vitals(url: str) -> Dict[str, Any]:
    """
    Analyse les Core Web Vitals via l'API Google PageSpeed Insights
    
    Args:
        url: URL de la page à analyser
        
    Returns:
        dict: Métriques Core Web Vitals pour desktop et mobile
    """
    if not has_api_key("pagespeed"):
        print("⚠️ Clé API PageSpeed manquante - analyse de performance limitée")
        return {
            'erreur': 'Clé API PageSpeed Insights non configurée',
            'desktop': {'erreur': 'API non disponible'},
            'mobile': {'erreur': 'API non disponible'}
        }
    
    print("⚡ Analyse des performances avec Google PageSpeed...")
    
    # Analyser desktop et mobile
    resultats = {
        'desktop': analyser_pagespeed_strategie(url, 'desktop'),
        'mobile': analyser_pagespeed_strategie(url, 'mobile')
    }
    
    print("✅ Analyse de performance terminée")
    return resultats


def analyser_pagespeed_strategie(url: str, strategie: str) -> Dict[str, Any]:
    """
    Analyse une URL avec une stratégie spécifique (desktop/mobile)
    
    Args:
        url: URL à analyser
        strategie: 'desktop' ou 'mobile'
        
    Returns:
        dict: Métriques de performance
    """
    # URL de l'API PageSpeed
    api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    # Paramètres de la requête
    parametres = {
        'url': url,
        'key': GOOGLE_PAGESPEED_API_KEY,
        'strategy': strategie,
        'category': 'performance',
        'locale': 'fr'
    }
    
    try:
        print(f"  📊 Analyse {strategie}...")
        
        # Faire la requête
        response = requests.get(
            f"{api_url}?{urlencode(parametres)}",
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            return {
                'erreur': f'Erreur API PageSpeed: {response.status_code}',
                'score_performance': 0
            }
        
        donnees = response.json()
        
        # Extraire les métriques importantes
        lighthouse_result = donnees.get('lighthouseResult', {})
        audits = lighthouse_result.get('audits', {})
        categories = lighthouse_result.get('categories', {})
        
        # Score de performance global
        score_performance = 0
        if 'performance' in categories:
            score_performance = categories['performance'].get('score', 0) * 100
        
        # Extraire les Core Web Vitals
        metriques = extraire_core_web_vitals(audits)
        metriques['score_performance'] = round(score_performance)
        metriques['strategie'] = strategie
        
        return metriques
        
    except requests.exceptions.Timeout:
        return {'erreur': 'Timeout lors de l\'analyse PageSpeed', 'score_performance': 0}
    except requests.exceptions.RequestException as e:
        return {'erreur': f'Erreur réseau: {str(e)}', 'score_performance': 0}
    except json.JSONDecodeError:
        return {'erreur': 'Réponse API invalide', 'score_performance': 0}
    except Exception as e:
        return {'erreur': f'Erreur inattendue: {str(e)}', 'score_performance': 0}


def extraire_core_web_vitals(audits: dict) -> Dict[str, Any]:
    """
    Extrait les métriques Core Web Vitals des audits Lighthouse
    
    Args:
        audits: Données d'audit Lighthouse
        
    Returns:
        dict: Métriques Core Web Vitals formatées
    """
    # Mapping des métriques importantes
    metriques_mapping = {
        'largest-contentful-paint': 'LCP',
        'interaction-to-next-paint': 'INP', 
        'cumulative-layout-shift': 'CLS',
        'first-contentful-paint': 'FCP',
        'total-blocking-time': 'TBT'
    }
    
    metriques = {}
    
    for audit_key, metric_name in metriques_mapping.items():
        if audit_key in audits:
            audit_data = audits[audit_key]
            
            # Valeur numérique
            if 'numericValue' in audit_data:
                valeur = audit_data['numericValue']
                
                # Convertir en millisecondes pour LCP, INP, FCP, TBT
                if metric_name in ['LCP', 'INP', 'FCP', 'TBT']:
                    metriques[f'{metric_name}_ms'] = round(valeur)
                else:  # CLS reste en score
                    metriques[f'{metric_name}_score'] = round(valeur, 3)
            
            # Score de l'audit (0 à 1)
            if 'score' in audit_data:
                score = audit_data['score']
                if score is not None:
                    metriques[f'{metric_name}_evaluation'] = evaluer_metrique_cwv(metric_name, score)
    
    # Calculer un score global des Core Web Vitals
    metriques['score_cwv'] = calculer_score_cwv(metriques)
    
    return metriques


def evaluer_metrique_cwv(metrique: str, score: float) -> str:
    """
    Évalue une métrique Core Web Vitals
    
    Args:
        metrique: Nom de la métrique
        score: Score entre 0 et 1
        
    Returns:
        str: Évaluation textuelle
    """
    if score >= 0.9:
        return "Excellent"
    elif score >= 0.5:
        return "À améliorer"
    else:
        return "Critique"


def calculer_score_cwv(metriques: dict) -> int:
    """
    Calcule un score global des Core Web Vitals
    
    Args:
        metriques: Dictionnaire des métriques
        
    Returns:
        int: Score entre 0 et 100
    """
    score_base = 50
    
    # LCP (Largest Contentful Paint)
    if 'LCP_ms' in metriques:
        lcp = metriques['LCP_ms']
        if lcp <= 2500:
            score_base += 20
        elif lcp <= 4000:
            score_base += 10
        else:
            score_base -= 10
    
    # INP (Interaction to Next Paint) 
    if 'INP_ms' in metriques:
        inp = metriques['INP_ms']
        if inp <= 200:
            score_base += 15
        elif inp <= 500:
            score_base += 5
        else:
            score_base -= 10
    
    # CLS (Cumulative Layout Shift)
    if 'CLS_score' in metriques:
        cls = metriques['CLS_score']
        if cls <= 0.1:
            score_base += 15
        elif cls <= 0.25:
            score_base += 5
        else:
            score_base -= 10
    
    return max(0, min(100, score_base))


def analyser_taille_page(url: str) -> Dict[str, Any]:
    """
    Analyse basique de la taille de la page
    
    Args:
        url: URL à analyser
        
    Returns:
        dict: Informations sur la taille
    """
    try:
        print("📏 Analyse de la taille de la page...")
        
        response = requests.head(url, timeout=REQUEST_TIMEOUT)
        
        taille_headers = response.headers.get('Content-Length')
        if taille_headers:
            taille_octets = int(taille_headers)
            taille_ko = round(taille_octets / 1024, 2)
            
            # Évaluation de la taille
            if taille_ko < 100:
                evaluation = "Très léger"
            elif taille_ko < 500:
                evaluation = "Léger"
            elif taille_ko < 1000:
                evaluation = "Moyen"
            elif taille_ko < 2000:
                evaluation = "Lourd"
            else:
                evaluation = "Très lourd"
            
            return {
                'taille_octets': taille_octets,
                'taille_ko': taille_ko,
                'evaluation_taille': evaluation,
                'score_taille': calculer_score_taille(taille_ko)
            }
        else:
            # Essayer avec GET si HEAD ne fonctionne pas
            response = requests.get(url, timeout=REQUEST_TIMEOUT, stream=True)
            # Lire seulement les premiers octets pour estimer
            content_sample = response.raw.read(1024 * 10)  # 10KB sample
            
            return {
                'taille_estimee': True,
                'taille_echantillon_ko': round(len(content_sample) / 1024, 2),
                'evaluation_taille': "Estimation partielle",
                'score_taille': 50
            }
            
    except Exception as e:
        return {
            'erreur': f'Impossible d\'analyser la taille: {str(e)}',
            'score_taille': 50
        }


def calculer_score_taille(taille_ko: float) -> int:
    """Calcule un score basé sur la taille de la page"""
    if taille_ko < 100:
        return 100
    elif taille_ko < 300:
        return 90
    elif taille_ko < 500:
        return 75
    elif taille_ko < 1000:
        return 60
    elif taille_ko < 2000:
        return 40
    else:
        return 20


def analyser_temps_reponse(url: str) -> Dict[str, Any]:
    """
    Mesure le temps de réponse basique du serveur
    
    Args:
        url: URL à analyser
        
    Returns:
        dict: Informations sur le temps de réponse
    """
    try:
        print("⏱️ Mesure du temps de réponse...")
        
        debut = time.time()
        response = requests.head(url, timeout=REQUEST_TIMEOUT)
        fin = time.time()
        
        temps_reponse_ms = round((fin - debut) * 1000)
        
        # Évaluation du temps de réponse
        if temps_reponse_ms < 200:
            evaluation = "Excellent"
            score = 100
        elif temps_reponse_ms < 500:
            evaluation = "Bon"
            score = 85
        elif temps_reponse_ms < 1000:
            evaluation = "Moyen"
            score = 60
        elif temps_reponse_ms < 2000:
            evaluation = "Lent"
            score = 40
        else:
            evaluation = "Très lent"
            score = 20
        
        return {
            'temps_reponse_ms': temps_reponse_ms,
            'evaluation_temps': evaluation,
            'score_temps_reponse': score,
            'status_code': response.status_code
        }
        
    except requests.exceptions.Timeout:
        return {
            'erreur': 'Timeout du serveur',
            'score_temps_reponse': 10
        }
    except Exception as e:
        return {
            'erreur': f'Erreur de connexion: {str(e)}',
            'score_temps_reponse': 20
        }


def analyser_performance_complete(url: str) -> Dict[str, Any]:
    """
    Fonction principale qui effectue toutes les analyses de performance
    
    Args:
        url: URL de la page à analyser
        
    Returns:
        dict: Toutes les analyses de performance
    """
    print("⚡ Début de l'analyse des performances...")
    
    # Effectuer toutes les analyses
    analyses = {
        'core_web_vitals': analyser_core_web_vitals(url),
        'taille_page': analyser_taille_page(url),
        'temps_reponse': analyser_temps_reponse(url)
    }
    
    # Calculer un score global de performance
    scores = []
    
    # Score des Core Web Vitals
    cwv_desktop = analyses['core_web_vitals'].get('desktop', {})
    cwv_mobile = analyses['core_web_vitals'].get('mobile', {})
    
    if 'score_performance' in cwv_desktop:
        scores.append(cwv_desktop['score_performance'])
    if 'score_performance' in cwv_mobile:
        scores.append(cwv_mobile['score_performance'])
    
    # Score de la taille
    if 'score_taille' in analyses['taille_page']:
        scores.append(analyses['taille_page']['score_taille'])
    
    # Score du temps de réponse
    if 'score_temps_reponse' in analyses['temps_reponse']:
        scores.append(analyses['temps_reponse']['score_temps_reponse'])
    
    # Moyenne des scores disponibles
    if scores:
        analyses['score_performance_global'] = round(sum(scores) / len(scores))
    else:
        analyses['score_performance_global'] = 50  # Score neutre si aucune donnée
    
    print("✅ Analyse des performances terminée")
    return analyses