# -*- coding: utf-8 -*-
"""
Analyseur SEO Principal
Point d'entrée principal pour analyser une page web
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from .config import (
    USER_MESSAGES, DEFAULT_USER_AGENT, REQUEST_TIMEOUT,
    SEO_ANALYSIS_DIR, SEO_SCORES_DIR, get_analysis_config
)
from .modules import (
    analyser_contenu_complet,
    analyser_structure_complete,
    analyser_performance_complete,
    calculer_score_global,
    generer_recommandations
)
from .utils.page_storage import save_page_content


def analyser_page_complete(url: str, options: dict = None) -> dict:
    """
    Analyse complète d'une page web avec tous les modules SEO
    
    Args:
        url: URL de la page à analyser
        options: Options d'analyse (optionnel)
        
    Returns:
        dict: Résultats complets de l'analyse SEO
    """
    print(f"\n🚀 DÉBUT DE L'ANALYSE SEO")
    print(f"🌐 URL: {url}")
    print("=" * 80)
    
    # Configuration par défaut
    if options is None:
        options = get_analysis_config()
    
    # Initialiser les résultats
    resultats = {
        'url': url,
        'date_analyse': datetime.now().isoformat(),
        'domaine': urlparse(url).netloc,
        'configuration': options,
        'succes': False,
        'erreurs': [],
        'analyses': {},
        'scores': {},
        'recommandations': {}
    }
    
    try:
        # === ÉTAPE 1: RÉCUPÉRATION DE LA PAGE ===
        print("📥 Récupération de la page web...")
        soup, contenu_brut = recuperer_page_web(url)
        
        if not soup:
            resultats['erreurs'].append("Impossible de récupérer le contenu de la page")
            return resultats
        
        # Sauvegarder la page pour cache/debug
        try:
            save_page_content(url, contenu_brut)
        except Exception as e:
            print(f"⚠️ Sauvegarde page échouée: {e}")
        
        print("✅ Page récupérée avec succès")
        
        # === ÉTAPE 2: ANALYSES PAR CATÉGORIE ===
        print("\n📊 ANALYSES PAR CATÉGORIE")
        print("-" * 50)
        
        # Analyse du contenu
        try:
            resultats['analyses']['contenu'] = analyser_contenu_complet(soup, url)
        except Exception as e:
            print(f"❌ Erreur analyse contenu: {e}")
            resultats['erreurs'].append(f"Analyse contenu échouée: {e}")
        
        # Analyse de la structure
        try:
            resultats['analyses']['structure'] = analyser_structure_complete(soup, url)
        except Exception as e:
            print(f"❌ Erreur analyse structure: {e}")
            resultats['erreurs'].append(f"Analyse structure échouée: {e}")
        
        # Analyse des performances (si activée)
        if options.get('performance_enabled', False):
            try:
                resultats['analyses']['performance'] = analyser_performance_complete(url)
            except Exception as e:
                print(f"❌ Erreur analyse performance: {e}")
                resultats['erreurs'].append(f"Analyse performance échouée: {e}")
        else:
            print("⚠️ Analyse performance désactivée (pas de clé API)")
        
        # === ÉTAPE 3: CALCUL DES SCORES ===
        print("\n🧮 CALCUL DES SCORES")
        print("-" * 30)
        
        try:
            resultats['scores'] = calculer_score_global(resultats['analyses'])
            print(f"📈 Score global: {resultats['scores']['score_global']}/100")
            print(f"🎯 Niveau: {resultats['scores']['niveau_performance']}")
        except Exception as e:
            print(f"❌ Erreur calcul scores: {e}")
            resultats['erreurs'].append(f"Calcul scores échoué: {e}")
        
        # === ÉTAPE 4: GÉNÉRATION DES RECOMMANDATIONS ===
        print("\n💡 GÉNÉRATION DES RECOMMANDATIONS")
        print("-" * 40)
        
        try:
            resultats['recommandations'] = generer_recommandations(
                resultats['analyses'], 
                resultats['scores']
            )
            nb_reco = sum(len(reco) for reco in resultats['recommandations'].values())
            print(f"✅ {nb_reco} recommandations générées")
        except Exception as e:
            print(f"❌ Erreur génération recommandations: {e}")
            resultats['erreurs'].append(f"Recommandations échouées: {e}")
        
        # === ÉTAPE 5: SAUVEGARDE ===
        print("\n💾 SAUVEGARDE DES RÉSULTATS")
        print("-" * 35)
        
        try:
            sauvegarder_resultats(resultats)
            resultats['succes'] = True
            print("✅ Résultats sauvegardés avec succès")
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            resultats['erreurs'].append(f"Sauvegarde échouée: {e}")
        
        # === RÉSUMÉ FINAL ===
        print("\n" + "=" * 80)
        print("🎉 ANALYSE TERMINÉE")
        
        if resultats['succes']:
            score = resultats['scores'].get('score_global', 0)
            niveau = resultats['scores'].get('niveau_performance', 'Inconnu')
            print(f"📊 Score final: {score}/100 ({niveau})")
            
            forces = resultats['scores'].get('forces', [])
            faiblesses = resultats['scores'].get('faiblesses', [])
            
            if forces:
                print(f"💪 Forces: {', '.join(forces)}")
            if faiblesses:
                print(f"⚠️ À améliorer: {', '.join(faiblesses)}")
        
        if resultats['erreurs']:
            print(f"⚠️ {len(resultats['erreurs'])} erreur(s) détectée(s)")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE: {e}")
        resultats['erreurs'].append(f"Erreur critique: {e}")
    
    return resultats


def recuperer_page_web(url: str) -> tuple:
    """
    Récupère le contenu HTML d'une page web
    
    Args:
        url: URL à récupérer
        
    Returns:
        tuple: (objet BeautifulSoup, contenu HTML brut) ou (None, None) si erreur
    """
    headers = {
        'User-Agent': DEFAULT_USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Cache-Control': 'no-cache'
    }
    
    try:
        print(f"  🔗 Connexion à {url}...")
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        
        if response.status_code != 200:
            print(f"  ❌ Code de statut HTTP: {response.status_code}")
            return None, None
        
        # Vérifier le type de contenu
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            print(f"  ⚠️ Type de contenu non HTML: {content_type}")
        
        # Parser avec BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"  ✅ Page récupérée ({len(response.text)} caractères)")
        return soup, response.text
        
    except requests.exceptions.Timeout:
        print(f"  ❌ Timeout après {REQUEST_TIMEOUT}s")
        return None, None
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Erreur de connexion")
        return None, None
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Erreur de requête: {e}")
        return None, None
    except Exception as e:
        print(f"  ❌ Erreur inattendue: {e}")
        return None, None


def sauvegarder_resultats(resultats: dict) -> None:
    """
    Sauvegarde les résultats dans les fichiers JSON
    
    Args:
        resultats: Dictionnaire des résultats complets
    """
    url = resultats['url']
    domaine = resultats['domaine']
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Nom de fichier sécurisé
    nom_fichier = nettoyer_nom_fichier(url)
    
    # Sauvegarder le rapport brut complet
    fichier_brut = SEO_ANALYSIS_DIR / f"rapport_{nom_fichier}.json"
    print(f"  💾 Sauvegarde rapport brut: {fichier_brut.name}")
    
    with open(fichier_brut, 'w', encoding='utf-8') as f:
        json.dump(resultats, f, indent=2, ensure_ascii=False)
    
    # Sauvegarder le rapport de scores simplifié
    if 'scores' in resultats and resultats['scores']:
        rapport_scores = {
            'url': url,
            'domaine': domaine,
            'date_analyse': resultats['date_analyse'],
            'score_global': resultats['scores'].get('score_global', 0),
            'niveau_performance': resultats['scores'].get('niveau_performance', 'Inconnu'),
            'scores_categories': resultats['scores'].get('scores_categories', {}),
            'forces': resultats['scores'].get('forces', []),
            'faiblesses': resultats['scores'].get('faiblesses', []),
            'nombre_recommandations': sum(len(reco) for reco in resultats.get('recommandations', {}).values()),
            'succes': resultats['succes']
        }
        
        fichier_scores = SEO_SCORES_DIR / f"scores_{nom_fichier}.json"
        print(f"  📊 Sauvegarde scores: {fichier_scores.name}")
        
        with open(fichier_scores, 'w', encoding='utf-8') as f:
            json.dump(rapport_scores, f, indent=2, ensure_ascii=False)


def nettoyer_nom_fichier(url: str) -> str:
    """
    Convertit une URL en nom de fichier sécurisé
    
    Args:
        url: URL à convertir
        
    Returns:
        str: Nom de fichier nettoyé
    """
    import re
    
    # Supprimer le protocole
    nom = url.replace('https://', '').replace('http://', '')
    
    # Remplacer les caractères spéciaux
    nom = re.sub(r'[^\w\-_.]', '_', nom)
    
    # Supprimer les underscores multiples
    nom = re.sub(r'_+', '_', nom)
    
    # Limiter la longueur
    if len(nom) > 100:
        nom = nom[:100]
    
    # Supprimer les underscores en début/fin
    nom = nom.strip('_')
    
    return nom if nom else 'page_inconnue'


def main():
    """Fonction principale pour lancement en ligne de commande"""
    import sys
    
    # Récupérer l'URL depuis les variables d'environnement ou arguments
    url = os.getenv('ANALYSIS_URL')
    
    if not url and len(sys.argv) > 1:
        url = sys.argv[1]
    
    if not url:
        print("❌ Aucune URL spécifiée")
        print("💡 Utilisez: ANALYSIS_URL=https://example.com python -m src.analyseur")
        print("💡 Ou: python -m src.analyseur https://example.com")
        return
    
    # Lancer l'analyse
    resultats = analyser_page_complete(url)
    
    # Afficher le résumé
    if resultats['succes']:
        print(f"\n🎯 Analyse terminée avec succès pour {url}")
    else:
        print(f"\n⚠️ Analyse terminée avec des erreurs pour {url}")


if __name__ == "__main__":
    main()