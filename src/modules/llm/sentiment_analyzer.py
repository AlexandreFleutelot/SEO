# -*- coding: utf-8 -*-
"""
Sentiment Analyzer - Analyse de sentiment avancée avec LLM
Module spécialisé dans l'analyse de sentiment pour marques et sources
"""

import re
from typing import Dict, List, Any, Optional
from .llm_providers import LLMProviderManager


class SentimentAnalyzer:
    """Analyseur de sentiment utilisant les LLM pour une analyse sophistiquée"""
    
    def __init__(self, llm_manager: LLMProviderManager):
        self.llm_manager = llm_manager
        
        # Templates de prompts optimisés
        self.prompt_templates = {
            'marques': self._get_prompt_template_marques(),
            'sources': self._get_prompt_template_sources()
        }
    
    
    def analyser_sentiment_marques(self, provider_name: str, texte_complet: str, 
                                 marques: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Analyse le sentiment exprimé envers chaque marque
        
        Args:
            provider_name: Nom du provider LLM à utiliser
            texte_complet: Texte complet de la réponse originale
            marques: Liste des marques détectées
            
        Returns:
            dict: Sentiments analysés par marque
        """
        print(f"    🎭 Analyse sentiment marques ({provider_name})...")
        
        if not marques:
            return {}
        
        # Construire le prompt spécialisé pour les marques
        prompt = self._construire_prompt_marques(texte_complet, marques)
        
        # Query le LLM
        reponse = self.llm_manager.query_provider(provider_name, prompt)
        
        if reponse:
            sentiments = self._parser_sentiment_marques(reponse, marques)
            print(f"    ✅ {len(sentiments)} sentiments marques analysés")
            return sentiments
        else:
            print(f"    ⚠️ Échec analyse sentiment marques")
            return self._generer_sentiments_fallback(marques, 'marque')
    
    
    def analyser_sentiment_sources(self, provider_name: str, texte_complet: str, 
                                 sources: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Analyse le sentiment exprimé envers chaque source
        
        Args:
            provider_name: Nom du provider LLM à utiliser
            texte_complet: Texte complet de la réponse originale
            sources: Liste des sources détectées
            
        Returns:
            dict: Sentiments analysés par source
        """
        print(f"    🎭 Analyse sentiment sources ({provider_name})...")
        
        if not sources:
            return {}
        
        # Construire le prompt spécialisé pour les sources
        prompt = self._construire_prompt_sources(texte_complet, sources)
        
        # Query le LLM
        reponse = self.llm_manager.query_provider(provider_name, prompt)
        
        if reponse:
            sentiments = self._parser_sentiment_sources(reponse, sources)
            print(f"    ✅ {len(sentiments)} sentiments sources analysés")
            return sentiments
        else:
            print(f"    ⚠️ Échec analyse sentiment sources")
            return self._generer_sentiments_fallback(sources, 'source')
    
    
    def analyser_sentiment_batch(self, provider_name: str, texte_complet: str,
                               marques: List[Dict[str, Any]], 
                               sources: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Analyse en batch marques et sources dans une seule requête LLM
        
        Args:
            provider_name: Provider LLM à utiliser
            texte_complet: Texte complet à analyser
            marques: Marques détectées
            sources: Sources détectées
            
        Returns:
            dict: Résultats d'analyse combinés
        """
        print(f"    🎭 Analyse sentiment batch ({provider_name})...")
        
        if not marques and not sources:
            return {'marques': {}, 'sources': {}}
        
        # Construire un prompt combiné
        prompt = self._construire_prompt_batch(texte_complet, marques, sources)
        
        # Query le LLM
        reponse = self.llm_manager.query_provider(provider_name, prompt)
        
        if reponse:
            resultats = self._parser_sentiment_batch(reponse, marques, sources)
            print(f"    ✅ Analyse batch terminée")
            return resultats
        else:
            print(f"    ⚠️ Échec analyse batch")
            return {
                'marques': self._generer_sentiments_fallback(marques, 'marque'),
                'sources': self._generer_sentiments_fallback(sources, 'source')
            }
    
    
    def _get_prompt_template_marques(self) -> str:
        """Template de prompt optimisé pour l'analyse de marques"""
        return """
Tu es un expert en analyse de perception de marques et de réputation d'entreprises.

Analyse le sentiment et la perception exprimés dans le texte suivant envers chaque marque/entreprise mentionnée.

TEXTE À ANALYSER:
{texte_complet}

MARQUES À ANALYSER:
{liste_marques}

Pour chaque marque, évalue précisément:

🎯 SENTIMENT GLOBAL: positif, négatif, neutre
🔬 CONFIANCE: score 0-100 sur ta certitude
💡 JUSTIFICATION: phrase expliquant ton analyse
🏢 PERCEPTION BUSINESS: leader/challenger/innovant/traditionnel/etc.
📊 RECOMMANDATION: recommandée/mentionnée/critiquée

FORMAT DE RÉPONSE OBLIGATOIRE:
=== ANALYSE MARQUES ===
Marque: [Nom exact]
Sentiment: [positif/négatif/neutre]
Confiance: [0-100]
Justification: [Explication détaillée]
Perception: [Positionnement perçu]
Recommandation: [Niveau de recommandation]
---
[Répéter pour chaque marque]

Sois précis et nuancé dans ton analyse.
"""
    
    
    def _get_prompt_template_sources(self) -> str:
        """Template de prompt optimisé pour l'analyse de sources"""
        return """
Tu es un expert en évaluation de sources d'information et de crédibilité.

Analyse le sentiment et la fiabilité exprimés dans le texte suivant envers chaque source mentionnée.

TEXTE À ANALYSER:
{texte_complet}

SOURCES À ANALYSER:
{liste_sources}

Pour chaque source, évalue:

🎯 SENTIMENT: positif, négatif, neutre (comment elle est présentée)
🔬 CONFIANCE: score 0-100 sur ta certitude
💡 JUSTIFICATION: pourquoi ce sentiment
📊 FIABILITÉ PERÇUE: très fiable/fiable/moyenne/douteuse
🎖️ AUTORITÉ: haute/moyenne/faible (expertise perçue)

FORMAT DE RÉPONSE OBLIGATOIRE:
=== ANALYSE SOURCES ===
Source: [Nom exact]
Sentiment: [positif/négatif/neutre]
Confiance: [0-100]
Justification: [Explication]
Fiabilité: [Niveau perçu]
Autorité: [Niveau d'expertise]
---
[Répéter pour chaque source]

Base ton analyse sur la façon dont la source est présentée dans le texte.
"""
    
    
    def _construire_prompt_marques(self, texte: str, marques: List[Dict[str, Any]]) -> str:
        """Construit le prompt d'analyse pour les marques"""
        liste_marques = "\n".join([f"- {marque['nom']}" for marque in marques])
        
        return self.prompt_templates['marques'].format(
            texte_complet=texte[:2000],  # Limiter pour éviter les tokens
            liste_marques=liste_marques
        )
    
    
    def _construire_prompt_sources(self, texte: str, sources: List[Dict[str, Any]]) -> str:
        """Construit le prompt d'analyse pour les sources"""
        liste_sources = "\n".join([f"- {source['nom']} ({source['url']})" for source in sources])
        
        return self.prompt_templates['sources'].format(
            texte_complet=texte[:2000],
            liste_sources=liste_sources
        )
    
    
    def _construire_prompt_batch(self, texte: str, marques: List[Dict[str, Any]], 
                               sources: List[Dict[str, Any]]) -> str:
        """Construit un prompt combiné pour analyse batch"""
        
        prompt_batch = """
Tu es un expert en analyse de sentiment et d'opinion. Analyse le texte suivant pour évaluer:
1. Le sentiment envers les marques/entreprises mentionnées
2. La perception des sources d'information citées

TEXTE À ANALYSER:
{texte_complet}

MARQUES À ANALYSER:
{liste_marques}

SOURCES À ANALYSER:  
{liste_sources}

FORMAT DE RÉPONSE:

🏢 ANALYSE MARQUES:
Marque: [Nom]
Sentiment: [positif/négatif/neutre]
Confiance: [0-100]
Justification: [Explication]
Perception: [Positionnement]
---

🔗 ANALYSE SOURCES:
Source: [Nom]
Sentiment: [positif/négatif/neutre]
Confiance: [0-100]
Justification: [Explication]
Fiabilité: [Niveau]
---

Répète ce format pour chaque entité.
"""
        
        liste_marques = "\n".join([f"- {marque['nom']}" for marque in marques]) if marques else "Aucune marque détectée"
        liste_sources = "\n".join([f"- {source['nom']}" for source in sources]) if sources else "Aucune source détectée"
        
        return prompt_batch.format(
            texte_complet=texte[:1500],
            liste_marques=liste_marques,
            liste_sources=liste_sources
        )
    
    
    def _parser_sentiment_marques(self, reponse_llm: str, marques: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Parse une réponse d'analyse de sentiment pour marques"""
        sentiments = {}
        
        # Pattern pour extraire les analyses de marques
        pattern = (r'Marque:\s*([^\n]+)\s*\n'
                  r'Sentiment:\s*([^\n]+)\s*\n'
                  r'Confiance:\s*(\d+)\s*\n'
                  r'Justification:\s*([^\n]+)\s*\n'
                  r'(?:Perception:\s*([^\n]+)\s*\n)?'
                  r'(?:Recommandation:\s*([^\n]+)\s*\n)?')
        
        for match in re.finditer(pattern, reponse_llm, re.MULTILINE | re.IGNORECASE):
            nom_marque = match.group(1).strip()
            sentiment = self._normaliser_sentiment(match.group(2).strip())
            confiance = self._normaliser_confiance(match.group(3))
            justification = match.group(4).strip()
            perception = match.group(5).strip() if match.group(5) else ""
            recommandation = match.group(6).strip() if match.group(6) else ""
            
            # Trouver la marque correspondante
            marque_correspondante = self._trouver_entite_correspondante(nom_marque, marques)
            
            if marque_correspondante:
                cle_marque = marque_correspondante['nom']
                
                sentiments[cle_marque] = {
                    'sentiment': sentiment,
                    'confiance': confiance,
                    'justification': justification,
                    'perception_business': perception,
                    'niveau_recommandation': recommandation,
                    'methode_analyse': 'llm_specialise',
                    'entite_originale': nom_marque
                }
        
        return sentiments
    
    
    def _parser_sentiment_sources(self, reponse_llm: str, sources: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Parse une réponse d'analyse de sentiment pour sources"""
        sentiments = {}
        
        # Pattern pour extraire les analyses de sources
        pattern = (r'Source:\s*([^\n]+)\s*\n'
                  r'Sentiment:\s*([^\n]+)\s*\n'
                  r'Confiance:\s*(\d+)\s*\n'
                  r'Justification:\s*([^\n]+)\s*\n'
                  r'(?:Fiabilité:\s*([^\n]+)\s*\n)?'
                  r'(?:Autorité:\s*([^\n]+)\s*\n)?')
        
        for match in re.finditer(pattern, reponse_llm, re.MULTILINE | re.IGNORECASE):
            nom_source = match.group(1).strip()
            sentiment = self._normaliser_sentiment(match.group(2).strip())
            confiance = self._normaliser_confiance(match.group(3))
            justification = match.group(4).strip()
            fiabilite = match.group(5).strip() if match.group(5) else ""
            autorite = match.group(6).strip() if match.group(6) else ""
            
            # Trouver la source correspondante
            source_correspondante = self._trouver_entite_correspondante(nom_source, sources)
            
            if source_correspondante:
                cle_source = source_correspondante['nom']
                
                sentiments[cle_source] = {
                    'sentiment': sentiment,
                    'confiance': confiance,
                    'justification': justification,
                    'fiabilite_percue': fiabilite,
                    'niveau_autorite': autorite,
                    'methode_analyse': 'llm_specialise',
                    'entite_originale': nom_source,
                    'url': source_correspondante.get('url', '')
                }
        
        return sentiments
    
    
    def _parser_sentiment_batch(self, reponse_llm: str, marques: List[Dict[str, Any]], 
                              sources: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Parse une réponse d'analyse batch"""
        
        # Séparer les sections marques et sources
        section_marques = self._extraire_section(reponse_llm, r'🏢\s*ANALYSE MARQUES:', r'🔗\s*ANALYSE SOURCES:')
        section_sources = self._extraire_section(reponse_llm, r'🔗\s*ANALYSE SOURCES:', r'$')
        
        # Parser chaque section
        sentiments_marques = {}
        sentiments_sources = {}
        
        if section_marques:
            sentiments_marques = self._parser_sentiment_marques(section_marques, marques)
        
        if section_sources:
            sentiments_sources = self._parser_sentiment_sources(section_sources, sources)
        
        return {
            'marques': sentiments_marques,
            'sources': sentiments_sources
        }
    
    
    def _normaliser_sentiment(self, sentiment_brut: str) -> str:
        """Normalise un sentiment en format standard"""
        sentiment_lower = sentiment_brut.lower().strip()
        
        if any(mot in sentiment_lower for mot in ['positif', 'positive', 'favorable', 'bon']):
            return 'positif'
        elif any(mot in sentiment_lower for mot in ['négatif', 'negative', 'défavorable', 'mauvais', 'critique']):
            return 'négatif'
        else:
            return 'neutre'
    
    
    def _normaliser_confiance(self, confiance_brut: str) -> int:
        """Normalise un score de confiance"""
        try:
            confiance = int(confiance_brut)
            return max(0, min(100, confiance))  # Borner entre 0 et 100
        except ValueError:
            return 50  # Valeur par défaut
    
    
    def _trouver_entite_correspondante(self, nom_recherche: str, entites: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Trouve l'entité correspondant au nom recherché"""
        nom_lower = nom_recherche.lower()
        
        # Recherche exacte d'abord
        for entite in entites:
            if entite['nom'].lower() == nom_lower:
                return entite
        
        # Recherche de correspondance partielle
        for entite in entites:
            nom_entite = entite['nom'].lower()
            if (nom_lower in nom_entite or nom_entite in nom_lower or
                self._similarite_noms(nom_lower, nom_entite) > 0.8):
                return entite
        
        return None
    
    
    def _similarite_noms(self, nom1: str, nom2: str) -> float:
        """Calcule la similarité entre deux noms (simple)"""
        # Algorithme simple de similarité basé sur les mots communs
        mots1 = set(nom1.split())
        mots2 = set(nom2.split())
        
        if not mots1 or not mots2:
            return 0.0
        
        intersection = len(mots1 & mots2)
        union = len(mots1 | mots2)
        
        return intersection / union if union > 0 else 0.0
    
    
    def _extraire_section(self, texte: str, pattern_debut: str, pattern_fin: str) -> str:
        """Extrait une section du texte"""
        start_match = re.search(pattern_debut, texte, re.IGNORECASE)
        if not start_match:
            return ""
        
        start = start_match.end()
        
        end_match = re.search(pattern_fin, texte[start:], re.IGNORECASE)
        if end_match:
            end = start + end_match.start()
            return texte[start:end].strip()
        else:
            return texte[start:].strip()
    
    
    def _generer_sentiments_fallback(self, entites: List[Dict[str, Any]], type_entite: str) -> Dict[str, Dict[str, Any]]:
        """Génère des sentiments par défaut en cas d'échec LLM"""
        sentiments_fallback = {}
        
        for entite in entites:
            nom = entite['nom']
            sentiments_fallback[nom] = {
                'sentiment': 'neutre',
                'confiance': 30,  # Faible confiance car fallback
                'justification': f'Analyse fallback pour {type_entite}',
                'methode_analyse': 'fallback_basic',
                'entite_originale': nom
            }
            
            # Ajouter des champs spécifiques selon le type
            if type_entite == 'marque':
                sentiments_fallback[nom].update({
                    'perception_business': 'inconnue',
                    'niveau_recommandation': 'neutre'
                })
            elif type_entite == 'source':
                sentiments_fallback[nom].update({
                    'fiabilite_percue': 'moyenne',
                    'niveau_autorite': 'moyenne',
                    'url': entite.get('url', '')
                })
        
        return sentiments_fallback
    
    
    def calculer_sentiment_majoritaire(self, sentiments_multi_provider: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcule le sentiment majoritaire à partir de plusieurs providers
        
        Args:
            sentiments_multi_provider: Sentiments de plusieurs providers
            
        Returns:
            dict: Sentiment consolidé avec métadonnées
        """
        if not sentiments_multi_provider:
            return {'sentiment': 'inconnu', 'confiance': 0}
        
        # Compter les sentiments
        compteur = {'positif': 0, 'neutre': 0, 'négatif': 0}
        confiances = {'positif': [], 'neutre': [], 'négatif': []}
        
        for provider_data in sentiments_multi_provider.values():
            sentiment = provider_data.get('sentiment', 'neutre')
            confiance = provider_data.get('confiance', 50)
            
            if sentiment in compteur:
                compteur[sentiment] += 1
                confiances[sentiment].append(confiance)
        
        # Trouver le sentiment majoritaire
        sentiment_majoritaire = max(compteur.items(), key=lambda x: x[1])
        
        # Calculer la confiance moyenne pour ce sentiment
        confiances_sentiment = confiances[sentiment_majoritaire[0]]
        confiance_moyenne = sum(confiances_sentiment) / len(confiances_sentiment) if confiances_sentiment else 50
        
        return {
            'sentiment': sentiment_majoritaire[0],
            'votes': sentiment_majoritaire[1],
            'total_providers': len(sentiments_multi_provider),
            'consensus_score': sentiment_majoritaire[1] / len(sentiments_multi_provider),
            'confiance_moyenne': round(confiance_moyenne),
            'distribution': compteur
        }