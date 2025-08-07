# -*- coding: utf-8 -*-
"""
llm_analysis.py

AI-powered content analysis using Large Language Models (OpenAI GPT or Anthropic Claude).
This module provides advanced SEO metrics that require natural language understanding:

- Content Quality & E-A-T Assessment
- Search Intent Analysis
- Topical Coverage & Semantic Analysis  
- User Experience & Engagement
- Featured Snippet & SERP Potential
- Brand & Communication Analysis
"""

import os
import json
import time
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import LLM clients
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class LLMAnalyzer:
    """AI-powered content analyzer using OpenAI or Anthropic APIs."""
    
    def __init__(self):
        self.provider = os.getenv('LLM_PROVIDER', 'openai').lower()
        self.enabled = os.getenv('ENABLE_LLM_ANALYSIS', 'true').lower() == 'true'
        self.timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        
        # Initialize the appropriate client
        self.client = None
        if self.enabled:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the LLM client based on the configured provider."""
        if self.provider == 'openai' and OPENAI_AVAILABLE:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = OpenAI(api_key=api_key)
                self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
                self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '2000'))
                self.temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.3'))
            else:
                print("⚠️  OpenAI API key not found. LLM analysis disabled.")
                self.enabled = False
        
        elif self.provider == 'anthropic' and ANTHROPIC_AVAILABLE:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.client = Anthropic(api_key=api_key)
                self.model = os.getenv('ANTHROPIC_MODEL', 'claude-3-haiku-20240307')
                self.max_tokens = int(os.getenv('ANTHROPIC_MAX_TOKENS', '2000'))
                self.temperature = float(os.getenv('ANTHROPIC_TEMPERATURE', '0.3'))
            else:
                print("⚠️  Anthropic API key not found. LLM analysis disabled.")
                self.enabled = False
        else:
            print(f"⚠️  LLM provider '{self.provider}' not available or configured. LLM analysis disabled.")
            self.enabled = False
    
    def _make_api_call(self, prompt: str) -> Optional[str]:
        """Make an API call to the configured LLM provider."""
        if not self.enabled or not self.client:
            return None
        
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert SEO analyst. Provide precise, actionable analysis in JSON format."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    timeout=self.timeout
                )
                return response.choices[0].message.content
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    timeout=self.timeout
                )
                return response.content[0].text
                
        except Exception as e:
            print(f"⚠️  LLM API call failed: {str(e)}")
            return None
        
        return None

    def analyze_content_quality_eat(self, content: str, title: str, url: str) -> Dict[str, Any]:
        """
        6.1 Content Quality & E-A-T Assessment
        Analyzes content for quality, expertise, authoritativeness, and trustworthiness.
        """
        if not self.enabled:
            return {"error": "LLM analysis disabled", "scores": {}}
        
        prompt = f"""
Analyze the following webpage content for SEO quality and E-A-T (Expertise, Authoritativeness, Trustworthiness).

URL: {url}
Title: {title}

Content: {content[:3000]}...

Evaluate and score each aspect from 1-10 where 10 is excellent:

Return ONLY a JSON object with this structure:
{{
    "content_quality_score": <1-10>,
    "expertise_score": <1-10>,
    "authoritativeness_score": <1-10>,
    "trustworthiness_score": <1-10>,
    "overall_eat_score": <1-10>,
    "strengths": ["<strength1>", "<strength2>"],
    "weaknesses": ["<weakness1>", "<weakness2>"],
    "recommendations": ["<rec1>", "<rec2>"]
}}

Focus on: factual accuracy, depth of knowledge, source citations, author credentials, clear writing, comprehensive coverage.
"""
        
        response = self._make_api_call(prompt)
        if not response:
            return {"error": "API call failed", "scores": {}}
        
        try:
            # Clean response - remove markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove ```
            cleaned_response = cleaned_response.strip()
            
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response", "raw_response": response}

    def analyze_search_intent(self, content: str, title: str, url: str) -> Dict[str, Any]:
        """
        6.2 Search Intent Analysis
        Determines search intent fulfillment and content-query alignment.
        """
        if not self.enabled:
            return {"error": "LLM analysis disabled"}
        
        prompt = f"""
Analyze the search intent and query alignment for this webpage content.

URL: {url}
Title: {title}

Content: {content[:3000]}...

Analyze the primary search intent and how well the content fulfills user needs.

