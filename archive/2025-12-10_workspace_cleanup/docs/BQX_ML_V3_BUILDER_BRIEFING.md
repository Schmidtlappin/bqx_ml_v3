# BQX ML V3 BUILDER AGENT BRIEFING

**Document Type**: Project Status Brief & Implementation Directive
**Date**: November 26, 2025
**From**: Chief Engineer, BQX ML V3 Project
**To**: BQX ML V3 Builder Agent
**Subject**: Current Infrastructure Status & Build Completion Directive

---

## 🎯 MISSION BRIEF

You are tasked with **completing the BQX ML V3 build** from its current state. The project has been initiated with some real infrastructure in place. Your mission is to:

1. **Leverage existing infrastructure** (verified below)
2. **Complete all 197 tasks** in the AirTable project plan
3. **Create REAL infrastructure** for every task
4. **Report progress** through AirTable updates

---

## ✅ CURRENT INFRASTRUCTURE STATUS (VERIFIED)

### What Already Exists (DO NOT RECREATE):

#### BigQuery Datasets (5/5 Complete)
```sql
✅ bqx-ml:bqx_ml_v3_features      -- Feature engineering data
✅ bqx-ml:bqx_ml_v3_models         -- Model artifacts and metadata
✅ bqx-ml:bqx_ml_v3_predictions    -- Prediction outputs
✅ bqx-ml:bqx_ml_v3_staging        -- Staging area for data processing
✅ bqx-ml:bqx_ml_v3_analytics      -- Analytics and reporting
```

#### BigQuery Tables (10/56 Complete)
```sql
-- Feature tables for 5 currency pairs (need 23 more pairs)
✅ bqx_ml_v3_features.eurusd_idx   ✅ bqx_ml_v3_features.eurusd_bqx
✅ bqx_ml_v3_features.gbpusd_idx   ✅ bqx_ml_v3_features.gbpusd_bqx
✅ bqx_ml_v3_features.usdjpy_idx   ✅ bqx_ml_v3_features.usdjpy_bqx
✅ bqx_ml_v3_features.audusd_idx   ✅ bqx_ml_v3_features.audusd_bqx
✅ bqx_ml_v3_features.usdcad_idx   ✅ bqx_ml_v3_features.usdcad_bqx

❌ Missing: Tables for remaining 23 currency pairs
❌ Missing: Model performance tracking tables
❌ Missing: Prediction log tables
```

#### Google Cloud Storage (1/4 Complete)
```bash
✅ gs://bqx-ml-v3-models/          -- Model storage bucket exists

❌ Missing: gs://bqx-ml-v3-data/
❌ Missing: gs://bqx-ml-v3-predictions/
❌ Missing: gs://bqx-ml-v3-staging/
```

#### Machine Learning Models (2/196 Complete)
```
✅ EURUSD model for 45-interval window
✅ EURUSD model for 90-interval window

❌ Missing: 194 models (remaining windows + all other pairs)
```

#### Vertex AI Resources (0/28 Complete)
```
❌ No endpoints deployed
❌ No training pipelines configured
❌ No batch prediction jobs scheduled
❌ No monitoring dashboards created
```

---

## 📊 AIRTABLE PROJECT STATUS

### Current State:
- **Total Tasks**: 197
- **Completed**: 0 (all reset to Todo for clean tracking)
- **In Progress**: 0
- **Todo**: 197

### Phase Breakdown:
| Phase | Description | Tasks | Priority |
|-------|-------------|-------|----------|
| P01 | Baseline Model Development | 17 | **START HERE** |
| P02 | Data Indexing & Intelligence | 23 | Critical |
| P03 | Cross-Validation & Features | 12 | Critical |
| P04 | Model Optimization | 13 | High |
| P05 | Currency Pair Relationships | 15 | High |
| P06 | BQX Paradigm Implementation | 25 | High |
| P07 | Advanced Features | 17 | Medium |
| P08 | Performance Optimization | 18 | Medium |
| P09 | Deployment and Serving | 25 | Critical |
| P10 | Production Validation | 16 | High |
| P11 | Security and Compliance | 16 | High |

---

## 🚀 IMMEDIATE NEXT STEPS

### Priority 1: Complete Foundation (P01)
Start with these tasks from Phase P01:

1. **MP03.P01.S01.T01**: Prepare training dataset
   - Load data from BigQuery
   - Create train/test splits
   - Implement temporal isolation

2. **MP03.P01.S02.T01**: Initialize Random Forest model
   - Set up baseline configuration
   - Create training script
   - Store model in GCS

3. **MP03.P01.S03.T01**: Load training data from BigQuery
   - Create data pipeline
   - Validate data quality
   - Set up feature preprocessing

### Priority 2: Complete Data Infrastructure (P02)
Continue with data indexing for remaining 23 currency pairs:

```python
remaining_pairs = [
    'USDCHF', 'NZDUSD', 'EURJPY', 'GBPJPY', 'EURGBP',
    'EURAUD', 'EURCAD', 'EURCHF', 'EURNZD', 'AUDJPY',
    'CADJPY', 'CHFJPY', 'NZDJPY', 'AUDCAD', 'AUDCHF',
    'AUDNZD', 'CADCHF', 'GBPAUD', 'GBPCAD', 'GBPCHF',
    'GBPNZD', 'NZDCAD', 'NZDCHF'
]
```

