# -*- coding: utf-8 -*-
"""
enhanced_structure.py

Analyses de structure améliorées pour l'optimisation LLM/GEO.

Nouvelles analyses :
1. Vérification du rendu côté serveur (SSR) pour JavaScript
2. Présence de l'année dans le titre et la description méta
3. Pertinence des balisages Structured Data (Schema.org)
4. Statut du fichier llms.txt
"""

import re
import json
import requests
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse


class EnhancedStructureAnalyzer:
    """Analyseur de structure amélioré pour l'optimisation LLM."""
    
    def __init__(self):
        self.current_year = datetime.now().year
    
    def check_ssr_javascript_rendering(self, url: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        2.1 Vérification du rendu côté serveur (SSR) pour JavaScript.
        Vérifie si le contenu est accessible sans exécution JavaScript.
        """
        
        # Analyser la présence de JavaScript critique
        js_scripts = soup.find_all('script')
        critical_js_indicators = [
            'React', 'Vue', 'Angular', 'document.write',
            'innerHTML', 'appendChild', 'ReactDOM.render'
        ]
        
        critical_js_detected = 0
        framework_detected = []
        
        for script in js_scripts:
            if script.string:
                script_content = script.string
                for indicator in critical_js_indicators:
                    if indicator in script_content:
                        critical_js_detected += 1
                        if indicator in ['React', 'Vue', 'Angular']:
                            framework_detected.append(indicator)
        
        # Vérifier les div/elements avec des IDs typiques de frameworks SPA
        spa_indicators = soup.find_all(['div', 'main'], 
                                     id=re.compile(r'app|root|vue|react|angular', re.I))
        
        # Analyser le contenu visible sans JS
        text_content_length = len(soup.get_text().strip())
        
        # Détecter les lazy loading et contenu dynamique
        lazy_elements = soup.find_all(attrs={'data-src': True}) + \
                       soup.find_all(attrs={'loading': 'lazy'})
        
        # Score SSR (100 = parfait, 0 = problématique)
        ssr_score = 100
        
        if critical_js_detected > 0:
            ssr_score -= critical_js_detected * 10
        
        if len(spa_indicators) > 0:
            ssr_score -= 20
        
        if text_content_length < 500:  # Contenu trop faible peut indiquer du rendu JS
            ssr_score -= 30
        
        ssr_score = max(ssr_score, 0)
        
        # Évaluation du niveau de compatibilité crawler
        if ssr_score >= 80:
            compatibility_level = "Excellent - Contenu entièrement accessible"
        elif ssr_score >= 60:
            compatibility_level = "Bon - Compatible avec quelques optimisations possibles"
        elif ssr_score >= 40:
            compatibility_level = "Moyen - Risques pour l'indexation IA"
        else:
            compatibility_level = "Problématique - SSR requis pour l'optimisation LLM"
        
        return {
            "ssr_compatibility_score": ssr_score,
            "compatibility_level": compatibility_level,
            "critical_js_detected": critical_js_detected,
            "frameworks_detected": list(set(framework_detected)),
            "spa_indicators_count": len(spa_indicators),
            "text_content_length": text_content_length,
            "lazy_elements_count": len(lazy_elements),
            "recommendations": self._get_ssr_recommendations(ssr_score, framework_detected)
        }
    
    def analyze_year_presence_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        2.2 Présence de l'année dans le titre et la description méta.
        Analyse cruciale pour la fraîcheur perçue par les LLM.
        """
        
        # Analyser le titre
        title_element = soup.find('title')
        title_text = title_element.get_text() if title_element else ""
        
        # Analyser la meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_desc_text = meta_desc.get('content', '') if meta_desc else ""
        
        # Patterns pour détecter l'année
        year_patterns = [
            str(self.current_year),
            str(self.current_year - 1),  # Année précédente acceptable
            r'\b20[2-3][0-9]\b'  # 2020-2039
        ]
        
        # Vérifier présence dans le titre
        title_has_current_year = str(self.current_year) in title_text
        title_has_recent_year = any(re.search(pattern, title_text) for pattern in year_patterns[:2])
        title_has_any_year = any(re.search(pattern, title_text) for pattern in year_patterns)
        
        # Vérifier présence dans la meta description
        desc_has_current_year = str(self.current_year) in meta_desc_text
        desc_has_recent_year = any(re.search(pattern, meta_desc_text) for pattern in year_patterns[:2])
        desc_has_any_year = any(re.search(pattern, meta_desc_text) for pattern in year_patterns)
        
        # Analyser les headings H1-H3 pour la fraîcheur
        headings_with_year = 0
        main_headings = soup.find_all(['h1', 'h2', 'h3'])
        for heading in main_headings:
            heading_text = heading.get_text()
            if any(re.search(pattern, heading_text) for pattern in year_patterns[:2]):
                headings_with_year += 1
        
        # Score de fraîcheur temporelle
        freshness_score = 0
        if title_has_current_year:
            freshness_score += 40
        elif title_has_recent_year:
            freshness_score += 25
        elif title_has_any_year:
            freshness_score += 10
        
        if desc_has_current_year:
            freshness_score += 30
        elif desc_has_recent_year:
            freshness_score += 20
        elif desc_has_any_year:
            freshness_score += 5
        
        freshness_score += min(headings_with_year * 10, 30)  # Bonus headings
        
        freshness_level = (
            "Excellent" if freshness_score >= 70
            else "Très bon" if freshness_score >= 50
            else "Bon" if freshness_score >= 30
            else "Amélioration nécessaire"
        )
        
        return {
            "title_analysis": {
                "has_current_year": title_has_current_year,
                "has_recent_year": title_has_recent_year,
                "has_any_year": title_has_any_year,
                "title_text": title_text[:100] + "..." if len(title_text) > 100 else title_text
            },
            "meta_description_analysis": {
                "has_current_year": desc_has_current_year,
                "has_recent_year": desc_has_recent_year,
                "has_any_year": desc_has_any_year,
                "description_text": meta_desc_text[:150] + "..." if len(meta_desc_text) > 150 else meta_desc_text
            },
            "headings_with_year_count": headings_with_year,
            "freshness_score": freshness_score,
            "freshness_level": freshness_level,
            "recommendations": self._get_year_recommendations(title_has_current_year, desc_has_current_year)
        }
    
    def analyze_structured_data_relevance(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        2.3 Pertinence des balisages Structured Data (Schema.org).
        Évalue la granularité et pertinence des schémas utilisés.
        """
        
        # Extraire tous les scripts JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        
        # Analyser les micro-données
        microdata_elements = soup.find_all(attrs={'itemtype': True})
        
        # Analyser les données structurées RDFa
        rdfa_elements = soup.find_all(attrs={'typeof': True})
        
        structured_schemas = []
        schema_relevance_scores = {}
        
        # Analyser JSON-LD
        for script in json_ld_scripts:
            try:
                if script.string:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        schema_type = data.get('@type', 'Unknown')
                        structured_schemas.append(schema_type)
                        
                        # Évaluer la pertinence du schéma
                        relevance = self._evaluate_schema_relevance(schema_type, data)
                        schema_relevance_scores[schema_type] = relevance
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                schema_type = item.get('@type', 'Unknown')
                                structured_schemas.append(schema_type)
                                relevance = self._evaluate_schema_relevance(schema_type, item)
                                schema_relevance_scores[schema_type] = relevance
            except json.JSONDecodeError:
                continue
        
        # Analyser les microdata
        for element in microdata_elements:
            itemtype = element.get('itemtype', '')
            if 'schema.org' in itemtype:
                schema_name = itemtype.split('/')[-1]
                structured_schemas.append(schema_name)
        
        # Score de qualité des données structurées
        total_schemas = len(structured_schemas)
        avg_relevance = (
            sum(schema_relevance_scores.values()) / len(schema_relevance_scores) 
            if schema_relevance_scores else 0
        )
        
        quality_score = min((total_schemas * 15) + (avg_relevance * 0.7), 100)
        
        # Recommandations de schémas manquants
        recommended_schemas = self._recommend_missing_schemas(soup, structured_schemas)
        
        return {
            "total_structured_schemas": total_schemas,
            "json_ld_count": len(json_ld_scripts),
            "microdata_count": len(microdata_elements),
            "rdfa_count": len(rdfa_elements),
            "schema_types_detected": list(set(structured_schemas)),
            "schema_relevance_scores": schema_relevance_scores,
            "average_relevance_score": round(avg_relevance, 1),
            "structured_data_quality_score": round(quality_score, 1),
            "recommended_missing_schemas": recommended_schemas,
            "schema_optimization_level": (
                "Expert" if quality_score >= 80
                else "Avancé" if quality_score >= 60
                else "Intermédiaire" if quality_score >= 40
                else "Basique"
            )
        }
    
    def check_llms_txt_status(self, url: str) -> Dict[str, Any]:
        """
        2.4 Statut du fichier llms.txt.
        Vérifie la présence et le contenu du fichier llms.txt.
        """
        
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        llms_txt_url = urljoin(base_url, '/llms.txt')
        
        try:
            response = requests.get(llms_txt_url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                content_length = len(content)
                
                # Analyser le contenu du fichier
                lines = content.split('\n')
                non_empty_lines = [line.strip() for line in lines if line.strip()]
                
                # Détecter les sections standard
                has_user_agent = any('User-agent' in line for line in lines)
                has_disallow = any('Disallow' in line for line in lines)
                has_allow = any('Allow' in line for line in lines)
                has_crawl_delay = any('Crawl-delay' in line for line in lines)
                
                # Format spécifique llms.txt
                has_ai_directive = any(keyword in content.lower() for keyword in 
                                     ['ai', 'llm', 'gpt', 'claude', 'bot', 'crawler'])
                
                status = "found_and_configured" if content_length > 50 else "found_but_minimal"
                
            elif response.status_code == 404:
                status = "not_found"
                content = ""
                content_length = 0
                non_empty_lines = []
                has_user_agent = has_disallow = has_allow = has_crawl_delay = has_ai_directive = False
            
            else:
                status = "error_accessing"
                content = f"HTTP {response.status_code}"
                content_length = 0
                non_empty_lines = []
                has_user_agent = has_disallow = has_allow = has_crawl_delay = has_ai_directive = False
        
        except requests.RequestException as e:
            status = "network_error"
            content = str(e)
            content_length = 0
            non_empty_lines = []
            has_user_agent = has_disallow = has_allow = has_crawl_delay = has_ai_directive = False
        
        # Évaluation de l'efficacité actuelle
        current_effectiveness = (
            "Très limitée" if status == "found_and_configured"
            else "Nulle" if status == "found_but_minimal"
            else "Sans objet"
        )
        
        return {
            "llms_txt_url": llms_txt_url,
            "status": status,
            "content_length": content_length,
            "lines_count": len(non_empty_lines),
            "has_user_agent_directive": has_user_agent,
            "has_disallow_directive": has_disallow,
            "has_allow_directive": has_allow,
            "has_crawl_delay": has_crawl_delay,
            "has_ai_specific_directives": has_ai_directive,
            "current_effectiveness": current_effectiveness,
            "implementation_recommendation": (
                "Le fichier llms.txt est une initiative expérimentale avec une efficacité "
                "actuellement très limitée. Sa mise en place peut être considérée comme "
                "une préparation pour l'avenir, mais ne doit pas être prioritaire."
            ),
            "sample_content": content[:200] + "..." if len(content) > 200 else content
        }
    
    def _get_ssr_recommendations(self, score: float, frameworks: List[str]) -> List[str]:
        """Génère des recommandations pour l'amélioration SSR."""
        recommendations = []
        
        if score < 60:
            recommendations.append("Implementer le Server-Side Rendering (SSR) ou la génération statique")
            
        if frameworks:
            if 'React' in frameworks:
                recommendations.append("Considérer Next.js pour le SSR avec React")
            if 'Vue' in frameworks:
                recommendations.append("Utiliser Nuxt.js pour l'optimisation Vue SSR")
            if 'Angular' in frameworks:
                recommendations.append("Activer Angular Universal pour le rendu serveur")
        
        if score < 80:
            recommendations.append("Optimiser le contenu critique above-the-fold")
            recommendations.append("Minimiser le JavaScript bloquant")
        
        return recommendations
    
    def _get_year_recommendations(self, title_has_year: bool, desc_has_year: bool) -> List[str]:
        """Génère des recommandations pour l'optimisation temporelle."""
        recommendations = []
        
        if not title_has_year:
            recommendations.append(f"Ajouter '{self.current_year}' dans le titre de la page")
        
        if not desc_has_year:
            recommendations.append(f"Inclure '{self.current_year}' dans la meta description")
        
        recommendations.append("Mettre à jour régulièrement les dates dans le contenu")
        recommendations.append("Utiliser des expressions comme 'dernière mise à jour' avec l'année courante")
        
        return recommendations
    
    def _evaluate_schema_relevance(self, schema_type: str, data: dict) -> float:
        """Évalue la pertinence et la complétude d'un schéma."""
        relevance_score = 50  # Base
        
        # Bonus pour les schémas très pertinents
        high_value_schemas = [
            'Article', 'NewsArticle', 'BlogPosting', 'WebPage',
            'Organization', 'LocalBusiness', 'Product', 'Service',
            'FAQ', 'HowTo', 'Recipe', 'Event'
        ]
        
        if schema_type in high_value_schemas:
            relevance_score += 30
        
        # Évaluer la complétude des propriétés
        required_props = {
            'Article': ['headline', 'author', 'datePublished'],
            'Organization': ['name', 'url'],
            'Product': ['name', 'description'],
            'LocalBusiness': ['name', 'address', 'telephone']
        }
        
        if schema_type in required_props:
            present_props = sum(1 for prop in required_props[schema_type] if prop in data)
            completeness = present_props / len(required_props[schema_type])
            relevance_score += completeness * 20
        
        return min(relevance_score, 100)
    
    def _recommend_missing_schemas(self, soup: BeautifulSoup, existing: List[str]) -> List[str]:
        """Recommande des schémas manquants basés sur le contenu."""
        recommendations = []
        
        # Analyser le contenu pour suggérer des schémas
        if soup.find('article') and 'Article' not in existing:
            recommendations.append('Article')
        
        if soup.find_all(['ul', 'ol']) and 'FAQ' not in existing:
            if any('?' in li.get_text() for li in soup.find_all('li')[:5]):
                recommendations.append('FAQPage')
        
        if re.search(r'comment|étape|instruction', soup.get_text(), re.I) and 'HowTo' not in existing:
            recommendations.append('HowTo')
        
        if 'Organization' not in existing and 'LocalBusiness' not in existing:
            recommendations.append('Organization')
        
        return recommendations


def analyze_enhanced_structure(url: str, soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Fonction principale pour l'analyse de structure améliorée.
    
    Args:
        url: URL de la page analysée
        soup: Objet BeautifulSoup de la page
    
    Returns:
        Dict contenant toutes les analyses de structure améliorées
    """
    
    analyzer = EnhancedStructureAnalyzer()
    
    print("🏗️  Analyse de structure améliorée...")
    
    # Exécuter toutes les analyses
    results = {
        "2.1_ssr_javascript": analyzer.check_ssr_javascript_rendering(url, soup),
        "2.2_year_metadata": analyzer.analyze_year_presence_metadata(soup),
        "2.3_structured_data_relevance": analyzer.analyze_structured_data_relevance(soup),
        "2.4_llms_txt_status": analyzer.check_llms_txt_status(url)
    }
    
    return results


if __name__ == "__main__":
    # Test simple
    test_html = """
    <html>
    <head>
        <title>Guide Crédit Immobilier 2025 - MeilleurTaux</title>
        <meta name="description" content="Découvrez les meilleures offres de crédit immobilier 2025. Comparaison des taux et conseils d'experts.">
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Guide Crédit 2025",
            "author": "Expert Finance",
            "datePublished": "2025-01-01"
        }
        </script>
    </head>
    <body>
        <h1>Crédit immobilier 2025</h1>
        <article>
            <p>Les taux d'intérêt en 2025...</p>
        </article>
    </body>
    </html>
    """
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(test_html, 'html.parser')
    url = "https://example.com/test"
    
    results = analyze_enhanced_structure(url, soup)
    
    print("Résultats d'analyse structure:")
    for key, value in results.items():
        print(f"{key}: {value}")