# AI Governance Control Register & Maturity Assessment Tool

A comprehensive Python-based tool for evaluating AI governance compliance with structured management frameworks, designed for the **mining and extractive industry** context.

## Overview

This tool provides a complete AI governance assessment platform covering:

- **Governance Assessment** against ISO/IEC 42001 and AI-Based ESG Monitoring frameworks
- **Automated Scoring** with maturity heat maps, gap analysis, and weighted scoring
- **ML-Based Prediction** using linear regression for maturity trend forecasting
- **AI Use Case Registry** with 8 mining industry use cases and priority ranking
- **ESG & Safety Dashboards** with executive summaries and KPI tracking
- **Validation Protocols** with 13-step deployment testing for AI-ML models
- **Best Practices Framework** with 13 standards for AI adoption in extractive industry

### Context

Built for the **Senior Specialist, Data Science & AI** role at **Ma'aden (Saudi Arabian Mining Company)**, aligned with:

- ISO/IEC 42001 AI Management Systems
- Saudi Vision 2030 & Saudi Green Initiative
- ICMM and IRMA governance standards

## Quick Start (Google Colab)

1. Open [`AI_Governance_Assessment_Tool.ipynb`](AI_Governance_Assessment_Tool.ipynb) in Google Colab
2. Run all cells: `Runtime > Run all`
3. No pip installs needed — only requires `matplotlib` (pre-installed in Colab)

The notebook is **fully self-contained** — all templates, modules, and demo data are embedded inline.

## Project Structure

```
.
├── AI_Governance_Assessment_Tool.ipynb   # Self-contained Colab notebook (all-in-one)
├── README.md                             # This file
├── templates/
│   ├── iso_42001_template.json           # ISO/IEC 42001 template (7 domains, 21 controls)
│   └── esg_ai_monitoring_template.json   # ESG monitoring template (4 domains, 15 controls)
├── ai_governance/                        # Python package (modular source code)
│   ├── __init__.py
│   ├── models.py                         # Data models (enums, dataclasses)
│   ├── scoring.py                        # Scoring algorithms & ML predictor
│   ├── validation.py                     # Validation & test protocols
│   ├── assessment.py                     # Assessment engine
│   ├── mining_use_cases.py               # Mining use case catalogue & best practices
│   └── dashboard.py                      # ESG & safety dashboard generator
├── tests/
│   ├── test_models.py
│   ├── test_scoring.py
│   ├── test_validation.py
│   └── test_assessment.py
└── build_notebook.py                     # Script to regenerate the notebook
```

## Modules

### Module 1: Data Models (`models.py`)

Core data structures for the entire tool:

| Class | Description |
|-------|-------------|
| `MaturityLevel` | Enum: INITIAL(1) through OPTIMIZING(5) |
| `RiskLevel` | Enum: LOW(1) through CRITICAL(4) |
| `UseCaseStatus` | Enum: PROPOSED(1) through RETIRED(5) |
| `GovernanceControl` | Single control with score, evidence, weight |
| `GovernanceDomain` | Domain grouping controls with auto-computed averages |
| `AssessmentResult` | Complete assessment with overall score/maturity |
| `AIUseCase` | AI-ML use case with techniques, data sources, governance mapping |
| `SafetyIncidentRecord` | Safety event record for incident tracking |

### Module 2: Templates

Two governance frameworks provided as JSON templates:

| Template | Domains | Controls | Focus |
|----------|---------|----------|-------|
| ISO/IEC 42001 | 7 | 21 | AI management system requirements |
| ESG Monitoring | 4 | 15 | Environmental, Social, Governance AI oversight |

**ISO/IEC 42001 Domains:**
1. Context of the Organization (3 controls)
2. Leadership & Commitment (3 controls)
3. Planning (3 controls)
4. Support & Resources (3 controls)
5. Operation (4 controls)
6. Performance Evaluation (3 controls)
7. Improvement (2 controls)

**ESG Monitoring Domains:**
1. Environmental AI Governance (4 controls)
2. Social AI Governance (4 controls)
3. Governance of AI in ESG Reporting (4 controls)
4. ESG Data Integration & AI Pipeline (3 controls)

### Module 3: Scoring & ML Prediction (`scoring.py`)

| Function/Class | Description |
|----------------|-------------|
| `compute_domain_scores()` | Average maturity scores per domain |
| `compute_weighted_domain_scores()` | Weighted average scoring |
| `compute_gap_analysis()` | Gap identification with priority classification |
| `generate_heat_map_data()` | Control-level heat map data |
| `generate_domain_heat_map()` | Domain-level heat map summary |
| `render_text_heat_map()` | Text-based heat map rendering |
| `MaturityPredictor` | OLS linear regression for maturity forecasting |
| `compute_use_case_priority_score()` | Multi-criteria use case scoring (0-100) |
| `rank_use_cases()` | Priority ranking of AI-ML use cases |

