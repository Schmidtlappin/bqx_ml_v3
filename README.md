# BQX ML V3: 28 Independent Models for Forex Momentum Prediction

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)]()

## 🎯 Overview

BQX ML V3 is a sophisticated machine learning system featuring **28 independent models** that predict BQX momentum values for forex currency pairs using a revolutionary **interval-centric architecture** and the **BQX paradigm shift**.

### Key Features
- 🎯 **28 Independent Models**: One specialized model per currency pair
- 🔄 **BQX Paradigm Shift**: BQX values as BOTH features AND targets (autoregressive prediction)
- 📊 **Interval-Centric**: All calculations use `ROWS BETWEEN`, not time-based windows
- 🏗️ **5-Algorithm Ensemble**: RandomForest, XGBoost, LightGBM, LSTM, GRU per pair (140 total models)
- ☁️ **Cloud-Native**: Built on Google Cloud Platform (BigQuery, Vertex AI, Cloud Run)
- 📈 **100% Project Coverage**: 70 stages across 11 phases, all scoring 90+

### Critical Mandates

1. **BQX Paradigm Shift** (2024-11-24): BQX values can be BOTH features (lags) AND targets (leads)
2. **Interval-Centric**: Use ROWS BETWEEN only, NEVER time-based windows
3. **Model Isolation**: Complete independence between 28 currency pair models
4. **AirTable Truth**: P03 project is single source of truth

## 🏗️ Architecture

### Currency Pairs (28 Total)
```
Majors:     EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD
EUR Crosses: EURGBP, EURJPY, EURCHF, EURAUD, EURCAD, EURNZD
GBP Crosses: GBPJPY, GBPCHF, GBPAUD, GBPCAD, GBPNZD
AUD Crosses: AUDJPY, AUDCHF, AUDCAD, AUDNZD
NZD Crosses: NZDJPY, NZDCHF, NZDCAD
Others:     CADJPY, CADCHF, CHFJPY
```

### Data Pipeline Stages
```
Market Data → regression → lag → regime → agg → align → Model Training
              (OHLCV)    (1-60)  (States) (Windows)      (140 Models)
```

### Repository Structure

```
bqx_ml_v3/
├── intelligence/        # 🧠 8 Intelligence JSON files (context, semantics, ontology, mandates, etc.)
├── docs/                # 📚 35 documentation files (~15,500 lines)
├── scripts/             # 🔧 33 Python/Bash scripts for automation
├── src/                 # 💻 Source code
│   ├── connectors/     # BigQuery, AirTable connectors
│   ├── pipelines/      # Data and ML pipelines
│   ├── models/         # 28 independent model implementations
│   ├── monitoring/     # Monitoring and alerting
│   └── utils/          # Utility functions
├── tests/              # ✅ Test suite (unit, integration, validation)
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── validation/     # Validation tests
├── credentials/        # 🔐 Credentials (gitignored)
├── .secrets/           # 🔒 Secrets (gitignored)
└── archive/            # 📦 Archived files
```

## 🚀 Quick Start

### Prerequisites
- **Python >= 3.10**
- **Node.js >= 18.0** (for VS Code extensions)
- **Google Cloud SDK** (for GCP interaction)
- **GitHub CLI** (for secrets management)

### Installation

```bash
# Clone repository
git clone https://github.com/Schmidtlappin/bqx_ml_v3.git
cd bqx_ml_v3

# Install Python dependencies
pip install -r requirements.txt

# Authenticate with GCP
gcloud auth activate-service-account --key-file=credentials/gcp-sa-key.json
gcloud config set project bqx-ml

# Verify installation
python scripts/validate_environment.py
```

### Configuration

All sensitive credentials are stored in GitHub Secrets:
- `AIRTABLE_API_KEY` - AirTable API access
- `AIRTABLE_BASE_ID` - AirTable base ID
- `GCP_PROJECT_ID` - Google Cloud project
- `GCP_SA_KEY` - Service account key

Access at: https://github.com/Schmidtlappin/bqx_ml_v3/settings/secrets/actions

## 📖 Intelligence Files

Comprehensive knowledge base in `/intelligence`:

| File | Purpose |
|------|---------|
| `context.json` | Project context, infrastructure, team |
| `semantics.json` | Terminology and concept definitions |
| `ontology.json` | Entity relationships and data model |
| `protocols.json` | Development and operational procedures |
| `constraints.json` | Architectural and business constraints |
| `workflows.json` | End-to-end process workflows |
| `mandates.json` | Critical user mandates and requirements |
| `metadata.json` | System metadata and references |

## 📊 Project Status

### Planning (AirTable P03)
- **Phases**: 11 (100% defined)
- **Stages**: 70 (100% scoring 90+, 74.3% scoring 95+)
- **Gap Coverage**: 100% (19 remediation stages added)
- **Current Phase**: P03.02 - Intelligence Architecture

### Implementation
- **BigQuery Tables**: 0 of 1,736 (planned)
- **ML Models**: 0 of 140 (planned)
- **REST APIs**: 0 of 28 (planned)
- **Tests**: 0 of 2,000+ (planned)

## 🔧 Development

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit (with Claude Code co-authorship)
git commit -m "feat: Your feature description

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push and create PR
git push origin feature/your-feature
```

### Testing
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test type
pytest tests/unit/
pytest tests/integration/
pytest tests/validation/
```

### Code Quality
```bash
# Linting
flake8 src/ tests/

# Type checking
mypy src/

# Format code
black src/ tests/
```

## 🔐 Security

- **Secrets**: Never commit secrets to git (enforced by push protection)
- **Credentials**: Use GitHub Secrets or GCP Secret Manager
- **Authentication**: Service accounts with least privilege
- **Encryption**: TLS 1.3 in transit, AES-256 at rest

## 📚 Documentation

Key documents in `/docs`:
- `PROJECT_PLAN_100_PERCENT_COMPLETE.md` - Project completion report
- `BQX_ML_V3_PIPELINE.md` - Data pipeline architecture
- `BQX_ML_FEATURE_MATRIX.md` - Feature engineering specifications
- `PARADIGM_SHIFT_UPDATE_20241124.md` - BQX paradigm shift details
- `SESSION_STATUS_REPORT.md` - Current system status

## 🏢 Infrastructure

### Google Cloud Platform
- **Project**: bqx-ml
- **Compute**: bqx-ml-master (us-east1-b, 34.148.152.67)
- **Data Warehouse**: BigQuery (bqx_ml dataset)
- **ML Platform**: Vertex AI
- **APIs**: Cloud Run

### AirTable
- **Project**: P03
- **Base ID**: appR3PPnrNkVo48mO
- **Phases**: 11
- **Stages**: 70

## 🤝 Contributing

This is a private repository. For authorized contributors:

1. Follow conventional commits
2. Maintain 80%+ test coverage
3. Update documentation
4. Get code review approval
5. Ensure all CI/CD checks pass

## 📞 Support

- **Repository**: https://github.com/Schmidtlappin/bqx_ml_v3
- **Issues**: GitHub Issues (private)
- **Documentation**: `/docs` directory
- **Intelligence**: `/intelligence` JSON files

## 📄 License

**Proprietary** - Private Repository - All Rights Reserved

---

*Last Updated: 2025-11-25*
*Version: 3.0.0*
*Status: Development Phase*
