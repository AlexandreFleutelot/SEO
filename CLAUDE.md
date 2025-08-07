# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Python-based SEO analysis tool with advanced competitive case studies capabilities. The platform provides:

### Core SEO Analysis (6 Categories):
1. Content & Semantics (content analysis, style, sources, freshness)
2. Structure (headings, metadata, images, structured data, crawlability)  
3. Linking (internal links and anchor text analysis)
4. Performance (Core Web Vitals via Google PageSpeed API)
5. AIO Optimization (AI search engine optimization features)
6. AI-Powered Content Analysis (LLM-powered quality, E-A-T, search intent analysis)

### Advanced Features:
- **Interactive Streamlit Dashboard**: Complete web interface with real-time visualizations
- **Competitive Case Studies**: Multi-LLM source extraction and comparative analysis system
- **Professional Reporting**: JSON, Excel export with executive summaries
- **Page Storage & Caching**: Automatic content management and persistence

## Architecture

The codebase follows a modular architecture organized in the following structure:

```
SEO/
├── src/
│   ├── page_analyzer.py - Main orchestrator that coordinates all analysis modules
│   ├── case_studies/ - Complete competitive case studies system
│   │   ├── __init__.py - Module initialization and exports
│   │   ├── models.py - Data models (CaseStudy, LLMResponse, SourceURL, etc.)
│   │   ├── case_manager.py - CRUD operations for case studies with JSON persistence
│   │   ├── llm_source_extractor.py - Multi-LLM source extraction with advanced filtering
│   │   ├── comparative_analyzer.py - Batch SEO analysis and competitive insights
│   │   └── case_report_generator.py - Professional report generation with visualizations
│   └── utils/
│       ├── content.py - Content analysis functions (richness, style, sources, freshness)
│       ├── structure.py - Technical structure analysis (headings, metadata, images, schema)
│       ├── linking.py - Internal linking and anchor text analysis
│       ├── performance.py - Performance analysis via Google PageSpeed API
│       ├── aio.py - AI optimization analysis (voice search, featured snippets)
│       ├── llm_analysis.py - AI-powered content analysis (OpenAI/Anthropic)
│       └── page_storage.py - Page content storage and caching system
├── dashboard/ - Complete Streamlit web interface
│   ├── app.py - Main dashboard application
│   ├── components/ - Reusable UI components (charts, etc.)
│   ├── pages/ - Dashboard pages
│   │   ├── 1_🔍_Analyse_Détaillée.py - Deep-dive page analysis
│   │   ├── 2_📊_Comparaisons.py - Side-by-side page comparisons
│   │   ├── 3_➕_Nouvelle_Analyse.py - Add new pages for analysis
│   │   ├── 4_📄_Pages_Sauvegardées.py - Manage cached pages
│   │   └── 5_🔬_Études_de_Cas.py - Competitive case studies interface
│   └── utils/
│       └── data_loader.py - Data loading utilities for dashboard
├── data/
│   ├── pages/ - Cached page content with metadata
│   ├── case_studies/ - Case study data storage
│   │   ├── active/ - Active studies in progress
│   │   ├── completed/ - Completed studies
│   │   └── reports/ - Generated case study reports
│   └── reports/ - SEO analysis reports
├── reports/
│   ├── raw/ - Raw JSON analysis reports
│   └── scores/ - Consolidated scoring reports
└── tests/ - Test files for system validation
```

## Dependencies

This project uses `uv` for dependency management. Dependencies are defined in `pyproject.toml`.

## Development Commands

### Setup Environment
Install dependencies and create virtual environment:
```bash
uv sync
```

### Install spaCy French Model
After setting up the environment, install the required French language model:
```bash
uv add https://github.com/explosion/spacy-models/releases/download/fr_core_news_sm-3.8.0/fr_core_news_sm-3.8.0-py3-none-any.whl
```

### Configure API Keys
Copy the `.env` file and add your API keys:
```bash
cp .env .env.local
# Edit .env.local with your actual API keys
```

Required API keys for full functionality:
- **Google PageSpeed Insights API**: For Core Web Vitals analysis
- **OpenAI API** (recommended): For AI-powered content analysis
- **Anthropic API** (alternative): Alternative LLM provider for content analysis

### Running Analysis
To run a full SEO analysis on a page:
```bash
uv run python -m src.page_analyzer
```

The target URL and optional PageSpeed API key are configured at the bottom of `src/page_analyzer.py`.

### Running the Dashboard
Launch the interactive Streamlit dashboard:
```bash
uv run streamlit run dashboard/app.py
```

The dashboard provides complete web interface with:
- Real-time SEO analysis visualization
- Page comparison tools  
- Competitive case studies management
- Professional report generation
- Interactive charts and metrics

### Running Individual Modules
Each module can be tested independently:
```bash
uv run python src/utils/content.py
uv run python src/utils/structure.py  
uv run python src/utils/linking.py
```

### Testing Case Studies System
Test the competitive case studies functionality:
```bash
uv run python test_case_study.py              # Basic functionality test
uv run python test_complete_case_study.py     # Complete workflow test
```

### Adding New Dependencies
To add new dependencies:
```bash
uv add package-name
```

### Development Dependencies
To add development-only dependencies:
```bash
uv add --dev package-name
```

