# BQX ML v3: 28 Independent Models with BQX Targets

## Overview

BQX ML v3 implements a paradigm shift from monolithic to specialized modeling, featuring 28 independent models that predict BQX momentum values for each currency pair.

### Key Principles

- **Interval-Centric Architecture**: All calculations use `ROWS BETWEEN`, not time periods
- **BQX as Targets Only**: BQX values are forward-looking predictions, never features
- **28 Independent Models**: Each currency pair has its own specialized model
- **Clean Separation**: Strict separation between features (backward-looking) and targets (forward-looking)

## Repository Structure

```
bqx_ml_v3/
├── .bqx_ml_v3/          # Repository intelligence
├── docs/                # Documentation
├── src/                 # Source code
│   ├── connectors/     # BigQuery, AirTable
│   ├── pipelines/      # Data and ML pipelines
│   └── models/         # 28 independent models
├── scripts/            # Execution scripts
└── tests/             # Testing suite
```

## Migration Status

Migrated from: `bqx-db`
AirTable Project: `P03`
Status: Foundation Phase

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up credentials
source credentials/setup_env.sh

# Run validation
python scripts/validate_migration.py
```

---

*Private Repository - Proprietary Code*
