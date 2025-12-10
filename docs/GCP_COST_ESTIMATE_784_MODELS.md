# BQX ML V3 - GCP Cost Estimate for 784 Models

**Date**: 2025-12-08
**Architecture**: 28 pairs × 7 horizons × 4 ensemble members = 784 models
**Target**: 95%+ directional accuracy

---

## Current BigQuery Storage (as of 2025-12-08)

| Dataset | Tables | Size (GB) | Status |
|---------|--------|-----------|--------|
| bqx_ml_v3_features (v1) | 5,146 | 1,279 GB | **DELETE** |
| bqx_bq_uscen1 (v1) | 2,463 | 1,220 GB | **DELETE** |
| bqx_ml_v3_features_v2 | 3,000 | 917 GB | Active |
| bqx_bq_uscen1_v2 | 2,210 | 131 GB | Active |
| bqx_ml_v3_analytics_v2 | 29 | 5 GB | Active |
| bqx_ml_v3_analytics | ~~70~~ | ~~68 GB~~ | **DELETED** (wrong values) |
| bqx_ml_v3_models | 16 | 0.01 GB | Active |
| bqx_ml_v3_predictions | 1 | 0.0 GB | Active |
| **TOTAL** | **12,960** | **3,683 GB** | |

### After V1 Deletion
| Dataset | Size (GB) |
|---------|-----------|
| bqx_ml_v3_features_v2 | 917 GB |
| bqx_bq_uscen1_v2 | 131 GB |
| bqx_ml_v3_analytics_v2 | 68 GB |
| **V2 TOTAL** | **1,116 GB** |

---

## Monthly Recurring Costs

### 1. BigQuery Storage

| Scenario | Size | Rate | Monthly Cost |
|----------|------|------|--------------|
| Current (v1 + v2) | 3,683 GB | $0.02/GB | **$73.66** |
| After v1 deletion | 1,116 GB | $0.02/GB | **$22.32** |
| Long-term (90+ days) | 1,116 GB | $0.01/GB | **$11.16** |

**Savings from v1 deletion**: $51.34/month (70%)

### 2. BigQuery ML Training

| Component | Calculation | Cost |
|-----------|-------------|------|
| Feature data processing | 1 TB × $5/TB | $5.00 |
| Model training (BQML) | 784 models × ~0.5 TB each | ~$25-50/cycle |
| Hyperparameter tuning | 5 configs × 784 models × 0.1 TB | ~$50/cycle |

**Training cost per full cycle**: ~$75-100 (one-time per training run)
**Monthly (weekly retraining)**: ~$300-400

### 3. GCS Backup (Coldline)

| Type | Size | Rate | Monthly Cost |
|------|------|------|--------------|
| V2 backup | 1,116 GB | $0.004/GB | **$4.46** |

### 4. Vertex AI (Optional for LSTM Meta-learners)

| Component | Units | Rate | Cost |
|-----------|-------|------|------|
| LSTM training | 196 models × 2 hrs | $2-5/hr (Spot) | $784-1,960 (one-time) |
| Monthly retrain (10%) | 20 models × 2 hrs | $2-5/hr | $80-200/month |

---

## Training Phase Costs (One-Time)

### Scenario A: BigQuery ML Only (Recommended)

| Step | Description | Estimated Cost |
|------|-------------|----------------|
| 1. Feature Selection | SHAP analysis on 28 pairs × sample data | $20-50 |
| 2. Base Model Training | 588 models (LightGBM, XGBoost, CatBoost via BQML) | $100-200 |
| 3. Meta-learner Training | 196 stacking models | $50-100 |
| 4. Walk-Forward Validation | 7 folds × 784 models | $200-400 |
| **TOTAL** | | **$370-750** |

### Scenario B: Hybrid (BQML + Vertex AI)

