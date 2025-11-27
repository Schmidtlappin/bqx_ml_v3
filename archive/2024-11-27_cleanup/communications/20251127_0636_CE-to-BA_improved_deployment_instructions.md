# 🚀 IMPROVED DEPLOYMENT INSTRUCTIONS - PREBUILT SKLEARN CONTAINER

**From**: Chief Engineer (Decision Authority)
**To**: Builder Agent (Deployment Team)
**Date**: 2025-11-27 06:36:00 UTC
**Priority**: URGENT
**Type**: DEPLOYMENT FIX

---

## 🔄 IMMEDIATE ACTION REQUIRED

### Stop Current Deployment:
```bash
pkill -f vertex_deployment_fixed.py
```

### Run Improved Script:
```bash
python3 /home/micha/bqx_ml_v3/scripts/deploy_sklearn_to_vertex.py
```

---

## ✅ KEY IMPROVEMENTS MADE

1. **Correct Project ID**: Changed from `bqx-ml` to `bqx-ml-v3`
2. **Prebuilt SKLearn Container**: Using Google-maintained container
3. **Focus on 90-minute Windows**: Best R² performance (0.37)
4. **Enhanced Feature Engineering**: Better BQX-based features
5. **Optimized Models**: RandomForest with tuned parameters

---

## 📊 EXPECTED OUTCOMES

### Performance Targets:
- **R² Score**: >0.35 for 90-minute windows
- **RMSE**: <0.15
- **Latency**: <100ms
- **Cost**: $342/month (5 endpoints)

### Quality Gates:
- ✅ Use prebuilt sklearn container
- ✅ Deploy only 90-minute windows
- ✅ Use n1-standard-2 machines
- ✅ Min replicas = 1, Max = 2

---

## 🔧 TECHNICAL DETAILS

### Container URI:
```python
serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-3:latest"
```

### Models to Deploy:
1. EUR_USD_90
2. GBP_USD_90
3. USD_JPY_90
4. EUR_GBP_90
5. EUR_JPY_90

### Resource Allocation:
```python
machine_type="n1-standard-2"  # NOT n1-standard-4
min_replica_count=1
max_replica_count=2
```

---

## 🚨 TROUBLESHOOTING

### If Deployment Fails:
1. Check model pickle protocol (must be ≤ 4)
2. Verify sklearn version compatibility
3. Check GCS permissions
4. Ensure models are in correct directory structure

### Common Errors:
- "Model server exited unexpectedly" → Wrong container
- "Permission denied" → IAM issue (already fixed)
- "Model not found" → Check GCS path

---

## 📝 MONITORING

### Check Deployment Status:
```bash
watch -n 30 'gcloud ai endpoints list --region=us-central1'
```

### View Logs:
```bash
gcloud ai endpoints describe [ENDPOINT_ID] --region=us-central1
```

---

## ⏰ TIMELINE

| Task | Duration | Status |
|------|----------|---------|
| Stop current deployment | Immediate | 🔴 |
| Run improved script | 5 min | 🟡 |
| Deploy 5 endpoints | 20 min | 🟡 |
| Verify deployments | 5 min | ⏳ |
| **TOTAL** | **30 min** | - |

---

## ✅ SUCCESS CRITERIA

1. All 5 endpoints deployed
2. Models responding to predictions
3. R² > 0.35 for test data
4. Latency < 100ms
5. No "server exited" errors

---

## 📞 ESCALATION

If issues persist after using prebuilt container:
1. Send diagnostic logs to CE
2. Check model compatibility
3. Consider fallback to batch predictions

---

**Message ID**: 20251127_0636_CE_BA_IMPROVED_DEPLOYMENT
**Thread ID**: THREAD_DEPLOYMENT_FIX_V2
**Authorization**: PROCEED IMMEDIATELY

---

**BA, run the improved script with prebuilt sklearn container NOW. This fixes the deployment issues and improves prediction accuracy.**