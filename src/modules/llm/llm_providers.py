# -*- coding: utf-8 -*-
"""
LLM Providers - Gestion des différents fournisseurs d'IA
Classes unifiées pour OpenAI, Anthropic et Google Gemini
"""

import requests
import json
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

from ...config import (
    OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_GEMINI_API_KEY, 
    OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS,
    ANTHROPIC_MODEL, ANTHROPIC_TEMPERATURE, ANTHROPIC_MAX_TOKENS,
    GEMINI_MODEL, GEMINI_TEMPERATURE, GEMINI_MAX_TOKENS,
    REQUEST_TIMEOUT, has_api_key
)


class LLMProvider(ABC):
    """Interface abstraite pour tous les providers LLM"""
    
    def __init__(self, name: str):
        self.name = name
        
    @abstractmethod
    def is_available(self) -> bool:
        """Vérifie si le provider est disponible (clé API configurée)"""
        pass
    
    @abstractmethod
    def query(self, prompt: str) -> Optional[str]:
        """Envoie une requête au LLM et retourne la réponse"""
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retourne les informations sur le modèle utilisé"""
        return {
            'provider': self.name,
            'available': self.is_available()
        }


class OpenAIProvider(LLMProvider):
    """Provider pour l'API OpenAI avec modèles configurables"""
    
    def __init__(self):
        super().__init__('openai')
        self.model = OPENAI_MODEL
        self.temperature = OPENAI_TEMPERATURE
        self.max_tokens = OPENAI_MAX_TOKENS
        self.api_key = OPENAI_API_KEY
    
    def is_available(self) -> bool:
        return has_api_key("openai")
    
    def query(self, prompt: str) -> Optional[str]:
        """Interroge l'API OpenAI"""
        if not self.is_available():
            return None
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model,
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.3,
                'max_tokens': 4000
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"❌ Erreur OpenAI: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur OpenAI: {e}")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        info = super().get_model_info()
        info.update({
            'model': self.model,
            'max_tokens': 4000,
            'temperature': 0.3
        })
        return info


class AnthropicProvider(LLMProvider):
    """Provider pour l'API Anthropic (Claude)"""
    
    def __init__(self):
        super().__init__('anthropic')
        self.model = 'claude-3-5-sonnet-20241022'
        self.api_key = ANTHROPIC_API_KEY
    
    def is_available(self) -> bool:
        return has_api_key("anthropic")
    
    def query(self, prompt: str) -> Optional[str]:
        """Interroge l'API Anthropic"""
        if not self.is_available():
            return None
            
        try:
            headers = {
                'x-api-key': self.api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            data = {
                'model': self.model,
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.3,
                'max_tokens': 4000
            }
            
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=data,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['content'][0]['text']
            else:
                print(f"❌ Erreur Anthropic: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur Anthropic: {e}")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        info = super().get_model_info()
        info.update({
            'model': self.model,
            'max_tokens': 4000,
            'temperature': 0.3
        })
        return info


class GeminiProvider(LLMProvider):
    """Provider pour l'API Google Gemini"""
    
    def __init__(self):
        super().__init__('gemini')
        self.model = 'gemini-1.5-pro-latest'
        self.api_key = GOOGLE_GEMINI_API_KEY
    
    def is_available(self) -> bool:
        return has_api_key("gemini")
    
    def query(self, prompt: str) -> Optional[str]:
        """Interroge l'API Google Gemini"""
        if not self.is_available():
            return None
            
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            data = {
                'contents': [{
                    'parts': [{'text': prompt}]
                }],
                'generationConfig': {
                    'temperature': 0.3,
                    'maxOutputTokens': 4000,
                    'topP': 0.8,
                    'topK': 10
                }
            }
            
            url = f'https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}'
            
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    return result['candidates'][0]['content']['parts'][0]['text']
                else:
                    print("❌ Réponse Gemini vide ou malformée")
                    return None
            else:
                print(f"❌ Erreur Gemini: {response.status_code}")
                if response.text:
                    print(f"   Détails: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur Gemini: {e}")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        info = super().get_model_info()
        info.update({
            'model': self.model,
            'max_tokens': 4000,
            'temperature': 0.3,
            'topP': 0.8,
            'topK': 10
        })
        return info


class LLMProviderManager:
    """Gestionnaire centralisé pour tous les providers LLM"""
    
    def __init__(self):
        self.providers = {
            'openai': OpenAIProvider(),
            'anthropic': AnthropicProvider(),
            'gemini': GeminiProvider()
        }
        self.available_providers = self._detect_available_providers()
    
    def _detect_available_providers(self) -> Dict[str, LLMProvider]:
        """Détecte automatiquement les providers disponibles"""
        available = {}
        
        for name, provider in self.providers.items():
            if provider.is_available():
                available[name] = provider
                print(f"✅ {name.upper()} API disponible")
            else:
                print(f"⚠️ {name.upper()} API non configurée")
        
        return available
    
    def get_available_providers(self) -> Dict[str, LLMProvider]:
        """Retourne les providers disponibles"""
        return self.available_providers
    
    def get_provider(self, name: str) -> Optional[LLMProvider]:
        """Retourne un provider spécifique s'il est disponible"""
        return self.available_providers.get(name)
    
    def query_provider(self, provider_name: str, prompt: str) -> Optional[str]:
        """Query un provider spécifique"""
        provider = self.get_provider(provider_name)
        if provider:
            return provider.query(prompt)
        return None
    
    def query_all_providers(self, prompt: str) -> Dict[str, Optional[str]]:
        """Query tous les providers disponibles avec le même prompt"""
        results = {}
        
        for name, provider in self.available_providers.items():
            print(f"🎯 Interrogation de {name.upper()}...")
            try:
                response = provider.query(prompt)
                results[name] = response
                if response:
                    print(f"✅ {name.upper()} : réponse reçue ({len(response)} caractères)")
                else:
                    print(f"❌ {name.upper()} : pas de réponse")
            except Exception as e:
                print(f"❌ {name.upper()} : erreur {e}")
                results[name] = None
        
        return results
    
    def get_all_model_info(self) -> Dict[str, Dict[str, Any]]:
        """Retourne les informations de tous les modèles disponibles"""
        return {
            name: provider.get_model_info() 
            for name, provider in self.available_providers.items()
        }
    
    def has_available_providers(self) -> bool:
        """Vérifie s'il y a au moins un provider disponible"""
        return len(self.available_providers) > 0