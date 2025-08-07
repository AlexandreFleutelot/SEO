# -*- coding: utf-8 -*-
"""
llm_source_extractor.py

Extracteur de sources depuis les réponses LLM pour les études de cas.
"""

import re
import os
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse, urljoin
from datetime import datetime

import requests
from openai import OpenAI
from anthropic import Anthropic

from .models import LLMResponse, SourceURL, LLMProvider


class LLMSourceExtractor:
    """Extracteur de sources depuis différents LLM."""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.google_client = None
        
        # Initialiser les clients disponibles
        self._init_clients()
        
        # Patterns pour extraire les URLs
        self.url_patterns = [
            r'https?://[^\s\)]+',
            r'www\.[^\s\)]+',
            r'\[([^\]]+)\]\((https?://[^\)]+)\)',  # Markdown links
            r'<(https?://[^>]+)>',  # Angular brackets
            r'"(https?://[^"]+)"',  # Quoted URLs
            r"'(https?://[^']+)'"   # Single quoted URLs
        ]
        
        # Prompts optimisés pour l'extraction de sources
        self.extraction_prompts = {
            "main_query": """Réponds à cette question de façon détaillée: "{question}"

🔗 CITATION DES SOURCES OBLIGATOIRE:
- Cite tes sources avec les URLs complètes et exactes
- Utilise ce format précis: "Source: [Nom du site] - URL: https://exemple.com/page-complete"
- Fournis 8-12 sources fiables et récentes
- Privilégie les sites d'autorité (gouvernementaux, institutionnels, presse reconnue)
- Évite Wikipedia et les forums généralistes
- Assure-toi que chaque URL est complète et accessible

EXEMPLE DE FORMAT ATTENDU:
Source: AMF France - URL: https://www.amf-france.org/fr/espace-epargnants/bien-investir/assurance-vie
Source: Les Echos - URL: https://www.lesechos.fr/finance-marches/banques/assurance-vie-guide-complet

Réponds maintenant en citant tes sources avec les URLs complètes.""",
            
            "structured_query": """Pour la question: "{question}"

Réponds au format JSON structuré suivant:
{{
  "reponse": "Ta réponse détaillée ici",
  "sources": [
    {{
      "nom": "Nom du site",
      "url": "https://url-complete.com/page",
      "pertinence": "Pourquoi cette source est pertinente",
      "fiabilite": "1-10"
    }}
  ]
}}

🚨 IMPORTANT: Fournis uniquement des URLs complètes, vérifiées et accessibles.""",
            
            "source_verification": """Analyse cette réponse et extrais UNIQUEMENT les URLs mentionnées. 
Retourne un JSON avec cette structure:
{{
  "urls": [
    {{
      "url": "https://exemple.com",
      "context": "Contexte où cette URL est mentionnée",
      "confidence": 0.9,
      "source_name": "Nom de la source"
    }}
  ]
}}

Réponse à analyser:
{response_text}""",
            
            "competitive_query": """ANALYSE CONCURRENTIELLE pour: "{question}"

🎯 Mission: Identifie les 10 meilleurs sites web traitant ce sujet

📋 Pour chaque site, fournis:
1. URL exacte et complète
2. Raison de sa pertinence
3. Score d'autorité (1-10)
4. Type de contenu (guide, article, officiel, etc.)

✅ Format obligatoire:
Site: [Nom complet] | URL: https://site-complet.com/page | Autorité: X/10 | Type: [guide/article/officiel] | Pertinence: [explication courte]

🔗 Cite tes sources avec les URLs complètes et vérifiées uniquement.""",
            
            "follow_up_sources": """Tu as mentionné {count} sources pour: "{question}"

🔄 Peux-tu me donner 5-8 sources supplémentaires de qualité sur ce même sujet ?

🚨 RÈGLES STRICTES:
- URLs complètes uniquement (https://...)
- Sources différentes de celles déjà mentionnées
- Sites fiables et reconnus dans le domaine
- Format: Source: [Nom] - URL: [URL complète] - Spécialité: [pourquoi cette source]

Cite tes sources avec les URLs complètes."""
        }
    
    def _init_clients(self):
        """Initialise les clients LLM disponibles."""
        try:
            if os.getenv('OPENAI_API_KEY'):
                self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                print("✅ Client OpenAI initialisé")
        except Exception as e:
            print(f"⚠️ Erreur initialisation OpenAI: {e}")
        
        try:
            if os.getenv('ANTHROPIC_API_KEY'):
                self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
                print("✅ Client Anthropic initialisé")
        except Exception as e:
            print(f"⚠️ Erreur initialisation Anthropic: {e}")
    
    def extract_sources_multi_llm(
        self, 
        research_question: str, 
        providers: List[LLMProvider] = None,
        max_sources_per_provider: int = 10,
        use_follow_up: bool = True
    ) -> List[LLMResponse]:
        """Extrait les sources depuis plusieurs LLM avec stratégies multiples."""
        
        if providers is None:
            providers = [LLMProvider.OPENAI, LLMProvider.ANTHROPIC]
        
        responses = []
        
        for provider in providers:
            print(f"🤖 Interrogation de {provider.value}...")
            
            try:
                # 1. Requête principale
                response = self._query_llm(provider, research_question)
                if response:
                    sources = self._extract_urls_from_response(response.response_text)
                    print(f"📊 Extraction initiale: {len(sources)} sources")
                    
                    # 2. Requête de suivi si peu de sources obtenues
                    if use_follow_up and len(sources) < max_sources_per_provider * 0.7:
                        print(f"🔄 Tentative d'obtenir plus de sources...")
                        follow_up_response = self._query_llm_follow_up(provider, research_question, len(sources))
                        if follow_up_response:
                            additional_sources = self._extract_urls_from_response(follow_up_response.response_text)
                            # Éviter les doublons
                            existing_urls = {s.url for s in sources}
                            new_sources = [s for s in additional_sources if s.url not in existing_urls]
                            sources.extend(new_sources)
                            print(f"➕ {len(new_sources)} sources supplémentaires")
                    
                    # 3. Validation et nettoyage avancés
                    sources = self._advanced_url_validation(sources)
                    
                    # Limiter le nombre de sources
                    sources = sources[:max_sources_per_provider]
                    
                    # Enrichir les sources
                    for i, source in enumerate(sources):
                        source.citation_order = i + 1
                        source.domain = self._extract_domain(source.url)
                        source.reliability_score = self._estimate_reliability(source.url)
                    
                    response.sources = sources
                    responses.append(response)
                    
                    print(f"✅ {len(sources)} sources finales extraites de {provider.value}")
                else:
                    print(f"❌ Échec de l'interrogation de {provider.value}")
                    
            except Exception as e:
                print(f"❌ Erreur avec {provider.value}: {e}")
                continue
        
        # 4. Déduplication croisée entre providers
        responses = self._deduplicate_across_providers(responses)
        
        return responses
    
    def _query_llm(self, provider: LLMProvider, question: str) -> Optional[LLMResponse]:
        """Interroge un LLM spécifique."""
        
        start_time = time.time()
        
        if provider == LLMProvider.OPENAI and self.openai_client:
            return self._query_openai(question, start_time)
        elif provider == LLMProvider.ANTHROPIC and self.anthropic_client:
            return self._query_anthropic(question, start_time)
        else:
            print(f"⚠️ Provider {provider.value} non disponible ou non configuré")
            return None
    
    def _query_openai(self, question: str, start_time: float) -> Optional[LLMResponse]:
        """Interroge OpenAI GPT."""
        try:
            prompt = self.extraction_prompts["main_query"].format(question=question)
            
            completion = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Tu es un expert en recherche web qui cite toujours ses sources avec des URLs précises."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            response_time = int((time.time() - start_time) * 1000)
            
            return LLMResponse(
                provider=LLMProvider.OPENAI,
                model_name="gpt-4o",
                query=question,
                response_text=completion.choices[0].message.content,
                timestamp=datetime.now(),
                tokens_used=completion.usage.total_tokens,
                response_time_ms=response_time
            )
            
        except Exception as e:
            print(f"❌ Erreur OpenAI: {e}")
            return None
    
    def _query_anthropic(self, question: str, start_time: float) -> Optional[LLMResponse]:
        """Interroge Anthropic Claude."""
        try:
            prompt = self.extraction_prompts["main_query"].format(question=question)
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.3,
                messages=[{
                    "role": "user", 
                    "content": prompt
                }]
            )
            
            response_time = int((time.time() - start_time) * 1000)
            
            return LLMResponse(
                provider=LLMProvider.ANTHROPIC,
                model_name="claude-3-5-sonnet-20241022",
                query=question,
                response_text=response.content[0].text,
                timestamp=datetime.now(),
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                response_time_ms=response_time
            )
            
        except Exception as e:
            print(f"❌ Erreur Anthropic: {e}")
            return None
    
    def _extract_urls_from_response(self, response_text: str) -> List[SourceURL]:
        """Extrait les URLs d'une réponse LLM."""
        urls = []
        found_urls = set()
        
        # Appliquer tous les patterns de recherche
        for pattern in self.url_patterns:
            matches = re.finditer(pattern, response_text, re.IGNORECASE)
            
            for match in matches:
                # Extraire l'URL (gérer les groupes de capture)
                if match.groups():
                    url = match.group(1) if len(match.groups()) >= 1 else match.group()
                else:
                    url = match.group()
                
                # Nettoyer l'URL
                url = self._clean_url(url)
                
                # Éviter les doublons
                if url and url not in found_urls and self._is_valid_url(url):
                    found_urls.add(url)
                    
                    # Extraire le contexte autour de l'URL
                    context_start = max(0, match.start() - 100)
                    context_end = min(len(response_text), match.end() + 100)
                    context = response_text[context_start:context_end].strip()
                    
                    # Calculer la confiance d'extraction
                    confidence = self._calculate_extraction_confidence(url, context)
                    
                    urls.append(SourceURL(
                        url=url,
                        citation_order=0,  # Sera défini plus tard
                        mentioned_in_context=context,
                        extraction_confidence=confidence
                    ))
        
        # Trier par confiance d'extraction
        urls.sort(key=lambda x: x.extraction_confidence, reverse=True)
        
        return urls
    
    def _clean_url(self, url: str) -> str:
        """Nettoie et normalise une URL."""
        if not url:
            return ""
        
        # Supprimer les caractères indésirables
        url = url.strip('.,;:!?()[]{}"\' \t\n\r')
        
        # Ajouter le protocole si manquant
        if url.startswith('www.') and not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Corrections communes
        url = url.replace(' ', '%20')
        
        return url
    
    def _is_valid_url(self, url: str) -> bool:
        """Vérifie si une URL est valide."""
        try:
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc]) and parsed.scheme in ['http', 'https']
        except:
            return False
    
    def _extract_domain(self, url: str) -> str:
        """Extrait le domaine d'une URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            return domain.replace('www.', '')
        except:
            return ""
    
    def _estimate_reliability(self, url: str) -> float:
        """Estime la fiabilité d'une source basée sur son domaine."""
        domain = self._extract_domain(url).lower()
        
        # Domaines hautement fiables
        high_authority = [
            'wikipedia.org', 'gov.', '.edu', 'scholar.google.com',
            'nature.com', 'science.org', 'pubmed.ncbi.nlm.nih.gov'
        ]
        
        # Domaines de presse reconnus
        news_authority = [
            'lemonde.fr', 'lefigaro.fr', 'liberation.fr',
            'bbc.com', 'reuters.com', 'ap.org',
            'wsj.com', 'ft.com', 'economist.com'
        ]
        
        # Domaines spécialisés finance/assurance
        finance_authority = [
            'banque-france.fr', 'amf-france.org', 'acpr.banque-france.fr',
            'cbanque.com', 'moneyvox.fr', 'boursorama.com'
        ]
        
        for auth_domain in high_authority:
            if auth_domain in domain:
                return 0.9
        
        for news_domain in news_authority:
            if news_domain in domain:
                return 0.8
        
        for finance_domain in finance_authority:
            if finance_domain in domain:
                return 0.75
        
        # Domaines commerciaux génériques
        if any(tld in domain for tld in ['.com', '.fr', '.org']):
            return 0.6
        
        return 0.5
    
    def _calculate_extraction_confidence(self, url: str, context: str) -> float:
        """Calcule la confiance d'extraction d'une URL."""
        confidence = 0.5  # Base
        
        # Bonus si l'URL est dans un contexte de citation
        citation_indicators = ['source:', 'référence:', 'voir:', 'lien:', 'url:', 'site:']
        if any(indicator in context.lower() for indicator in citation_indicators):
            confidence += 0.3
        
        # Bonus si l'URL semble complète et propre
        if url.startswith('https://') and len(url) > 20:
            confidence += 0.1
        
        # Malus si l'URL semble tronquée
        if url.endswith('...') or len(url) < 10:
            confidence -= 0.2
        
        return min(1.0, max(0.0, confidence))
    
    def verify_urls_accessibility(self, sources: List[SourceURL]) -> List[SourceURL]:
        """Vérifie l'accessibilité des URLs et met à jour les scores."""
        
        print(f"🔍 Vérification de l'accessibilité de {len(sources)} URLs...")
        
        for source in sources:
            try:
                response = requests.head(
                    source.url, 
                    timeout=10, 
                    allow_redirects=True,
                    headers={'User-Agent': 'Mozilla/5.0 (compatible; SEO-Analyzer/1.0)'}
                )
                
                if response.status_code == 200:
                    source.reliability_score += 0.1  # Bonus d'accessibilité
                    print(f"✅ {source.domain} - accessible")
                elif response.status_code in [301, 302]:
                    # Redirection - acceptable mais pas optimal
                    source.reliability_score += 0.05
                    print(f"🔄 {source.domain} - redirection")
                else:
                    source.reliability_score -= 0.2
                    print(f"⚠️ {source.domain} - code {response.status_code}")
                    
            except requests.RequestException as e:
                source.reliability_score -= 0.3  # Pénalité d'inaccessibilité
                print(f"❌ {source.domain} - inaccessible: {str(e)[:50]}...")
                
            except Exception as e:
                print(f"⚠️ Erreur vérification {source.domain}: {e}")
        
        # Recalculer les scores entre 0 et 1
        for source in sources:
            source.reliability_score = max(0.0, min(1.0, source.reliability_score))
        
        return sources
    
    def _query_llm_follow_up(self, provider: LLMProvider, question: str, current_count: int) -> Optional[LLMResponse]:
        """Requête de suivi pour obtenir plus de sources."""
        
        start_time = time.time()
        follow_up_prompt = self.extraction_prompts["follow_up_sources"].format(
            count=current_count, 
            question=question
        )
        
        try:
            if provider == LLMProvider.OPENAI and self.openai_client:
                completion = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Tu es un expert en recherche qui connaît de nombreuses sources fiables dans tous les domaines."},
                        {"role": "user", "content": follow_up_prompt}
                    ],
                    max_tokens=1500,
                    temperature=0.4
                )
                
                response_time = int((time.time() - start_time) * 1000)
                return LLMResponse(
                    provider=provider,
                    model_name="gpt-4o",
                    query=f"Follow-up: {question}",
                    response_text=completion.choices[0].message.content,
                    timestamp=datetime.now(),
                    tokens_used=completion.usage.total_tokens,
                    response_time_ms=response_time
                )
                
            elif provider == LLMProvider.ANTHROPIC and self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1500,
                    temperature=0.4,
                    messages=[{"role": "user", "content": follow_up_prompt}]
                )
                
                response_time = int((time.time() - start_time) * 1000)
                return LLMResponse(
                    provider=provider,
                    model_name="claude-3-5-sonnet-20241022",
                    query=f"Follow-up: {question}",
                    response_text=response.content[0].text,
                    timestamp=datetime.now(),
                    tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                    response_time_ms=response_time
                )
                
        except Exception as e:
            print(f"⚠️ Erreur requête de suivi {provider.value}: {e}")
            return None
    
    def _advanced_url_validation(self, sources: List[SourceURL]) -> List[SourceURL]:
        """Validation avancée des URLs extraites."""
        
        validated_sources = []
        
        for source in sources:
            # 1. Validation de base
            if not self._is_valid_url(source.url):
                continue
                
            # 2. Filtrer les URLs trop courtes ou suspectes
            if len(source.url) < 15:
                continue
            
            # 2b. Filtrer les URLs de raccourcissement (shorteners)
            shortener_domains = ['bit.ly', 't.co', 'tinyurl.com', 'goo.gl', 'ow.ly', 'a.co', 'amzn.to', 'youtu.be']
            if any(shortener in source.url.lower() for shortener in shortener_domains):
                continue
                
            # 3. Filtrer les URLs de recherche Google/Bing
            if any(search_engine in source.url.lower() for search_engine in 
                   ['google.com/search', 'bing.com/search', 'yahoo.com/search']):
                continue
                
            # 4. Filtrer les URLs de réseaux sociaux (sauf pages officielles)
            if any(social in source.url.lower() for social in 
                   ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com']):
                # Garder seulement si c'est une page officielle d'entreprise
                if not any(official in source.url.lower() for official in 
                          ['/company/', '/official/', '/pages/']):
                    continue
            
            # 5. Privilégier les URLs avec des paths significatifs
            parsed = urlparse(source.url)
            if parsed.path and len(parsed.path) > 1:
                source.extraction_confidence += 0.1
                
            # 6. Bonus pour les URLs avec des mots-clés pertinents dans le path
            relevant_keywords = ['guide', 'article', 'blog', 'ressource', 'documentation']
            if any(keyword in parsed.path.lower() for keyword in relevant_keywords):
                source.extraction_confidence += 0.05
                
            validated_sources.append(source)
        
        # Trier par confiance d'extraction
        validated_sources.sort(key=lambda x: x.extraction_confidence, reverse=True)
        
        print(f"🔍 Validation avancée: {len(validated_sources)}/{len(sources)} sources conservées")
        return validated_sources
    
    def _deduplicate_across_providers(self, responses: List[LLMResponse]) -> List[LLMResponse]:
        """Dédupliquer les sources entre différents providers."""
        
        if len(responses) <= 1:
            return responses
        
        # Collecter toutes les URLs avec leur provider d'origine
        url_to_provider = {}
        url_to_best_source = {}
        
        for response in responses:
            for source in response.sources:
                url = source.url
                if url not in url_to_provider:
                    url_to_provider[url] = []
                    url_to_best_source[url] = source
                else:
                    # Garder la source avec le meilleur score de confiance
                    if source.extraction_confidence > url_to_best_source[url].extraction_confidence:
                        url_to_best_source[url] = source
                
                url_to_provider[url].append(response.provider.value)
        
        # Mettre à jour les réponses avec les sources dédupliquées
        for response in responses:
            unique_sources = []
            for source in response.sources:
                if url_to_best_source[source.url] == source:  # C'est la meilleure version
                    # Ajouter des métadonnées sur la duplication
                    if len(url_to_provider[source.url]) > 1:
                        source.mentioned_in_context += f" [Trouvée par: {', '.join(url_to_provider[source.url])}]"
                        source.reliability_score += 0.1  # Bonus pour la validation croisée
                    unique_sources.append(source)
            
            response.sources = unique_sources
            response.extraction_metadata['deduplicated'] = True
        
        total_unique = sum(len(r.sources) for r in responses)
        print(f"✨ Déduplication terminée: {total_unique} sources uniques conservées")
        
        return responses
    
    def try_structured_extraction(self, provider: LLMProvider, question: str) -> Optional[LLMResponse]:
        """Tente une extraction structurée au format JSON."""
        
        if provider == LLMProvider.OPENAI and self.openai_client:
            try:
                start_time = time.time()
                prompt = self.extraction_prompts["structured_query"].format(question=question)
                
                completion = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Tu réponds uniquement en JSON valide avec les sources citées."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.2
                )
                
                response_text = completion.choices[0].message.content
                
                # Tenter de parser le JSON
                try:
                    response_json = json.loads(response_text)
                    sources = []
                    
                    if 'sources' in response_json:
                        for i, source_data in enumerate(response_json['sources']):
                            if 'url' in source_data and 'nom' in source_data:
                                source = SourceURL(
                                    url=self._clean_url(source_data['url']),
                                    citation_order=i + 1,
                                    mentioned_in_context=source_data.get('pertinence', ''),
                                    extraction_confidence=0.9  # JSON structuré = haute confiance
                                )
                                source.domain = self._extract_domain(source.url)
                                source.reliability_score = self._estimate_reliability(source.url)
                                sources.append(source)
                    
                    response_time = int((time.time() - start_time) * 1000)
                    llm_response = LLMResponse(
                        provider=provider,
                        model_name="gpt-4o-structured",
                        query=question,
                        response_text=response_json.get('reponse', response_text),
                        timestamp=datetime.now(),
                        tokens_used=completion.usage.total_tokens,
                        response_time_ms=response_time,
                        sources=sources
                    )
                    llm_response.extraction_metadata['structured'] = True
                    
                    print(f"✅ Extraction JSON structurée: {len(sources)} sources")
                    return llm_response
                    
                except json.JSONDecodeError:
                    print("⚠️ Réponse JSON malformée, utilisation extraction standard")
                    return None
                    
            except Exception as e:
                print(f"❌ Erreur extraction structurée: {e}")
                return None
        
        return None