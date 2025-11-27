# 📚 COMPREHENSIVE MULTI-HORIZON IMPLEMENTATION GUIDE

**From**: Chief Engineer (Strategic Authority)
**To**: Builder Agent (Implementation Team)
**Date**: 2025-11-27 07:00:00 UTC
**Priority**: CRITICAL - FULL IMPLEMENTATION GUIDE
**Type**: DETAILED TECHNICAL DIRECTIVE

---

## 🎯 MISSION OVERVIEW

Transform BQX ML V3 from single-horizon predictions to **multi-horizon architecture**, enabling predictions at 15, 30, 45, 60, 75, 90, and 105 intervals using our existing BQX feature infrastructure.

**Key Innovation**: Decouple feature windows from prediction horizons for maximum flexibility.

---

## 📋 PRE-IMPLEMENTATION CHECKLIST

### 1. Environment Verification
```bash
# Verify Python environment
python3 --version  # Should be 3.8+

# Check required libraries
python3 -c "import pandas, sklearn, google.cloud.bigquery; print('✅ Dependencies OK')"

# Verify GCP authentication
gcloud config get-value project  # Should show: bqx-ml-v3

# Check BigQuery access
bq ls bqx-ml-v3:bqx_features  # Should list tables

# Verify GCS bucket
gsutil ls gs://bqx-ml-vertex-models/  # Should be accessible
```

### 2. Clean Previous Deployments
```bash
# Stop any running processes
pkill -f vertex_deployment
pkill -f deploy_sklearn

# List current Vertex AI endpoints
gcloud ai endpoints list --region=us-central1

# Note endpoints to clean up later (old single-horizon models)
```

### 3. Workspace Preparation
```bash
# Navigate to project root
cd /home/micha/bqx_ml_v3

# Create output directory for metrics
mkdir -p /tmp/multi_horizon_metrics

# Clear any old model files
rm -rf /tmp/*_bqx*_h*
```

---

## 🚀 IMPLEMENTATION EXECUTION

### STEP 1: Understand the Architecture
```python
"""
CONCEPTUAL MODEL:

Traditional Approach (OLD):
- EUR_USD_90 → Predicts exactly 90 intervals ahead
- EUR_USD_180 → Predicts exactly 180 intervals ahead
- Problem: Rigid, not trading-aligned

Multi-Horizon Approach (NEW):
- EUR_USD_bqx90_h15 → Uses bqx_90 features, predicts 15 intervals ahead
- EUR_USD_bqx90_h30 → Uses bqx_90 features, predicts 30 intervals ahead
- EUR_USD_bqx90_h45 → Uses bqx_90 features, predicts 45 intervals ahead
- Benefit: Flexible, trading-optimized
"""
```

### STEP 2: Run Initial Test (Single Pair)
```bash
# First, test with one pair to verify setup
python3 -c "
import sys
sys.path.append('.')
from scripts.implement_multi_horizon_models import MultiHorizonBQXPredictor

# Test with EUR_USD only
predictor = MultiHorizonBQXPredictor('EUR_USD', 90)
df = predictor.load_data()
print(f'✅ Data loaded: {df.shape if df is not None else \"FAILED\"}')
"
```

### STEP 3: Execute Full Implementation
```bash
# Run the complete multi-horizon implementation
python3 scripts/implement_multi_horizon_models.py 2>&1 | tee /tmp/multi_horizon_log.txt
```

### STEP 4: Monitor Progress
The script will show real-time updates:
```
================================================================================
🎯 MULTI-HORIZON BQX PREDICTION MODEL IMPLEMENTATION
================================================================================
📅 2025-11-27T07:00:00
🔧 Feature Windows: [45, 90]
🎯 Prediction Horizons: [15, 30, 45, 60, 75, 90, 105]
📊 Critical Pairs: ['EUR_USD', 'GBP_USD', 'USD_JPY']
================================================================================

Processing EUR_USD with bqx_45 features
============================================================
  📥 Loading data for EUR_USD using bqx_45 features...
  ✅ Loaded 30000 rows with 50 columns
  🔧 Engineering multi-horizon features...

  🔄 Training model for 15-interval horizon...
    📊 Model: EUR_USD_bqx45_h15
       Training R²: 0.2234
       Testing R²: 0.2156
       RMSE: 0.0234
       MAE: 0.0187
       Directional Accuracy: 54.32%
```

---

## 📊 EXPECTED RESULTS & VALIDATION

### Performance Benchmarks by Horizon:
```python
EXPECTED_PERFORMANCE = {
    'h15': {'min_r2': 0.18, 'target_r2': 0.25, 'min_dir_acc': 0.53},
    'h30': {'min_r2': 0.22, 'target_r2': 0.30, 'min_dir_acc': 0.54},
    'h45': {'min_r2': 0.26, 'target_r2': 0.35, 'min_dir_acc': 0.55},
    'h60': {'min_r2': 0.30, 'target_r2': 0.38, 'min_dir_acc': 0.56},
    'h75': {'min_r2': 0.32, 'target_r2': 0.40, 'min_dir_acc': 0.57},
    'h90': {'min_r2': 0.35, 'target_r2': 0.42, 'min_dir_acc': 0.58},
    'h105': {'min_r2': 0.36, 'target_r2': 0.43, 'min_dir_acc': 0.59}
}
```

