# -*- coding: utf-8 -*-
"""
Utilitaires pour le calcul des scores et la génération de recommandations
Ce module centralise la logique de scoring et les conseils d'amélioration
"""

from typing import Dict, List, Any
from ..config import SCORING_THRESHOLDS


def calculer_score_global(analyses: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcule le score SEO global basé sur toutes les analyses
    
    Args:
        analyses: Dictionnaire contenant toutes les analyses
        
    Returns:
        dict: Score global et détails par catégorie
    """
    print("🧮 Calcul des scores SEO...")
    
    scores_categories = {}
    
    # === CONTENU (35% du score) ===
    if 'contenu' in analyses:
        score_contenu = calculer_score_contenu(analyses['contenu'])
        scores_categories['contenu'] = score_contenu
    
    # === STRUCTURE (25% du score) ===
    if 'structure' in analyses:
        score_structure = calculer_score_structure(analyses['structure'])
        scores_categories['structure'] = score_structure
    
    # === PERFORMANCE (25% du score) ===
    if 'performance' in analyses:
        score_performance = analyses['performance'].get('score_performance_global', 50)
        scores_categories['performance'] = score_performance
    
    # === MAILLAGE (15% du score) ===
    if 'maillage' in analyses:
        score_maillage = calculer_score_maillage(analyses['maillage'])
        scores_categories['maillage'] = score_maillage
    
    # Calculer le score global pondéré
    poids = {
        'contenu': 0.35,
        'structure': 0.25,
        'performance': 0.25,
        'maillage': 0.15
    }
    
    score_global = 0
    total_poids = 0
    
    for categorie, score in scores_categories.items():
        if score > 0:  # Ignorer les scores nuls (analyses échouées)
            score_global += score * poids.get(categorie, 0)
            total_poids += poids.get(categorie, 0)
    
    # Normaliser si certaines analyses ont échoué
    if total_poids > 0:
        score_global = score_global / total_poids
    else:
        score_global = 0
    
    # Déterminer le niveau de performance
    niveau_performance = determiner_niveau_performance(score_global)
    
    # Identifier les forces et faiblesses
    forces, faiblesses = identifier_forces_faiblesses(scores_categories)
    
    return {
        'score_global': round(score_global, 1),
        'niveau_performance': niveau_performance,
        'scores_categories': scores_categories,
        'forces': forces,
        'faiblesses': faiblesses,
        'details_scoring': {
            'poids_utilises': {k: v for k, v in poids.items() if k in scores_categories},
            'nombre_categories': len(scores_categories)
        }
    }


def calculer_score_contenu(analyse_contenu: Dict[str, Any]) -> int:
    """Calcule le score de la catégorie contenu"""
    score = 0
    nombre_metriques = 0
    
    # Score de richesse
    if 'richesse_couverture' in analyse_contenu:
        richesse = analyse_contenu['richesse_couverture']
        if 'nombre_mots' in richesse:
            nb_mots = richesse['nombre_mots']
            if nb_mots >= 1500:
                score += 90
            elif nb_mots >= 1000:
                score += 75
            elif nb_mots >= 500:
                score += 60
            elif nb_mots >= 300:
                score += 45
            else:
                score += 20
            nombre_metriques += 1
        
        if 'nombre_entites' in richesse:
            nb_entites = richesse['nombre_entites']
            if nb_entites >= 20:
                score += 85
            elif nb_entites >= 10:
                score += 70
            elif nb_entites >= 5:
                score += 50
            else:
                score += 30
            nombre_metriques += 1
    
    # Score de lisibilité
    if 'style_clarte' in analyse_contenu:
        style = analyse_contenu['style_clarte']
        if 'lisibilite_score' in style:
            score += style['lisibilite_score']
            nombre_metriques += 1
    
    # Score de crédibilité
    if 'sources_fiabilite' in analyse_contenu:
        sources = analyse_contenu['sources_fiabilite']
        if 'score_credibilite' in sources:
            score += sources['score_credibilite']
            nombre_metriques += 1
    
    # Score de fraîcheur
    if 'fraicheur' in analyse_contenu:
        fraicheur = analyse_contenu['fraicheur']
        if 'score_fraicheur' in fraicheur:
            score += fraicheur['score_fraicheur']
            nombre_metriques += 1
    
    # Score de naturalité (anti-IA)
    if 'detection_ia' in analyse_contenu:
        ia = analyse_contenu['detection_ia']
        if 'score_naturel' in ia:
            score += ia['score_naturel']
            nombre_metriques += 1
    
    return round(score / nombre_metriques) if nombre_metriques > 0 else 0


def calculer_score_structure(analyse_structure: Dict[str, Any]) -> int:
    """Calcule le score de la catégorie structure"""
    score = 0
    nombre_metriques = 0
    
    # Score des titres
    if 'structure_titres' in analyse_structure:
        titres = analyse_structure['structure_titres']
        if 'score_structure_titres' in titres:
            score += titres['score_structure_titres']
            nombre_metriques += 1
    
    # Score des métadonnées
    if 'metadonnees' in analyse_structure:
        meta = analyse_structure['metadonnees']
        if 'score_metadonnees' in meta:
            score += meta['score_metadonnees']
            nombre_metriques += 1
    
    # Score des images
    if 'images' in analyse_structure:
        images = analyse_structure['images']
        if 'score_images' in images:
            score += images['score_images']
            nombre_metriques += 1
    
    # Score des données structurées
    if 'donnees_structurees' in analyse_structure:
        schema = analyse_structure['donnees_structurees']
        if 'score_donnees_structurees' in schema:
            score += schema['score_donnees_structurees']
            nombre_metriques += 1
    
    # Score de crawlabilité
    if 'crawlabilite' in analyse_structure:
        crawl = analyse_structure['crawlabilite']
        if 'score_crawlabilite' in crawl:
            score += crawl['score_crawlabilite']
            nombre_metriques += 1
    
    return round(score / nombre_metriques) if nombre_metriques > 0 else 0


def calculer_score_maillage(analyse_maillage: Dict[str, Any]) -> int:
    """Calcule le score de la catégorie maillage interne"""
    # Score par défaut si pas d'analyse de maillage
    return 60


def determiner_niveau_performance(score: float) -> str:
    """Détermine le niveau de performance basé sur le score"""
    if score >= SCORING_THRESHOLDS['excellent']:
        return "Excellent"
    elif score >= SCORING_THRESHOLDS['bon']:
        return "Bon"
    elif score >= SCORING_THRESHOLDS['moyen']:
        return "Moyen"
    else:
        return "Faible"


def identifier_forces_faiblesses(scores: Dict[str, int]) -> tuple:
    """Identifie les forces et faiblesses basées sur les scores"""
    forces = []
    faiblesses = []
    
    for categorie, score in scores.items():
        nom_categorie = nom_convivial_categorie(categorie)
        
        if score >= SCORING_THRESHOLDS['excellent']:
            forces.append(nom_categorie)
        elif score < SCORING_THRESHOLDS['moyen']:
            faiblesses.append(nom_categorie)
    
    return forces, faiblesses


def nom_convivial_categorie(categorie: str) -> str:
    """Convertit le nom technique en nom convivial"""
    mapping = {
        'contenu': 'Contenu & Sémantique',
        'structure': 'Structure Technique', 
        'performance': 'Performance & Vitesse',
        'maillage': 'Maillage Interne'
    }
    return mapping.get(categorie, categorie.title())


def generer_recommandations(analyses: Dict[str, Any], scores: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Génère des recommandations personnalisées basées sur les analyses
    
    Args:
        analyses: Toutes les analyses effectuées
        scores: Scores calculés par catégorie
        
    Returns:
        dict: Recommandations organisées par catégorie
    """
    print("💡 Génération des recommandations...")
    
    recommandations = {
        'contenu': [],
        'structure': [],
        'performance': [],
        'maillage': [],
        'prioritaires': []
    }
    
    # === RECOMMANDATIONS CONTENU ===
    if 'contenu' in analyses:
        reco_contenu = generer_recommandations_contenu(analyses['contenu'])
        recommandations['contenu'].extend(reco_contenu)
    
    # === RECOMMANDATIONS STRUCTURE ===
    if 'structure' in analyses:
        reco_structure = generer_recommandations_structure(analyses['structure'])
        recommandations['structure'].extend(reco_structure)
    
    # === RECOMMANDATIONS PERFORMANCE ===
    if 'performance' in analyses:
        reco_performance = generer_recommandations_performance(analyses['performance'])
        recommandations['performance'].extend(reco_performance)
    
    # === RECOMMANDATIONS PRIORITAIRES ===
    score_global = scores.get('score_global', 0)
    if score_global < 50:
        recommandations['prioritaires'].append(
            "🔥 URGENT: Score global faible - concentrez-vous sur les faiblesses identifiées"
        )
    
    # Identifier les 3 recommandations les plus importantes
    toutes_reco = []
    for categorie, reco_list in recommandations.items():
        if categorie != 'prioritaires':
            toutes_reco.extend(reco_list[:2])  # Max 2 par catégorie
    
    if len(toutes_reco) >= 3:
        recommandations['prioritaires'].extend(toutes_reco[:3])
    
    print("✅ Recommandations générées")
    return recommandations


def generer_recommandations_contenu(analyse_contenu: Dict[str, Any]) -> List[str]:
    """Génère des recommandations pour le contenu"""
    recommendations = []
    
    # Richesse du contenu
    if 'richesse_couverture' in analyse_contenu:
        richesse = analyse_contenu['richesse_couverture']
        
        if 'nombre_mots' in richesse:
            nb_mots = richesse['nombre_mots']
            if nb_mots < 300:
                recommendations.append("📝 Enrichir le contenu : ajouter au moins 300 mots pour améliorer la pertinence SEO")
            elif nb_mots < 800:
                recommendations.append("📈 Développer le contenu : viser 800-1500 mots pour un meilleur positionnement")
        
        if 'nombre_entites' in richesse and richesse['nombre_entites'] < 5:
            recommendations.append("🏷️ Ajouter plus d'entités nommées (personnes, lieux, organisations) pour enrichir la sémantique")
    
    # Lisibilité
    if 'style_clarte' in analyse_contenu:
        style = analyse_contenu['style_clarte']
        
        if 'nombre_listes' in style and style['nombre_listes'] == 0:
            recommendations.append("📋 Structurer avec des listes à puces pour améliorer la lisibilité")
        
        if 'longueur_moyenne_phrase' in style and style['longueur_moyenne_phrase'] > 25:
            recommendations.append("✂️ Raccourcir les phrases (actuellement > 25 mots) pour une meilleure lisibilité")
    
    # Sources et crédibilité
    if 'sources_fiabilite' in analyse_contenu:
        sources = analyse_contenu['sources_fiabilite']
        
        if 'sources_fiables' in sources and sources['sources_fiables'] == 0:
            recommendations.append("🔗 Ajouter des liens vers des sources fiables (.gouv, .edu, organisations reconnues)")
        
        if 'citations_textuelles' in sources and sources['citations_textuelles'] == 0:
            recommendations.append("📚 Inclure des citations et références pour renforcer la crédibilité")
    
    # Fraîcheur
    if 'fraicheur' in analyse_contenu:
        fraicheur = analyse_contenu['fraicheur']
        
        if fraicheur.get('niveau_fraicheur') == 'ancien':
            recommendations.append("🔄 Mettre à jour le contenu : les informations semblent anciennes")
        elif fraicheur.get('jours_depuis_maj') is None:
            recommendations.append("📅 Ajouter une date de publication/mise à jour visible")
    
    # Détection IA
    if 'detection_ia' in analyse_contenu:
        ia = analyse_contenu['detection_ia']
        
        if ia.get('score_naturel', 100) < 60:
            recommendations.append("✍️ Humaniser le contenu : le texte semble trop généré par IA, ajouter plus de personnalité")
    
    return recommendations[:5]  # Limiter à 5 recommandations max


def generer_recommandations_structure(analyse_structure: Dict[str, Any]) -> List[str]:
    """Génère des recommandations pour la structure"""
    recommendations = []
    
    # Structure des titres
    if 'structure_titres' in analyse_structure:
        titres = analyse_structure['structure_titres']
        
        if titres.get('nombre_h1') == 0:
            recommendations.append("🏷️ IMPORTANT: Ajouter un titre H1 unique et descriptif")
        elif titres.get('nombre_h1') > 1:
            recommendations.append("⚠️ Utiliser un seul H1 par page (actuellement {})".format(titres['nombre_h1']))
        
        if not titres.get('hierarchie_correcte'):
            recommendations.append("📊 Corriger la hiérarchie des titres (H1→H2→H3...)")
    
    # Métadonnées
    if 'metadonnees' in analyse_structure:
        meta = analyse_structure['metadonnees']
        
        if meta.get('qualite_titre') == 'manquant':
            recommendations.append("📝 CRITIQUE: Ajouter un titre de page (balise title)")
        elif meta.get('qualite_titre') in ['trop court', 'trop long']:
            recommendations.append("📏 Optimiser le titre : viser 30-60 caractères (actuellement {})".format(meta.get('longueur_titre')))
        
        if meta.get('qualite_description') == 'manquant':
            recommendations.append("📄 Ajouter une meta description attractive de 150-160 caractères")
        elif meta.get('qualite_description') in ['trop court', 'trop long']:
            recommendations.append("📐 Ajuster la meta description : viser 150-160 caractères")
        
        if not meta.get('url_canonical'):
            recommendations.append("🔗 Ajouter une URL canonique pour éviter le contenu dupliqué")
    
    # Images
    if 'images' in analyse_structure:
        images = analyse_structure['images']
        
        if images.get('couverture_alt_pourcentage', 0) < 80:
            recommendations.append("🖼️ Ajouter des attributs alt à toutes les images ({:.0f}% actuellement)".format(images.get('couverture_alt_pourcentage', 0)))
        
        if images.get('alt_vides', 0) > 0:
            recommendations.append("✏️ Remplir les attributs alt vides des images")
    
    # Données structurées
    if 'donnees_structurees' in analyse_structure:
        schema = analyse_structure['donnees_structurees']
        
        if not schema.get('json_ld_present') and not schema.get('microdata_present'):
            recommendations.append("🏗️ Implémenter des données structurées (JSON-LD) pour améliorer l'affichage dans les résultats")
    
    # Crawlabilité
    if 'crawlabilite' in analyse_structure:
        crawl = analyse_structure['crawlabilite']
        
        if crawl.get('noindex'):
            recommendations.append("🚫 ATTENTION: Page marquée noindex - elle ne sera pas indexée")
        
        if crawl.get('nombre_liens_internes', 0) < 3:
            recommendations.append("🔗 Améliorer le maillage interne : ajouter plus de liens vers d'autres pages")
    
    return recommendations[:5]


def generer_recommandations_performance(analyse_performance: Dict[str, Any]) -> List[str]:
    """Génère des recommandations pour la performance"""
    recommendations = []
    
    # Core Web Vitals
    if 'core_web_vitals' in analyse_performance:
        cwv = analyse_performance['core_web_vitals']
        
        # Desktop
        if 'desktop' in cwv and not cwv['desktop'].get('erreur'):
            desktop = cwv['desktop']
            
            if desktop.get('LCP_ms', 0) > 2500:
                recommendations.append("🖥️ Améliorer le LCP Desktop : réduire le temps de chargement du plus grand élément")
            
            if desktop.get('INP_ms', 0) > 200:
                recommendations.append("⚡ Optimiser l'interactivité Desktop : réduire le délai de réponse")
            
            if desktop.get('CLS_score', 0) > 0.1:
                recommendations.append("📐 Réduire les décalages visuels Desktop : stabiliser la mise en page")
        
        # Mobile
        if 'mobile' in cwv and not cwv['mobile'].get('erreur'):
            mobile = cwv['mobile']
            
            if mobile.get('LCP_ms', 0) > 2500:
                recommendations.append("📱 Améliorer le LCP Mobile : optimiser pour les connexions lentes")
            
            if mobile.get('score_performance', 0) < 50:
                recommendations.append("📱 Performance mobile critique : optimiser pour les appareils mobiles")
    
    # Taille de page
    if 'taille_page' in analyse_performance:
        taille = analyse_performance['taille_page']
        
        if taille.get('taille_ko', 0) > 1000:
            recommendations.append("💾 Réduire la taille de la page : actuellement {:.1f} KB".format(taille.get('taille_ko', 0)))
    
    # Temps de réponse
    if 'temps_reponse' in analyse_performance:
        temps = analyse_performance['temps_reponse']
        
        if temps.get('temps_reponse_ms', 0) > 1000:
            recommendations.append("⏱️ Améliorer le temps de réponse serveur : actuellement {} ms".format(temps.get('temps_reponse_ms', 0)))
    
    return recommendations[:4]  # Max 4 pour performance