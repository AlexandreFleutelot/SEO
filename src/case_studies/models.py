# -*- coding: utf-8 -*-
"""
models.py

Modèles de données pour les études de cas SEO.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class CaseStatus(Enum):
    """Statuts possibles d'une étude de cas."""
    DRAFT = "draft"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    ERROR = "error"


class LLMProvider(Enum):
    """Fournisseurs LLM supportés."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic" 
    GOOGLE = "google"
    CUSTOM = "custom"


@dataclass
class SourceURL:
    """Représente une URL source extraite d'une réponse LLM."""
    url: str
    citation_order: int
    mentioned_in_context: str
    reliability_score: float = 0.0
    domain: str = ""
    is_analyzed: bool = False
    analysis_id: Optional[str] = None
    extraction_confidence: float = 0.0


@dataclass 
class LLMResponse:
    """Réponse d'un LLM avec sources extraites."""
    provider: LLMProvider
    model_name: str
    query: str
    response_text: str
    sources: List[SourceURL] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    tokens_used: int = 0
    response_time_ms: int = 0
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompetitorInsight:
    """Insights sur un concurrent basés sur l'analyse SEO."""
    domain: str
    url: str
    seo_score: float
    position_rank: int
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    content_approach: str = ""
    target_keywords: List[str] = field(default_factory=list)
    brand_mentions: List[str] = field(default_factory=list)
    sentiment_score: float = 0.0
    authority_indicators: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GapAnalysis:
    """Analyse des gaps concurrentiels."""
    missing_topics: List[str] = field(default_factory=list)
    underrepresented_keywords: List[str] = field(default_factory=list)
    content_opportunities: List[str] = field(default_factory=list)
    competitive_advantages: List[str] = field(default_factory=list)
    optimization_priorities: List[str] = field(default_factory=list)
    market_positioning: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CaseStudy:
    """Étude de cas complète."""
    id: str
    title: str
    research_question: str
    description: str = ""
    status: CaseStatus = CaseStatus.DRAFT
    created_date: datetime = field(default_factory=datetime.now)
    updated_date: datetime = field(default_factory=datetime.now)
    
    # Configuration LLM
    llm_providers: List[LLMProvider] = field(default_factory=lambda: [LLMProvider.OPENAI])
    max_sources_per_llm: int = 10
    
    # Données collectées
    llm_responses: List[LLMResponse] = field(default_factory=list)
    analyzed_sources: List[SourceURL] = field(default_factory=list)
    competitor_insights: List[CompetitorInsight] = field(default_factory=list)
    
    # Analyses générées
    gap_analysis: Optional[GapAnalysis] = None
    comparative_scores: Dict[str, float] = field(default_factory=dict)
    keyword_analysis: Dict[str, Any] = field(default_factory=dict)
    sentiment_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Métadonnées
    total_sources_found: int = 0
    sources_analyzed: int = 0
    analysis_duration_minutes: float = 0.0
    cost_estimate_usd: float = 0.0
    
    def add_llm_response(self, response: LLMResponse) -> None:
        """Ajoute une réponse LLM à l'étude."""
        self.llm_responses.append(response)
        self.total_sources_found += len(response.sources)
        self.updated_date = datetime.now()
    
    def add_analyzed_source(self, source: SourceURL) -> None:
        """Marque une source comme analysée."""
        source.is_analyzed = True
        if source not in self.analyzed_sources:
            self.analyzed_sources.append(source)
        self.sources_analyzed = len(self.analyzed_sources)
        self.updated_date = datetime.now()
    
    def get_progress_percentage(self) -> float:
        """Calcule le pourcentage de progression de l'analyse."""
        if self.total_sources_found == 0:
            return 0.0
        return (self.sources_analyzed / self.total_sources_found) * 100
    
    def get_all_domains(self) -> List[str]:
        """Retourne tous les domaines uniques trouvés."""
        domains = set()
        for response in self.llm_responses:
            for source in response.sources:
                if source.domain:
                    domains.add(source.domain)
        return sorted(list(domains))
    
    def get_sources_by_domain(self, domain: str) -> List[SourceURL]:
        """Retourne toutes les sources pour un domaine donné."""
        sources = []
        for response in self.llm_responses:
            for source in response.sources:
                if source.domain == domain:
                    sources.append(source)
        return sources
    
    def update_status(self, status: CaseStatus) -> None:
        """Met à jour le statut de l'étude."""
        self.status = status
        self.updated_date = datetime.now()


@dataclass
class CaseStudyReport:
    """Rapport final d'une étude de cas."""
    case_study_id: str
    title: str
    executive_summary: str
    generated_date: datetime = field(default_factory=datetime.now)
    
    # Données de synthèse
    key_findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    competitive_landscape: Dict[str, Any] = field(default_factory=dict)
    market_opportunities: List[str] = field(default_factory=list)
    
    # Visualisations et métriques
    performance_matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)
    keyword_clusters: Dict[str, List[str]] = field(default_factory=dict)
    sentiment_breakdown: Dict[str, float] = field(default_factory=dict)
    
    # Métadonnées d'export
    export_formats: List[str] = field(default_factory=lambda: ["json", "pdf", "excel"])
    file_paths: Dict[str, str] = field(default_factory=dict)
    
    def add_finding(self, finding: str, priority: str = "medium") -> None:
        """Ajoute une découverte clé avec priorité."""
        self.key_findings.append(f"[{priority.upper()}] {finding}")
    
    def add_recommendation(self, recommendation: str, impact: str = "medium") -> None:
        """Ajoute une recommandation avec niveau d'impact."""
        self.recommendations.append(f"[Impact {impact.upper()}] {recommendation}")