For each pair, create:
- `{pair}_idx` table (indexed OHLCV values)
- `{pair}_bqx` table (BQX momentum features)

### Priority 3: Train Models (P04)
For each pair-window combination:
1. Load features from BigQuery
2. Train XGBoost model
3. Validate quality gates (R² ≥ 0.35)
4. Save to GCS bucket
5. Register in model catalog

---

## 📝 TASK EXECUTION PROTOCOL

### For Each Task:

1. **RETRIEVE from AirTable**
   ```python
   # Get next Todo task
   task = get_next_todo_task()
   update_status(task.id, "In Progress")
   ```

2. **IMPLEMENT with Real Commands**
   ```bash
   # Example: Create table
   bq mk --table "bqx-ml:bqx_ml_v3_features.nzdusd_idx" \
     interval_time:TIMESTAMP,pair:STRING,open_idx:FLOAT64...
   ```

3. **VERIFY Infrastructure**
   ```bash
   # Confirm creation
   bq show bqx-ml:bqx_ml_v3_features.nzdusd_idx
   ```

4. **UPDATE AirTable**
   ```python
   update_task(task.id,
     status="Done",
     notes=f"""
     ### Completed: {timestamp}

     Created: bqx-ml:bqx_ml_v3_features.nzdusd_idx

     Verification:
     bq show bqx-ml:bqx_ml_v3_features.nzdusd_idx

     Status: ✅ Verified
     """)
   ```

---

## ⚠️ CRITICAL REQUIREMENTS

### Quality Gates (MUST ACHIEVE)
- **R² Score**: ≥ 0.35 for all models
- **RMSE**: ≤ 0.15 for all models
- **Directional Accuracy**: ≥ 55% for all models
- **Inference Latency**: < 100ms
- **Throughput**: ≥ 1000 QPS

### INTERVAL-CENTRIC Implementation
```sql
-- CORRECT: Use ROWS BETWEEN (intervals)
LAG(close, 45) OVER (
  PARTITION BY pair
  ORDER BY interval_time
  ROWS BETWEEN 45 PRECEDING AND CURRENT ROW
)

-- WRONG: Never use RANGE BETWEEN (time)
```

### Data Leakage Prevention
- Use LAG for features (look back)
- Use LEAD for targets (look forward)
- Maintain 100-interval gap in cross-validation

---

## 📊 PROGRESS TRACKING

### Daily Deliverables Expected:
- **Minimum 10 tasks** moved from Todo → Done
- **All infrastructure verified** before marking Done
- **AirTable notes updated** with verification commands

### Weekly Milestones:
- Week 1: Complete P01 & P02 (40 tasks)
- Week 2: Complete P03, P04, P05 (40 tasks)
- Week 3: Complete P06, P07 (42 tasks)
- Week 4: Complete P08, P09 (43 tasks)
- Week 5: Complete P10, P11 (32 tasks)

---

## 🔧 TECHNICAL RESOURCES

### Environment Variables
```bash
export PROJECT_ID=bqx-ml
export REGION=us-central1
export DATASET_PREFIX=bqx_ml_v3
```

### Key Scripts Available
```
/home/micha/bqx_ml_v3/scripts/
├── create_feature_tables.py      # Template for table creation
├── check_airtable_status.py      # Monitor task status
└── check_gcp_services.py         # Verify GCP services
```

### Credentials
```python
# AirTable access
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
    secrets = json.load(f)
    API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
    BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']
```

---

## 📞 ESCALATION & SUPPORT

### When to Escalate to Chief Engineer:
- Quota limits reached
- Permission denied errors
- Unclear task requirements
- Technical blockers
- Quality gates not achievable

### How to Escalate:
1. Document issue in AirTable task notes
2. Keep task as "In Progress"
3. Include error messages and attempted solutions
4. Await guidance through user relay

---

## 🎯 SUCCESS CRITERIA

Your build will be considered **COMPLETE** when:

1. ✅ All 197 tasks show "Done" status in AirTable
2. ✅ All infrastructure is verified in GCP
3. ✅ 196 models trained and deployed (28 pairs × 7 windows)
4. ✅ All quality gates achieved
5. ✅ Production endpoints serving predictions
6. ✅ Monitoring dashboards operational

---

## 🚦 AUTHORIZATION TO PROCEED

You are hereby **authorized and directed** to:
1. Begin immediate implementation
2. Create all required GCP resources
3. Update AirTable in real-time
4. Complete the entire BQX ML V3 build

**Expected Completion**: 5 weeks from start date
**Daily Check-ins**: Via AirTable updates
**Weekly Reviews**: Progress assessment by Chief Engineer

---

## 📋 FIRST TASK TO EXECUTE

**Start with**: MP03.P01.S01.T01 - "Prepare training dataset"

1. Query AirTable for this task
2. Update to "In Progress"
3. Implement the data preparation
4. Verify results
5. Update to "Done" with outcomes
6. Move to next task

---

**Chief Engineer**: Claude (BQX ML V3)
**Date**: November 26, 2025
**Status**: BRIEFING COMPLETE - BUILD AUTHORIZED

**BEGIN IMPLEMENTATION IMMEDIATELY**