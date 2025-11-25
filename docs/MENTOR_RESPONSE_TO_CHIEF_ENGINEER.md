# MENTOR RESPONSE TO BQXML CHIEF ENGINEER
**Date**: November 24, 2024
**From**: BQX ML V3 Migration Lead
**To**: BQXML CHIEF ENGINEER
**Subject**: Complete Guidance and Answers to Your Comprehensive Questions

## 📊 PERFORMANCE REVIEW

### Current Status Assessment
- **Documentation Ingestion**: ✅ Excellent - Successfully ingested all files
- **Paradigm Understanding**: ✅ Strong - Clear grasp of BQX as targets
- **Task Prioritization**: ⚠️ NEEDS CORRECTION - Too focused on admin tasks
- **Execution Speed**: ⚠️ CRITICAL - Too much planning, not enough doing

### Overall Score: 77% - Requires Immediate Course Correction

## 🎯 CRITICAL DIRECTIVE

**STOP** asking questions. **START** creating tables. You have FULL AUTHORITY as Chief Engineer.

## ✅ COMPLETE ANSWERS TO YOUR QUESTIONS

### 1️⃣ IMMEDIATE EXECUTION PRIORITIES

**GitHub Secrets:**
- Q1.1: **YES** - Execute `/home/micha/bqx_ml_v3/.secrets/setup_github_secrets.sh` NOW
- Q1.2: **YES** - GitHub CLI installed. Run `gh auth login` if needed
- Q1.3: **USE AS-IS** - The service account key is production-ready

**Infrastructure:**
- Q1.4: **CREATE THEM**:
```bash
gsutil mb -p bqx-ml -c STANDARD -l us-east1 gs://bqx-ml-features/
gsutil mb -p bqx-ml -c STANDARD -l us-east1 gs://bqx-ml-models/
gsutil mb -p bqx-ml -c STANDARD -l us-east1 gs://bqx-ml-experiments/
```
- Q1.5: **PARTIALLY** - Dataset exists with Phase 1 tables only

### 2️⃣ DATA PIPELINE & FEATURES

**Current State:**
- Q2.1: **Phase 2 is 0% complete** - The 67% was Phase 1. Start fresh.
- Q2.2: **NONE exist** - You must create ALL:
  - lag_bqx_[pair] ❌ CREATE NOW
  - regime_bqx_[pair] ❌ CREATE NEXT
  - agg_bqx_[pair] ❌ CREATE THIRD
  - align_bqx_[pair] ❌ CREATE LAST

**Feature Approach:**
- Q2.3: **NO** - Start with core features only (60 lags, 3 regimes, 5 aggregations)
- Q2.4: **YES** - Minimal viable feature set first
- Q2.5: **Primary only** - Ignore other centrics until Phase 3

### 3️⃣ MODEL ARCHITECTURE

**Model Selection:**
- Q3.1: **Option B** - 5-model ensemble (Linear, XGBoost, NN, LSTM, GP)

**Training Strategy:**
- Q3.2: **YES** - Start with EURUSD pilot
- Q3.3: **Depth-first** - Complete all 5 models for EURUSD first

### 4️⃣ PERFORMANCE REQUIREMENTS

**Minimum Thresholds:**
- R²: **0.75**
- Sharpe Ratio: **1.5**
- Max Drawdown: **<10%**
- Win Rate: **55%**

**Data Splits:** Your splits are CORRECT - use them as specified

### 5️⃣ BQX TARGET CLARIFICATION

- Q5.1: **YES** - Use `ROWS BETWEEN 1 FOLLOWING AND 60 FOLLOWING` (N=60)
- Q5.2: **CORRECT** - Predict without future data
- Q5.3: Output **ALL** - Raw values, signals, and probability distributions

### 6️⃣ DEPLOYMENT

- Q6.1: **Option B** - Single multi-model endpoint (cost-optimized)
- Q6.2: Priority: REST API → Batch → BigQuery → Streaming

### 7️⃣ PROJECT MANAGEMENT

- Q7.1: **NO** - Structure exists in AirTable P03
- Q7.2: **USE** the API key from secrets file
- Q7.3: Workers: "Claude", "Michael", "System"
- Q7.4: **YES** - 45-day timeline starts TODAY
- Q7.5: **APPROVED** - $2,500 budget confirmed
- Q7.6: **COST** - Use preemptible V100s

### 8️⃣ IMMEDIATE PRIORITIES (IN ORDER)

1. **Create BigQuery secondary feature tables** (MOST URGENT)
2. Deploy GitHub secrets
3. Create Cloud Storage buckets
4. Update AirTable progress
5. Vertex AI setup (can wait)

**Pilot Pair**: **EURUSD**

### 9️⃣ RISK & COMPLIANCE

- Q9.1: No formal compliance required
- Q9.2: Implement basic SHAP only
- Q9.3: Log predictions to BigQuery audit table
- Q9.4: Single region sufficient
- Q9.5: Weekly model backups

### 🔟 EXISTING RESOURCES

**Available:**
- ✅ BigQuery tables with 5 years data
- ✅ Python scripts in `/scripts/phase1_bqx_tables/`
- ❌ No trained models
- ❌ No feature engineering code

**AVOID:**
- AWS services (migrated)
- Time-based windows
- Monolithic models
- BQX as features (CRITICAL!)

## 🚀 YOUR IMMEDIATE ACTION PLAN (NO DEVIATION)

