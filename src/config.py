# -*- coding: utf-8 -*-
"""
Configuration centralisée pour l'analyseur SEO
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# === CHEMINS ET DOSSIERS ===
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PAGES_STORAGE_DIR = DATA_DIR / "pages" 
REPORTS_DIR = PROJECT_ROOT / "reports"
RAW_REPORTS_DIR = REPORTS_DIR / "raw"
SCORES_DIR = REPORTS_DIR / "scores"

# Créer les dossiers s'ils n'existent pas
for directory in [DATA_DIR, PAGES_STORAGE_DIR, REPORTS_DIR, RAW_REPORTS_DIR, SCORES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# === CONFIGURATION API ===
GOOGLE_PAGESPEED_API_KEY = os.getenv("PAGESPEED_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# === PARAMÈTRES D'ANALYSE ===
# LLM
ENABLE_LLM_ANALYSIS = os.getenv("ENABLE_LLM_ANALYSIS", "true").lower() == "true"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # "openai" ou "anthropic"

# Analyses améliorées
ENABLE_ENHANCED_ANALYSIS = os.getenv("ENABLE_ENHANCED_ANALYSIS", "true").lower() == "true"

# Performance
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
REQUEST_TIMEOUT = 30

# Limites de traitement
MAX_TEXT_LENGTH = 1000000  # Pour spaCy
MAX_EXTERNAL_LINKS = 10    # Pour lisibilité

# === SEUILS DE SCORING ===
SCORING_THRESHOLDS = {
    "excellent": 80,
    "bon": 60, 
    "moyen": 40,
    "faible": 0
}

# === MESSAGES UTILISATEUR ===
USER_MESSAGES = {
    "analysis_start": "🔍 Début de l'analyse SEO...",
    "analysis_complete": "✅ Analyse SEO terminée !",
    "error_fetch": "❌ Impossible de récupérer la page web",
    "error_analysis": "❌ Erreur pendant l'analyse",
    "warning_no_api": "⚠️ Clé API manquante, fonctionnalité limitée"
}

def has_api_key(service: str) -> bool:
    """Vérifie si la clé API est disponible pour un service."""
    if service == "pagespeed":
        return bool(GOOGLE_PAGESPEED_API_KEY)
    elif service == "openai":
        return bool(OPENAI_API_KEY)
    elif service == "anthropic":
        return bool(ANTHROPIC_API_KEY)
    return False

def get_analysis_config() -> dict:
    """Retourne la configuration actuelle pour les analyses."""
    return {
        "llm_enabled": ENABLE_LLM_ANALYSIS and (has_api_key("openai") or has_api_key("anthropic")),
        "enhanced_enabled": ENABLE_ENHANCED_ANALYSIS,
        "performance_enabled": has_api_key("pagespeed"),
        "llm_provider": LLM_PROVIDER if ENABLE_LLM_ANALYSIS else None
    }