| Step | Description | Estimated Cost |
|------|-------------|----------------|
| 1-3. Same as Scenario A | | $170-350 |
| 4. LSTM Meta-learners | 196 models on Spot VMs | $800-1,200 |
| 5. Walk-Forward Validation | | $200-400 |
| **TOTAL** | | **$1,170-1,950** |

---

## Monthly Operational Costs Summary

### Optimized Plan (Recommended)

| Component | Monthly Cost |
|-----------|--------------|
| BigQuery Storage (v2 only) | $22.32 |
| BigQuery ML Training (weekly retrain) | $100-150 |
| GCS Backup (Coldline) | $4.46 |
| Inference/Serving | $50-100 |
| **TOTAL** | **$177-277/month** |

### With Vertex AI LSTM

| Component | Monthly Cost |
|-----------|--------------|
| BigQuery Storage (v2 only) | $22.32 |
| BigQuery ML Base Models | $75-100 |
| Vertex AI LSTM Meta-learners | $80-200 |
| GCS Backup | $4.46 |
| Inference/Serving | $100-150 |
| **TOTAL** | **$282-477/month** |

---

## Cost Optimization Strategies

### 1. Storage Optimization (-70%)
- [x] Delete v1 datasets after v2 validation
- [ ] Enable long-term storage pricing (90+ days)
- [ ] Use Coldline for backups instead of Nearline

### 2. Training Optimization (-60%)
- [ ] Use BigQuery ML instead of Vertex AI where possible
- [ ] Feature selection first (8,214 → 500-1,000 features)
- [ ] Use Spot/Preemptible VMs for any custom training
- [ ] Incremental retraining (only retrain underperforming models)

### 3. Inference Optimization (-50%)
- [ ] Reserved capacity for production endpoints
- [ ] Batch predictions instead of real-time where possible
- [ ] Model compression/quantization for serving

---

## Cost Comparison: 784 vs 672 Models

| Metric | 672 Models (6 horizons) | 784 Models (7 horizons) | Difference |
|--------|------------------------|------------------------|------------|
| Training (one-time) | $320-650 | $370-750 | +$50-100 |
| Monthly storage | Same | Same | $0 |
| Monthly training | $85-130 | $100-150 | +$15-20 |
| **Monthly Total** | $150-240 | $177-277 | +$27-37 |

The 7th horizon (h105) adds ~15% to training costs but enables:
- Longer prediction windows for swing traders
- Additional accuracy data points for horizon selection
- Potential for longer-term signals on major pairs

---

## Break-Even Analysis

| Investment | One-Time Cost | Monthly Savings | Break-Even |
|------------|---------------|-----------------|------------|
| V1 deletion | $0 | $51.34 | Immediate |
| Coldline backup | $0 | $0.54 | Immediate |
| Feature selection | $50 | ~$100 (faster training) | 0.5 months |
| Long-term storage | $0 | $11.16 (after 90 days) | Immediate |

---

## Recommended Budget Allocation

### Phase 1: Infrastructure (Month 1)
- V1 deletion: $0
- V2 validation: $10-20
- GCS backup setup: $5
- **Total**: $15-25

### Phase 2: Training (Month 1-2)
- Feature selection: $50
- 784 model training: $300-600
- Validation: $100-200
- **Total**: $450-850

### Phase 3: Operations (Monthly)
- Storage: $22
- Retraining: $100-150
- Inference: $50-100
- Backup: $5
- **Total**: $177-277/month

---

## Summary

| Category | Cost |
|----------|------|
| **One-time training** | $450-850 |
| **Monthly operations** | $177-277 |
| **Annual operations** | $2,124-3,324 |

**Total Year 1 Cost**: $2,574-4,174

**Compared to original estimate** ($755/month = $9,060/year):
- **Savings**: 64-72%
- **Annual savings**: $4,886-6,486

---

*Generated: 2025-12-08*
*Models: 784 (28 pairs × 7 horizons × 4 ensemble)*
*Target: 95%+ directional accuracy*
