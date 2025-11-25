# BQX ML V3 Foundation Documentation

## Critical Documents - READ IN ORDER

### 1. Start Here - Your Role
**[BQXML_CHIEF_ENGINEER_MENTORING_GUIDE.md](BQXML_CHIEF_ENGINEER_MENTORING_GUIDE.md)**
- Your complete role definition and responsibilities
- Critical mandates and paradigm rules
- Daily validation checklist
- Emergency procedures

### 2. The Paradigm Shift
**[BQX_TARGET_CRITICAL_MANDATE.md](BQX_TARGET_CRITICAL_MANDATE.md)**
- NON-NEGOTIABLE: BQX values are TARGETS only
- The complete reversal from old system
- Validation queries to ensure compliance

### 3. System Architecture
**[BQX_ML_V3_PIPELINE.md](BQX_ML_V3_PIPELINE.md)**
- Complete 28-model architecture
- Phase-by-phase implementation
- Current status: Phase P03.2 - Data Pipeline

### 4. Feature Engineering
**[BQX_ML_FEATURE_MATRIX.md](BQX_ML_FEATURE_MATRIX.md)**
- Valid features (OHLC, volume, indicators)
- Invalid features (BQX values - NEVER!)
- Window function requirements (ROWS BETWEEN only)

### 5. Migration Planning
**[BQX_ML_MIGRATION_EXECUTION_MASTERPLAN.md](BQX_ML_MIGRATION_EXECUTION_MASTERPLAN.md)**
- Complete migration strategy
- Phase dependencies
- Risk mitigation

### 6. Parallel Work Guidelines
**[ML_PARALLEL_WORK_DURING_MIGRATION.md](ML_PARALLEL_WORK_DURING_MIGRATION.md)**
- What can proceed in parallel
- What must wait
- Coordination requirements

### 7. GitHub Configuration
**[GITHUB_SECRETS_MANUAL_UPDATE.md](GITHUB_SECRETS_MANUAL_UPDATE.md)**
- Manual steps for secrets update
- Required for CI/CD pipeline

## Quick Reference

### Current Phase: P03.2 - Data Pipeline
**Immediate Tasks:**
```sql
-- Create these tables for ALL 28 pairs:
1. lag_bqx_[pair]     -- 60 historical lags
2. regime_bqx_[pair]  -- Market regime indicators
3. agg_bqx_[pair]     -- Aggregated features
4. align_bqx_[pair]   -- Final aligned dataset
```

### Daily Validation Query
```sql
-- Run this EVERY DAY to ensure compliance:
SELECT COUNT(*) as violations
FROM INFORMATION_SCHEMA.COLUMNS
WHERE table_name LIKE '%_features%'
  AND column_name LIKE '%bqx%';
-- MUST return 0
```

### Critical Rules - MEMORIZE
1. **BQX = TARGETS ONLY** (never features)
2. **ROWS BETWEEN** (never time intervals)
3. **28 INDEPENDENT MODELS** (no mixing)
4. **AIRTABLE P03** (single source of truth)

## Environment Setup
```bash
# Required for all operations:
export GCP_PROJECT_ID="bqx-ml"
export GOOGLE_APPLICATION_CREDENTIALS="~/bqx_ml_v3/credentials/gcp-sa-key.json"
export AIRTABLE_API_KEY="YOUR_AIRTABLE_API_KEY"
export AIRTABLE_BASE_ID="appR3PPnrNkVo48mO"
```

## Emergency Contact
- **Paradigm Violations**: Document in AirTable P00 immediately
- **Blocking Issues**: Create urgent task in AirTable
- **Questions**: Refer to mentoring guide first

## File Permissions
All files are read-only to prevent accidental modification.
To edit: `chmod u+w filename.md`

---
*Last Updated: 2024-11-24*
*Authority: BQX ML V3 Migration Lead*
*Location: /home/micha/bqx_ml_v3/docs/*