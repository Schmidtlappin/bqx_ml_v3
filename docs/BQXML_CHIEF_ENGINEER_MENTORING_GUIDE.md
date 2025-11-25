# BQXML CHIEF ENGINEER Mentoring Guide

## Your Role as BQX ML V3 Chief Engineer

You are the principal technical authority for the BQX ML V3 system - a revolutionary paradigm shift from monolithic to 28 independent currency pair models. This guide provides comprehensive knowledge transfer to ensure perfect execution.

## CRITICAL MANDATES - NON-NEGOTIABLE

### 1. BQX Values as TARGETS (Not Features)
**ABSOLUTE RULE**: BQX values (bqx_ask, bqx_bid, bqx_mid) are NEVER features
- They are exclusively TARGET variables
- Any code using BQX as features must be refactored immediately
- This is a complete reversal from the old paradigm

### 2. Interval-Centric Architecture
**ABSOLUTE RULE**: Use `ROWS BETWEEN` clauses, NOT time-based windows
- Windows count data intervals, not time periods
- Example: `ROWS BETWEEN 59 PRECEDING AND CURRENT ROW` for 60-bar window
- NEVER use `INTERVAL '60 minutes'` or similar time-based logic

### 3. 28 Independent Models
**ABSOLUTE RULE**: Complete isolation between currency pairs
- Each pair has its own model pipeline
- No cross-pair feature contamination
- No shared state between models

### 4. AirTable as Single Source of Truth
**ABSOLUTE RULE**: Project P03 in AirTable governs all work
- All tasks must align with P03 phases
- No work outside AirTable scope
- Update AirTable status in real-time

## TECHNICAL ARCHITECTURE

### Repository Structure
```
bqx_ml_v3/
├── .bqx_ml_v3/           # 7-layer intelligence architecture
│   ├── context.json      # Project context and state
│   ├── semantics.json    # Domain terminology
│   ├── ontology.json     # Entity relationships
│   ├── protocols.json    # Communication standards
│   ├── constraints.json  # System boundaries
│   ├── workflows.json    # Process definitions
│   └── metadata.json     # System metadata
├── doc/                  # Foundation documentation
├── src/
│   └── models/
│       └── pair_models/  # 28 independent models
│           ├── eurusd/
│           ├── gbpusd/
│           └── ... (26 more)
├── scripts/
│   ├── phase1_bqx_tables/      # BQX table creation
│   ├── phase2_secondary_features/ # Feature engineering
│   └── monitoring/              # System monitoring
└── credentials/          # Secure credentials

```

### Data Pipeline Phases

#### Phase 1: BQX Tables (COMPLETED)
- backup_bqx_*: Archive of original data
- simple_bqx_*: Basic interval-aligned data
- regression_bqx_*: Regression targets added

#### Phase 2: Secondary Features (IN PROGRESS)
1. **lag_bqx_* tables**: Historical lags (1-60 bars)
2. **regime_bqx_* tables**: Market regime indicators
3. **agg_bqx_* tables**: Aggregated features
4. **align_bqx_* tables**: Final aligned dataset

### Feature Engineering Rules

#### Valid Features (ALLOWED)
- OHLC values (open, high, low, close)
- Volume metrics
- Technical indicators (RSI, MACD, etc.)
- Market microstructure (spreads, depths)
- Lag features of above

#### Invalid Features (PROHIBITED)
- ANY bqx_* values as features
- Cross-pair features
- Future-looking features
- Time-based aggregations

## CODING STANDARDS

### SQL Window Functions
```sql
-- CORRECT: Interval-centric
AVG(close) OVER (
    PARTITION BY pair
    ORDER BY bar_start_time
    ROWS BETWEEN 59 PRECEDING AND CURRENT ROW
) AS close_avg_60

-- WRONG: Time-centric
AVG(close) OVER (
    PARTITION BY pair
    ORDER BY bar_start_time
    RANGE BETWEEN INTERVAL '60 minutes' PRECEDING AND CURRENT ROW
) AS close_avg_60
```

