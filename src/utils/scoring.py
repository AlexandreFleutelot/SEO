# -*- coding: utf-8 -*-
"""
scoring.py

Système de scoring pour convertir les analyses raw en scores comparables.
Permet de comparer les performances SEO entre différentes pages.

Ce module calcule des scores normalisés (0-100) pour chaque catégorie
et génère un score global SEO.
"""

import json
import math
from datetime import datetime
from typing import Dict, Any, Optional


class SEOScoring:
    """Classe pour calculer les scores SEO normalisés."""
    
    def __init__(self):
        # Poids des différentes catégories pour le score global
        self.category_weights = {
            "category_1_content": 0.25,        # 25% - Contenu crucial
            "category_2_structure": 0.20,      # 20% - Structure technique
            "category_3_linking": 0.15,        # 15% - Maillage interne
            "category_4_performance": 0.20,    # 20% - Performance critique
            "category_5_aio": 0.10,            # 10% - AIO émergent
            "category_6_llm_analysis": 0.10    # 10% - Analyse IA
        }
    
    def calculate_content_score(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule le score pour la catégorie Contenu & Sémantique."""
        scores = {}
        
        # 1.1 Richesse et couverture
        richness = content_data.get("1.1_richness_coverage", {})
        word_count = richness.get("word_count", 0)
        entity_count = richness.get("entity_count", 0)
        
        # Score basé sur le nombre de mots (optimal 800-1500)
        if word_count < 300:
            word_score = min(word_count / 300 * 50, 50)
        elif word_count <= 1500:
            word_score = 50 + (word_count - 300) / 1200 * 40
        else:
            word_score = min(90 + (word_count - 1500) / 500 * 10, 100)
        
        # Score basé sur les entités (optimal 30-80)
        entity_score = min(entity_count / 50 * 100, 100)
        
        scores["richness_score"] = (word_score * 0.6 + entity_score * 0.4)
        
        # 1.2 Style et clarté
        style = content_data.get("1.2_style_clarity", {})
        avg_sentence_length = style.get("avg_sentence_length_words", 15)
        list_count = style.get("list_count", 0)
        
        # Score longueur phrases (optimal 12-18 mots)
        if 12 <= avg_sentence_length <= 18:
            sentence_score = 100
        elif 8 <= avg_sentence_length < 12 or 18 < avg_sentence_length <= 25:
            sentence_score = 80
        else:
            sentence_score = max(60 - abs(avg_sentence_length - 15) * 2, 20)
        
        # Score listes (plus c'est mieux pour la structure)
        list_score = min(list_count / 10 * 100, 100)
        
        scores["style_score"] = (sentence_score * 0.7 + list_score * 0.3)
        
        # 1.3 Sources et fiabilité
        sources = content_data.get("1.3_sources_reliability", {})
        external_links = sources.get("external_link_count", 0)
        citations = sources.get("textual_citation_count", 0)
        
        # Score liens externes (optimal 3-8)
        if 3 <= external_links <= 8:
            external_score = 100
        elif external_links == 0:
            external_score = 20
        elif external_links < 3:
            external_score = 50 + external_links / 3 * 50
        else:
            external_score = max(100 - (external_links - 8) * 5, 40)
        
        # Score citations textuelles
        citation_score = min(citations * 25, 100)
        
        scores["sources_score"] = (external_score * 0.7 + citation_score * 0.3)
        
        # 1.4 Fraîcheur
        freshness = content_data.get("1.4_freshness", {})
        detected_dates = freshness.get("detected_dates_in_text", [])
        
        # Score basé sur la présence de dates récentes
        if detected_dates:
            # Vérifier si on a des dates récentes (derniers 12 mois)
            current_year = datetime.now().year
            recent_dates = [d for d in detected_dates if str(current_year) in str(d)]
            freshness_score = min(len(recent_dates) * 20 + 40, 100)
        else:
            freshness_score = 30
        
        scores["freshness_score"] = freshness_score
        
        # Score global contenu (moyenne pondérée)
        scores["category_score"] = (
            scores["richness_score"] * 0.35 +
            scores["style_score"] * 0.25 +
            scores["sources_score"] * 0.25 +
            scores["freshness_score"] * 0.15
        )
        
        return scores
    
    def calculate_structure_score(self, structure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule le score pour la catégorie Structure."""
        scores = {}
        
        # 2.1 Structure Hn
        hn_structure = structure_data.get("2.1_hn_structure", {})
        h1_count = hn_structure.get("h1_count", 0)
        hierarchy_issues = len(hn_structure.get("hierarchy_issues", []))
        
        # Score H1 (doit être exactement 1)
        if h1_count == 1:
            h1_score = 100
        elif h1_count == 0:
            h1_score = 0
        else:
            h1_score = max(80 - (h1_count - 1) * 20, 20)
        
        # Score hiérarchie (moins d'issues = mieux)
        hierarchy_score = max(100 - hierarchy_issues * 15, 0)
        
        scores["hn_score"] = (h1_score * 0.6 + hierarchy_score * 0.4)
        
        # 2.2 Métadonnées
        metadata = structure_data.get("2.2_metadata", {})
        title_length = metadata.get("title_length", 0)
        meta_desc_length = metadata.get("meta_description_length", 0)
        
        # Score titre (optimal 50-60 caractères)
        if 50 <= title_length <= 60:
            title_score = 100
        elif 40 <= title_length < 50 or 60 < title_length <= 70:
            title_score = 85
        elif title_length < 30:
            title_score = 30
        else:
            title_score = max(70 - abs(title_length - 55), 20)
        
        # Score meta description (optimal 150-160 caractères)
        if 150 <= meta_desc_length <= 160:
            desc_score = 100
        elif 140 <= meta_desc_length < 150 or 160 < meta_desc_length <= 170:
            desc_score = 85
        elif meta_desc_length == 0:
            desc_score = 0
        else:
            desc_score = max(70 - abs(meta_desc_length - 155) / 2, 20)
        
        scores["metadata_score"] = (title_score * 0.6 + desc_score * 0.4)
        
        # 2.3 Optimisation images
        images = structure_data.get("2.3_images_optimization", {})
        alt_coverage = images.get("alt_coverage_percentage", 0)
        
        scores["images_score"] = alt_coverage  # Déjà en pourcentage
        
        # 2.4 Données structurées
        structured_data = structure_data.get("2.4_structured_data", {})
        schema_count = structured_data.get("schema_count", 0)
        
        scores["schema_score"] = min(schema_count * 25 + 25, 100)
        
        # 2.5 Crawlabilité
        crawlability = structure_data.get("2.5_crawlability", {})
        robots_status = crawlability.get("robots_txt_status", "")
        sitemap_status = crawlability.get("sitemap_xml_status", "")
        
        robots_score = 100 if robots_status == "found" else 0
        sitemap_score = 100 if sitemap_status == "found" else 0
        
        scores["crawlability_score"] = (robots_score * 0.4 + sitemap_score * 0.6)
        
        # Score global structure
        scores["category_score"] = (
            scores["hn_score"] * 0.25 +
            scores["metadata_score"] * 0.25 +
            scores["images_score"] * 0.20 +
            scores["schema_score"] * 0.15 +
            scores["crawlability_score"] * 0.15
        )
        
        return scores
    
    def calculate_linking_score(self, linking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule le score pour la catégorie Maillage."""
        scores = {}
        
        internal_linking = linking_data.get("3.1_3.2_internal_linking", {})
        internal_count = internal_linking.get("internal_link_count", 0)
        anchor_diversity = internal_linking.get("anchor_text_diversity", 0)
        non_descriptive = internal_linking.get("non_descriptive_anchor_count", 0)
        
        # Score nombre de liens internes (optimal 5-15 pour 1000 mots)
        if 5 <= internal_count <= 20:
            internal_score = 100
        elif internal_count < 5:
            internal_score = internal_count / 5 * 80
        else:
            internal_score = max(100 - (internal_count - 20) * 2, 40)
        
        # Score diversité des ancres
        diversity_score = min(anchor_diversity / internal_count * 100 if internal_count > 0 else 0, 100)
        
        # Score ancres non descriptives (moins c'est mieux)
        if internal_count > 0:
            descriptive_score = max(100 - (non_descriptive / internal_count * 100), 0)
        else:
            descriptive_score = 50
        
        scores["internal_links_score"] = internal_score
        scores["anchor_diversity_score"] = diversity_score
        scores["descriptive_anchors_score"] = descriptive_score
        
        # Score global maillage
        scores["category_score"] = (
            scores["internal_links_score"] * 0.4 +
            scores["anchor_diversity_score"] * 0.3 +
            scores["descriptive_anchors_score"] * 0.3
        )
        
        return scores
    
    def calculate_performance_score(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule le score pour la catégorie Performance."""
        scores = {}
        
        desktop = performance_data.get("4.1_4.2_desktop_performance", {})
        mobile = performance_data.get("4.1_4.2_mobile_performance", {})
        
        # Fonction pour scorer les Core Web Vitals
        def score_lcp(lcp_ms):
            if lcp_ms is None:
                return 0
            if lcp_ms <= 2500:
                return 100
            elif lcp_ms <= 4000:
                return 100 - (lcp_ms - 2500) / 1500 * 50
            else:
                return max(50 - (lcp_ms - 4000) / 1000 * 10, 0)
        
        def score_inp(inp_ms):
            if inp_ms is None:
                return 0
            if inp_ms <= 200:
                return 100
            elif inp_ms <= 500:
                return 100 - (inp_ms - 200) / 300 * 50
            else:
                return max(50 - (inp_ms - 500) / 100 * 10, 0)
        
        def score_cls(cls_score):
            if cls_score is None:
                return 0
            if cls_score <= 0.1:
                return 100
            elif cls_score <= 0.25:
                return 100 - (cls_score - 0.1) / 0.15 * 50
            else:
                return max(50 - (cls_score - 0.25) / 0.1 * 10, 0)
        
        # Scores desktop
        if not desktop.get("error"):
            desktop_lcp = score_lcp(desktop.get("LCP_ms"))
            desktop_inp = score_inp(desktop.get("INP_ms"))
            desktop_cls = score_cls(desktop.get("CLS_score"))
            scores["desktop_score"] = (desktop_lcp + desktop_inp + desktop_cls) / 3
        else:
            scores["desktop_score"] = 0
        
        # Scores mobile
        if not mobile.get("error"):
            mobile_lcp = score_lcp(mobile.get("LCP_ms"))
            mobile_inp = score_inp(mobile.get("INP_ms"))
            mobile_cls = score_cls(mobile.get("CLS_score"))
            scores["mobile_score"] = (mobile_lcp + mobile_inp + mobile_cls) / 3
        else:
            scores["mobile_score"] = 0
        
        # Score global performance (mobile privilégié)
        scores["category_score"] = scores["mobile_score"] * 0.7 + scores["desktop_score"] * 0.3
        
        return scores
    
    def calculate_aio_score(self, aio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule le score pour la catégorie AIO."""
        scores = {}
        
        # 5.1 Atomicité et réponse directe
        atomicity = aio_data.get("5.1_atomicity_direct_answer", {})
        qa_pairs = atomicity.get("potential_qa_pairs", 0)
        summary_blocks = atomicity.get("summary_block_count", 0)
        
        scores["atomicity_score"] = min(qa_pairs * 20 + summary_blocks * 30, 100)
        
        # 5.2 Données quantifiables
        quantifiable = aio_data.get("5.2_quantifiable_data", {})
        percentages = quantifiable.get("percentage_count", 0)
        currency = quantifiable.get("currency_mention_count", 0)
        dates = quantifiable.get("numeric_date_count", 0)
        
        scores["quantifiable_score"] = min((percentages * 5 + currency * 10 + dates * 2), 100)
        
        # 5.3 Signaux d'expertise
        expertise = aio_data.get("5.3_expertise_signals", {})
        author_schema = expertise.get("author_schema_present", False)
        about_page = expertise.get("about_page_linked", False)
        
        scores["expertise_score"] = (50 if author_schema else 0) + (50 if about_page else 0)
        
        # 5.4 Interopérabilité multimodale
        multimodal = aio_data.get("5.4_multimodal_interoperability", {})
        videos = multimodal.get("video_embed_count", 0)
        api_links = multimodal.get("potential_api_link_count", 0)
        
        scores["multimodal_score"] = min(videos * 30 + api_links * 40, 100)
        
        # Score global AIO
        scores["category_score"] = (
            scores["atomicity_score"] * 0.3 +
            scores["quantifiable_score"] * 0.25 +
            scores["expertise_score"] * 0.25 +
            scores["multimodal_score"] * 0.2
        )
        
        return scores
    
    def calculate_llm_score(self, llm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule le score pour la catégorie Analyse LLM."""
        scores = {}
        
        # Vérifier si l'analyse LLM est disponible
        if all(category.get("error") for category in llm_data.values()):
            scores["category_score"] = 0
            return scores
        
        # 6.1 Qualité contenu & E-A-T
        eat = llm_data.get("6.1_content_quality_eat", {})
        if not eat.get("error"):
            scores["eat_score"] = eat.get("overall_eat_score", 0) * 10
        else:
            scores["eat_score"] = 0
        
        # 6.2 Intention de recherche
        intent = llm_data.get("6.2_search_intent", {})
        if not intent.get("error"):
            intent_score = (intent.get("intent_fulfillment_score", 0) + 
                          intent.get("query_alignment_score", 0)) / 2
            scores["intent_score"] = intent_score * 10
        else:
            scores["intent_score"] = 0
        
        # 6.3 Couverture thématique
        coverage = llm_data.get("6.3_topical_coverage", {})
        if not coverage.get("error"):
            coverage_score = (coverage.get("topic_completeness_score", 0) + 
                            coverage.get("semantic_richness_score", 0)) / 2
            scores["coverage_score"] = coverage_score * 10
        else:
            scores["coverage_score"] = 0
        
        # 6.4 Expérience utilisateur
        ux = llm_data.get("6.4_user_experience", {})
        if not ux.get("error"):
            ux_score = (ux.get("engagement_potential_score", 0) + 
                       ux.get("readability_score", 0) + 
                       ux.get("actionability_score", 0)) / 3
            scores["ux_score"] = ux_score * 10
        else:
            scores["ux_score"] = 0
        
        # 6.5 Potentiel featured snippet
        snippet = llm_data.get("6.5_featured_snippet_potential", {})
        if not snippet.get("error"):
            scores["snippet_score"] = snippet.get("featured_snippet_potential", 0) * 10
        else:
            scores["snippet_score"] = 0
        
        # 6.6 Communication de marque
        brand = llm_data.get("6.6_brand_communication", {})
        if not brand.get("error"):
            brand_score = (brand.get("tone_consistency_score", 0) + 
                          brand.get("communication_clarity_score", 0)) / 2
            scores["brand_score"] = brand_score * 10
        else:
            scores["brand_score"] = 0
        
        # Score global LLM
        scores["category_score"] = (
            scores["eat_score"] * 0.25 +
            scores["intent_score"] * 0.2 +
            scores["coverage_score"] * 0.2 +
            scores["ux_score"] * 0.15 +
            scores["snippet_score"] * 0.1 +
            scores["brand_score"] * 0.1
        )
        
        return scores
    
    def calculate_global_score(self, category_scores: Dict[str, float]) -> Dict[str, Any]:
        """Calcule le score global SEO et les classements."""
        
        # Score global pondéré
        global_score = 0
        for category, weight in self.category_weights.items():
            score = category_scores.get(category, 0)
            global_score += score * weight
        
        # Déterminer le niveau de performance
        if global_score >= 90:
            performance_level = "Excellent"
            level_color = "green"
        elif global_score >= 75:
            performance_level = "Très bon"
            level_color = "lightgreen"
        elif global_score >= 60:
            performance_level = "Bon"
            level_color = "yellow"
        elif global_score >= 40:
            performance_level = "Moyen"
            level_color = "orange"
        else:
            performance_level = "Faible"
            level_color = "red"
        
        # Identifier les forces et faiblesses
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        strengths = [cat for cat, score in sorted_categories[:2] if score >= 70]
        weaknesses = [cat for cat, score in sorted_categories[-2:] if score < 60]
        
        return {
            "global_score": round(global_score, 1),
            "performance_level": performance_level,
            "level_color": level_color,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "category_breakdown": category_scores
        }
    
    def process_raw_report(self, raw_report: Dict[str, Any]) -> Dict[str, Any]:
        """Traite un rapport raw et génère le rapport de scores."""
        
        analysis_results = raw_report.get("analysis_results", {})
        
        # Calculer les scores par catégorie
        category_scores = {}
        detailed_scores = {}
        
        # Catégorie 1: Contenu
        if "category_1_content" in analysis_results:
            content_scores = self.calculate_content_score(analysis_results["category_1_content"])
            category_scores["category_1_content"] = content_scores["category_score"]
            detailed_scores["category_1_content"] = content_scores
        
        # Catégorie 2: Structure
        if "category_2_structure" in analysis_results:
            structure_scores = self.calculate_structure_score(analysis_results["category_2_structure"])
            category_scores["category_2_structure"] = structure_scores["category_score"]
            detailed_scores["category_2_structure"] = structure_scores
        
        # Catégorie 3: Maillage
        if "category_3_linking" in analysis_results:
            linking_scores = self.calculate_linking_score(analysis_results["category_3_linking"])
            category_scores["category_3_linking"] = linking_scores["category_score"]
            detailed_scores["category_3_linking"] = linking_scores
        
        # Catégorie 4: Performance
        if "category_4_performance" in analysis_results:
            performance_scores = self.calculate_performance_score(analysis_results["category_4_performance"])
            category_scores["category_4_performance"] = performance_scores["category_score"]
            detailed_scores["category_4_performance"] = performance_scores
        
        # Catégorie 5: AIO
        if "category_5_aio" in analysis_results:
            aio_scores = self.calculate_aio_score(analysis_results["category_5_aio"])
            category_scores["category_5_aio"] = aio_scores["category_score"]
            detailed_scores["category_5_aio"] = aio_scores
        
        # Catégorie 6: LLM
        if "category_6_llm_analysis" in analysis_results:
            llm_scores = self.calculate_llm_score(analysis_results["category_6_llm_analysis"])
            category_scores["category_6_llm_analysis"] = llm_scores["category_score"]
            detailed_scores["category_6_llm_analysis"] = llm_scores
        
        # Score global et analyse
        global_analysis = self.calculate_global_score(category_scores)
        
        # Rapport de scores final
        score_report = {
            "url": raw_report.get("url"),
            "analysis_date": datetime.now().isoformat(),
            "global_analysis": global_analysis,
            "category_scores": {
                "content_semantics": {
                    "score": round(category_scores.get("category_1_content", 0), 1),
                    "details": detailed_scores.get("category_1_content", {})
                },
                "technical_structure": {
                    "score": round(category_scores.get("category_2_structure", 0), 1),
                    "details": detailed_scores.get("category_2_structure", {})
                },
                "internal_linking": {
                    "score": round(category_scores.get("category_3_linking", 0), 1),
                    "details": detailed_scores.get("category_3_linking", {})
                },
                "performance": {
                    "score": round(category_scores.get("category_4_performance", 0), 1),
                    "details": detailed_scores.get("category_4_performance", {})
                },
                "aio_optimization": {
                    "score": round(category_scores.get("category_5_aio", 0), 1),
                    "details": detailed_scores.get("category_5_aio", {})
                },
                "llm_analysis": {
                    "score": round(category_scores.get("category_6_llm_analysis", 0), 1),
                    "details": detailed_scores.get("category_6_llm_analysis", {})
                }
            },
            "scoring_metadata": {
                "scoring_version": "1.0",
                "category_weights": self.category_weights,
                "total_categories": len(category_scores)
            }
        }
        
        return score_report


def generate_score_report(raw_report_path: str, output_path: str = None) -> Dict[str, Any]:
    """
    Génère un rapport de scores à partir d'un rapport raw.
    
    Args:
        raw_report_path: Chemin vers le fichier de rapport raw JSON
        output_path: Chemin de sortie (optionnel, généré automatiquement si non fourni)
    
    Returns:
        Dict contenant le rapport de scores
    """
    
    # Charger le rapport raw
    with open(raw_report_path, 'r', encoding='utf-8') as f:
        raw_report = json.load(f)
    
    # Créer le scorer et traiter le rapport
    scorer = SEOScoring()
    score_report = scorer.process_raw_report(raw_report)
    
    # Générer le chemin de sortie si non fourni
    if output_path is None:
        url = raw_report.get("url", "unknown")
        url_clean = url.split('//')[1].replace('/', '_') if '//' in url else "unknown"
        output_path = f"reports/scores/scores_{url_clean}.json"
    
    # Sauvegarder le rapport de scores
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(score_report, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Rapport de scores sauvegardé : {output_path}")
    
    return score_report


if __name__ == "__main__":
    # Test avec le dernier rapport disponible
    import os
    
    raw_reports_dir = "reports/raw"
    if os.path.exists(raw_reports_dir):
        raw_files = [f for f in os.listdir(raw_reports_dir) if f.endswith('.json')]
        if raw_files:
            latest_report = os.path.join(raw_reports_dir, raw_files[-1])
            print(f"Génération du rapport de scores pour: {latest_report}")
            
            score_report = generate_score_report(latest_report)
            
            # Afficher un résumé
            global_analysis = score_report["global_analysis"]
            print(f"\n🎯 Score Global SEO: {global_analysis['global_score']}/100")
            print(f"📊 Niveau de Performance: {global_analysis['performance_level']}")
            print(f"💪 Forces: {', '.join(global_analysis['strengths'])}")
            print(f"⚠️  Faiblesses: {', '.join(global_analysis['weaknesses'])}")
        else:
            print("Aucun rapport raw trouvé dans reports/raw/")
    else:
        print("Répertoire reports/raw/ non trouvé")