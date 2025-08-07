# -*- coding: utf-8 -*-
"""
enhanced_content.py

Analyses de contenu améliorées basées sur les recommandations TODO.md
pour l'optimisation LLM et GEO (Generative Engine Optimization).

Nouvelles analyses :
1. Densité informationnelle et couverture exhaustive des entités
2. Qualité des micro-blocs atomiques et autosuffisants
3. Détection du "ton IA-généré" et du "blabla"
4. Présence et valorisation des données originales/internes
5. Cohérence NAP (Nom, Adresse, Téléphone) pour les entités
"""

import spacy
import re
import statistics
from collections import Counter
from typing import Dict, Any, List, Tuple
from bs4 import BeautifulSoup
import datefinder
from datetime import datetime


class EnhancedContentAnalyzer:
    """Analyseur de contenu amélioré pour l'optimisation LLM."""
    
    def __init__(self):
        try:
            self.nlp = spacy.load("fr_core_news_sm")
        except OSError:
            print("⚠️  Modèle spaCy français non trouvé. Certaines analyses seront limitées.")
            self.nlp = None
    
    def analyze_informational_density(self, text: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        1.1 Densité informationnelle et couverture exhaustive des entités.
        Évalue la profondeur et l'exhaustivité de la couverture thématique.
        """
        if not self.nlp:
            return {"error": "Modèle spaCy non disponible"}
        
        # Limiter le texte pour spaCy
        text_limited = text[:1000000] if len(text) > 1000000 else text
        doc = self.nlp(text_limited)
        
        # Extraction avancée des entités
        entities_by_type = {}
        entity_relations = []
        
        for ent in doc.ents:
            if ent.label_ not in entities_by_type:
                entities_by_type[ent.label_] = []
            entities_by_type[ent.label_].append(ent.text)
        
        # Analyser les relations entre entités
        for sent in doc.sents:
            sent_entities = [ent for ent in sent.ents]
            if len(sent_entities) >= 2:
                entity_relations.append([ent.text for ent in sent_entities])
        
        # Détecter les concepts clés et leur couverture
        concept_coverage = self._analyze_concept_coverage(text, entities_by_type)
        
        # Évaluer la profondeur thématique
        thematic_depth = self._evaluate_thematic_depth(doc, entities_by_type)
        
        # Vérifier la présence de liens vers sources d'autorité
        authority_links = self._detect_authority_links(soup)
        
        return {
            "total_entities": len(doc.ents),
            "entities_by_type": {k: len(set(v)) for k, v in entities_by_type.items()},
            "entity_relations_count": len(entity_relations),
            "concept_coverage_score": concept_coverage,
            "thematic_depth_score": thematic_depth,
            "authority_links": authority_links,
            "informational_density_score": self._calculate_density_score(
                len(doc.ents), len(entity_relations), concept_coverage, len(authority_links)
            )
        }
    
    def analyze_atomic_blocks(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        1.2 Qualité des micro-blocs atomiques et autosuffisants.
        Évalue si chaque section peut "vivre seule" et être comprise hors contexte.
        """
        
        # Identifier les blocs de contenu atomiques
        atomic_blocks = []
        
        # Questions/réponses
        qa_patterns = [
            r"(?:Q\s*:|Question\s*:)(.*?)(?:R\s*:|Réponse\s*:)(.*?)(?=Q\s*:|Question\s*:|$)",
            r"(?:Qu'est-ce que|Comment|Pourquoi|Quand)(.*?)\?",
        ]
        
        for pattern in qa_patterns:
            matches = re.findall(pattern, soup.get_text(), re.DOTALL | re.IGNORECASE)
            atomic_blocks.extend(matches)
        
        # Définitions (phrases commençant par "Le/La/Les [terme] est/sont")
        definition_pattern = r"(?:Le|La|Les)\s+([A-Za-zÀ-ÿ\s]+)\s+(?:est|sont)\s+([^.!?]+[.!?])"
        definitions = re.findall(definition_pattern, soup.get_text())
        atomic_blocks.extend(definitions)
        
        # Blocs "Key Takeaways" / Points clés
        key_elements = soup.find_all(['div', 'section', 'aside'], 
                                   class_=re.compile(r'key|takeaway|summary|highlight', re.I))
        takeaways = [elem.get_text().strip() for elem in key_elements if elem.get_text().strip()]
        
        # Listes à puces auto-suffisantes
        lists = soup.find_all(['ul', 'ol'])
        self_sufficient_lists = []
        for lst in lists:
            list_text = lst.get_text().strip()
            # Une liste est auto-suffisante si elle contient des phrases complètes
            if len(re.findall(r'[.!?]', list_text)) >= len(lst.find_all('li')) * 0.7:
                self_sufficient_lists.append(list_text[:200] + "...")
        
        # Évaluer la qualité des blocs atomiques
        atomic_quality_score = self._evaluate_atomic_quality(
            len(definitions), len(takeaways), len(self_sufficient_lists)
        )
        
        return {
            "qa_pairs_detected": len([m for pattern in qa_patterns 
                                    for m in re.findall(pattern, soup.get_text(), re.DOTALL | re.IGNORECASE)]),
            "definitions_detected": len(definitions),
            "key_takeaways_blocks": len(takeaways),
            "self_sufficient_lists": len(self_sufficient_lists),
            "atomic_blocks_total": len(atomic_blocks) + len(takeaways) + len(self_sufficient_lists),
            "atomic_quality_score": atomic_quality_score,
            "sample_definitions": definitions[:3],  # Échantillon pour debug
            "sample_takeaways": takeaways[:2] if takeaways else []
        }
    
    def detect_ai_generated_content(self, text: str) -> Dict[str, Any]:
        """
        1.3 Détection du "ton IA-généré" et du "blabla".
        Identifie les formulations stéréotypées et contenus dilués.
        """
        
        # Phrases typiquement IA-générées (patterns français)
        ai_patterns = [
            r"il est important de noter que",
            r"il convient de souligner que",
            r"dans le contexte de",
            r"en conclusion",
            r"pour résumer",
            r"il faut savoir que",
            r"il est essentiel de",
            r"dans cet article, nous allons",
            r"nous explorerons",
            r"plongeons dans",
            r"découvrons ensemble",
            r"explorons les tenants et aboutissants"
        ]
        
        ai_phrase_count = 0
        detected_phrases = []
        
        for pattern in ai_patterns:
            matches = re.findall(pattern, text.lower())
            ai_phrase_count += len(matches)
            if matches:
                detected_phrases.append(pattern)
        
        # Détecter les répétitions excessives
        sentences = re.split(r'[.!?]+', text)
        sentence_similarities = self._detect_repetitive_patterns(sentences)
        
        # Analyser la densité informationnelle vs "blabla"
        info_density = self._calculate_info_vs_fluff_ratio(text)
        
        # Détecter les transitions mécaniques
        mechanical_transitions = [
            "par ailleurs", "en outre", "de plus", "également", "en effet",
            "ainsi", "donc", "c'est pourquoi", "par conséquent"
        ]
        
        transition_count = sum(len(re.findall(transition, text.lower())) 
                             for transition in mechanical_transitions)
        
        # Score de naturalité (0-100, plus c'est haut, plus c'est naturel)
        naturalness_score = max(100 - (ai_phrase_count * 5) - (sentence_similarities * 10) 
                              - (transition_count * 2), 0)
        
        return {
            "ai_generated_phrases_count": ai_phrase_count,
            "detected_ai_patterns": detected_phrases,
            "repetitive_patterns_score": sentence_similarities,
            "mechanical_transitions_count": transition_count,
            "info_density_ratio": info_density,
            "naturalness_score": naturalness_score,
            "content_authenticity": "Naturel" if naturalness_score >= 80 
                                  else "Suspect" if naturalness_score >= 50 
                                  else "Probablement IA-généré"
        }
    
    def analyze_original_data_presence(self, text: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        1.4 Présence et valorisation des données originales/internes.
        Évalue la présence de données uniques et vérifiables.
        """
        
        # Détecter les statistiques et pourcentages
        percentage_pattern = r'\d+(?:[,.]?\d+)?%'
        percentages = re.findall(percentage_pattern, text)
        
        # Détecter les chiffres et données numériques
        numeric_data_patterns = [
            r'\d+(?:[,.]?\d+)?\s*(?:millions?|milliards?|milliers?)',
            r'\d+(?:[,.]?\d+)?\s*(?:€|euros?|\$|dollars?)',
            r'\d+(?:[,.]?\d+)?\s*(?:personnes?|utilisateurs?|clients?)',
            r'\d{4}\s*(?:participants?|répondants?|sondés?)'
        ]
        
        numeric_data = []
        for pattern in numeric_data_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            numeric_data.extend(matches)
        
        # Détecter les références à des études/enquêtes internes
        study_patterns = [
            r"selon\s+(?:notre|nos)\s+(?:étude|enquête|baromètre|analyse)",
            r"d'après\s+(?:notre|nos)\s+(?:données|recherches?)",
            r"résultats?\s+de\s+(?:notre|nos)\s+(?:sondage|enquête)",
            r"(?:notre|nos)\s+(?:statistiques?|chiffres?)\s+montrent"
        ]
        
        internal_studies = []
        for pattern in study_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            internal_studies.extend(matches)
        
        # Détecter les témoignages et cas d'usage
        testimonial_patterns = [
            r"témoignage\s+de",
            r"cas\s+(?:client|d'usage|pratique)",
            r"retour\s+d'expérience",
            r"exemple\s+concret"
        ]
        
        testimonials = []
        for pattern in testimonial_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            testimonials.extend(matches)
        
        # Évaluer l'originalité des données
        data_originality_score = self._calculate_data_originality_score(
            len(percentages), len(numeric_data), len(internal_studies), len(testimonials)
        )
        
        # Détecter les dates récentes (indicateur de fraîcheur)
        current_year = datetime.now().year
        dates_found = list(datefinder.find_dates(text))
        recent_dates = [d for d in dates_found if d.year >= current_year - 1]
        
        return {
            "percentage_data_points": len(percentages),
            "numeric_data_points": len(numeric_data),
            "internal_studies_references": len(internal_studies),
            "testimonials_case_studies": len(testimonials),
            "recent_dates_count": len(recent_dates),
            "data_originality_score": data_originality_score,
            "sample_percentages": percentages[:5],
            "sample_numeric_data": numeric_data[:5],
            "sample_internal_refs": internal_studies[:3]
        }
    
    def analyze_nap_consistency(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        1.5 Cohérence NAP (Nom, Adresse, Téléphone) pour les entités.
        Vérifie la cohérence des informations d'entreprise.
        """
        
        # Patterns pour détecter les informations NAP
        phone_patterns = [
            r'(?:\+33|0)[1-9](?:[.\s-]?\d{2}){4}',
            r'\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}'
        ]
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        address_patterns = [
            r'\d+[,\s]+(?:rue|avenue|boulevard|place|impasse|allée)[^,\n]{10,50}',
            r'\d{5}\s+[A-Za-zÀ-ÿ\s-]+(?:,\s*France)?'
        ]
        
        # Extraire les informations
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, soup.get_text()))
        
        emails = re.findall(email_pattern, soup.get_text())
        
        addresses = []
        for pattern in address_patterns:
            addresses.extend(re.findall(pattern, soup.get_text(), re.IGNORECASE))
        
        # Détecter le nom de l'entreprise (à partir du title ou meta)
        company_name = ""
        if soup.title:
            title_text = soup.title.get_text()
            # Extraire le nom après le dernier " - "
            if " - " in title_text:
                company_name = title_text.split(" - ")[-1].strip()
        
        # Vérifier la cohérence dans les données structurées
        schema_data = soup.find_all('script', type='application/ld+json')
        structured_nap = {}
        for script in schema_data:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'name' in data:
                        structured_nap['name'] = data['name']
                    if 'telephone' in data:
                        structured_nap['telephone'] = data['telephone']
                    if 'address' in data:
                        structured_nap['address'] = data['address']
            except:
                pass
        
        return {
            "company_name": company_name,
            "phone_numbers_found": len(set(phones)),
            "email_addresses_found": len(set(emails)),
            "physical_addresses_found": len(set(addresses)),
            "structured_data_nap": bool(structured_nap),
            "nap_consistency_score": self._calculate_nap_score(
                len(set(phones)), len(set(emails)), len(set(addresses)), bool(structured_nap)
            ),
            "sample_phones": list(set(phones))[:2],
            "sample_emails": list(set(emails))[:2],
            "sample_addresses": list(set(addresses))[:2]
        }
    
    def _analyze_concept_coverage(self, text: str, entities: Dict[str, List]) -> float:
        """Analyse la couverture conceptuelle du contenu."""
        if not entities:
            return 0
        
        # Score basé sur la diversité des types d'entités
        entity_diversity = len(entities.keys())
        
        # Score basé sur la richesse des entités par type
        entity_richness = sum(len(set(ents)) for ents in entities.values()) / len(entities)
        
        # Normaliser sur 100
        coverage_score = min((entity_diversity * 10) + (entity_richness * 5), 100)
        return coverage_score
    
    def _evaluate_thematic_depth(self, doc, entities: Dict[str, List]) -> float:
        """Évalue la profondeur thématique du contenu."""
        if not doc or not entities:
            return 0
        
        # Analyser la complexité syntaxique
        complex_sentences = 0
        for sent in doc.sents:
            if len([token for token in sent if token.pos_ in ['VERB', 'NOUN']]) > 5:
                complex_sentences += 1
        
        # Score basé sur la complexité et la richesse des entités
        depth_score = min((complex_sentences / len(list(doc.sents)) * 100) + 
                         (len(entities) * 5), 100)
        return depth_score
    
    def _detect_authority_links(self, soup: BeautifulSoup) -> List[str]:
        """Détecte les liens vers des sources d'autorité."""
        authority_domains = [
            'wikipedia.org', 'gov.fr', 'legifrance.gouv.fr',
            'insee.fr', 'banque-france.fr', 'service-public.fr',
            'amf-france.org', 'cnil.fr', 'economie.gouv.fr'
        ]
        
        authority_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            for domain in authority_domains:
                if domain in href:
                    authority_links.append(href)
                    break
        
        return authority_links
    
    def _calculate_density_score(self, entities: int, relations: int, 
                                coverage: float, authority_links: int) -> float:
        """Calcule le score de densité informationnelle."""
        base_score = min(entities * 2, 50)
        relation_bonus = min(relations * 5, 20)
        coverage_bonus = min(coverage * 0.2, 20)
        authority_bonus = min(authority_links * 5, 10)
        
        return base_score + relation_bonus + coverage_bonus + authority_bonus
    
    def _evaluate_atomic_quality(self, definitions: int, takeaways: int, lists: int) -> float:
        """Évalue la qualité des blocs atomiques."""
        return min((definitions * 15) + (takeaways * 20) + (lists * 10), 100)
    
    def _detect_repetitive_patterns(self, sentences: List[str]) -> float:
        """Détecte les patterns répétitifs dans les phrases."""
        if len(sentences) < 2:
            return 0
        
        # Analyser la similarité entre phrases
        similarities = 0
        for i, sent1 in enumerate(sentences[:10]):  # Limiter pour performance
            for sent2 in sentences[i+1:i+5]:
                if len(sent1.split()) > 3 and len(sent2.split()) > 3:
                    # Simple similarité basée sur les mots communs
                    words1 = set(sent1.lower().split())
                    words2 = set(sent2.lower().split())
                    if len(words1 & words2) / max(len(words1), len(words2)) > 0.5:
                        similarities += 1
        
        return min(similarities * 10, 100)
    
    def _calculate_info_vs_fluff_ratio(self, text: str) -> float:
        """Calcule le ratio information vs "blabla"."""
        # Mots informatifs vs mots de remplissage
        info_words = len(re.findall(r'\b(?:\d+|[A-ZÀ-Ÿ][a-zà-ÿ]{4,})\b', text))
        total_words = len(text.split())
        
        if total_words == 0:
            return 0
        
        return (info_words / total_words) * 100
    
    def _calculate_data_originality_score(self, percentages: int, numeric: int, 
                                        studies: int, testimonials: int) -> float:
        """Calcule le score d'originalité des données."""
        return min((percentages * 5) + (numeric * 3) + (studies * 15) + (testimonials * 10), 100)
    
    def _calculate_nap_score(self, phones: int, emails: int, 
                           addresses: int, structured: bool) -> float:
        """Calcule le score de cohérence NAP."""
        base_score = min((phones * 20) + (emails * 15) + (addresses * 25), 80)
        structured_bonus = 20 if structured else 0
        return base_score + structured_bonus


