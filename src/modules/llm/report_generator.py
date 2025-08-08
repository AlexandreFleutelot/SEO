# -*- coding: utf-8 -*-
"""
Report Generator - Génération de rapports JSON structurés
Module spécialisé dans la création de rapports complets d'analyse multi-LLM
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from ...config import LLM_ANALYSIS_DIR


class MultiLLMReportGenerator:
    """Générateur de rapports JSON pour les analyses multi-LLM"""
    
    def __init__(self):
        # Utiliser le dossier dédié aux rapports LLM
        self.reports_dir = LLM_ANALYSIS_DIR
        self.version = "2.0"
    
    
    def generer_rapport_complet(self, donnees_analyse: Dict[str, Any], 
                              nom_fichier: Optional[str] = None) -> str:
        """
        Génère un rapport JSON complet et structuré
        
        Args:
            donnees_analyse: Données complètes de l'analyse multi-LLM
            nom_fichier: Nom du fichier (optionnel)
            
        Returns:
            str: Chemin du fichier rapport généré
        """
        print("📊 Génération du rapport JSON complet...")
        
        # Déterminer le nom de fichier
        if not nom_fichier:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nom_fichier = f"multi_llm_analysis_{timestamp}.json"
        
        fichier_path = self.reports_dir / nom_fichier
        
        # Construire la structure du rapport
        rapport = self._construire_structure_rapport(donnees_analyse)
        
        # Sauvegarder le rapport
        with open(fichier_path, 'w', encoding='utf-8') as f:
            json.dump(rapport, f, indent=2, ensure_ascii=False)
        
        # Calculer les statistiques du rapport
        taille_fichier = fichier_path.stat().st_size
        print(f"✅ Rapport généré: {fichier_path.name}")
        print(f"📊 Taille: {taille_fichier/1024:.1f} KB")
        print(f"🔧 Sections: {len(rapport)} principales")
        
        return str(fichier_path)
    
    
    def _construire_structure_rapport(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Construit la structure complète du rapport JSON"""
        
        rapport = {
            # === MÉTADONNÉES ===
            'metadata': self._generer_metadata(donnees),
            
            # === CONFIGURATION ===
            'configuration': self._generer_section_configuration(donnees),
            
            # === RÉPONSES LLM BRUTES ===
            'reponses_llm_brutes': self._generer_section_reponses_brutes(donnees),
            
            # === INFORMATIONS EXTRAITES ===
            'extractions': {
                'marques_detectees': self._generer_section_marques(donnees),
                'sources_extraites': self._generer_section_sources(donnees),
                'citations_ordonnees': self._generer_section_citations(donnees)
            },
            
            # === ANALYSE DE SENTIMENT ===
            'analyse_sentiment': self._generer_section_sentiment(donnees),
            
            # === CONSENSUS ET COMPARAISONS ===
            'consensus_inter_llm': self._generer_section_consensus(donnees),
            
            # === STATISTIQUES ET MÉTRIQUES ===
            'statistiques_detaillees': self._generer_section_statistiques(donnees),
            
            # === RAPPORTS SPÉCIALISÉS ===
            'rapports_specialises': {
                'extraction_urls': donnees.get('rapport_urls', {}),
                'qualite_extractions': self._evaluer_qualite_extractions(donnees)
            }
        }
        
        return rapport
    
    
    def _generer_metadata(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Génère les métadonnées du rapport"""
        return {
            'question_originale': donnees.get('question', ''),
            'contexte_fourni': donnees.get('contexte', ''),
            'timestamp_analyse': donnees.get('timestamp', datetime.now().isoformat()),
            'timestamp_rapport': datetime.now().isoformat(),
            'version_analyseur': self.version,
            'providers_interroges': donnees.get('providers_utilises', []),
            'nombre_providers': len(donnees.get('providers_utilises', [])),
            'duree_analyse_estimee': self._calculer_duree_analyse(donnees),
            'id_session': self._generer_id_session(donnees)
        }
    
    
    def _generer_section_configuration(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Génère la section de configuration"""
        return {
            'providers_configuration': donnees.get('configuration_providers', {}),
            'extraction_strategies': {
                'urls_multicouches': True,
                'marques_patterns_avances': True,
                'sentiment_llm_specialise': True
            },
            'parametres_analyse': {
                'temperature': 0.3,
                'max_tokens': 4000,
                'timeout_requests': 30
            }
        }
    
    
    def _generer_section_reponses_brutes(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Génère la section des réponses LLM brutes"""
        reponses_brutes = {}
        
        for provider, reponse in donnees.get('reponses_brutes', {}).items():
            reponses_brutes[provider] = {
                'reponse_complete': reponse,
                'statistiques_reponse': {
                    'longueur_caracteres': len(reponse) if reponse else 0,
                    'nombre_mots': len(reponse.split()) if reponse else 0,
                    'nombre_lignes': reponse.count('\n') if reponse else 0,
                    'presence_urls': len(self._extraire_urls_basique(reponse)) if reponse else 0,
                    'presence_listes': reponse.count('\n-') + reponse.count('\n*') if reponse else 0
                }
            }
        
        return reponses_brutes
    
    
    def _generer_section_marques(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Génère la section des marques détectées"""
        return {
            'par_provider': donnees.get('marques_detectees', {}),
            'consolidation': {
                'marques_uniques': self._consolider_marques(donnees),
                'statistiques': self._calculer_stats_marques(donnees),
                'classification_types': self._classifier_marques_par_type(donnees)
            }
        }
    
    
    def _generer_section_sources(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Génère la section des sources extraites"""
        return {
            'par_provider': donnees.get('sources_extraites', {}),
            'consolidation': {
                'sources_uniques': self._consolider_sources(donnees),
                'statistiques': self._calculer_stats_sources(donnees),
                'analyse_fiabilite': self._analyser_fiabilite_sources(donnees)
            }
        }
    
    
    def _generer_section_citations(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Génère la section des citations ordonnées"""
        return {
            'par_provider': donnees.get('citations_ordonnees', {}),
            'analyse_consensus': self._analyser_consensus_citations(donnees)
        }
    
    
    def _generer_section_sentiment(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Génère la section d'analyse de sentiment"""
        return {
            'sentiments_bruts': {
                'marques': donnees.get('sentiment_marques', {}),
                'sources': donnees.get('sentiment_sources', {})
            },
            'sentiments_consolides': self._consolider_sentiments(donnees),
            'analyse_consensus_sentiment': self._analyser_consensus_sentiment(donnees),
            'distribution_sentiments': self._calculer_distribution_sentiments(donnees)
        }
    
    
    def _generer_section_consensus(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Génère la section de consensus inter-LLM"""
        rapport_consolide = donnees.get('rapport_consolide', {})
        
        return {
            'consensus_marques': rapport_consolide.get('consensus_marques', {}),
            'consensus_sources': rapport_consolide.get('consensus_sources', {}),
            'scores_accord': self._calculer_scores_accord(donnees),
            'divergences_majeures': self._identifier_divergences(donnees)
        }
    
    
    def _generer_section_statistiques(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Génère la section des statistiques détaillées"""
        stats_base = donnees.get('statistiques', {})
        
        # Enrichir avec des statistiques avancées
        stats_avancees = {
            'efficacite_extraction': self._calculer_efficacite_extraction(donnees),
            'qualite_reponses': self._evaluer_qualite_reponses(donnees),
            'couverture_informations': self._calculer_couverture_informations(donnees),
            'coherence_inter_providers': self._evaluer_coherence_providers(donnees)
        }
        
        # Combiner stats de base et avancées
        stats_base.update(stats_avancees)
        
        return stats_base
    
    
    def _evaluer_qualite_extractions(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Évalue la qualité des extractions effectuées"""
        
        total_marques = sum(len(marques) for marques in donnees.get('marques_detectees', {}).values())
        total_sources = sum(len(sources) for sources in donnees.get('sources_extraites', {}).values())
        
        # Scores de qualité basés sur plusieurs critères
        score_quantite = min(100, (total_marques * 10) + (total_sources * 20))  # Plus de poids aux sources
        
        score_diversite = len(set(
            marque['nom'] for provider_marques in donnees.get('marques_detectees', {}).values()
            for marque in provider_marques
        )) * 15
        
        score_urls_valides = self._calculer_score_urls_valides(donnees)
        
        score_global = min(100, (score_quantite + score_diversite + score_urls_valides) / 3)
        
        return {
            'score_global_qualite': round(score_global),
            'details_scoring': {
                'quantite_extractions': score_quantite,
                'diversite_entites': score_diversite,
                'validite_urls': score_urls_valides
            },
            'recommandations_amelioration': self._generer_recommandations_qualite(donnees)
        }
    
    
    def _consolider_marques(self, donnees: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Consolide toutes les marques détectées"""
        marques_consolidees = {}
        
        for provider, marques in donnees.get('marques_detectees', {}).items():
            for marque in marques:
                nom = marque['nom']
                if nom not in marques_consolidees:
                    marques_consolidees[nom] = {
                        'nom': nom,
                        'providers_detection': [],
                        'descriptions': [],
                        'mentions_total': 0,
                        'types_detection': set()
                    }
                
                marques_consolidees[nom]['providers_detection'].append(provider)
                if marque.get('description'):
                    marques_consolidees[nom]['descriptions'].append(marque['description'])
                marques_consolidees[nom]['mentions_total'] += marque.get('mentions', 0)
                marques_consolidees[nom]['types_detection'].add(marque.get('source_detection', 'inconnue'))
        
        # Convertir sets en listes pour JSON
        for marque in marques_consolidees.values():
            marque['types_detection'] = list(marque['types_detection'])
        
        return list(marques_consolidees.values())
    
    
    def _consolider_sources(self, donnees: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Consolide toutes les sources extraites"""
        sources_consolidees = {}
        
        for provider, sources in donnees.get('sources_extraites', {}).items():
            for source in sources:
                url = source.get('url', source.get('nom', ''))
                if url not in sources_consolidees:
                    sources_consolidees[url] = {
                        'nom': source.get('nom', ''),
                        'url': url,
                        'domaine': source.get('domaine', ''),
                        'providers_detection': [],
                        'methodes_extraction': set(),
                        'fiabilite_evaluee': source.get('fiabilite', '')
                    }
                
                sources_consolidees[url]['providers_detection'].append(provider)
                sources_consolidees[url]['methodes_extraction'].add(source.get('methode_extraction', 'inconnue'))
        
        # Convertir sets en listes
        for source in sources_consolidees.values():
            source['methodes_extraction'] = list(source['methodes_extraction'])
        
        return list(sources_consolidees.values())
    
    
    def _calculer_stats_marques(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule les statistiques sur les marques"""
        all_marques = [
            marque for provider_marques in donnees.get('marques_detectees', {}).values()
            for marque in provider_marques
        ]
        
        return {
            'total_detections': len(all_marques),
            'marques_uniques': len(set(marque['nom'] for marque in all_marques)),
            'mentions_moyennes': sum(marque.get('mentions', 0) for marque in all_marques) / len(all_marques) if all_marques else 0,
            'marque_plus_mentionnee': max(all_marques, key=lambda m: m.get('mentions', 0))['nom'] if all_marques else None
        }
    
    
    def _calculer_stats_sources(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule les statistiques sur les sources"""
        all_sources = [
            source for provider_sources in donnees.get('sources_extraites', {}).values()
            for source in provider_sources
        ]
        
        domaines = [source.get('domaine', '') for source in all_sources if source.get('domaine')]
        
        return {
            'total_extractions': len(all_sources),
            'sources_uniques': len(set(source.get('url', '') for source in all_sources)),
            'domaines_uniques': len(set(domaines)),
            'domaine_plus_frequent': max(set(domaines), key=domaines.count) if domaines else None
        }
    
    
    def _consolider_sentiments(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Consolide les sentiments de tous les providers"""
        sentiments_consolides = {
            'marques': {},
            'sources': {}
        }
        
        # Consolider sentiments marques
        for provider, sentiments in donnees.get('sentiment_marques', {}).items():
            for nom, sentiment_data in sentiments.items():
                if nom not in sentiments_consolides['marques']:
                    sentiments_consolides['marques'][nom] = {}
                sentiments_consolides['marques'][nom][provider] = sentiment_data
        
        # Consolider sentiments sources
        for provider, sentiments in donnees.get('sentiment_sources', {}).items():
            for nom, sentiment_data in sentiments.items():
                if nom not in sentiments_consolides['sources']:
                    sentiments_consolides['sources'][nom] = {}
                sentiments_consolides['sources'][nom][provider] = sentiment_data
        
        return sentiments_consolides
    
    
    def _calculer_distribution_sentiments(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule la distribution des sentiments"""
        distribution = {
            'marques': {'positif': 0, 'neutre': 0, 'négatif': 0},
            'sources': {'positif': 0, 'neutre': 0, 'négatif': 0}
        }
        
        # Compter sentiments marques
        for sentiments_provider in donnees.get('sentiment_marques', {}).values():
            for sentiment_data in sentiments_provider.values():
                sentiment = sentiment_data.get('sentiment', 'neutre')
                if sentiment in distribution['marques']:
                    distribution['marques'][sentiment] += 1
        
        # Compter sentiments sources
        for sentiments_provider in donnees.get('sentiment_sources', {}).values():
            for sentiment_data in sentiments_provider.values():
                sentiment = sentiment_data.get('sentiment', 'neutre')
                if sentiment in distribution['sources']:
                    distribution['sources'][sentiment] += 1
        
        return distribution
    
    
    def _calculer_duree_analyse(self, donnees: Dict[str, Any]) -> str:
        """Calcule la durée estimée de l'analyse"""
        # Estimation basée sur le nombre de providers et la complexité
        nb_providers = len(donnees.get('providers_utilises', []))
        estimation_secondes = nb_providers * 15  # ~15 secondes par provider
        
        if estimation_secondes < 60:
            return f"{estimation_secondes}s"
        else:
            return f"{estimation_secondes//60}m{estimation_secondes%60}s"
    
    
    def _generer_id_session(self, donnees: Dict[str, Any]) -> str:
        """Génère un ID unique pour la session d'analyse"""
        import hashlib
        
        # Créer un hash basé sur la question et le timestamp
        contenu = f"{donnees.get('question', '')}{donnees.get('timestamp', '')}"
        return hashlib.md5(contenu.encode()).hexdigest()[:12]
    
    
    def _extraire_urls_basique(self, texte: str) -> List[str]:
        """Extraction basique d'URLs pour statistiques"""
        import re
        return re.findall(r'https?://[^\s]+', texte)
    
    
    # Méthodes utilitaires pour les statistiques avancées (stubs)
    def _calculer_efficacite_extraction(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule l'efficacité de l'extraction"""
        return {'score': 75, 'details': 'Évaluation basique'}
    
    def _evaluer_qualite_reponses(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Évalue la qualité des réponses LLM"""
        return {'score': 80, 'criteres': ['longueur', 'structure', 'sources']}
    
    def _calculer_couverture_informations(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule la couverture des informations"""
        return {'score': 85, 'completude': 'Bonne'}
    
    def _evaluer_coherence_providers(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Évalue la cohérence entre providers"""
        return {'score': 70, 'divergences': 'Mineures'}
    
    def _calculer_scores_accord(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule les scores d'accord entre providers"""
        return {'marques': 0.8, 'sources': 0.6, 'sentiments': 0.7}
    
    def _identifier_divergences(self, donnees: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifie les divergences majeures"""
        return []
    
    def _analyser_consensus_citations(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse le consensus sur les citations"""
        return {'consensus_level': 'moyen'}
    
    def _analyser_consensus_sentiment(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse le consensus sur les sentiments"""
        return {'accord_sentiment': 0.75}
    
    def _analyser_fiabilite_sources(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse la fiabilité des sources"""
        return {'fiabilite_moyenne': 'élevée'}
    
    def _classifier_marques_par_type(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """Classifie les marques par type"""
        return {'banques': 3, 'fintech': 2, 'assurances': 1}
    
    def _calculer_score_urls_valides(self, donnees: Dict[str, Any]) -> int:
        """Calcule le score des URLs valides"""
        return 60  # Score par défaut
    
    def _generer_recommandations_qualite(self, donnees: Dict[str, Any]) -> List[str]:
        """Génère des recommandations d'amélioration"""
        return [
            "Améliorer l'extraction des URLs avec des prompts plus spécifiques",
            "Diversifier les sources de détection des marques"
        ]