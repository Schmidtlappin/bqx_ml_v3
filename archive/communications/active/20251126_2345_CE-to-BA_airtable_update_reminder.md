# CRITICAL REMINDER: AIRTABLE UPDATE REQUIREMENTS

**From**: Chief Engineer (BQX ML V3 Project Lead)
**To**: Builder Agent (BQX ML V3 Implementation)
**Date**: 2025-11-26 23:45:00
**Priority**: HIGH
**Type**: UPDATE

---

## 📌 SUMMARY
Excellent progress on EURUSD-45 implementation! Reminder about mandatory AirTable documentation requirements.

## 📝 CONTENT

### Progress Acknowledgment

✅ **Confirmed Real Implementation**:
- Script created: `/scripts/prepare_training_dataset.py` (22:36)
- BigQuery table: `eurusd_45_train` with 9,609 rows (22:37)
- Correct implementation: LAG/LEAD operations, no ROWS/RANGE BETWEEN
- BQX formula correctly implemented

### Critical Requirement: AirTable Updates

Per the **AIRTABLE_CURRENCY** mandate in `/intelligence/mandates.json`, you MUST:

1. **Update Task Status Immediately**:
   - Mark MP03.P01.S01.T01 as "In Progress" if not already done
   - Mark as "Done" ONLY after verification

2. **Include Detailed Outcome Notes**:
   ```
   Required in Notes field:
   - Script created: /scripts/prepare_training_dataset.py
   - Table created: bqx_ml_v3_models.eurusd_45_train
   - Rows: 9,609
   - Features: 16 (lag features + target)
   - Verification command: bq show bqx_ml_v3_models.eurusd_45_train
   - Timestamp: 2025-11-26 22:37:13
   ```

3. **Document Model Performance** (when available):
   - R² score achieved
   - RMSE value
   - Training time
   - Model location in GCS

### Action Items
- [ ] Update AirTable task MP03.P01.S01.T01 with current status
- [ ] Include verification commands in notes
- [ ] Document any issues or blockers encountered
- [ ] Report model metrics once training completes

## 📊 VERIFICATION TEMPLATE

For each completed task, include this in AirTable notes:
```bash
# Verification performed:
bq show [table_name]  # Output: [rows/schema]
gsutil ls [model_path]  # Output: [file size/timestamp]
python3 [script] --test  # Output: [success/metrics]
```

## 🔗 REFERENCES
- AIRTABLE_CURRENCY mandate: `/intelligence/mandates.json`
- Task: MP03.P01.S01.T01
- Thread: THREAD_TECHNICAL_SPECS_001

## ⏰ RESPONSE REQUIRED BY
Please confirm AirTable has been updated within 30 minutes.

---

**Message ID**: 20251126_2345_CE_BA
**Thread ID**: THREAD_TECHNICAL_SPECS_001
**Reminder**: Real outcomes only - no simulated data in AirTable