# Advanced SEO Analysis Platform

A comprehensive Python-based SEO analysis platform featuring AI-powered insights, LLM-based competitive analysis, and interactive reporting. Provides deep analysis across 6 categories with professional-grade reporting capabilities.

## ✨ Recent Enhancements

**🔧 Modular Architecture (v2.0)**
- Refactored monolithic 1000+ line codebase into specialized modules
- Organized structure: `seo/`, `core/`, `llm/` directories  
- Clean separation of concerns and improved maintainability

**🤖 Advanced LLM Analysis**
- Multi-provider support: OpenAI, Anthropic, Google Gemini
- Intelligent 3-tier URL extraction strategy with 90%+ success rate
- Cross-provider sentiment analysis and consensus scoring
- Professional JSON reports (32KB+ detailed insights)

**📊 Enhanced Reporting**
- Organized report directories: `seo_analysis/`, `seo_scores/`, `llm_analysis/`
- Real-time progress tracking with detailed console output
- Comprehensive metadata and session tracking

**🎯 Robust URL Extraction**
- Persuasive prompting strategies to overcome LLM limitations
- Smart domain filtering and accessibility validation  
- Cross-LLM deduplication and reliability scoring

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Dashboard Interface](#dashboard-interface)
- [LLM Analysis System](#llm-analysis-system)
- [Analysis Categories](#analysis-categories)
- [Interpreting Results](#interpreting-results)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

🔍 **Comprehensive Analysis** - 6 categories of SEO analysis
- Content & Semantics analysis
- Technical structure evaluation  
- Internal linking assessment
- Performance metrics via Google PageSpeed API
- AI optimization features
- **AI-powered content insights** using OpenAI/Anthropic

🤖 **AI-Enhanced Insights** - Advanced content analysis
- Content quality & E-A-T assessment
- Search intent analysis
- Topical coverage evaluation
- User experience scoring
- Featured snippet optimization potential
- Brand communication analysis

📊 **Interactive Dashboard** - Complete Streamlit interface
- Real-time analysis visualization
- Multi-page comparison tools
- Interactive charts and metrics
- Page storage and cache management
- Export capabilities (JSON, Excel)

🤖 **Advanced LLM Analysis** - Multi-provider intelligence
- Multi-LLM source extraction (OpenAI, Anthropic, Google)
- Intelligent URL extraction with 3-tier fallback strategy
- Brand and entity detection across responses
- Cross-provider sentiment analysis and consensus
- Structured JSON reporting with 32KB+ detailed insights
- Professional report generation with metadata tracking

📋 **Professional Reporting** - Comprehensive export options
- Structured JSON reports with raw data
- Executive summaries with actionable insights
- Visual charts and competitive positioning
- Excel exports with detailed breakdowns

## Installation

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SEO
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Install spaCy French language model**
   ```bash
   uv add https://github.com/explosion/spacy-models/releases/download/fr_core_news_sm-3.8.0/fr_core_news_sm-3.8.0-py3-none-any.whl
   ```

4. **Configure API keys**
   ```bash
   cp .env .env.local
   # Edit .env.local with your actual API keys
   ```

## Configuration

### Required API Keys

Create a `.env` file in the root directory with the following keys:

```env
# Google PageSpeed Insights API (for performance analysis)
PAGESPEED_API_KEY=your_pagespeed_api_key_here

# OpenAI API (recommended for AI analysis)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API (alternative for AI analysis)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# LLM Configuration
LLM_PROVIDER=openai  # or "anthropic"
ENABLE_LLM_ANALYSIS=true
```

### Getting API Keys

- **Google PageSpeed API**: [Get your key here](https://developers.google.com/speed/docs/insights/v5/get-started)
- **OpenAI API**: [Get your key here](https://platform.openai.com/api-keys)
- **Anthropic API**: [Get your key here](https://console.anthropic.com/)

## Usage

### SEO Analysis

```bash
uv run python -m src.page_analyzer
```

Edit the target URL in `src/page_analyzer.py`:

```python
TARGET_URL = "https://your-website.com/page-to-analyze"
```

### LLM Analysis

```bash
uv run python test_multi_llm.py
```

Or test interactively:

```python
from src.modules import analyser_question_multi_llm

results = analyser_question_multi_llm(
    "What are the best online banks in France in 2024?",
    "For a comparison intended for individuals looking to open an online bank account"
)
```

### Output

The analyzers generate:
- Console output with real-time progress
- SEO reports in `reports/seo_analysis/` and `reports/seo_scores/`
- LLM analysis reports in `reports/llm_analysis/`
- Comprehensive metrics and actionable recommendations

## Dashboard Interface

### Starting the Dashboard

Launch the interactive Streamlit dashboard:

```bash
uv run streamlit run dashboard/app.py
```

The dashboard provides:
- **🏠 Dashboard**: Overview and quick analysis
- **🔍 Analyse Détaillée**: Deep-dive into specific page metrics
- **📊 Comparaisons**: Side-by-side page comparisons with interactive charts
- **➕ Nouvelle Analyse**: Add new pages for analysis
- **📄 Pages Sauvegardées**: Manage cached page content
- **🔬 Études de Cas**: LLM-powered competitive analysis

### Key Features

- **Real-time Visualization**: Interactive Plotly charts
- **Page Management**: Automatic caching and storage of analyzed pages
- **Export Options**: JSON and Excel report generation
- **Responsive Design**: Works on desktop and mobile devices

## LLM Analysis System

### Overview

The LLM Analysis system provides advanced research capabilities through:
1. **Multi-Provider Intelligence**: OpenAI, Anthropic, and Google Gemini support
2. **Smart URL Extraction**: 3-tier fallback strategy for reliable source extraction  
3. **Entity Detection**: Automatic brand and entity recognition across responses
4. **Sentiment Analysis**: Cross-provider consensus and reliability scoring
5. **Professional Reporting**: Comprehensive JSON reports with detailed metadata

#### Intelligent URL Extraction Strategy
- **Strategy 1**: Parse initial responses for existing URLs
- **Strategy 2**: Explicit source requests when insufficient URLs found  
- **Strategy 3**: Forced citation requests with persuasive prompts
- **Validation**: Domain filtering, accessibility testing, deduplication

#### Brand & Entity Detection
- **Pattern Recognition**: Multiple detection strategies (structured sections, contextual patterns, capitalization analysis)
- **Entity Classification**: Automatic categorization (banks, insurance, etc.)
- **Deduplication**: Smart normalization and merging across providers

#### Cross-Provider Analysis  
- **Sentiment Consensus**: Aggregate sentiment analysis across multiple LLM responses
- **Reliability Scoring**: Domain-based authority assessment (0.5-0.9 scale)
- **Performance Metrics**: Extraction efficiency, URL accessibility, response quality

### Usage Examples

#### Basic LLM Analysis
```python
from src.modules import analyser_question_multi_llm

# Analyze a research question
results = analyser_question_multi_llm(
    "Quelles sont les meilleures banques en ligne en France en 2024?",
    "Je cherche des informations fiables pour un comparatif"
)

# Results include:
print(f"Brands detected: {len(results['rapport_consolide']['toutes_marques'])}")
print(f"Sources extracted: {len(results['rapport_consolide']['toutes_sources'])}")
print(f"Providers used: {results['providers_utilises']}")
```

#### Direct Module Usage
```python  
from src.modules.llm import MultiLLMAnalyzer

analyzer = MultiLLMAnalyzer()
complete_results = analyzer.analyser_question_complete(
    "What are the best investment platforms?",
    "For retirement planning research"
)

# Generate detailed report
report_path = analyzer.generer_rapport_complet(complete_results)
print(f"Report saved to: {report_path}")
```

### Competitive Analysis Results

The system provides:

- **📈 Competitor Rankings**: SEO score-based leaderboard
- **🏆 Market Leader Analysis**: Detailed insights on top performer
- **🎯 Gap Analysis**: Missing topics and underrepresented keywords
- **💡 Optimization Priorities**: High/medium/low priority recommendations
- **📊 Performance Matrix**: Multi-dimensional competitive positioning
- **🔍 Keyword Clusters**: Thematic grouping of target keywords

### Report Generation

Complete reports include:
- **Executive Summary**: High-level findings and recommendations
- **📊 Visual Charts**: Performance comparisons and positioning matrices
- **🔍 Key Findings**: Prioritized insights with impact levels
- **💡 Strategic Recommendations**: Actionable optimization suggestions
- **📤 Export Options**: JSON, Excel, and PDF formats (planned)

### Example Case Study Workflow

```bash
# 1. Create case study
Title: "Best Life Insurance Advice Sites 2025"
Question: "What are the most authoritative life insurance advice websites?"

# 2. LLM extraction results
OpenAI: 8 sources extracted
Anthropic: 6 sources extracted  
Deduplication: 12 unique sources

# 3. Batch SEO analysis
12/12 sources analyzed successfully
Average SEO score: 72.5/100
Market leader: amf-france.org (89.2/100)

# 4. Gap analysis
Missing topics: ["tax benefits", "investment comparison"]  
Optimization priorities: 5 high, 3 medium, 2 low

# 5. Report generation
Executive summary: 450 words
Visual charts: 3 interactive plots
Export: JSON (data/case_studies/reports/case_report_*.json)
```

## Analysis Categories

### 1. Content & Semantics
- **Word count and entity analysis**
- **Style and clarity metrics**
- **Source reliability assessment**
- **Content freshness detection**

### 2. Technical Structure
- **Heading hierarchy (H1-H6)**
- **Meta tags optimization**
- **Image optimization**
- **Structured data presence**
- **Crawlability factors**

### 3. Internal Linking
- **Link count and distribution**
- **Anchor text diversity**
- **Navigation structure**

### 4. Performance
- **Core Web Vitals** (LCP, INP, CLS)
- **Desktop and mobile metrics**
- **Google PageSpeed Insights data**

### 5. AI Optimization (AIO)
- **Voice search readiness**
- **Featured snippet potential**
- **AI search engine compatibility**

### 6. AI-Powered Content Analysis
- **Content Quality & E-A-T Assessment**
- **Search Intent Analysis**
- **Topical Coverage Evaluation**
- **User Experience Scoring**
- **SERP Feature Optimization**
- **Brand Communication Analysis**

## Interpreting Results

### Understanding Scores

Most metrics use a **1-10 scale** where:
- **1-3**: Poor - Immediate attention required
- **4-6**: Fair - Room for improvement
- **7-8**: Good - Minor optimizations possible
- **9-10**: Excellent - Minimal improvements needed

### Content & Semantics Criteria

#### 1.1 Richness & Coverage
- **Word Count**: Minimum 300 words for basic content, 1000+ for comprehensive topics
- **Entity Count**: Higher entity density indicates topic comprehensiveness
- **Entity Distribution**: Balance of locations (LOC), organizations (ORG), miscellaneous (MISC), and persons (PER)

**Interpretation:**
- Low word count (<300): Content may be thin
- High entity count: Rich, detailed content
- Balanced entity types: Comprehensive coverage

#### 1.2 Style & Clarity
- **Sentence Count**: More sentences generally indicate detailed content
- **Average Sentence Length**: 15-20 words optimal for readability
- **List Count**: Bullet points and numbered lists improve scannability
- **Table Count**: Structured data presentation

**Interpretation:**
- Long sentences (>25 words): May reduce readability
- High list count: Good content structure
- Tables present: Enhanced data presentation

#### 1.3 Sources & Reliability
- **External Link Count**: Quality over quantity
- **External Links**: Should link to authoritative sources
- **Textual Citations**: In-text references boost credibility

**Interpretation:**
- 0 external links: May lack supporting evidence
- 3-5 quality external links: Good sourcing
- 10+ external links: May dilute page authority

#### 1.4 Freshness
- **Publication Date**: Recent content ranks better
- **Detected Dates**: Current dates indicate fresh content
- **Year in Title/H1**: Explicit year dating

**Interpretation:**
- Recent dates: Content is current
- No dates found: Content may appear outdated
- Year in title: Clear date targeting

### Technical Structure Criteria

#### 2.1 Heading Structure
- **H1 Count**: Should be exactly 1
- **Heading Hierarchy**: Proper H1 → H2 → H3 flow
- **Hierarchy Issues**: Skipped levels or multiple H1s

**Interpretation:**
- Multiple H1s: SEO confusion
- Missing hierarchy levels: Poor content structure
- Well-structured headings: Good SEO foundation

#### 2.2 Metadata
- **Title Length**: 50-60 characters optimal
- **Meta Description Length**: 150-160 characters optimal

**Interpretation:**
- Title too short (<30): Missing opportunities
- Title too long (>60): May be truncated in SERPs
- Description missing: Reduces click-through rates

#### 2.3 Image Optimization
- **Alt Coverage**: Should be 95%+ for accessibility
- **Figcaption Usage**: Enhanced accessibility

**Interpretation:**
- <80% alt coverage: Accessibility issues
- >95% alt coverage: Excellent optimization
- No figcaptions: Missed enhancement opportunity

#### 2.4 Structured Data
- **Schema Count**: Rich snippets potential
- **Schema Types**: Specific markup types implemented

**Interpretation:**
- No schema: Missing rich snippets opportunity
- Multiple schemas: Enhanced SERP features
- Relevant schema types: Targeted optimization

#### 2.5 Crawlability
- **Robots.txt Status**: Should be accessible
- **Sitemap.xml Status**: Should be available

**Interpretation:**
- Robots.txt missing: Crawl guidance absent
- Sitemap missing: Reduced discoverability

### Linking Criteria

#### 3.1-3.2 Internal Linking
- **Internal Link Count**: 3-5 per 1000 words recommended
- **Anchor Text Diversity**: Variety indicates natural linking
- **Non-descriptive Anchors**: "Click here", "Read more" should be minimal

**Interpretation:**
- High anchor diversity: Natural link profile
- Many non-descriptive anchors: Poor user experience
- Appropriate link count: Good internal structure

### Performance Criteria

#### 4.1-4.2 Core Web Vitals
- **LCP (Largest Contentful Paint)**: <2.5s good, <4s needs improvement
- **INP (Interaction to Next Paint)**: <200ms good, <500ms needs improvement  
- **CLS (Cumulative Layout Shift)**: <0.1 good, <0.25 needs improvement

**Interpretation:**
- All metrics green: Excellent user experience
- LCP high: Slow loading content
- INP high: Poor interactivity
- CLS high: Layout instability

### AI Optimization Criteria

#### 5.1 Direct Answer Potential
- **QA Pairs**: Content formatted as questions/answers
- **Summary Blocks**: Concise answer sections

#### 5.2 Quantifiable Data
- **Percentages**: Specific statistical data
- **Currency Mentions**: Financial specificity
- **Numeric Dates**: Temporal precision

#### 5.3 Expertise Signals
- **Author Schema**: Structured authorship data
- **About Page**: Credibility indicators

#### 5.4 Multimodal Content
- **Video Embeds**: Rich media presence
- **API Links**: Programmatic access

### AI-Powered Analysis Criteria

#### 6.1 Content Quality & E-A-T (1-10 Scale)
- **Content Quality**: Writing clarity, depth, accuracy
- **Expertise**: Subject matter knowledge demonstration
- **Authoritativeness**: Credible source indicators
- **Trustworthiness**: Transparency, citations, credentials

**Interpretation:**
- Score 8-10: High-quality, trustworthy content
- Score 6-7: Good content with room for improvement
- Score <6: Significant quality issues requiring attention

#### 6.2 Search Intent Analysis
- **Primary Intent**: Main user goal (informational/commercial/navigational/transactional)
- **Intent Fulfillment**: How well content meets user needs (1-10)
- **Target Keywords**: Primary terms the content targets

**Interpretation:**
- High fulfillment score: Content matches user expectations
- Intent mismatch: Content doesn't serve user goals
- Clear keyword focus: Good search targeting

#### 6.3 Topical Coverage (1-10 Scale)
- **Topic Completeness**: Comprehensive subject coverage
- **Semantic Richness**: Related concept coverage
- **Content Depth**: Surface/moderate/deep/expert level

**Interpretation:**
- High completeness: Comprehensive topic coverage
- Rich semantics: Well-connected concepts
- Expert depth: Authority-building content

#### 6.4 User Experience (1-10 Scale)
- **Engagement Potential**: Content's ability to engage users
- **Readability**: Ease of reading and comprehension
- **Actionability**: Clear next steps for users

**Interpretation:**
- High engagement: Content likely to retain users
- Good readability: Accessible to target audience
- Clear actions: Supports user journey

#### 6.5 Featured Snippet Potential (1-10 Scale)
- **Direct Answer Suitability**: Ready for position zero
- **List Format**: Bullet/numbered list optimization
- **Voice Search**: Conversational query optimization

**Interpretation:**
- High snippet potential: Likely to capture position zero
- Good formatting: Structured for SERP features
- Voice optimized: Ready for voice search

#### 6.6 Brand Communication (1-10 Scale)
- **Tone Consistency**: Uniform brand voice
- **Message Coherence**: Clear, aligned messaging
- **Audience Alignment**: Content matches target audience

**Interpretation:**
- Consistent tone: Strong brand identity
- Coherent messaging: Clear communication
- Audience aligned: Content serves target users

## Project Structure

```
SEO/
├── src/
│   ├── analyseur.py              # Main SEO analysis orchestrator
│   ├── page_analyzer.py          # Legacy entry point (deprecated)
│   ├── config.py                 # Configuration and paths management
│   └── modules/                  # Modular analysis components
│       ├── seo/                  # SEO analysis modules
│       │   ├── contenu.py        # Content analysis and semantics
│       │   ├── structure.py      # Technical structure evaluation
│       │   └── performance.py    # Performance metrics (PageSpeed API)
│       ├── core/                 # Core utilities
│       │   └── utils.py          # Scoring and recommendations
│       └── llm/                  # Large Language Model analysis
│           ├── multi_llm_analyzer.py    # Main LLM orchestrator
│           ├── llm_providers.py         # Provider management (OpenAI/Anthropic/Gemini)
│           ├── url_extractor.py         # Advanced URL extraction
│           ├── information_extractor.py # Brand/entity detection
│           ├── sentiment_analyzer.py    # Cross-provider sentiment analysis
│           └── report_generator.py      # Professional report generation
├── dashboard/                     # Interactive Streamlit interface
│   ├── app.py                     # Main dashboard application
│   ├── components/               # Reusable UI components
│   └── pages/                    # Dashboard pages
│       ├── 1_🔍_Analyse_Détaillée.py  # Deep-dive analysis
│       ├── 2_📊_Comparaisons.py       # Page comparisons
│       ├── 3_➕_Nouvelle_Analyse.py    # Add new analyses
│       ├── 4_📄_Pages_Sauvegardées.py # Page management
│       ├── 5_🔬_Études_de_Cas.py      # LLM case studies
│       └── 6_Analyse_Concurrentielle.py # Competitive analysis
├── reports/                       # Analysis outputs (organized by type)
│   ├── seo_analysis/             # SEO analysis reports (JSON)
│   ├── seo_scores/               # SEO scoring summaries
│   └── llm_analysis/             # LLM analysis reports
├── data/
│   └── pages/                    # Cached page content and metadata
├── test_multi_llm.py             # LLM system test script
├── .env                          # API key configuration
├── pyproject.toml                # Project dependencies (uv format)
├── uv.lock                       # Dependency lock file
├── CLAUDE.md                     # Project context documentation
└── README.md                     # This documentation
```

## Dependencies

### Core Dependencies
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests
- `spacy` - Natural language processing
- `datefinder` - Date extraction
- `python-dotenv` - Environment variable management

### Dashboard Dependencies
- `streamlit` - Web dashboard framework
- `plotly` - Interactive visualizations
- `pandas` - Data manipulation
- `openpyxl` - Excel export functionality

### AI Analysis Dependencies
- `openai` - OpenAI GPT models
- `anthropic` - Anthropic Claude models

### Language Models
- `fr_core_news_sm` - French spaCy model

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development

### Running Tests
```bash
# SEO analysis tests
uv run python src/modules/seo/contenu.py      # Test content analysis
uv run python src/modules/seo/structure.py    # Test structure analysis
uv run python src/modules/seo/performance.py  # Test performance analysis

# LLM system tests  
uv run python test_multi_llm.py               # Complete LLM analysis test

# Dashboard tests
uv run streamlit run dashboard/app.py         # Launch interactive dashboard
```

### Adding New Analysis Modules
1. Create new module in appropriate directory:
   - SEO modules: `src/modules/seo/`
   - LLM modules: `src/modules/llm/`
   - Core utilities: `src/modules/core/`
2. Implement analysis functions with proper error handling
3. Update imports in `src/modules/__init__.py`
4. Add configuration in `src/config.py` if needed
5. Update documentation

## Troubleshooting

### Common Issues

**Import Errors**
- Ensure all dependencies installed: `uv sync`
- Check Python version: `python --version` (3.11+ required)

**API Key Issues**
- Verify `.env` file contains valid keys
- Check API key permissions and quotas
- Test API connectivity independently

**Performance Analysis Fails**
- Verify Google PageSpeed API key is valid
- Check internet connectivity
- Some URLs may not be accessible to PageSpeed API

**LLM Analysis Issues**
- Check `ENABLE_LLM_ANALYSIS=true` in `.env`
- Verify OpenAI or Anthropic API key is valid
- Check API quota and billing status
- Test individual providers: `from src.modules.llm.llm_providers import LLMProviderManager`
- For URL extraction issues: Check internet connectivity and domain accessibility

**Module Import Errors**
- Ensure proper directory structure in `src/modules/`
- Check `__init__.py` files are present in all module directories
- Verify import paths match the new modular structure

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [uv](https://github.com/astral-sh/uv) for fast dependency management
- Uses [spaCy](https://spacy.io/) for natural language processing
- Powered by [OpenAI](https://openai.com/) and [Anthropic](https://anthropic.com/) for AI analysis
- Performance data from [Google PageSpeed Insights](https://developers.google.com/speed/pagespeed/insights/)