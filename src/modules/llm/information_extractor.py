# -*- coding: utf-8 -*-
"""
Information Extractor - Extraction des marques et entités depuis les réponses LLM
Module spécialisé dans la détection et l'analyse des informations clés
"""

import re
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse


class InformationExtractor:
    """Extracteur d'informations (marques, entités, citations) depuis les réponses LLM"""
    
    def __init__(self):
        # Patterns pour détecter les sections structurées
        self.section_patterns = {
            'marques': [
                r'🏷️\s*MARQUES?\s*MENTIONN[EÉ]ES?:',
                r'MARQUES?\s*[EÉ]T\s*ENTREPRISES?:',
                r'ENTREPRISES?\s*CITÉES?:'
            ],
            'sources': [
                r'🔗\s*SOURCES?\s*CONSULT[EÉ]ES?:',
                r'SOURCES?\s*ET\s*R[EÉ]F[EÉ]RENCES?:',
                r'BIBLIOGRAPHIE:'
            ],
            'classement': [
                r'📊\s*CLASSEMENT:',
                r'ORDRE\s*D[\'\']IMPORTANCE:',
                r'HI[EÉ]RARCHIE:'
            ]
        }
    
    
    def extraire_marques_completes(self, reponse_llm: str) -> List[Dict[str, Any]]:
        """
        Extrait toutes les marques mentionnées dans une réponse LLM
        
        Args:
            reponse_llm: Texte de la réponse du LLM
            
        Returns:
            list: Marques détectées avec métadonnées
        """
        print("    🏷️ Extraction des marques...")
        
        marques = []
        
        # Stratégie 1: Chercher dans les sections structurées
        marques.extend(self._extraire_marques_sections_structurees(reponse_llm))
        
        # Stratégie 2: Détection par patterns si pas assez trouvé
        if len(marques) < 3:
            marques.extend(self._detecter_marques_patterns(reponse_llm))
        
        # Stratégie 3: Analyse par capitalisation et contexte
        marques.extend(self._detecter_marques_capitalisation(reponse_llm))
        
        # Déduplication et enrichissement
        marques_finales = self._deduplication_et_enrichissement_marques(marques, reponse_llm)
        
        print(f"    ✅ {len(marques_finales)} marques extraites")
        return marques_finales
    
    
    def extraire_ordre_citations(self, reponse_llm: str) -> List[Dict[str, Any]]:
        """
        Extrait l'ordre d'importance/citation depuis une réponse LLM
        
        Args:
            reponse_llm: Texte de la réponse du LLM
            
        Returns:
            list: Citations ordonnées avec positions
        """
        print("    📊 Extraction ordre des citations...")
        
        citations = []
        
        # Chercher dans les sections de classement
        for pattern in self.section_patterns['classement']:
            section = self._extraire_section_texte(reponse_llm, pattern)
            if section:
                citations.extend(self._parser_elements_ordonnes(section))
        
        # Si pas de section dédiée, chercher les listes numérotées
        if not citations:
            citations = self._detecter_listes_numerotees(reponse_llm)
        
        print(f"    ✅ {len(citations)} éléments dans l'ordre des citations")
        return citations
    
    
    def _extraire_marques_sections_structurees(self, texte: str) -> List[Dict[str, Any]]:
        """Extrait les marques depuis les sections structurées"""
        marques = []
        
        for pattern in self.section_patterns['marques']:
            section = self._extraire_section_texte(texte, pattern)
            if section:
                # Parser les éléments de la section
                elements = self._parser_elements_listes(section)
                
                for element in elements:
                    nom_marque, description = self._separer_nom_description(element)
                    if nom_marque:
                        marques.append({
                            'nom': nom_marque,
                            'description': description,
                            'source_detection': 'section_structuree',
                            'element_brut': element
                        })
        
        return marques
    
    
    def _detecter_marques_patterns(self, texte: str) -> List[Dict[str, Any]]:
        """Détecte les marques via patterns spécifiques"""
        marques = []
        
        # Patterns spécifiques aux marques/entreprises
        patterns = [
            r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:est|propose|offre|fournit)',  # "Boursorama Banque propose"
            r'(?:chez|avec|par)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',          # "chez Orange Bank"
            r'\b([A-Z][a-z]+\s*!?)\s+(?:se|dispose|permet)',                  # "Hello bank! se"
            r'(?:banque|société|groupe|entreprise)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', # "banque Fortuneo"
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, texte, re.MULTILINE)
            for match in matches:
                nom_marque = match.group(1).strip()
                
                # Filtrer les faux positifs courants
                if self._est_nom_marque_valide(nom_marque):
                    marques.append({
                        'nom': nom_marque,
                        'description': '',
                        'source_detection': 'pattern_contextuel',
                        'contexte_detection': match.group(0)
                    })
        
        return marques
    
    
    def _detecter_marques_capitalisation(self, texte: str) -> List[Dict[str, Any]]:
        """Détecte les marques par analyse de capitalisation"""
        marques = []
        
        # Pattern pour mots/expressions capitalisés
        pattern_caps = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        
        # Compteur de fréquence pour identifier les vrais noms de marque
        candidats = {}
        
        for match in re.finditer(pattern_caps, texte):
            candidat = match.group(0).strip()
            
            # Filtrer les mots courants qui ne sont pas des marques
            if (len(candidat) > 2 and 
                candidat not in ['Le', 'La', 'Les', 'Un', 'Une', 'Ce', 'Cette', 'Dans', 'Pour'] and
                not candidat.startswith(('Http', 'Www'))):
                
                candidats[candidat] = candidats.get(candidat, 0) + 1
        
        # Garder les candidats mentionnés plusieurs fois ou avec des indicateurs de marque
        for nom, freq in candidats.items():
            if freq >= 2 or self._a_indicateurs_marque(texte, nom):
                marques.append({
                    'nom': nom,
                    'description': '',
                    'source_detection': 'capitalisation',
                    'frequence': freq
                })
        
        return marques
    
    
    def _deduplication_et_enrichissement_marques(self, marques: List[Dict[str, Any]], 
                                               texte_complet: str) -> List[Dict[str, Any]]:
        """Déduplique et enrichit la liste des marques"""
        marques_uniques = {}
        
        for marque in marques:
            nom = marque['nom'].strip()
            
            # Normaliser le nom (gérer les variations)
            nom_normalise = self._normaliser_nom_marque(nom)
            
            if nom_normalise not in marques_uniques:
                # Enrichir avec des informations du texte complet
                marque_enrichie = marque.copy()
                marque_enrichie['nom'] = nom  # Garder le nom original
                marque_enrichie['mentions'] = texte_complet.count(nom)
                marque_enrichie['contexte'] = self._extraire_contexte_marque(texte_complet, nom)
                marque_enrichie['type_entite'] = self._classifier_type_entite(nom, texte_complet)
                
                marques_uniques[nom_normalise] = marque_enrichie
            else:
                # Fusionner les informations si marque déjà présente
                marque_existante = marques_uniques[nom_normalise]
                
                # Prendre la description la plus complète
                if not marque_existante.get('description') and marque.get('description'):
                    marque_existante['description'] = marque['description']
                
                # Combiner les sources de détection
                sources = marque_existante.get('source_detection', '')
                nouvelle_source = marque.get('source_detection', '')
                if nouvelle_source and nouvelle_source not in sources:
                    marque_existante['source_detection'] = f"{sources}, {nouvelle_source}"
        
        return list(marques_uniques.values())
    
    
    def _parser_elements_ordonnes(self, section: str) -> List[Dict[str, Any]]:
        """Parse une section avec éléments ordonnés"""
        elements = []
        
        # Pattern pour éléments numérotés
        pattern = r'(\d+)\.\s*([^\n]+?)(?:\s*[-–]\s*([^\n]+))?'
        
        for match in re.finditer(pattern, section, re.MULTILINE):
            position = int(match.group(1))
            element = match.group(2).strip()
            raison = match.group(3).strip() if match.group(3) else ""
            
            elements.append({
                'position': position,
                'element': element,
                'raison': raison,
                'score_importance': max(0, 100 - (position - 1) * 10)  # Score décroissant
            })
        
        return elements
    
    
    def _detecter_listes_numerotees(self, texte: str) -> List[Dict[str, Any]]:
        """Détecte les listes numérotées dans tout le texte"""
        listes = []
        
        # Chercher les patterns de listes numérotées
        pattern = r'(?:^|\n)(\d+)[\.\)]\s+([^\n]+)'
        
        matches = list(re.finditer(pattern, texte, re.MULTILINE))
        
        # Garder seulement les séquences cohérentes (1, 2, 3...)
        if len(matches) >= 3:  # Au moins 3 éléments pour considérer comme liste
            for match in matches:
                position = int(match.group(1))
                element = match.group(2).strip()
                
                listes.append({
                    'position': position,
                    'element': element,
                    'raison': '',
                    'score_importance': max(0, 100 - (position - 1) * 10)
                })
        
        return listes
    
    
    def _extraire_section_texte(self, texte: str, pattern_debut: str, pattern_fin: str = None) -> str:
        """Extrait une section du texte entre deux marqueurs"""
        start_match = re.search(pattern_debut, texte, re.IGNORECASE)
        if not start_match:
            return ""
        
        start = start_match.end()
        
        if pattern_fin:
            end_match = re.search(pattern_fin, texte[start:], re.IGNORECASE)
            if end_match:
                end = start + end_match.start()
                return texte[start:end].strip()
        
        # Si pas de pattern de fin, prendre jusqu'à la prochaine section ou fin
        next_section_patterns = [
            r'\n\n[🔍🏷️🔗💭📊]',  # Prochaine section avec emoji
            r'\n\n[A-Z]{2,}:',      # Prochaine section en majuscules
            r'\n\n\d+\.',           # Prochaine liste numérotée
        ]
        
        end = len(texte)
        for pattern in next_section_patterns:
            match = re.search(pattern, texte[start:])
            if match:
                end = min(end, start + match.start())
        
        return texte[start:end].strip()
    
    
    def _parser_elements_listes(self, section: str) -> List[str]:
        """Parse les éléments d'une liste (numérotée ou à puces)"""
        elements = []
        
        # Patterns pour différents types de listes
        patterns = [
            r'^\d+\.\s*(.+)$',           # 1. Element
            r'^[-\*\•]\s*(.+)$',         # - Element ou * Element
            r'^([A-Z][^\n]+)$',          # Ligne commençant par majuscule
        ]
        
        lignes = section.split('\n')
        
        for ligne in lignes:
            ligne = ligne.strip()
            if not ligne:
                continue
                
            for pattern in patterns:
                match = re.match(pattern, ligne)
                if match:
                    elements.append(match.group(1).strip())
                    break
        
        return elements
    
    
    def _separer_nom_description(self, element: str) -> tuple:
        """Sépare un nom de marque de sa description"""
        # Patterns de séparation courants
        separateurs = [' - ', ' – ', ' : ', ' (', ' |']
        
        for sep in separateurs:
            if sep in element:
                parties = element.split(sep, 1)
                nom = parties[0].strip()
                description = parties[1].strip().rstrip(')')
                return nom, description
        
        # Si pas de séparateur, tout est considéré comme nom
        return element.strip(), ""
    
    
    def _est_nom_marque_valide(self, nom: str) -> bool:
        """Vérifie si un nom est probablement une vraie marque"""
        # Filtrer les faux positifs courants
        faux_positifs = {
            'France', 'French', 'European', 'Global', 'International',
            'Service', 'Services', 'Client', 'Clients', 'Premium',
            'Standard', 'Classic', 'Basic', 'Advanced', 'Pro'
        }
        
        return (len(nom) > 1 and 
                nom not in faux_positifs and
                not nom.isdigit() and
                not nom.lower() in ['le', 'la', 'les', 'un', 'une', 'des'])
    
    
    def _a_indicateurs_marque(self, texte: str, nom: str) -> bool:
        """Vérifie si un nom a des indicateurs suggérant que c'est une marque"""
        # Chercher des indicateurs contextuels
        indicateurs = [
            f'{nom} propose', f'{nom} offre', f'{nom} permet',
            f'chez {nom}', f'avec {nom}', f'par {nom}',
            f'{nom} est une', f'{nom} est un', f'{nom} dispose'
        ]
        
        return any(indicateur.lower() in texte.lower() for indicateur in indicateurs)
    
    
    def _normaliser_nom_marque(self, nom: str) -> str:
        """Normalise un nom de marque pour la déduplication"""
        # Supprimer les caractères spéciaux et normaliser la casse
        nom_norm = re.sub(r'[^\w\s]', '', nom.lower().strip())
        
        # Gérer les variations communes
        variations = {
            'hello bank': 'hellobank',
            'credit agricole': 'creditagricole',
            'societe generale': 'societegenerale',
            'bnp paribas': 'bnpparibas'
        }
        
        return variations.get(nom_norm, nom_norm)
    
    
    def _extraire_contexte_marque(self, texte: str, marque: str, rayon: int = 150) -> str:
        """Extrait le contexte autour d'une marque"""
        index = texte.lower().find(marque.lower())
        if index == -1:
            return ""
        
        debut = max(0, index - rayon)
        fin = min(len(texte), index + len(marque) + rayon)
        
        return texte[debut:fin].strip()
    
    
    def _classifier_type_entite(self, nom: str, contexte: str) -> str:
        """Classifie le type d'entité (banque, assurance, etc.)"""
        nom_lower = nom.lower()
        contexte_lower = contexte.lower()
        
        # Classifications par mots-clés
        if any(mot in contexte_lower for mot in ['banque', 'crédit', 'compte', 'carte']):
            return 'banque'
        elif any(mot in contexte_lower for mot in ['assurance', 'assureur', 'mutuelle']):
            return 'assurance'
        elif any(mot in contexte_lower for mot in ['investissement', 'bourse', 'trading']):
            return 'investissement'
        elif any(mot in contexte_lower for mot in ['néobanque', 'fintech']):
            return 'néobanque'
        else:
            return 'entreprise'
    
    
    def generer_rapport_extraction(self, marques: List[Dict[str, Any]], 
                                 citations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Génère un rapport sur l'extraction d'informations"""
        
        rapport = {
            'marques': {
                'total': len(marques),
                'par_source_detection': {},
                'par_type_entite': {},
                'mentions_totales': 0
            },
            'citations': {
                'total': len(citations),
                'elements_ordonnes': bool(citations)
            }
        }
        
        for marque in marques:
            # Source de détection
            source = marque.get('source_detection', 'inconnue')
            rapport['marques']['par_source_detection'][source] = rapport['marques']['par_source_detection'].get(source, 0) + 1
            
            # Type d'entité
            type_entite = marque.get('type_entite', 'inconnue')
            rapport['marques']['par_type_entite'][type_entite] = rapport['marques']['par_type_entite'].get(type_entite, 0) + 1
            
            # Mentions
            rapport['marques']['mentions_totales'] += marque.get('mentions', 0)
        
        return rapport