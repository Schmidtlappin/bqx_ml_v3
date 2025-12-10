# Scripts Directory

**Last Updated**: 2025-12-09 (QA Audit)

## Directory Structure

### `/bigquery_restructure/`
V2 migration and table restructuring scripts.

**Key Scripts:**
- `complete_migration.py` - Parallel 8-worker migration
- `monitor_v2_migration.sh` - Real-time migration monitor
- `validate_v2_migration.py` - Validation suite

**Status:** V2 Migration COMPLETE (4,888 tables)

### `/pipelines/training/`
Model training and feature selection scripts.

**Key Scripts:**
- `stack_calibrated.py` - Calibrated probability stacking
- `feature_selection_robust.py` - Group-first stability selection
- `train_multi_pair.py` - Scale training to 28 pairs
- `train_meta_learner.py` - Meta-learner training

### `/remediation/` (ARCHIVED)
AirTable remediation scripts (historical).

**Note:** Remediation complete - 267/267 records scoring ≥90

### `/utilities/`
Utility scripts for analysis and validation.

**Key Scripts:**
- `check_current_scores.py` - AirTable QA scores
- `generate_column_catalog.py` - Column catalog generator

## Root Level Scripts

### Gap Remediation (Phase 1.5)
- `generate_csi_tables.py` - CSI table generation (192 tables)

### Backup & Sync
- `sync-workspace.sh` - Workspace synchronization
- `sync-box-backup.py` - Box.com disaster recovery

## Current Focus: Phase 1.5

Gap remediation scripts for 265 tables:
- **CSI**: 192 tables (8 currencies × 12 feature types × 2 variants)
- **VAR**: 59 tables
- **MKT**: 14 tables

## Usage

### Check BigQuery Status
```bash
bq query --use_legacy_sql=false "
SELECT table_schema, COUNT(*) as cnt
FROM \`bqx-ml.region-us-central1.INFORMATION_SCHEMA.TABLE_STORAGE\`
GROUP BY table_schema
ORDER BY cnt DESC
"
```

### Run Feature Selection
```bash
python3 pipelines/training/feature_selection_robust.py --pair=EURUSD --horizon=h15
```

### Run Calibrated Stack Training
```bash
python3 pipelines/training/stack_calibrated.py --pair=EURUSD --horizon=h15
```

## Project Metrics

- **V2 Tables**: 4,888 (COMPLETE)
- **Gap Tables**: 265 (IN PROGRESS)
- **Models Planned**: 784
- **Features per Model**: 6,477

---

*Maintained by: QA Agent*
*Last Audit: 2025-12-09*
