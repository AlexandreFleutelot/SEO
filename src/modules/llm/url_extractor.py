# -*- coding: utf-8 -*-
"""
URL Extractor - Module spécialisé dans l'extraction d'URLs depuis les réponses LLM
Stratégies multiples pour garantir la récupération des sources avec URLs
"""

import re
import requests
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse, urljoin
from .llm_providers import LLMProviderManager


class URLExtractor:
    """Extracteur spécialisé dans la récupération d'URLs depuis les réponses LLM"""
    
    def __init__(self, llm_manager: LLMProviderManager):
        self.llm_manager = llm_manager
        
        # Patterns pour détecter les URLs
        self.url_patterns = [
            r'https?://[^\s\]\)\,\;\!\?\"\']+',  # URLs complètes
            r'www\.[^\s\]\)\,\;\!\?\"\']+',      # URLs commençant par www
            r'Source:\s*\[([^\]]+)\]\s*-\s*URL:\s*(https?://[^\s]+)',  # Format structuré
            r'(?:source|référence|lien):\s*(https?://[^\s]+)',         # Format libre
        ]
        
        # Domaines à exclure (peu fiables pour les sources)
        self.excluded_domains = {
            'google.com', 'bing.com', 'yahoo.com', 'duckduckgo.com',
            'facebook.com', 'twitter.com', 'x.com', 'linkedin.com',
            'instagram.com', 'youtube.com', 'tiktok.com',
            'bit.ly', 'tinyurl.com', 'short.ly', 't.co'
        }
    
    
    def extraire_urls_depuis_reponse(self, provider_name: str, question: str, 
                                   reponse_initiale: str) -> List[Dict[str, Any]]:
        """
        Extrait les URLs depuis une réponse LLM avec stratégies multiples et validation SEO
        
        Args:
            provider_name: Nom du provider LLM
            question: Question originale
            reponse_initiale: Première réponse du LLM
            
        Returns:
            list: Sources avec URLs extraites et validées pour SEO
        """
        print(f"  🔗 Extraction URLs avancée ({provider_name})...")
        
        sources = []
        
        # Stratégie 1: Parser la réponse initiale
        sources.extend(self._parser_urls_reponse_initiale(reponse_initiale))
        
        # Stratégie 2: Si pas assez d'URLs, demande explicite de sources
        if len(sources) < 2:  # Seuil minimum d'URLs
            sources_supplementaires = self._demander_sources_explicites(provider_name, question, reponse_initiale)
            sources.extend(sources_supplementaires)
        
        # Stratégie 3: Si encore insuffisant, requête de citation forcée
        if len(sources) < 1:
            sources_forcees = self._forcer_citations_sources(provider_name, question)
            sources.extend(sources_forcees)
        
        # Validation avec évaluation SEO
        sources_validees = self._valider_et_nettoyer_urls(sources)
        
        # Stratégie 4: Si trop peu d'URLs exploitables, demander des URLs plus spécifiques
        urls_exploitables = [s for s in sources_validees if s.get('exploitable_seo', False)]
        if len(urls_exploitables) < 2:
            print(f"    🎯 Seulement {len(urls_exploitables)} URLs exploitables - demande d'URLs spécifiques...")
            sources_specifiques = self._demander_urls_specifiques(provider_name, question)
            if sources_specifiques:
                sources_specifiques_validees = self._valider_et_nettoyer_urls(sources_specifiques)
                sources_validees.extend(sources_specifiques_validees)
        
        # Déduplication finale
        sources_finales = self._deduplication_finale(sources_validees)
        
        print(f"  ✅ {len(sources_finales)} URLs finales extraites et validées")
        return sources_finales
    
    
    def _parser_urls_reponse_initiale(self, reponse: str) -> List[Dict[str, Any]]:
        """Parse la réponse initiale pour extraire les URLs"""
        sources = []
        urls_trouvees = set()  # Éviter les doublons
        
        # Essayer chaque pattern d'extraction
        for pattern in self.url_patterns:
            matches = re.finditer(pattern, reponse, re.IGNORECASE)
            
            for match in matches:
                if 'Source:' in match.group(0) and len(match.groups()) >= 2:
                    # Format structuré : Source: [Nom] - URL: https://...
                    nom_source = match.group(1).strip()
                    url = match.group(2).strip()
                else:
                    # URL simple trouvée
                    url = match.group(0).strip()
                    nom_source = self._extraire_nom_depuis_url(url)
                
                # Nettoyer l'URL
                url = self._nettoyer_url(url)
                
                if url and url not in urls_trouvees and self._url_valide(url):
                    urls_trouvees.add(url)
                    
                    sources.append({
                        'nom': nom_source,
                        'url': url,
                        'domaine': urlparse(url).netloc,
                        'methode_extraction': 'parsing_initial',
                        'contexte': self._extraire_contexte_url(reponse, url)
                    })
        
        return sources
    
    
    def _demander_sources_explicites(self, provider_name: str, question: str, 
                                   reponse_initiale: str) -> List[Dict[str, Any]]:
        """Demande explicitement les sources avec URLs au LLM"""
        print(f"    🔍 Demande sources explicites...")
        
        prompt_sources = f"""
Tu viens de répondre à cette question : "{question}"

Ta réponse précédente :
{reponse_initiale[:500]}...

🚨 URGENCE: Je DOIS ABSOLUMENT avoir des sources avec URLs SPÉCIFIQUES pour cette réponse !

🔗 MISSION CRITIQUE - SOURCES AVEC PAGES PRÉCISES :
Même si tes données ne sont pas parfaitement récentes, tu DOIS me fournir des URLs SPÉCIFIQUES pointant vers des ARTICLES, GUIDES ou DOSSIERS détaillés.

⚠️ INTERDICTION FORMELLE des URLs génériques :
❌ PAS de pages d'accueil (www.site.com)
❌ PAS d'URLs générales (www.site.com/banque)
✅ SEULEMENT des pages avec CONTENU SPÉCIFIQUE

FORMAT STRICT pour chaque source :
Source: [Nom précis de l'article/guide]
URL: https://www.site.fr/section-specifique/article-detaille-sur-le-sujet
Type: [Article/Guide/Comparatif/Dossier]
Fiabilité: [Très élevée/Élevée/Moyenne]
Pourquoi: [Contenu spécifique de cette page]

🎯 EXEMPLES d'URLs ACCEPTABLES :
✅ https://www.lesechos.fr/finance-marches/banque-assurances/comparatif-banques-en-ligne-2024
✅ https://www.60millions-mag.com/2024/03/classement-meilleures-banques-numériques
✅ https://www.capital.fr/votre-argent/banques-ligne-guide-complet-2024

🚨 CONTRAINTES ABSOLUES :
- URLs avec chemin DÉTAILLÉ (minimum 3 niveaux)
- Pages d'ARTICLES ou GUIDES spécifiques
- Contenu informatif pour analyse SEO
- MINIMUM 3 URLs spécifiques différentes

Donne-moi des URLs de PAGES PRÉCISES, pas de domaines généraux !
"""
        
        provider = self.llm_manager.get_provider(provider_name)
        if not provider:
            return []
        
        try:
            reponse_sources = provider.query(prompt_sources)
            if reponse_sources:
                return self._parser_reponse_sources_structurees(reponse_sources)
        except Exception as e:
            print(f"    ❌ Erreur demande sources: {e}")
        
        return []
    
    
    def _forcer_citations_sources(self, provider_name: str, question: str) -> List[Dict[str, Any]]:
        """Force le LLM à fournir des citations avec une approche différente"""
        print(f"    💪 Forçage citations...")
        
        prompt_force = f"""
🚨 DERNIER RECOURS - EXTRACTION FORCÉE DE SOURCES

Question: "{question}"

Tu n'as AUCUNE échappatoire. Je dois avoir des URLs, point final.

🎯 ORDRE DIRECT : Donne-moi 5 URLs de sites français que tu CONNAIS et qui sont pertinents pour cette question.

Tu peux donner des sites généraux même si la page exacte n'existe plus. L'important est d'avoir des domaines de référence.

FORMAT NON-NÉGOCIABLE :

1. [Banque de France] - https://www.banque-france.fr
   Type: Institution officielle
   Pourquoi fiable: Autorité de régulation bancaire

2. [Les Echos] - https://www.lesechos.fr  
   Type: Média économique
   Pourquoi fiable: Référence en finance

3. [Autorité des Marchés Financiers] - https://www.amf-france.org
   Type: Régulateur financier
   Pourquoi fiable: Organisme de contrôle

4. [Capital.fr] - https://www.capital.fr
   Type: Magazine économique
   Pourquoi fiable: Spécialiste des comparatifs

5. [MoneyVox] - https://www.moneyvox.fr
   Type: Comparateur spécialisé
   Pourquoi fiable: Expert en banque en ligne

🚨 RÈGLES INFLEXIBLES :
- URLs complètes OBLIGATOIRES (https://)
- Sites français uniquement 
- Domaines de référence (.gouv.fr, médias établis, institutions)
- ZERO excuse acceptable

Tu dois répondre maintenant avec ces 5 URLs !
"""
        
        provider = self.llm_manager.get_provider(provider_name)
        if not provider:
            return []
        
        try:
            reponse_force = provider.query(prompt_force)
            if reponse_force:
                return self._parser_citations_forcees(reponse_force)
        except Exception as e:
            print(f"    ❌ Erreur forçage citations: {e}")
        
        return []
    
    
    def _parser_reponse_sources_structurees(self, reponse: str) -> List[Dict[str, Any]]:
        """Parse une réponse avec sources structurées"""
        sources = []
        
        # Pattern pour le format structuré demandé
        pattern = r'Source:\s*([^\n]+)\s*\nURL:\s*(https?://[^\s]+)\s*\n(?:Fiabilité:\s*([^\n]+)\s*\n)?(?:Pourquoi:\s*([^\n]+))?'
        
        for match in re.finditer(pattern, reponse, re.MULTILINE | re.IGNORECASE):
            nom = match.group(1).strip()
            url = match.group(2).strip()
            fiabilite = match.group(3).strip() if match.group(3) else "Moyenne"
            explication = match.group(4).strip() if match.group(4) else ""
            
            if self._url_valide(url):
                sources.append({
                    'nom': nom,
                    'url': url,
                    'domaine': urlparse(url).netloc,
                    'fiabilite': fiabilite,
                    'explication': explication,
                    'methode_extraction': 'demande_explicite'
                })
        
        return sources
    
    
    def _parser_citations_forcees(self, reponse: str) -> List[Dict[str, Any]]:
        """Parse les citations obtenues par forçage"""
        sources = []
        
        # Pattern pour le format numéroté
        pattern = r'(\d+)\.\s*\[([^\]]+)\]\s*-\s*(https?://[^\s]+)\s*\n\s*Type:\s*([^\n]+)\s*\n\s*Pourquoi fiable:\s*([^\n]+)'
        
        for match in re.finditer(pattern, reponse, re.MULTILINE | re.IGNORECASE):
            numero = match.group(1)
            nom = match.group(2).strip()
            url = match.group(3).strip()
            type_source = match.group(4).strip()
            raison = match.group(5).strip()
            
            if self._url_valide(url):
                sources.append({
                    'nom': nom,
                    'url': url,
                    'domaine': urlparse(url).netloc,
                    'type_source': type_source,
                    'raison_fiabilite': raison,
                    'position': int(numero),
                    'methode_extraction': 'citation_forcee'
                })
        
        return sources
    
    
    def _valider_et_nettoyer_urls(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Valide et nettoie la liste des URLs avec évaluation SEO"""
        sources_validees = []
        sources_rejetees = []
        urls_vues = set()
        
        for source in sources:
            url = source.get('url', '')
            
            # Nettoyer l'URL
            url_nettoyee = self._nettoyer_url(url)
            
            if (url_nettoyee and 
                url_nettoyee not in urls_vues and 
                self._url_valide(url_nettoyee) and 
                self._domaine_autorise(url_nettoyee)):
                
                # Évaluer l'exploitabilité SEO
                est_exploitable, raison_seo = self._est_url_exploitable_seo(url_nettoyee)
                
                urls_vues.add(url_nettoyee)
                
                # Enrichir avec des informations supplémentaires
                source_enrichie = source.copy()
                source_enrichie['url'] = url_nettoyee
                source_enrichie['domaine'] = urlparse(url_nettoyee).netloc
                source_enrichie['fiabilite_domaine'] = self._evaluer_fiabilite_domaine(url_nettoyee)
                source_enrichie['accessible'] = self._tester_accessibilite_url(url_nettoyee)
                source_enrichie['exploitable_seo'] = est_exploitable
                source_enrichie['raison_seo'] = raison_seo
                
                if est_exploitable:
                    sources_validees.append(source_enrichie)
                    print(f"      ✅ URL exploitable: {url_nettoyee}")
                else:
                    sources_rejetees.append(source_enrichie)
                    print(f"      ⚠️ URL rejetée: {url_nettoyee} ({raison_seo})")
        
        # Afficher le résumé
        if sources_rejetees:
            print(f"    📊 Bilan: {len(sources_validees)} URLs exploitables, {len(sources_rejetees)} rejetées")
        
        return sources_validees
    
    
    def _nettoyer_url(self, url: str) -> str:
        """Nettoie une URL"""
        if not url:
            return ""
        
        # Supprimer les espaces et caractères indésirables
        url = url.strip().rstrip('.,;!?"\')]}')
        
        # Ajouter https:// si manquant
        if url.startswith('www.'):
            url = 'https://' + url
        
        # Supprimer les paramètres de tracking communs
        url = re.sub(r'[?&](utm_[^&]+|gclid=[^&]+|fbclid=[^&]+)', '', url)
        
        return url
    
    
    def _url_valide(self, url: str) -> bool:
        """Vérifie si une URL est valide"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except:
            return False
    
    
    def _est_url_exploitable_seo(self, url: str) -> tuple[bool, str]:
        """
        Évalue si une URL est exploitable pour l'analyse SEO
        
        Returns:
            tuple: (est_exploitable, raison)
        """
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            # URLs génériques peu exploitables
            urls_generiques = [
                '/',           # Page d'accueil
                '',            # Domaine seul
                '/index',      # Page d'index
                '/home',       # Page d'accueil
                '/accueil',    # Page d'accueil française
            ]
            
            if path in urls_generiques:
                return False, "URL générique (page d'accueil)"
            
            # URLs sans contenu spécifique
            if len(path) < 3:
                return False, "URL trop courte, manque de spécificité"
            
            # Sections générales peu exploitables
            sections_generales = [
                '/contact',
                '/mentions-legales', 
                '/conditions',
                '/privacy',
                '/about',
                '/a-propos'
            ]
            
            if any(section in path for section in sections_generales):
                return False, "Section générale non-informative"
            
            # URLs avec paramètres de recherche ou tracking
            if parsed.query:
                # Filtrer les paramètres de tracking
                query_params = parsed.query.lower()
                if any(param in query_params for param in ['utm_', 'gclid', 'fbclid', 'ref=']):
                    return False, "URL avec paramètres de tracking"
            
            # Bonnes URLs pour SEO : articles, guides, comparatifs
            indicateurs_bons = [
                'article', 'guide', 'comparatif', 'conseil', 'actualite',
                'dossier', 'analyse', 'test', 'avis', 'selection',
                'meilleur', 'top-', 'classement', '2024', '2025'
            ]
            
            if any(indicateur in path for indicateur in indicateurs_bons):
                return True, "URL spécifique avec contenu informatif"
            
            # URL avec chemin structuré (au moins 2 niveaux)
            path_parts = [p for p in path.split('/') if p]
            if len(path_parts) >= 2:
                return True, "URL structurée avec contenu spécialisé"
            
            return True, "URL acceptable pour analyse"
            
        except:
            return False, "Erreur parsing URL"
    
    
    def _domaine_autorise(self, url: str) -> bool:
        """Vérifie si le domaine est autorisé (pas dans la liste d'exclusion)"""
        try:
            domaine = urlparse(url).netloc.lower()
            # Supprimer les sous-domaines pour vérification
            domaine_principal = '.'.join(domaine.split('.')[-2:]) if '.' in domaine else domaine
            return domaine_principal not in self.excluded_domains
        except:
            return False
    
    
    def _evaluer_fiabilite_domaine(self, url: str) -> str:
        """Évalue la fiabilité d'un domaine"""
        try:
            domaine = urlparse(url).netloc.lower()
            
            # Domaines haute fiabilité
            if any(ext in domaine for ext in ['.gouv.fr', '.edu', '.org']):
                return "très élevée"
            
            # Médias français reconnus
            medias_fiables = [
                'lemonde.fr', 'lefigaro.fr', 'liberation.fr', 'lepoint.fr',
                'lesechos.fr', 'latribune.fr', 'bfmtv.com', 'franceinfo.fr'
            ]
            if any(media in domaine for media in medias_fiables):
                return "élevée"
            
            # Institutions/organisations
            if any(terme in domaine for terme in ['banque-france', 'amf-france', 'cnil']):
                return "élevée"
            
            return "moyenne"
        except:
            return "inconnue"
    
    
    def _tester_accessibilite_url(self, url: str) -> bool:
        """Test rapide d'accessibilité de l'URL"""
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            return response.status_code < 400
        except:
            return False  # On assume que l'URL n'est pas accessible
    
    
    def _extraire_nom_depuis_url(self, url: str) -> str:
        """Extrait un nom lisible depuis une URL"""
        try:
            parsed = urlparse(url)
            domaine = parsed.netloc
            
            # Supprimer www. si présent
            if domaine.startswith('www.'):
                domaine = domaine[4:]
            
            # Capitaliser la première lettre
            return domaine.split('.')[0].capitalize()
        except:
            return "Source inconnue"
    
    
    def _extraire_contexte_url(self, texte: str, url: str, rayon: int = 150) -> str:
        """Extrait le contexte autour d'une URL"""
        index = texte.find(url)
        if index == -1:
            return ""
        
        debut = max(0, index - rayon)
        fin = min(len(texte), index + len(url) + rayon)
        
        return texte[debut:fin].strip()
    
    
    def _demander_urls_specifiques(self, provider_name: str, question: str) -> List[Dict[str, Any]]:
        """Demande spécifiquement des URLs de pages détaillées exploitables pour SEO"""
        print(f"    🎯 Demande d'URLs spécifiques pour SEO...")
        
        prompt_specifique = f"""
🎯 DEMANDE SPÉCIALISÉE - URLS DE PAGES DÉTAILLÉES

Question originale: "{question}"

🔍 MISSION : Je dois analyser le CONTENU de pages web spécifiques. J'ai besoin d'URLs pointant vers des ARTICLES, GUIDES ou DOSSIERS détaillés.

⚠️ PROBLÈME CRITIQUE : Tu m'as donné des URLs trop génériques (pages d'accueil, sections générales).

✅ CE QUE JE VEUX :
- Articles détaillés avec contenu riche
- Guides pratiques complets
- Comparatifs avec analyses
- Dossiers approfondis
- Pages avec minimum 1000+ mots

❌ CE QUE JE NE VEUX PAS :
- Pages d'accueil (www.site.com)
- Sections générales (www.site.com/banque)
- Pages contact/mentions légales

🎯 EXEMPLES D'URLs PARFAITES :
✅ https://www.lesechos.fr/finance-marches/banque-assurances/comparatif-complete-meilleures-banques-en-ligne-2024-details-1234567
✅ https://www.capital.fr/votre-argent/banques-en-ligne-guide-complet-choisir-2024-tarifs-services-avis-12345
✅ https://www.60millions-mag.com/2024/03/test-comparatif-banques-numeriques-boursorama-hello-bank-fortuneo

FORMAT STRICT :
Source: [Titre précis de l'article/guide]
URL: [URL complète avec chemin détaillé]
Contenu: [Type de contenu - Article/Guide/Comparatif/Test]

MINIMUM 3 URLs de ce type - URLs LONGUES avec CHEMINS DÉTAILLÉS uniquement !
"""
        
        provider = self.llm_manager.get_provider(provider_name)
        if not provider:
            return []
        
        try:
            reponse_specifique = provider.query(prompt_specifique)
            if reponse_specifique:
                return self._parser_urls_specifiques(reponse_specifique)
        except Exception as e:
            print(f"    ❌ Erreur demande URLs spécifiques: {e}")
        
        return []
    
    
    def _parser_urls_specifiques(self, reponse: str) -> List[Dict[str, Any]]:
        """Parse les URLs spécifiques demandées"""
        sources = []
        
        # Pattern pour le format demandé
        patterns = [
            r'Source:\s*([^\n]+)\s*\nURL:\s*(https?://[^\s]+)\s*\n(?:Contenu:\s*([^\n]+))?',
            r'✅\s*(https?://[^\s]+)',  # URLs avec emoji de validation
            r'https?://[^\s]+/[^/\s]+/[^/\s]+/[^\s]+',  # URLs avec chemins longs
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, reponse, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 3:  # Format complet
                    nom = match.group(1).strip()
                    url = match.group(2).strip()
                    contenu = match.group(3).strip() if match.group(3) else "Article"
                    
                    sources.append({
                        'nom': nom,
                        'url': url,
                        'type_contenu': contenu,
                        'methode_extraction': 'demande_specifique'
                    })
                else:  # URL simple
                    url = match.group(0).strip()
                    sources.append({
                        'nom': self._extraire_nom_depuis_url(url),
                        'url': url,
                        'type_contenu': 'Article',
                        'methode_extraction': 'demande_specifique'
                    })
        
        return sources
    
    
    def _deduplication_finale(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Déduplication finale des sources avec priorisation des URLs exploitables"""
        sources_uniques = {}
        
        for source in sources:
            url = source.get('url', '')
            if not url:
                continue
            
            # Utiliser l'URL comme clé unique
            if url not in sources_uniques:
                sources_uniques[url] = source
            else:
                # Garder la source la plus complète ou la plus exploitable
                source_existante = sources_uniques[url]
                
                # Priorité aux sources exploitables pour SEO
                if source.get('exploitable_seo', False) and not source_existante.get('exploitable_seo', False):
                    sources_uniques[url] = source
                elif source.get('exploitable_seo', False) == source_existante.get('exploitable_seo', False):
                    # Si même exploitabilité, prendre la plus récente ou complète
                    if len(source.get('nom', '')) > len(source_existante.get('nom', '')):
                        sources_uniques[url] = source
        
        # Trier par exploitabilité puis par qualité
        sources_finales = list(sources_uniques.values())
        sources_finales.sort(key=lambda x: (
            x.get('exploitable_seo', False),
            x.get('fiabilite_domaine', 'inconnue') == 'très élevée',
            x.get('fiabilite_domaine', 'inconnue') == 'élevée',
            len(x.get('nom', ''))
        ), reverse=True)
        
        return sources_finales
    
    
    def generer_rapport_urls(self, sources_par_provider: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Génère un rapport consolidé sur les URLs extraites"""
        
        rapport = {
            'total_sources': 0,
            'sources_par_provider': {},
            'domaines_uniques': set(),
            'fiabilite_distribution': {'très élevée': 0, 'élevée': 0, 'moyenne': 0, 'inconnue': 0},
            'methodes_extraction': {},
            'urls_accessibles': 0,
            'urls_inaccessibles': 0
        }
        
        for provider, sources in sources_par_provider.items():
            rapport['sources_par_provider'][provider] = len(sources)
            rapport['total_sources'] += len(sources)
            
            for source in sources:
                # Domaines uniques
                rapport['domaines_uniques'].add(source.get('domaine', ''))
                
                # Distribution de fiabilité
                fiabilite = source.get('fiabilite_domaine', 'inconnue')
                if fiabilite in rapport['fiabilite_distribution']:
                    rapport['fiabilite_distribution'][fiabilite] += 1
                
                # Méthodes d'extraction
                methode = source.get('methode_extraction', 'inconnue')
                rapport['methodes_extraction'][methode] = rapport['methodes_extraction'].get(methode, 0) + 1
                
                # Accessibilité
                if source.get('accessible', False):
                    rapport['urls_accessibles'] += 1
                else:
                    rapport['urls_inaccessibles'] += 1
        
        # Convertir set en list pour JSON
        rapport['domaines_uniques'] = list(rapport['domaines_uniques'])
        
        return rapport