**MaturityPredictor** fits a linear regression model on historical assessment data to:
- Forecast maturity trajectory for future periods
- Estimate time-to-target for a desired maturity level
- Report R-squared, slope, and trend direction

### Module 4: Validation & Test Protocols (`validation.py`)

Validation for controls, domains, assessments, and use cases, plus a
**13-step AI-ML Deployment Test Protocol** across 5 categories:

| Category | Steps | Focus |
|----------|-------|-------|
| Data Quality | DQ-01 to DQ-03 | Completeness, distribution, outliers |
| Model Performance | MP-01 to MP-03 | Accuracy, robustness, regression |
| Bias & Fairness | BF-01 to BF-02 | Demographic bias, explainability |
| Security | SC-01 to SC-02 | Privacy, access control |
| Integration | IT-01 to IT-03 | System integration, failover, monitoring |

### Module 5: Assessment Engine (`assessment.py`)

Orchestrates the full assessment pipeline:

```python
report = run_assessment(
    "iso_42001_template.json",
    "ASSESSMENT-001",
    "Ma'aden (Saudi Arabian Mining Company)",
    scores={"D1-C01": 3, "D1-C02": 4, ...},
    target_level=4,
)
```

Returns a comprehensive report with overall score, domain scores, gap
analysis, heat map data, and validation results.

### Module 6: Mining Use Cases (`mining_use_cases.py`)

**8 AI-ML use cases** for mining operations:

| ID | Use Case | Business Unit | Status |
|----|----------|---------------|--------|
| MN-UC-001 | Predictive Maintenance for SAG/Ball Mills | Processing Plant | Piloting |
| MN-UC-002 | Ore Grade Prediction & Blast Optimization | Mining Operations | Evaluating |
| MN-UC-003 | AI-Powered Safety Incident Prediction | Safety & Sustainability | Proposed |
| MN-UC-004 | AI-Based ESG Dashboard & Sustainability Reporting | Sustainability | Evaluating |
| MN-UC-005 | Energy Consumption Optimization | Processing Plant | Piloting |
| MN-UC-006 | Autonomous Haul Truck Fleet Management | Mining Operations | Proposed |
| MN-UC-007 | Water Treatment Process Optimization | Environmental Mgmt | Evaluating |
| MN-UC-008 | Mineral Exploration Target Identification | Exploration | Proposed |

Plus **13 best practices** across 4 categories for AI adoption in
extractive industry.

### Module 7: Dashboard (`dashboard.py`)

Executive dashboard combining:
- Governance maturity overview
- Domain heat map with severity indicators
- Gap analysis summary
- AI-ML use case portfolio breakdown
- Safety incident overview with resolution tracking

## Notebook Demos

The Jupyter notebook includes **13 interactive demos**:

| # | Demo | Visualization |
|---|------|---------------|
| 1 | ISO/IEC 42001 Assessment | Text heat map |
| 2 | Domain Maturity Heat Map | Horizontal bar chart |
| 3 | ESG Monitoring Assessment | Text heat map |
| 4 | ESG Radar Chart | Polar/radar chart |
| 5 | Control-Level Heat Map | Color-mapped bars (21 controls) |
| 6 | ML Maturity Prediction | Time series with forecast |
| 7 | Use Case Priority Ranking | Stacked bar chart |
| 8 | Gap Analysis | Grouped bar chart with annotations |
| 9 | Deployment Test Protocol | Pie + stacked bar |
| 10 | Executive Dashboard | Text-based dashboard |
| 11 | Best Practices Framework | Formatted text display |
| 12 | Dual Framework Comparison | Side-by-side bar charts |
| 13 | Unit Tests | 21 self-verification tests |

## Running the Python Package

For development outside of Colab:

```bash
# Clone the repository
git clone https://github.com/ajiteguh85/AI-Governance-Control-Register-and-Maturity-Assessment-Tool-.git
cd AI-Governance-Control-Register-and-Maturity-Assessment-Tool-

# Run tests
python -m pytest tests/ -v

# Use the package
python -c "
from ai_governance.assessment import run_assessment

report = run_assessment(
    'iso_42001_template.json',
    'DEMO-001',
    'My Organization',
    {'D1-C01': 3, 'D1-C02': 4, 'D1-C03': 3},
    target_level=3,
)
print(report['text_heat_map'])
"
```

## Regenerating the Notebook

If you modify the Python source files, regenerate the notebook:

```bash
python build_notebook.py
```

This reads all source files from `ai_governance/` and `templates/`,
embeds them into a self-contained `.ipynb`, and validates the result.

## Requirements

- **Python 3.10+**
- **matplotlib** (for visualizations in the notebook)
- No other external dependencies — the tool uses only the Python standard library

## License

This project is provided for educational and professional development purposes.