## Key Implementation Details

- Text processing uses spaCy NLP pipeline for French content analysis
- BeautifulSoup handles HTML parsing and DOM manipulation
- The main analyzer creates separate soup instances to avoid conflicts between modules
- Error handling isolates failures in individual analysis categories
- Results are structured as nested dictionaries for JSON serialization
- Reports are automatically saved as JSON files with URL-based filenames

## Configuration

- Target URL is set in `src/page_analyzer.py` main block
- Google PageSpeed Insights API key is optional (set `PAGESPEED_API_KEY` in .env)
- LLM analysis requires either OpenAI or Anthropic API key (configurable in .env)
- LLM provider can be switched between 'openai' and 'anthropic' via `LLM_PROVIDER` setting
- LLM analysis can be disabled by setting `ENABLE_LLM_ANALYSIS=false`
- Text analysis is limited to spaCy's max_length for performance
- External link analysis limits results to first 10 for readability

### New AI-Powered Analysis Features

Category 6 provides advanced content analysis using Large Language Models:

1. **Content Quality & E-A-T Assessment**: Evaluates expertise, authoritativeness, trustworthiness
2. **Search Intent Analysis**: Determines how well content matches user search intent  
3. **Topical Coverage**: Assesses topic completeness and semantic richness
4. **User Experience & Engagement**: Analyzes content for user engagement potential
5. **Featured Snippet Potential**: Evaluates SERP feature optimization opportunities
6. **Brand & Communication**: Assesses tone consistency and communication effectiveness

Each analysis provides detailed scores (1-10), insights, and specific recommendations for improvement.

## Competitive Case Studies System

The case studies system is a complete competitive analysis platform that enables comprehensive market research and competitive intelligence.

### Core Components

1. **CaseStudyManager** (`src/case_studies/case_manager.py`)
   - CRUD operations for case studies
   - JSON-based persistence with organized directory structure
   - Statistics tracking and metadata management

2. **LLMSourceExtractor** (`src/case_studies/llm_source_extractor.py`)
   - Multi-LLM source extraction (OpenAI, Anthropic, Google)
   - Advanced prompt engineering with explicit URL citation requirements
   - Smart URL validation and filtering (removes search engines, social media, shorteners)
   - Cross-provider deduplication and reliability scoring

3. **ComparativeAnalyzer** (`src/case_studies/comparative_analyzer.py`)
   - Batch SEO analysis of extracted competitor sources
   - Competitive insights generation with strengths/weaknesses analysis
   - Gap analysis identifying missing topics and underrepresented keywords
   - Market positioning and optimization priorities

4. **CaseReportGenerator** (`src/case_studies/case_report_generator.py`)
   - Professional report generation with executive summaries
   - Interactive Plotly visualizations and performance matrices
   - Multi-format export (JSON, Excel, PDF planned)

### Optimized Source Extraction

The system uses advanced prompt engineering to maximize source extraction quality:

```
🔗 CITATION DES SOURCES OBLIGATOIRE:
- Cite tes sources avec les URLs complètes et exactes
- Utilise ce format précis: "Source: [Nom du site] - URL: https://exemple.com/page-complete"
- Fournis 8-12 sources fiables et récentes
- Privilégie les sites d'autorité (gouvernementaux, institutionnels, presse reconnue)
```

**Advanced Features:**
- **Follow-up Queries**: Automatic retry with additional prompts if insufficient sources
- **Smart Validation**: Filters out search engines, social media, URL shorteners
- **Reliability Scoring**: Domain-based authority assessment (0.5-0.9 scale)
- **Cross-LLM Deduplication**: Removes duplicates across different providers
- **JSON Structured Mode**: Alternative extraction format for higher precision

### Case Study Workflow

1. **Creation**: Define study title, research question, and LLM configuration
2. **Source Extraction**: Query multiple LLMs to extract competitor sources
3. **Validation**: Apply smart filtering and accessibility verification
4. **Batch Analysis**: Perform SEO analysis on all extracted sources
5. **Comparative Analysis**: Generate insights, rankings, and gap analysis
6. **Report Generation**: Create executive summaries with visualizations
7. **Export**: Save as JSON, Excel with professional formatting

### Data Storage Structure

```
data/case_studies/
├── active/           # Studies in progress (.json files)
├── completed/        # Finished studies (.json files)
└── reports/          # Generated reports with timestamps
```

Each case study includes:
- Metadata (title, question, status, dates)
- LLM responses with extracted sources
- SEO analysis results for each source
- Competitive insights and gap analysis
- Generated reports and visualizations

### Key Metrics and Scoring

- **Extraction Confidence**: 0.0-1.0+ based on citation context and URL quality
- **Reliability Score**: 0.5-0.9 based on domain authority
- **SEO Scores**: 0-100 for content, structure, linking, performance
- **Gap Analysis**: Missing topics, underrepresented keywords, optimization priorities
- **Market Position**: Competitive ranking and positioning matrix

### Integration with Dashboard

The case studies system is fully integrated into the Streamlit dashboard via the "🔬 Études de Cas" page, providing:
- Wizard-style case creation interface
- Real-time progress tracking during analysis
- Interactive results visualization
- Professional report viewing and export
- Study management (active/completed/statistics)