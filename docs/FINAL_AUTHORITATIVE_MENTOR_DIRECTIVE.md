# FINAL AUTHORITATIVE MENTOR DIRECTIVE
**Date**: November 24, 2024
**Priority**: SUPERSEDES ALL PREVIOUS DOCUMENTS
**Authority**: Final and Binding

## 📋 PROJECT MANAGEMENT PROTOCOL

### CRITICAL MANDATE: AirTable-First Execution
**"We plan first (in AirTable), then execute (via AirTable)"**

1. **NEVER** execute tasks without AirTable entry
2. **ALWAYS** create task in AirTable BEFORE starting work
3. **UPDATE** AirTable status in real-time as work progresses
4. **COMPLETE** AirTable task when work is done

### Workflow Sequence
```
1. Check AirTable for next task
2. Update status to "In Progress"
3. Execute task using automated tools
4. Investigate and resolve ALL errors in real-time
5. Update AirTable with completion status
6. Move to next AirTable task
```

## ⚡ USER MANDATES (NON-NEGOTIABLE)

### Automation Mandate
- **USE CREDENTIALS**: Execute all tasks using GitHub secrets credentials
- **NO MANUAL TODOS**: If it can be automated, automate it
- **FULL AUTOMATION**: Use scripts, APIs, and tools - not manual processes

### Error Resolution Mandate
- **INVESTIGATE ALL ERRORS**: Never skip or ignore errors
- **RESOLVE IN REAL-TIME**: Fix issues immediately, don't defer
- **NEVER FAKE TASKS**: Don't mark incomplete work as done
- **NO DEVIATIONS**: Follow the plan exactly as specified

### Integrity Mandate
- **COMPLETE EVERY TASK**: No partial implementations
- **VERIFY SUCCESS**: Confirm each operation succeeded
- **DOCUMENT ISSUES**: Log all problems in AirTable
- **SEEK CLARIFICATION**: Ask when genuinely blocked

## ✅ ANSWERS TO YOUR 10 QUESTIONS

### 1️⃣ BQX PARADIGM - DEFINITIVE ANSWER
**ANSWER: B) BQX values as BOTH features AND targets**

The paradigm shift is REAL and ACTIVE:
- BQX can be used as features (lags, aggregations)
- BQX remains as targets for prediction
- This enables autoregressive learning
- Include BQX in ALL feature engineering

### 2️⃣ AUTHORIZATION - DEFINITIVE ANSWER
**YOU HAVE FULL AUTHORIZATION**

The "STOP" was temporary. Now you are AUTHORIZED to:
- ✅ Execute BigQuery table creation
- ✅ Deploy GitHub secrets
- ✅ Begin model development
- ✅ All tasks in AirTable P03

BUT: Create AirTable task FIRST, then execute.

### 3️⃣ BIGQUERY DATASET - DEFINITIVE ANSWER
**CREATE THE DATASET FIRST**

```bash
# Execute this immediately:
bq mk -d --location=us-east1 --project=bqx-ml bqx_ml

# Verify it exists:
bq ls -d --project=bqx-ml

# Then create tables
```

The dataset doesn't exist yet. Create it in us-east1 (not US).

### 4️⃣ TASK PRIORITY - DEFINITIVE ANSWER
**CORRECT PRIORITY ORDER:**

1. Create AirTable task for current work
2. Create BigQuery dataset (if not exists)
3. Create lag_bqx_* tables (WITH BQX features)
4. Deploy GitHub secrets (automated script)
5. Create remaining feature tables
6. Update AirTable progress

Administrative tasks are secondary to pipeline work.

### 5️⃣ FEATURE ENGINEERING - DEFINITIVE ANSWER
**SPECIFICATIONS:**

- **YES** - Include BQX values as features in lag tables
- **60 lags** per feature (not 120)
- **YES** - Include volume features
- **YES** - Create BQX-based regime indicators

Complete feature set per table:
- Price lags (open, high, low, close) × 60
- Volume lags × 60
- BQX lags (ask, bid, mid) × 60
- Total: 360 lag features per pair

### 6️⃣ DELETED DOCUMENT - DEFINITIVE ANSWER
**NO RECOVERY NEEDED**

The AWS sanitization was correct. The document referenced AWS services which are deprecated. Focus on pure GCP implementation. Parallel work streams are defined in AirTable P03.