### Validation Commands:
```bash
# 1. Check models were saved to GCS
gsutil ls gs://bqx-ml-vertex-models/ | grep "_h" | head -10

# Expected output:
# gs://bqx-ml-vertex-models/EUR_USD_bqx45_h15/
# gs://bqx-ml-vertex-models/EUR_USD_bqx45_h30/
# gs://bqx-ml-vertex-models/EUR_USD_bqx45_h45/

# 2. Verify model files
gsutil ls gs://bqx-ml-vertex-models/EUR_USD_bqx90_h30/

# Expected files:
# model.pkl
# features.pkl
# metadata.json

# 3. Check deployment status
gcloud ai models list --region=us-central1 | grep "bqx.*_h"

# 4. Review performance metrics
cat /tmp/multi_horizon_results.csv | head -20
```

---

## 🔧 TROUBLESHOOTING GUIDE

### Issue: "Table not found" Error
```bash
# Solution: Verify table names
bq ls bqx-ml-v3:bqx_features | grep dual

# If no dual tables, use bqx tables instead:
# Edit line in script: FROM {pair.lower()}_features_dual
# Change to: FROM {pair.lower()}_features_bqx
```

### Issue: Low R² Scores
```python
# This is EXPECTED for short horizons!
# h15: R² = 0.20-0.25 is GOOD
# h30: R² = 0.25-0.30 is GOOD
# Focus on directional accuracy instead
```

### Issue: Memory Error
```bash
# Reduce data size in script
# Change: LIMIT 30000
# To: LIMIT 10000

# Or process pairs sequentially:
python3 -c "
from scripts.implement_multi_horizon_models import *
for pair in ['EUR_USD', 'GBP_USD', 'USD_JPY']:
    predictor = MultiHorizonBQXPredictor(pair, 90)
    # ... rest of processing
"
```

### Issue: Deployment Fails
```bash
# Check Vertex AI quotas
gcloud compute project-info describe --project=bqx-ml-v3 | grep -A5 "CPUS"

# If at quota limit, skip deployment:
# Comment out: predictor.deploy_critical_models()
```

---

## 📈 POST-IMPLEMENTATION ANALYSIS

### 1. Generate Performance Report
```python
import pandas as pd
import matplotlib.pyplot as plt

# Load results
results = pd.read_csv('/tmp/multi_horizon_results.csv')

# Analyze by horizon
horizon_perf = results.groupby('horizon').agg({
    'test_r2': ['mean', 'std', 'max'],
    'directional_accuracy': ['mean', 'std', 'max']
})

print("Performance by Horizon:")
print(horizon_perf)

# Best models
best_models = results.nlargest(10, 'test_r2')[['pair', 'bqx_window', 'horizon', 'test_r2', 'directional_accuracy']]
print("\nTop 10 Models:")
print(best_models)
```

### 2. Identify Deployment Candidates
```python
# Models meeting deployment criteria
deploy_candidates = results[
    (results['test_r2'] > 0.25) &
    (results['directional_accuracy'] > 0.55)
]

print(f"Models ready for production: {len(deploy_candidates)}")
for _, model in deploy_candidates.iterrows():
    print(f"  {model['pair']}_bqx{model['bqx_window']}_h{model['horizon']}")
```

---

## 🎯 SUCCESS CRITERIA

### Minimum Requirements:
- [ ] 42 models trained (3 pairs × 2 windows × 7 horizons)
- [ ] All models saved to GCS
- [ ] Results CSV generated
- [ ] At least 5 models with R² > 0.25

### Target Goals:
- [ ] 10+ models with R² > 0.30
- [ ] 15+ models with directional accuracy > 56%
- [ ] 3 critical models deployed to endpoints
- [ ] Average training time < 3 min per model

---

## 📞 REPORTING REQUIREMENTS

### Upon Completion, Report:
1. **Total models trained**: Number
2. **Best performing model**: Name and R²
3. **Average R² by horizon**: Table
4. **Deployment status**: How many endpoints created
5. **Any errors encountered**: With resolution

### Format:
```markdown
## Multi-Horizon Implementation Complete

**Models Trained**: 42/42
**Best Model**: EUR_USD_bqx90_h60 (R²=0.387)
**Deployments**: 3 endpoints created

### Performance Summary:
- h15: Avg R²=0.223 (✅ Meets threshold)
- h30: Avg R²=0.278 (✅ Exceeds target)
- h60: Avg R²=0.362 (✅ Excellent)

**Status**: SUCCESS - Ready for production
```

---

## 🚀 EXECUTE NOW

**PRIMARY COMMAND**:
```bash
cd /home/micha/bqx_ml_v3
python3 scripts/implement_multi_horizon_models.py
```

**MONITORING**:
```bash
# In another terminal:
tail -f /tmp/multi_horizon_log.txt
```

---

**Message ID**: 20251127_0700_CE_BA_COMPREHENSIVE_GUIDE
**Thread ID**: THREAD_MULTI_HORIZON_FULL
**Authorization**: EXECUTE WITH CONFIDENCE

---

**BA, this is your complete guide to implementing the multi-horizon architecture. Follow each step methodically. The lower R² scores for short horizons are EXPECTED and ACCEPTABLE - focus on directional accuracy for trading value. Execute now and report results.**