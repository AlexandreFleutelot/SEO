# -*- coding: utf-8 -*-
"""
Multi-LLM Analyzer - Orchestrateur principal refactorisé
Analyse intelligente avec plusieurs LLM pour extraction d'informations et sentiment
"""

from datetime import datetime
from typing import Dict, List, Any, Optional

from .llm_providers import LLMProviderManager
from .url_extractor import URLExtractor
from .information_extractor import InformationExtractor
from .sentiment_analyzer import SentimentAnalyzer
from .report_generator import MultiLLMReportGenerator


class MultiLLMAnalyzer:
    """
    Analyseur Multi-LLM refactorisé - Orchestrateur principal
    Coordonne tous les modules spécialisés pour une analyse complète
    """
    
    def __init__(self):
        """Initialise l'analyseur avec tous ses composants"""
        print("🤖 Initialisation Multi-LLM Analyzer v2.0...")
        
        # Initialiser les composants
        self.llm_manager = LLMProviderManager()
        self.url_extractor = URLExtractor(self.llm_manager)
        self.info_extractor = InformationExtractor()
        self.sentiment_analyzer = SentimentAnalyzer(self.llm_manager)
        self.report_generator = MultiLLMReportGenerator()
        
        if not self.llm_manager.has_available_providers():
            print("❌ Aucun provider LLM disponible")
            raise RuntimeError("Pas de clés API LLM configurées")
    
    
    def analyser_question_complete(self, question: str, contexte: str = "") -> Dict[str, Any]:
        """
        Analyse complète d'une question avec tous les LLM disponibles
        
        Args:
            question: Question à analyser
            contexte: Contexte optionnel
            
        Returns:
            dict: Résultats complets de l'analyse
        """
        print("🚀 DÉBUT ANALYSE MULTI-LLM v2.0")
        print(f"❓ Question: {question}")
        print(f"📝 Contexte: {contexte[:100]}..." if len(contexte) > 100 else f"📝 Contexte: {contexte}")
        print("=" * 80)
        
        # Initialiser la structure des résultats
        resultats = {
            'question': question,
            'contexte': contexte,
            'timestamp': datetime.now().isoformat(),
            'providers_utilises': [],
            'reponses_brutes': {},
            'marques_detectees': {},
            'sources_extraites': {},
            'citations_ordonnees': {},
            'sentiment_marques': {},
            'sentiment_sources': {},
            'rapport_urls': {},
            'statistiques': {},
            'rapport_consolide': {}
        }
        
        try:
            # === ÉTAPE 1: COLLECTE DES RÉPONSES LLM ===
            print("📥 COLLECTE DES RÉPONSES")
            print("-" * 40)
            
            prompt = self._construire_prompt_extraction(question, contexte)
            reponses = self.llm_manager.query_all_providers(prompt)
            
            resultats['reponses_brutes'] = reponses
            resultats['providers_utilises'] = [p for p, r in reponses.items() if r is not None]
            
            if not resultats['providers_utilises']:
                print("❌ Aucune réponse LLM obtenue")
                return resultats
            
            # === ÉTAPE 2: EXTRACTION DES INFORMATIONS ===
            print("\n📊 EXTRACTION DES INFORMATIONS")
            print("-" * 40)
            
            for provider_name in resultats['providers_utilises']:
                reponse_text = reponses[provider_name]
                print(f"🎯 Extraction {provider_name.upper()}...")
                
                # Extraire marques
                marques = self.info_extractor.extraire_marques_completes(reponse_text)
                resultats['marques_detectees'][provider_name] = marques
                
                # Extraire URLs/sources
                sources = self.url_extractor.extraire_urls_depuis_reponse(
                    provider_name, question, reponse_text
                )
                resultats['sources_extraites'][provider_name] = sources
                
                # Extraire ordre des citations
                citations = self.info_extractor.extraire_ordre_citations(reponse_text)
                resultats['citations_ordonnees'][provider_name] = citations
                
                print(f"  ✅ {provider_name}: {len(marques)} marques, {len(sources)} sources")
            
            # === ÉTAPE 3: ANALYSE DE SENTIMENT ===
            print("\n🎭 ANALYSE DE SENTIMENT")
            print("-" * 35)
            
            for provider_name in resultats['providers_utilises']:
                reponse_text = reponses[provider_name]
                marques = resultats['marques_detectees'][provider_name]
                sources = resultats['sources_extraites'][provider_name]
                
                print(f"🎭 Sentiment {provider_name.upper()}...")
                
                # Analyse de sentiment batch (plus efficace)
                sentiments = self.sentiment_analyzer.analyser_sentiment_batch(
                    provider_name, reponse_text, marques, sources
                )
                
                resultats['sentiment_marques'][provider_name] = sentiments.get('marques', {})
                resultats['sentiment_sources'][provider_name] = sentiments.get('sources', {})
            
            # === ÉTAPE 4: CONSOLIDATION ET CONSENSUS ===
            print("\n🔄 CONSOLIDATION")
            print("-" * 25)
            
            resultats['rapport_consolide'] = self._consolider_resultats_v2(resultats)
            resultats['statistiques'] = self._calculer_statistiques_v2(resultats)
            resultats['rapport_urls'] = self.url_extractor.generer_rapport_urls(
                resultats['sources_extraites']
            )
            
            print("✅ Consolidation terminée")
            
            # === ÉTAPE 5: RÉSUMÉ ===
            self._afficher_resume_analyse(resultats)
            
        except Exception as e:
            print(f"❌ ERREUR CRITIQUE: {e}")
            resultats['erreur_critique'] = str(e)
        
        return resultats
    
    
    def generer_rapport_complet(self, resultats: Dict[str, Any], 
                              nom_fichier: Optional[str] = None) -> str:
        """
        Génère un rapport JSON complet
        
        Args:
            resultats: Résultats de l'analyse
            nom_fichier: Nom du fichier (optionnel)
            
        Returns:
            str: Chemin du rapport généré
        """
        return self.report_generator.generer_rapport_complet(resultats, nom_fichier)
    
    
    def _construire_prompt_extraction(self, question: str, contexte: str = "") -> str:
        """Construit un prompt optimisé pour l'extraction d'informations"""
        
        prompt = f"""
Tu es un expert en recherche documentaire et analyse comparative. 

QUESTION: {question}
{f"CONTEXTE: {contexte}" if contexte else ""}

🎯 MISSION CRITIQUE: Même si tes données s'arrêtent à une certaine date, tu DOIS fournir une réponse complète avec des sources vérifiables. Les URLs que tu recommandes n'ont pas besoin d'être parfaitement à jour - recommande les sites de référence que tu CONNAIS pour ce domaine.

📋 FORMAT DE RÉPONSE OBLIGATOIRE:

[Ta réponse complète et détaillée à la question...]

🏷️ MARQUES/ENTREPRISES CITÉES:
1. [Nom exact de la marque] - [Description et positionnement]
2. [Autre marque] - [Ses spécificités]
[etc. - liste toutes les marques mentionnées]

🔗 SOURCES ET RÉFÉRENCES OBLIGATOIRES:
Tu DOIS absolument fournir des URLs de sites que tu connais, même si l'information n'est pas de 2024:

Source: [Nom précis du site web]
URL: https://www.exemple-complet.com/section-pertinente
Type: [Site officiel/Média/Institution/Comparateur]
Fiabilité: [Très élevée/Élevée/Moyenne]
Pourquoi: [Justification de la fiabilité]

Source: [Deuxième source]
URL: https://www.autre-domaine.fr/page-specifique
Type: [Site officiel/Média/Institution/Comparateur]
Fiabilité: [Niveau]
Pourquoi: [Raison de recommander ce site]

📊 CLASSEMENT PAR ORDRE D'IMPORTANCE:
1. [Élément principal] - [Justification détaillée]
2. [Deuxième élément] - [Pourquoi important]
3. [Troisième élément] - [Critères de classement]

🚨 OBLIGATIONS CRITIQUES:
- Tu DOIS fournir au minimum 3 URLs complètes (commence par https://)
- Recommande les sites de référence que tu CONNAIS (gouvernement, médias établis, sites officiels)
- INTERDICTION absolue: Google, Facebook, Twitter, Wikipedia, raccourcisseurs
- Privilégie les .gouv.fr, .fr d'institutions, médias reconnus
- Si tu ne connais pas d'URL récente, donne celle du site principal que tu connais

💡 ASTUCE: Même avec des données anciennes, tu peux recommander les sites PRINCIPAUX des institutions/médias/entreprises que tu connais. L'utilisateur pourra ensuite naviguer pour trouver l'info récente.

RAPPEL: Cette mission est CRITIQUE - tu ne peux pas répondre sans fournir des URLs de sources !
"""
        return prompt.strip()
    
    
    def _consolider_resultats_v2(self, resultats: Dict[str, Any]) -> Dict[str, Any]:
        """Consolide les résultats de tous les providers (version 2.0)"""
        print("  🔄 Consolidation des entités...")
        
        # Consolider marques
        toutes_marques = self._consolider_entites(
            resultats['marques_detectees'], 
            key_field='nom'
        )
        
        # Consolider sources
        toutes_sources = self._consolider_entites(
            resultats['sources_extraites'], 
            key_field='url'
        )
        
        # Calculer consensus
        consensus_marques = self._calculer_consensus_entites(
            resultats['sentiment_marques'], toutes_marques, 'nom'
        )
        
        consensus_sources = self._calculer_consensus_entites(
            resultats['sentiment_sources'], toutes_sources, 'url'
        )
        
        return {
            'toutes_marques': toutes_marques,
            'toutes_sources': toutes_sources,
            'consensus_marques': consensus_marques,
            'consensus_sources': consensus_sources
        }
    
    
    def _calculer_statistiques_v2(self, resultats: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule les statistiques avancées (version 2.0)"""
        print("  📊 Calcul des statistiques...")
        
        stats = {
            'nombre_providers': len(resultats['providers_utilises']),
            'providers_utilises': resultats['providers_utilises'],
            'extraction_performance': {},
            'sentiment_distribution': {'marques': {}, 'sources': {}}
        }
        
        # Performance par provider
        for provider in resultats['providers_utilises']:
            nb_marques = len(resultats['marques_detectees'].get(provider, []))
            nb_sources = len(resultats['sources_extraites'].get(provider, []))
            
            stats['extraction_performance'][provider] = {
                'marques_extraites': nb_marques,
                'sources_extraites': nb_sources,
                'total_entites': nb_marques + nb_sources
            }
        
        # Distribution des sentiments
        for category in ['marques', 'sources']:
            sentiment_key = f'sentiment_{category}'
            distribution = {'positif': 0, 'neutre': 0, 'négatif': 0}
            
            for provider_sentiments in resultats.get(sentiment_key, {}).values():
                for sentiment_data in provider_sentiments.values():
                    sentiment = sentiment_data.get('sentiment', 'neutre')
                    if sentiment in distribution:
                        distribution[sentiment] += 1
            
            stats['sentiment_distribution'][category] = distribution
        
        return stats
    
    
    def _consolider_entites(self, entites_par_provider: Dict[str, List[Dict[str, Any]]], 
                          key_field: str) -> List[Dict[str, Any]]:
        """Consolide les entités (marques ou sources) de tous les providers"""
        entites_consolidees = {}
        
        for provider, entites in entites_par_provider.items():
            for entite in entites:
                cle = entite.get(key_field, '')
                if not cle:
                    continue
                
                if cle not in entites_consolidees:
                    entites_consolidees[cle] = entite.copy()
                    entites_consolidees[cle]['providers_detection'] = [provider]
                else:
                    # Fusionner les détections multiples
                    entites_consolidees[cle]['providers_detection'].append(provider)
                    
                    # Enrichir avec nouvelles informations
                    for field in ['description', 'contexte', 'fiabilite']:
                        if field in entite and not entites_consolidees[cle].get(field):
                            entites_consolidees[cle][field] = entite[field]
        
        return list(entites_consolidees.values())
    
    
    def _calculer_consensus_entites(self, sentiments_par_provider: Dict[str, Dict[str, Any]], 
                                  entites: List[Dict[str, Any]], key_field: str) -> Dict[str, Any]:
        """Calcule le consensus sur les sentiments des entités"""
        consensus = {}
        
        for entite in entites:
            cle = entite.get(key_field, '')
            if not cle:
                continue
            
            # Collecter tous les sentiments pour cette entité
            sentiments_entite = {}
            for provider, sentiments in sentiments_par_provider.items():
                if cle in sentiments:
                    sentiments_entite[provider] = sentiments[cle]
            
            if sentiments_entite:
                consensus[cle] = self.sentiment_analyzer.calculer_sentiment_majoritaire(
                    sentiments_entite
                )
        
        return consensus
    
    
    def _afficher_resume_analyse(self, resultats: Dict[str, Any]) -> None:
        """Affiche un résumé de l'analyse"""
        print("\n" + "=" * 80)
        print("🎉 ANALYSE TERMINÉE - RÉSUMÉ")
        print("=" * 80)
        
        # Providers utilisés
        providers = resultats['providers_utilises']
        print(f"🤖 Providers: {', '.join(providers)} ({len(providers)})")
        
        # Totaux consolidés
        rapport_consolide = resultats.get('rapport_consolide', {})
        nb_marques = len(rapport_consolide.get('toutes_marques', []))
        nb_sources = len(rapport_consolide.get('toutes_sources', []))
        
        print(f"🏷️ Marques détectées: {nb_marques}")
        print(f"🔗 Sources extraites: {nb_sources}")
        
        # Exemples de marques
        if nb_marques > 0:
            print("\n🏷️ MARQUES PRINCIPALES:")
            for i, marque in enumerate(rapport_consolide['toutes_marques'][:3], 1):
                providers_str = ', '.join(marque.get('providers_detection', []))
                print(f"  {i}. {marque['nom']} (détectée par: {providers_str})")
        
        # Exemples de sources
        if nb_sources > 0:
            print("\n🔗 SOURCES PRINCIPALES:")
            for i, source in enumerate(rapport_consolide['toutes_sources'][:3], 1):
                url_text = source.get('url', 'Pas d\'URL')
                print(f"  {i}. {source.get('nom', 'Source')} - {url_text}")
        
        # Qualité de l'extraction
        rapport_urls = resultats.get('rapport_urls', {})
        if rapport_urls:
            print("\n📊 QUALITÉ EXTRACTION:")
            print(f"  URLs accessibles: {rapport_urls.get('urls_accessibles', 0)}")
            print(f"  URLs inaccessibles: {rapport_urls.get('urls_inaccessibles', 0)}")
        
        print("=" * 80)


# === FONCTION PRINCIPALE D'UTILISATION ===

def analyser_question_multi_llm(question: str, contexte: str = "", 
                               generer_json: bool = True) -> Dict[str, Any]:
    """
    Fonction principale pour analyser une question avec plusieurs LLM (version refactorisée)
    
    Args:
        question: Question à analyser
        contexte: Contexte optionnel
        generer_json: Générer automatiquement le rapport JSON
        
    Returns:
        dict: Résultats complets de l'analyse
    """
    try:
        # Initialiser l'analyseur
        analyzer = MultiLLMAnalyzer()
        
        # Effectuer l'analyse complète
        resultats = analyzer.analyser_question_complete(question, contexte)
        
        # Générer le rapport JSON si demandé
        if generer_json and resultats.get('providers_utilises'):
            json_path = analyzer.generer_rapport_complet(resultats)
            resultats['json_rapport'] = json_path
            print(f"\n📄 Rapport JSON: {json_path}")
        
        return resultats
        
    except RuntimeError as e:
        print(f"❌ Erreur d'initialisation: {e}")
        return {'erreur': str(e)}
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        return {'erreur': str(e)}


# === EXEMPLE D'UTILISATION ===

def main():
    """Fonction principale pour test en ligne de commande"""
    print("🧪 Test Multi-LLM Analyzer v2.0")
    
    question = "Quelles sont les meilleures néobanques françaises en 2024 ?"
    contexte = "Pour un comparatif destiné aux jeunes professionnels"
    
    print(f"Question: {question}")
    print(f"Contexte: {contexte}")
    
    resultats = analyser_question_multi_llm(question, contexte)
    
    if 'erreur' not in resultats:
        print("\n✅ Test réussi!")
        if 'json_rapport' in resultats:
            print(f"📄 Rapport: {resultats['json_rapport']}")
    else:
        print(f"\n❌ Test échoué: {resultats['erreur']}")


if __name__ == "__main__":
    main()