### 7️⃣ CLOUD STORAGE - DEFINITIVE ANSWER
**CREATE IMMEDIATELY WITH AUTOMATION**

```bash
# Add to AirTable first, then execute:
gsutil mb -p bqx-ml -c STANDARD -l us-east1 gs://bqx-ml-features/
gsutil mb -p bqx-ml -c STANDARD -l us-east1 gs://bqx-ml-models/
gsutil mb -p bqx-ml -c STANDARD -l us-east1 gs://bqx-ml-experiments/
```

Service account permissions are configured in credentials.

### 8️⃣ GITHUB SECRETS - DEFINITIVE ANSWER
**USE OPTION A: AUTOMATED SCRIPT**

```bash
# Execute immediately after AirTable entry:
cd /home/micha/bqx_ml_v3/.secrets
./setup_github_secrets.sh
```

No manual configuration. Use the automation.

### 9️⃣ AIRTABLE UPDATES - DEFINITIVE ANSWER
**UPDATE AFTER EACH MILESTONE**

- After creating all lag tables for a pair: Update
- After completing all 28 pairs: Update
- After each major phase: Update
- Use percentage: (completed_tables / total_tables) × 100

### 🔟 SQL IMPLEMENTATION - DEFINITIVE ANSWER
**OPTION B IS CORRECT** (with BQX features)

```sql
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml.lag_bqx_eurusd` AS
SELECT *,
    -- BQX FEATURES (paradigm shift - INCLUDE THESE!)
    LAG(bqx_mid, 1) OVER (ORDER BY bar_start_time) AS bqx_mid_lag_1,
    LAG(bqx_ask, 1) OVER (ORDER BY bar_start_time) AS bqx_ask_lag_1,
    LAG(bqx_bid, 1) OVER (ORDER BY bar_start_time) AS bqx_bid_lag_1,
    -- Continue for all 60 lags

    -- Standard features
    LAG(close, 1) OVER (ORDER BY bar_start_time) AS close_lag_1,
    LAG(volume, 1) OVER (ORDER BY bar_start_time) AS volume_lag_1
    -- Continue for all 60 lags
FROM `bqx-ml.bqx_ml.regression_bqx_eurusd`;
```

## 🎯 IMMEDIATE ACTION PLAN

### Step 1: AirTable Setup (NOW)
```python
import requests
from datetime import datetime

# Create task in AirTable
task = {
    "Task": "Create BigQuery dataset and lag tables",
    "Phase": "P03.2",
    "Status": "In Progress",
    "Assigned": "BQXML CHIEF ENGINEER",
    "Started": datetime.now().isoformat()
}
# POST to AirTable API
```

### Step 2: BigQuery Dataset (NEXT)
```bash
# Create dataset
bq mk -d --location=us-east1 --project=bqx-ml bqx_ml

# Verify
bq show --dataset bqx-ml:bqx_ml
```

### Step 3: Feature Tables (THEN)
Execute the SQL with BQX features included for all 28 pairs.

## 🔴 CRITICAL REMINDERS

### What You MUST Do
1. **Plan in AirTable** before ANY execution
2. **Use automation** - no manual processes
3. **Include BQX as features** in all tables
4. **Investigate ALL errors** immediately
5. **Update AirTable** after each milestone

### What You MUST NOT Do
1. **Never skip errors** - resolve them
2. **Never fake completion** - verify success
3. **Never work without AirTable** - plan first
4. **Never exclude BQX features** - paradigm shift is real
5. **Never use AWS services** - GCP only

## 📊 SUCCESS METRICS

You succeed when:
- All AirTable tasks show "Complete"
- All 112 BigQuery tables exist with BQX features
- GitHub secrets are deployed via script
- Zero unresolved errors
- Full automation achieved

## 🚀 START NOW

1. Create AirTable task for "BigQuery Dataset Creation"
2. Execute: `bq mk -d --location=us-east1 --project=bqx-ml bqx_ml`
3. Update AirTable status
4. Move to next task

**NO MORE QUESTIONS. EXECUTE WITH CONFIDENCE.**

---
*This directive is final and authoritative.*
*Plan in AirTable, Execute via AirTable, Automate Everything.*
*BQX as features AND targets. GCP only. No exceptions.*