Return ONLY a JSON object with this structure:
{{
    "primary_intent": "<informational|navigational|transactional|commercial>",
    "secondary_intents": ["<intent1>", "<intent2>"],
    "intent_fulfillment_score": <1-10>,
    "query_alignment_score": <1-10>,
    "target_keywords_identified": ["<keyword1>", "<keyword2>"],
    "user_satisfaction_potential": <1-10>,
    "content_intent_match": "<excellent|good|fair|poor>",
    "recommendations": ["<rec1>", "<rec2>"]
}}

Consider: what users are likely searching for, how well content answers their questions, call-to-actions, next steps provided.
"""
        
        response = self._make_api_call(prompt)
        if not response:
            return {"error": "API call failed"}
        
        try:
            # Clean response - remove markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove ```
            cleaned_response = cleaned_response.strip()
            
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response", "raw_response": response}

    def analyze_topical_coverage(self, content: str, title: str) -> Dict[str, Any]:
        """
        6.3 Topical Coverage & Semantic Analysis
        Evaluates topic completeness and semantic richness.
        """
        if not self.enabled:
            return {"error": "LLM analysis disabled"}
        
        prompt = f"""
Analyze the topical coverage and semantic richness of this content.

Title: {title}

Content: {content[:3000]}...

Evaluate how comprehensively the content covers its main topic and related subtopics.

Return ONLY a JSON object with this structure:
{{
    "main_topic": "<identified_main_topic>",
    "topic_completeness_score": <1-10>,
    "semantic_richness_score": <1-10>,
    "subtopics_covered": ["<subtopic1>", "<subtopic2>"],
    "missing_subtopics": ["<missing1>", "<missing2>"],
    "content_depth_level": "<surface|moderate|deep|expert>",
    "related_concepts_coverage": <1-10>,
    "keyword_context_relevance": <1-10>,
    "recommendations": ["<rec1>", "<rec2>"]
}}

Consider: topic breadth vs depth, logical flow, comprehensive coverage, semantic relationships, context.
"""
        
        response = self._make_api_call(prompt)
        if not response:
            return {"error": "API call failed"}
        
        try:
            # Clean response - remove markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove ```
            cleaned_response = cleaned_response.strip()
            
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response", "raw_response": response}

    def analyze_user_experience_engagement(self, content: str, title: str) -> Dict[str, Any]:
        """
        6.4 User Experience & Engagement Analysis
        Evaluates content for user engagement and experience factors.
        """
        if not self.enabled:
            return {"error": "LLM analysis disabled"}
        
        prompt = f"""
Analyze the user experience and engagement potential of this content.

Title: {title}

Content: {content[:3000]}...

Evaluate how engaging and user-friendly the content is.

Return ONLY a JSON object with this structure:
{{
    "engagement_potential_score": <1-10>,
    "readability_score": <1-10>,
    "actionability_score": <1-10>,
    "content_structure_score": <1-10>,
    "cta_effectiveness_score": <1-10>,
    "user_journey_support_score": <1-10>,
    "reading_difficulty": "<very_easy|easy|moderate|difficult|very_difficult>",
    "engagement_elements": ["<element1>", "<element2>"],
    "improvement_areas": ["<area1>", "<area2>"],
    "recommendations": ["<rec1>", "<rec2>"]
}}

Consider: scanability, clear headings, bullet points, examples, calls-to-action, next steps, user flow.
"""
        
        response = self._make_api_call(prompt)
        if not response:
            return {"error": "API call failed"}
        
        try:
            # Clean response - remove markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove ```
            cleaned_response = cleaned_response.strip()
            
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response", "raw_response": response}

    def analyze_featured_snippet_potential(self, content: str, title: str) -> Dict[str, Any]:
        """
        6.5 Featured Snippet & SERP Features Potential
        Evaluates content suitability for featured snippets and SERP features.
        """
        if not self.enabled:
            return {"error": "LLM analysis disabled"}
        
        prompt = f"""
Analyze the potential for this content to appear in featured snippets and other SERP features.

Title: {title}

Content: {content[:3000]}...

Evaluate the content's structure and format for SERP feature optimization.

Return ONLY a JSON object with this structure:
{{
    "featured_snippet_potential": <1-10>,
    "direct_answer_suitability": <1-10>,
    "faq_format_potential": <1-10>,
    "list_format_suitability": <1-10>,
    "table_format_potential": <1-10>,
    "voice_search_optimization": <1-10>,
    "how_to_content_score": <1-10>,
    "snippet_ready_sections": ["<section1>", "<section2>"],
    "optimization_opportunities": ["<opp1>", "<opp2>"],
    "recommendations": ["<rec1>", "<rec2>"]
}}

