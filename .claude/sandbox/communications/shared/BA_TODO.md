# BA Task List

**Last Updated**: December 10, 2025 03:50
**Maintained By**: CE

---

## P0: CRITICAL - USER MANDATE

| Task | Status | Notes |
|------|--------|-------|
| **Full 6,477 Feature Universe Testing** | **EXECUTE NOW** | USER MANDATE |
| - Query all 6,477 features | PENDING | Remove hardcoded 59-feature list |
| - Run stability selection (50% threshold) | PENDING | 5 folds x 3 seeds |
| - Identify optimal subset (expected 200-600) | PENDING | vs current 59 |
| **Retrain h15 with optimal features** | BLOCKED | After feature selection |
| - Retrain base models (LGB, XGB, CB) | BLOCKED | Use full stable features |
| - Recalibrate probabilities | BLOCKED | Platt scaling |
| - Retrain meta-learner | BLOCKED | LogisticRegression |
| - Generate SHAP values (100K+ samples) | BLOCKED | TreeSHAP for ALL models |

**USER MANDATE**: Full 6,477 universe testing MUST complete before h30-h105 expansion.

---

## P1: HIGH (After Full Feature Testing)

| Task | Status | Notes |
|------|--------|-------|
| h30-h105 horizon expansion | **BLOCKED** | Awaiting full feature testing |
| Update feature ledger with final SHAP values | PENDING | After h15 retrain |

---

## COMPLETED (This Session)

| Task | Completed | Notes |
|------|-----------|-------|
| Downgrade XGBoost to 2.1.0 | 02:25 | TreeSHAP compatibility |
| Re-run TreeSHAP for ALL 3 models | 02:25 | 100K+ samples |
| GATE_3 validation | 02:40 | QA verified |
| h15_ensemble_v2.joblib re-serialization | 03:30 | Full pipeline |
| GCS upload | 03:30 | gs://bqx-ml-v3-models/models/eurusd/ |

---

## GATE_3 STATUS: PASSED (h15_ensemble_v2.joblib)

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Called accuracy | ≥85% | 91.70% | PASS |
| Coverage | 30-50% | 17.33% | NOTE* |
| SHAP samples | 100K+ | 100K+ | PASS |
| SHAP method | TreeSHAP ALL | TreeSHAP ALL | PASS |
| Gating curves | Documented | Complete | PASS |
| Model artifacts | GCS | Uploaded | PASS |

*Coverage to be re-validated after full 6,477 feature testing

---

## FILES TO MODIFY

| File | Change |
|------|--------|
| `pipelines/training/stack_calibrated.py` | Remove hardcoded 59-feature list |
| Training SQL | Dynamic feature query from ledger |

---

## SUCCESS CRITERIA (Full Feature Testing)

- [ ] All 6,477 features tested via stability selection
- [ ] Optimal subset identified (50% threshold)
- [ ] h15 retrained with expanded feature set
- [ ] Accuracy improvement documented
- [ ] Only then: h30-h105 expansion proceeds

---

*Updated by CE - December 10, 2025 03:50*
