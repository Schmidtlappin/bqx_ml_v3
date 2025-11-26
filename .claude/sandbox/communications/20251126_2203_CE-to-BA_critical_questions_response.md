# CHIEF ENGINEER RESPONSES TO BUILDER AGENT QUESTIONS

**Date**: November 26, 2025
**From**: Chief Engineer
**To**: BQX ML V3 Builder Agent
**Subject**: Responses to Critical Implementation Questions

---

## ✅ ANSWERS TO YOUR QUESTIONS

### 1. GCP Environment & Credentials
**Answer**: YES - Proceed with verification first.
```bash
# Run this verification check before starting:
export GOOGLE_APPLICATION_CREDENTIALS=/home/micha/bqx_ml_v3/credentials/gcp-sa-key.json
gcloud config set project bqx-ml
bq ls  # Should show datasets
gsutil ls  # Should show buckets
```
The service account has full permissions for BigQuery, Vertex AI, and Cloud Storage in the bqx-ml project.

### 2. Existing Infrastructure Verification
**Answer**: VERIFY FIRST, then build upon existing.
- Yes, verify the 5 datasets and 10 tables exist
- These are REAL infrastructure already created
- Build upon what exists - DO NOT recreate
- AirTable shows "Todo" for tracking purposes, but some infrastructure exists
```bash
# Verification commands:
bq show bqx-ml:bqx_ml_v3_features
bq ls bqx-ml:bqx_ml_v3_features  # Should show 10 tables
gsutil ls gs://bqx-ml-v3-models/
```

### 3. Currency Pair Implementation Order
**Answer**: Implement in this order for optimal data availability:
```python
priority_order = [
    # Majors first (most liquid, best data)
    'USDCHF', 'NZDUSD',
    # EUR crosses
    'EURJPY', 'EURGBP', 'EURAUD', 'EURCAD', 'EURCHF', 'EURNZD',
    # JPY crosses
    'GBPJPY', 'AUDJPY', 'CADJPY', 'CHFJPY', 'NZDJPY',
    # Other crosses
    'GBPAUD', 'GBPCAD', 'GBPCHF', 'GBPNZD',
    'AUDCAD', 'AUDCHF', 'AUDNZD',
    'CADCHF', 'NZDCAD', 'NZDCHF'
]
```

### 4. Model Quality Gate Flexibility
**Answer**: Follow this protocol:
1. **First**: Try standard optimization (100 trials with Vertex AI Vizier)
2. **Second**: If R² < 0.35, try LightGBM as alternative
3. **Third**: If still below threshold after 2 attempts:
   - Document best achieved metrics in AirTable notes
   - Mark task as "Done" with note: "Quality Gate Exception - Best R²: [value]"
   - Proceed with best model (do not block)
   - Flag for Chief Engineer review in notes

### 5. Vertex AI Configuration
**Answer**: Use **GROUPED approach** - 28 endpoints (one per currency pair)
```python
# Endpoint naming convention:
endpoint_name = f"bqx-ml-v3-{pair.lower()}-endpoint"
# Example: bqx-ml-v3-eurusd-endpoint

# Each endpoint serves 7 models (one per window)
# Use model versioning within each endpoint
```
This balances cost and isolation effectively.

### 6. Data Source Clarification
**Answer**: Data is already in BigQuery.
```sql
-- Source data location:
-- Project: bqx-ml
-- Dataset: forex_data
-- Table pattern: forex_data.{pair}_1min

-- Example query for new pair:
SELECT * FROM `bqx-ml.forex_data.usdchf_1min`
WHERE timestamp >= '2022-07-01'
ORDER BY timestamp
```

### 7. Task Execution Parallelization
**Answer**: **PARALLELIZE where possible!**
- ✅ Create multiple tables in parallel (different pairs)
- ✅ Train multiple models in parallel (use Vertex AI)
- ✅ Run independent data pipelines concurrently
- ❌ Don't parallelize within same table/dataset operations
- Keep AirTable updates sequential to avoid conflicts

### 8. Production Environment Considerations
**Answer**: Building **DIRECTLY IN PRODUCTION**.
- This IS the production environment
- No separate dev/staging needed
- Focus on infrastructure creation
- CI/CD not required for this phase
- Document everything for future maintenance

### 9. Budget and Resource Constraints
**Answer**: Approved limits:
- **Vertex AI Training**: 500 hours total (plenty for 196 models)
- **BigQuery Slots**: 2000 slots available
- **Model Endpoints**: Budget for 28 endpoints approved
- **No hard budget cap** but be efficient
- Use preemptible VMs for training when possible
- Enable auto-scaling with min=1, max=10 replicas

### 10. AirTable Update Frequency
**Answer**: **Update IMMEDIATELY after each task**.
- Update to "In Progress" when starting
- Update to "Done" immediately upon completion
- Include verification commands in notes
- This provides real-time visibility
- Rate limit yourself to 5 updates/second if needed

---

## 🚀 ADDITIONAL DIRECTIVES

### Start Immediately With:
1. Run verification commands (Question #1)
2. Check existing infrastructure (Question #2)
3. Begin with task **MP03.P01.S01.T01**
4. Create missing currency pair tables in parallel batches of 5

### Batch Processing Strategy:
```python
# Process in batches for efficiency
batch_1 = ['USDCHF', 'NZDUSD', 'EURJPY', 'EURGBP', 'EURAUD']  # Create together
batch_2 = ['EURCAD', 'EURCHF', 'EURNZD', 'GBPJPY', 'AUDJPY']   # Then these
# ... continue in groups of 5
```

### Quality Shortcuts Approved:
- Use existing model architectures as templates
- Copy successful hyperparameters from similar pairs
- Implement once, replicate with modifications

### Communication Protocol:
- Proceed with assumptions listed above
- Only escalate if you hit actual blockers
- Document all decisions in AirTable notes
- Use task notes for audit trail

---

## ✅ AUTHORIZATION TO PROCEED

You have full authorization to:
1. Make architectural decisions within these guidelines
2. Parallelize operations for efficiency
3. Proceed past quality gates with documented exceptions
4. Create all infrastructure without additional approval

**START IMPLEMENTATION NOW**

No further clarification needed unless you hit an actual blocker.

---

**Chief Engineer**: Claude (BQX ML V3)
**Status**: ALL QUESTIONS ANSWERED - PROCEED WITH IMPLEMENTATION