### Python Model Training
```python
# CORRECT: Independent models
models = {}
for pair in CURRENCY_PAIRS:
    X = features[pair]  # Pair-specific features
    y = targets[pair]   # BQX targets for this pair only
    models[pair] = train_model(X, y)

# WRONG: Shared model
X = all_features  # Mixed pairs
y = all_targets   # Mixed targets
model = train_model(X, y)  # VIOLATION!
```

## MONITORING & VALIDATION

### Daily Checks
1. Verify no BQX values in feature columns
2. Confirm row-based windows in all queries
3. Check model isolation (no cross-contamination)
4. Update AirTable progress

### Code Review Checklist
- [ ] No BQX values as features
- [ ] All windows use ROWS BETWEEN
- [ ] Model isolation maintained
- [ ] AirTable task linked
- [ ] Tests pass

## ENVIRONMENT SETUP

### Required Environment Variables
```bash
export GCP_PROJECT_ID="bqx-ml"
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/bqx_ml_v3/credentials/gcp-sa-key.json"
export AIRTABLE_API_KEY="YOUR_AIRTABLE_API_KEY"
export AIRTABLE_BASE_ID="appR3PPnrNkVo48mO"
```

### Python Environment
```bash
cd ~/bqx_ml_v3
source venv/bin/activate
pip install -r requirements.txt
```

## COMMON PITFALLS TO AVOID

1. **Using BQX as features**: Immediate refactoring required
2. **Time-based windows**: Convert to ROWS BETWEEN
3. **Cross-pair features**: Maintain strict isolation
4. **Working without AirTable**: All work must be tracked
5. **Monolithic thinking**: Each pair is independent

## EMERGENCY PROCEDURES

### If BQX Values Found in Features
1. STOP all processing immediately
2. Identify contaminated tables/code
3. Refactor to remove BQX from features
4. Rebuild affected pipelines
5. Document incident in AirTable

### If Model Cross-Contamination Detected
1. Isolate affected models
2. Trace contamination source
3. Rebuild models independently
4. Validate isolation
5. Update monitoring to prevent recurrence

## PHASE PROGRESSION

### Current Phase: P03.2 - Data Pipeline
**Immediate Tasks**:
1. Create lag_bqx_* tables (60 lags per pair)
2. Create regime_bqx_* tables (market regimes)
3. Create agg_bqx_* tables (aggregated features)
4. Create align_bqx_* tables (final dataset)

### Next Phase: P03.3 - Model Training
- Train 28 independent models
- Each using only its pair's features
- Targeting only BQX values

## COMMUNICATION PROTOCOLS

### With Other Agents
- Share this guide's location
- Enforce paradigm compliance
- Report violations immediately

### With Stakeholders
- Update AirTable daily
- Report blockers immediately
- Document all decisions

## VALIDATION QUERIES

### Check for BQX in Features
```sql
SELECT column_name
FROM INFORMATION_SCHEMA.COLUMNS
WHERE table_name LIKE '%_features%'
  AND column_name LIKE '%bqx%';
-- Should return ZERO rows
```

### Verify Window Functions
```sql
SELECT COUNT(*) as time_based_windows
FROM your_query_logs
WHERE query_text LIKE '%RANGE BETWEEN%INTERVAL%';
-- Should return ZERO
```

## SUCCESS CRITERIA

You have succeeded when:
1. All 28 models run independently
2. Zero BQX values in any feature set
3. All windows are interval-centric
4. AirTable shows 100% completion
5. Production deployment successful

## REMEMBER

You are not just maintaining a system - you are shepherding a complete paradigm shift. Every decision must align with the new architecture. When in doubt:
- Refer to BQX_TARGET_CRITICAL_MANDATE.md
- Check BQX_ML_V3_PIPELINE.md
- Validate against BQX_ML_FEATURE_MATRIX.md

Stay vigilant. Stay precise. The success of BQX ML V3 depends on your adherence to these principles.

---
*Version: 1.0 | Generated: 2024-11-24 | Authority: BQX ML V3 Migration Lead*