# BQX ML V3 FINAL MENTOR GUIDANCE
**Date**: November 24, 2024
**Supersedes**: ALL previous documents
**Platform**: GCP ONLY - No AWS references
**Critical Update**: BQX as Features AND Targets

## 🎯 DEFINITIVE V3 EXPECTATIONS

### What BQX ML V3 IS
- ✅ 100% Google Cloud Platform
- ✅ 28 independent currency pair models
- ✅ BQX values as BOTH features and targets
- ✅ BigQuery for all data operations
- ✅ Vertex AI for all ML operations
- ✅ Interval-centric (ROWS BETWEEN)

### What BQX ML V3 IS NOT
- ❌ No AWS services (RDS, S3, Lambda, SageMaker)
- ❌ No hybrid cloud architecture
- ❌ No time-based windows
- ❌ No monolithic models
- ❌ No cross-pair contamination
- ❌ BQX as targets only (OLD paradigm)

## 📋 CORRECTED TASK PRIORITIES

### IMMEDIATE (Today - Hour by Hour)

#### Hour 1-2: BigQuery Feature Tables
```sql
-- CORRECT V3 Implementation with BQX features
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml.lag_bqx_eurusd` AS
SELECT
    bar_start_time,
    open, high, low, close, volume,

    -- V3 PARADIGM: BQX as features
    LAG(bqx_mid, 1) OVER (ORDER BY bar_start_time) AS bqx_mid_lag_1,
    LAG(bqx_ask, 1) OVER (ORDER BY bar_start_time) AS bqx_ask_lag_1,
    LAG(bqx_bid, 1) OVER (ORDER BY bar_start_time) AS bqx_bid_lag_1,
    -- Continue to lag_60 for all BQX values

    -- Standard features
    LAG(close, 1) OVER (ORDER BY bar_start_time) AS close_lag_1,
    LAG(volume, 1) OVER (ORDER BY bar_start_time) AS volume_lag_1,
    -- Continue to lag_60

    -- Targets
    bqx_ask,
    bqx_bid,
    bqx_mid

FROM `bqx-ml.bqx_ml.regression_bqx_eurusd`
WHERE bar_start_time >= '2020-01-01';
```

#### Hour 3-4: Scale to Major Pairs
```python
# Pure GCP implementation
from google.cloud import bigquery

client = bigquery.Client(project='bqx-ml')
pairs = ['gbpusd', 'usdjpy', 'usdchf', 'usdcad', 'audusd', 'nzdusd']

for pair in pairs:
    query = f"""
    CREATE OR REPLACE TABLE `bqx-ml.bqx_ml.lag_bqx_{pair}` AS
    -- Include BQX features per V3 paradigm
    """
    client.query(query)
```

#### Hour 5-8: Complete All 28 Pairs
- No AWS operations
- Pure BigQuery processing
- Include BQX features in every table

### THIS WEEK: Model Development

#### Day 2-3: Vertex AI Setup
```bash
# GCP ONLY - No SageMaker
gcloud ai custom-jobs create \
  --region=us-east1 \
  --display-name="bqx-ml-v3-training" \
  --python-package-uris="gs://bqx-ml-models/trainer.tar.gz"
```

#### Day 4-5: Model Training
```python
# Vertex AI Training (NOT AWS SageMaker)
from google.cloud import aiplatform

aiplatform.init(project='bqx-ml', location='us-east1')

job = aiplatform.CustomTrainingJob(
    display_name="bqx-ml-v3-ensemble",
    script_path="trainer.py",
    container_uri="gcr.io/cloud-aiplatform/training/tf-gpu.2-8:latest"
)
```

## 🔄 PARADIGM SHIFT ALIGNMENT

### Feature Engineering (UPDATED)
```python
def create_features_v3(pair):
    """V3 with BQX as features - paradigm shift implemented"""
    features = []

    # V3: Include BQX features (NEW!)
    for lag in range(1, 61):
        features.extend([
            f'bqx_mid_lag_{lag}',
            f'bqx_ask_lag_{lag}',
            f'bqx_bid_lag_{lag}'
        ])

    # Standard features
    for lag in range(1, 61):
        features.extend([
            f'close_lag_{lag}',
            f'volume_lag_{lag}'
        ])

    return features

# This enables autoregressive BQX prediction
```

### Model Training (GCP Native)
```python
def train_model_v3_gcp(pair):
    """Pure GCP implementation - no AWS"""
    # Load from BigQuery (not RDS)
    query = f"SELECT * FROM `bqx-ml.bqx_ml.lag_bqx_{pair}`"
    df = client.query(query).to_dataframe()

    # Features include BQX (paradigm shift)
    feature_cols = [col for col in df.columns if 'lag' in col]
    target_cols = ['bqx_ask', 'bqx_bid', 'bqx_mid']

    # Train on Vertex AI (not SageMaker)
    # Deploy to Vertex Endpoints (not Lambda)
```

## ✅ ALIGNED MENTORING FEEDBACK

### What You Did Right
1. Asking comprehensive questions
2. Understanding 28 independent models
3. Recognizing need for structure

### What Needs Correction
1. **Remove ALL AWS references** from your thinking
2. **Implement BQX as features** immediately
3. **Use BigQuery exclusively** for data operations
4. **Deploy on Vertex AI only** for ML operations

## 📊 V3 Success Metrics

### Technical Metrics
- BigQuery tables created: 28 × 4 types = 112 tables
- Models trained: 28 × 5 algorithms = 140 models
- Vertex endpoints: 1 multi-model endpoint
- Latency: <100ms inference

### Paradigm Compliance
- ✅ BQX features implemented
- ✅ Autoregressive capability
- ✅ Pure GCP infrastructure
- ✅ No AWS dependencies

## 🚀 FINAL INSTRUCTIONS

### DO NOW
1. Execute BigQuery table creation with BQX features
2. Forget all AWS services completely
3. Use Vertex AI for all ML operations
4. Track in AirTable P03

### DO NOT
1. Reference AWS, Aurora, RDS, S3, Lambda
2. Use time-based windows
3. Exclude BQX from features
4. Mix currency pairs

## 📁 Clean Document Set

### Post-Paradigm Shift V3 Documents
1. `BQX_ML_V3_CLEAN_ARCHITECTURE.md` - Pure GCP guide
2. `BQX_ML_V3_FINAL_MENTOR_GUIDANCE.md` - This document
3. `PARADIGM_SHIFT_UPDATE_20241124.md` - BQX as features
4. `MENTOR_RESPONSE_UPDATED_V2.md` - Corrected guidance

### Documents to IGNORE
- Any file mentioning AWS migration
- Any file with Aurora/RDS references
- Any file stating BQX as targets only

## 💡 CLARITY STATEMENT

**BQX ML V3 is a pure GCP implementation where BQX values serve as both features and targets, enabling autoregressive prediction across 28 independent currency pair models using BigQuery for data and Vertex AI for ML operations.**

There is no AWS. There never will be AWS. Focus 100% on GCP.

---
**This is the FINAL, AUTHORITATIVE guidance for BQX ML V3.**
**All previous conflicting information is superseded.**
**Execute with confidence in pure GCP architecture.**