def analyze_enhanced_content(soup: BeautifulSoup, main_text: str) -> Dict[str, Any]:
    """
    Fonction principale pour l'analyse de contenu améliorée.
    
    Args:
        soup: Objet BeautifulSoup de la page
        main_text: Texte principal extrait
    
    Returns:
        Dict contenant toutes les analyses améliorées
    """
    
    analyzer = EnhancedContentAnalyzer()
    
    print("🔍 Analyse de contenu améliorée...")
    
    # Exécuter toutes les analyses
    results = {
        "1.1_informational_density": analyzer.analyze_informational_density(main_text, soup),
        "1.2_atomic_blocks": analyzer.analyze_atomic_blocks(soup),
        "1.3_ai_generated_detection": analyzer.detect_ai_generated_content(main_text),
        "1.4_original_data": analyzer.analyze_original_data_presence(main_text, soup),
        "1.5_nap_consistency": analyzer.analyze_nap_consistency(soup)
    }
    
    return results


if __name__ == "__main__":
    # Test simple
    test_html = """
    <html>
    <head><title>Test - Ma Société</title></head>
    <body>
        <h1>Analyse des taux immobiliers 2025</h1>
        <p>Selon notre étude, 75% des emprunteurs préfèrent les taux fixes. 
           Notre baromètre montre une augmentation de 2,3% cette année.</p>
        <p>Téléphone: 01 23 45 67 89</p>
        <p>Email: contact@masociete.fr</p>
        <p>Adresse: 123 rue de la Paix, 75001 Paris</p>
    </body>
    </html>
    """
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(test_html, 'html.parser')
    text = soup.get_text()
    
    results = analyze_enhanced_content(soup, text)
    
    print("Résultats d'analyse:")
    for key, value in results.items():
        print(f"{key}: {value}")