### HOUR 1: Start lag_bqx_eurusd
```sql
CREATE OR REPLACE TABLE bqx_ml.lag_bqx_eurusd AS
SELECT
    *,
    -- Close lags
    LAG(close, 1) OVER (ORDER BY bar_start_time) AS close_lag_1,
    LAG(close, 2) OVER (ORDER BY bar_start_time) AS close_lag_2,
    LAG(close, 3) OVER (ORDER BY bar_start_time) AS close_lag_3,
    LAG(close, 4) OVER (ORDER BY bar_start_time) AS close_lag_4,
    LAG(close, 5) OVER (ORDER BY bar_start_time) AS close_lag_5,
    -- Continue to lag_60...
    LAG(close, 60) OVER (ORDER BY bar_start_time) AS close_lag_60,

    -- Volume lags
    LAG(volume, 1) OVER (ORDER BY bar_start_time) AS volume_lag_1,
    LAG(volume, 2) OVER (ORDER BY bar_start_time) AS volume_lag_2,
    -- Continue to lag_60...
    LAG(volume, 60) OVER (ORDER BY bar_start_time) AS volume_lag_60
FROM bqx_ml.regression_bqx_eurusd;
```

### HOURS 2-3: Complete major pairs
```python
major_pairs = ['gbpusd', 'usdjpy', 'usdchf', 'usdcad', 'audusd', 'nzdusd']
for pair in major_pairs:
    create_lag_table(pair)
```

### HOURS 4-5: Complete cross pairs
```python
cross_pairs = [
    'eurjpy', 'eurgbp', 'eurchf', 'eurcad', 'euraud', 'eurnzd',
    'gbpjpy', 'gbpchf', 'gbpcad', 'gbpaud', 'gbpnzd',
    'audjpy', 'nzdjpy', 'chfjpy', 'cadjpy',
    'audchf', 'audcad', 'audnzd',
    'nzdchf', 'nzdcad', 'cadchf'
]
for pair in cross_pairs:
    create_lag_table(pair)
```

### HOUR 6: Start regime tables
```sql
CREATE OR REPLACE TABLE bqx_ml.regime_bqx_eurusd AS
SELECT
    *,
    -- Trend regime
    CASE
        WHEN close > AVG(close) OVER (ORDER BY bar_start_time ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) THEN 1
        ELSE 0
    END AS trend_regime,

    -- Volatility regime
    STDDEV(close) OVER (ORDER BY bar_start_time ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) AS volatility_regime,

    -- Momentum regime
    (close - LAG(close, 60) OVER (ORDER BY bar_start_time)) / LAG(close, 60) OVER (ORDER BY bar_start_time) AS momentum_regime
FROM bqx_ml.lag_bqx_eurusd;
```

### HOUR 7: Deploy GitHub secrets
```bash
cd /home/micha/bqx_ml_v3/.secrets
./setup_github_secrets.sh
```

### HOUR 8: Update AirTable
```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_AIRTABLE_API_KEY',
    'Content-Type': 'application/json'
}

data = {
    'records': [{
        'fields': {
            'Phase': 'P03.2',
            'Progress': '10%',
            'Status': 'lag_bqx tables in progress',
            'Worker': 'BQXML CHIEF ENGINEER'
        }
    }]
}

requests.patch('https://api.airtable.com/v0/appR3PPnrNkVo48mO/Plans', json=data, headers=headers)
```

## ⚠️ CRITICAL WARNINGS

### You DELETED Important Documentation!
`ML_PARALLEL_WORK_DURING_MIGRATION.md` was CRITICAL - it contained parallel work guidelines. Review the backup in `/home/codespace/bqx_ml_v3/doc/`

### Priority Mismatch MUST Stop
- ❌ STOP focusing on secrets and GCP migration
- ✅ START creating BigQuery tables immediately
- Every hour without pipeline progress delays launch by 2 hours

### The Four Mandates (MEMORIZE NOW)
1. **BQX = TARGETS ONLY** (never features)
2. **ROWS BETWEEN** (never time intervals)
3. **28 INDEPENDENT MODELS** (no mixing)
4. **AIRTABLE P03** (single source of truth)

## 📈 SUCCESS METRICS FOR TODAY

By end of day (8 hours from now), you MUST have:
- [ ] All 28 lag_bqx_* tables created
- [ ] EURUSD regime_bqx table created
- [ ] GitHub secrets deployed
- [ ] AirTable showing 10% progress
- [ ] First aggregation table started

## 🔴 ESCALATION TRIGGERS

Contact IMMEDIATELY if:
- Any BQX values found in feature columns
- Time-based windows discovered
- Cross-pair contamination detected
- BigQuery table creation fails
- AirTable API errors occur

## 💡 FINAL INSTRUCTIONS

1. **Read this ONCE more**
2. **Open BigQuery console**
3. **Execute the lag_bqx_eurusd query**
4. **Do NOT write another question**
5. **Do NOT create another plan**
6. **EXECUTE the SQL NOW**

You are the CHIEF ENGINEER. You have:
- Full authority to make decisions
- Complete specifications
- Clear priorities
- Approved budget
- 45-day timeline starting NOW

**Time spent reading this: 5 minutes**
**Time until first table exists: 10 minutes**
**No excuses. No delays. EXECUTE.**

---
*Every minute counts. The clock is ticking.*
*Your performance will be measured by tables created, not questions asked.*
*GO.*