# 🔧 TECHNICAL DECISION: CUSTOM PREDICTION ROUTINE STRATEGY

**From**: Chief Engineer (Decision Authority)
**To**: Builder Agent (Deployment Team)
**Date**: 2025-11-27 06:30:00 UTC
**Priority**: HIGH
**Type**: TECHNICAL DIRECTIVE

---

## 🔍 ISSUE ANALYSIS

### Deployment Failures Observed:
- EUR_USD_90: Model server exited unexpectedly
- GBP_USD_90: Model server exited unexpectedly
- USD_JPY_90: Currently deploying (likely to fail)

### Root Cause:
Raw `.pkl` files are incompatible with Vertex AI's default containers. The models were trained with scikit-learn but not properly packaged for Vertex AI deployment.

---

## 🎯 SOLUTION OPTIONS EVALUATED

### Option 1: Custom Prediction Routine (Complex)
```python
# Create custom predictor class
# Package with setup.py
# Upload as tarball
# Higher complexity, more control
```
**Pros**: Full control, custom preprocessing
**Cons**: Complex, longer deployment, maintenance burden
**Cost**: Same ($342/month)
**Time**: 2-3 hours

### Option 2: Prebuilt SKLearn Container (Recommended) ✅
```python
serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-3:latest"
```
**Pros**: Simple, fast, Google-maintained
**Cons**: Less flexibility
**Cost**: Same ($342/month)
**Time**: 30 minutes

### Option 3: Pivot to BigQuery ML Only
**Pros**: No endpoint issues
**Cons**: No real-time predictions
**Cost**: ~$200/month
**Time**: 1 hour

---

## ✅ CHIEF ENGINEER DECISION

### APPROVED: Option 2 - Prebuilt SKLearn Container

**Rationale**:
1. **Simplicity wins** - Less code = fewer bugs
2. **Google maintains the container** - Security updates handled
3. **Same cost** - No financial penalty
4. **Faster deployment** - 30 min vs 3 hours
5. **Models already compatible** - .pkl format works directly

---

## 📋 IMPLEMENTATION DIRECTIVE

### Immediate Actions:

1. **Stop failing deployments**
   ```bash
   # Kill existing deployment processes
   pkill -f deploy_critical_endpoints.py
   ```

2. **Run fixed deployment**
   ```bash
   python3 /home/micha/bqx_ml_v3/scripts/deploy_sklearn_to_vertex.py
   ```

3. **Monitor deployment**
   ```bash
   watch -n 30 'gcloud ai endpoints list --region=us-central1'
   ```

---

## 🏗️ TECHNICAL SPECIFICATIONS

### Container Selection:
```python
# CORRECT - Use prebuilt scikit-learn container
serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-3:latest"

# INCORRECT - Don't use generic containers
# serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/tf2-cpu.2-3:latest"
```

### Resource Allocation:
```python
machine_type="n1-standard-2"  # NOT n1-standard-4
min_replica_count=1           # Start minimal
max_replica_count=2           # Allow small scaling
```

### Model Upload:
```python
model = aiplatform.Model.upload(
    display_name=f"bqx-{model_name}-sklearn",
    artifact_uri=f"gs://bqx-ml-vertex-models/{model_name}/",
    serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-3:latest",
    sync=True
)
```

---

## 💰 COST CONFIRMATION

No change from Smart Architecture plan:
- 5 endpoints × $68.40 = $342/month
- Savings: $12,978/month (97%)
- Within budget: ✅

---

## ⏰ REVISED TIMELINE

| Task | Start | Duration | Status |
|------|-------|----------|--------|
| Fix deployment script | 06:30 UTC | Done | ✅ |
| Deploy 5 endpoints | 06:35 UTC | 30 min | 🔄 |
| Update Cloud Functions | 07:05 UTC | 15 min | ⏳ |
| Integration testing | 07:20 UTC | 30 min | ⏳ |
| **COMPLETE** | **07:50 UTC** | - | - |

---

## 🚫 AVOID THESE MISTAKES

1. **DON'T use custom predictors** unless absolutely necessary
2. **DON'T use TensorFlow containers** for scikit-learn models
3. **DON'T use n1-standard-4** machines (double the cost)
4. **DON'T wait for sync deployment** (use sync=False after first model)

---

## ✅ SUCCESS CRITERIA

1. All 5 endpoints deployed successfully
2. Models respond to test predictions
3. Latency < 100ms for critical models
4. Total cost < $350/month

---

## 📞 ESCALATION

If deployment still fails with prebuilt container:
1. Check model pickle protocol (must be ≤ 4)
2. Verify scikit-learn version compatibility
3. Consider BigQuery ML fallback
4. Contact CE for architecture pivot decision

---

**Message ID**: 20251127_0630_CE_BA_CUSTOM_PREDICTION
**Thread ID**: THREAD_DEPLOYMENT_FIX
**Authorization**: PROCEED WITH OPTION 2

---

**BA, use the prebuilt scikit-learn container. It's simpler, faster, and Google-maintained. Run the fixed script immediately.**