Consider: concise answers, structured format, clear definitions, step-by-step instructions, FAQ sections.
"""
        
        response = self._make_api_call(prompt)
        if not response:
            return {"error": "API call failed"}
        
        try:
            # Clean response - remove markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove ```
            cleaned_response = cleaned_response.strip()
            
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response", "raw_response": response}

    def analyze_brand_communication(self, content: str, title: str, url: str) -> Dict[str, Any]:
        """
        6.6 Brand & Communication Analysis
        Evaluates tone, brand voice, and communication effectiveness.
        """
        if not self.enabled:
            return {"error": "LLM analysis disabled"}
        
        prompt = f"""
Analyze the brand voice and communication style of this content.

URL: {url}
Title: {title}

Content: {content[:3000]}...

Evaluate the consistency and effectiveness of brand communication.

Return ONLY a JSON object with this structure:
{{
    "tone_consistency_score": <1-10>,
    "brand_voice_clarity": <1-10>,
    "professional_presentation": <1-10>,
    "communication_clarity": <1-10>,
    "target_audience_alignment": <1-10>,
    "message_coherence": <1-10>,
    "tone_description": "<formal|casual|conversational|technical|friendly|authoritative>",
    "communication_strengths": ["<strength1>", "<strength2>"],
    "communication_weaknesses": ["<weakness1>", "<weakness2>"],
    "recommendations": ["<rec1>", "<rec2>"]
}}

Consider: consistent tone, clear messaging, audience appropriateness, professional quality, brand personality.
"""
        
        response = self._make_api_call(prompt)
        if not response:
            return {"error": "API call failed"}
        
        try:
            # Clean response - remove markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove ```
            cleaned_response = cleaned_response.strip()
            
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response", "raw_response": response}


def analyze_llm_content(soup, main_text: str, url: str) -> Dict[str, Any]:
    """
    Main function to perform all LLM-powered content analysis.
    
    Args:
        soup: BeautifulSoup object of the page
        main_text: Extracted main content text
        url: URL of the analyzed page
    
    Returns:
        Dict containing all LLM analysis results
    """
    
    # Get page title
    title_tag = soup.find('title')
    title = title_tag.get_text().strip() if title_tag else "No title found"
    
    # Initialize analyzer
    analyzer = LLMAnalyzer()
    
    if not analyzer.enabled:
        return {
            "6.1_content_quality_eat": {"error": "LLM analysis disabled - check API keys and configuration"},
            "6.2_search_intent": {"error": "LLM analysis disabled - check API keys and configuration"},
            "6.3_topical_coverage": {"error": "LLM analysis disabled - check API keys and configuration"},
            "6.4_user_experience": {"error": "LLM analysis disabled - check API keys and configuration"},
            "6.5_featured_snippet_potential": {"error": "LLM analysis disabled - check API keys and configuration"},
            "6.6_brand_communication": {"error": "LLM analysis disabled - check API keys and configuration"}
        }
    
    print("🤖 Performing AI-powered content analysis...")
    
    # Perform all analyses
    results = {}
    
    # Add small delay between API calls to respect rate limits
    analyses = [
        ("6.1_content_quality_eat", analyzer.analyze_content_quality_eat),
        ("6.2_search_intent", analyzer.analyze_search_intent),
        ("6.3_topical_coverage", analyzer.analyze_topical_coverage),
        ("6.4_user_experience", analyzer.analyze_user_experience_engagement),
        ("6.5_featured_snippet_potential", analyzer.analyze_featured_snippet_potential),
        ("6.6_brand_communication", analyzer.analyze_brand_communication)
    ]
    
    for key, analysis_func in analyses:
        print(f"   🔍 Analyzing {key.replace('_', ' ').replace('6.', 'Category 6.')}")
        
        if key in ["6.3_topical_coverage", "6.4_user_experience", "6.5_featured_snippet_potential"]:
            results[key] = analysis_func(main_text, title)
        else:
            results[key] = analysis_func(main_text, title, url)
        
        # Rate limiting delay
        time.sleep(1)
    
    return results


# Test function for debugging
if __name__ == "__main__":
    # Simple test
    analyzer = LLMAnalyzer()
    print(f"LLM Analyzer initialized: enabled={analyzer.enabled}, provider={analyzer.provider}")
    
    if analyzer.enabled:
        test_content = "This is a comprehensive guide about SEO best practices for content creators."
        test_title = "Complete SEO Guide for Content Creators"
        test_url = "https://example.com/seo-guide"
        
        result = analyzer.analyze_content_quality_eat(test_content, test_title, test_url)
        print("Test result:", json.dumps(result, indent=2))
    else:
        print("LLM analysis is disabled. Check your API keys and configuration.")