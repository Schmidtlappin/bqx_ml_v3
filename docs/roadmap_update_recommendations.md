# Roadmap Enhancement Recommendations (v2 → v2.1)
**Goal:** Ensure the roadmap *defensibly* evaluates **3,813 features** (per pair, verified 2025-12-09), selects robust feature sets, and improves *persistent* out-of-sample directional performance for the BQX oscillator forecasting system.

> **Audit Note (2025-12-09):** Original "8,416+" was an estimate. Actual BQ count is 3,813 features per pair. See `/intelligence/feature_catalogue.json`.

---

## 1) Clarify Definitions (so results are not gameable)
### 1.1 Metric Contract (required)
Lock a **Metric Contract** used everywhere (feature selection, ablations, stacking, monitoring):

- **Primary:** **Balanced Sign Accuracy** (positive vs negative)  
- **Secondary:**  
  - Called-signal sign accuracy + coverage  
  - Calibration (logloss/Brier + reliability/ECE)  
  - Magnitude (conditional on correct sign): exact band + within ±1 band

**Deliverable:** `metrics_contract.md` defining:
- exact label mapping (+/−, 1o/2o/3o)
- “accuracy” computation rules (macro/balanced vs micro)
- acceptance thresholds per horizon (and per pair once scaled)

### 1.2 Persistence Contract (required)
Define “persists” as *stability across time*:
- Must meet targets in **≥ X of Y walk-forward windows** spanning **≥ Z months**.
- Worst-window performance must not fall below an agreed tolerance (e.g., no >D point collapse).

**Deliverable:** `persistence_contract.md`

---

## 2) Make "Testing 3,813 Features" Auditable (feature-level lineage)
### 2.1 Feature Lineage Ledger (required)
Create an artifact that accounts for **every** feature and records what happened to it.

**Add to roadmap:** Generate a table for all features with columns:
- `feature_name`
- `source_table` / `feature_family`
- `cluster_id`
- `group_id`
- `pruned_stage` (if removed)
- `prune_reason` (constant, duplicate, missingness, invalid, leakage, etc.)
- `screen_score` (group screening)
- `stability_freq` (selection frequency)
- `importance_mean`, `importance_std` (across folds/seeds)
- `ablation_delta` (group-level)
- `final_status` (kept / merged into cluster rep / dropped)

**Deliverable:** `feature_ledger.parquet` (and `feature_ledger.md` summary)

### 2.2 “Definition of Tested”
A feature is considered “tested” if it reaches any of:
- screened via group/clustering pipeline with recorded scores, **or**
- removed with an explicit, logged reason in Stage 1/2.

---

## 3) Tighten Leakage Controls (highest-risk gap)
### 3.1 Dynamic embargo (replace fixed embargo)
Replace any fixed `embargo_intervals: 30` with:
- `embargo = max_feature_lookback_intervals + horizon_buffer`

**Why:** rolling features can leak information across the split boundary if embargo is too small.

**Deliverable:** `leakage_guardrails.md` and automated checks.

### 3.2 Add a Leakage Audit Checklist milestone (required)
Include automated tests for:
- no `t+1` data used in `t` row (alignment test)
- no centered windows / future-inclusive rolls
- scalers/normalizers fit on train only
- join-time aggregation uses only past data
- label generation uses only information available at prediction time

**Deliverable:** CI tests in `/tests/leakage/`

---

## 4) Upgrade Feature Selection for Wide, Correlated, Time-Series Data
### 4.1 Correlation clustering: go beyond Pearson r (recommended)
Keep Pearson |r|>0.95 for near-duplicates **but add**:
- Spearman correlation for monotonic links
- MI/association-based checks for non-linear ties
- categorical association metrics (if applicable)

**Deliverable:** `clustering_report.md` + `clusters.json`

### 4.2 Add cross-group interaction coverage (key gap)
Group-first screening can miss “weak alone, strong together” interactions.

**Add one of:**
- **Pairwise group test** for top N groups (e.g., N=20 → 190 pairs)  
- or a **global model** early + group permutation importance on that model  
- or “regime group always-on” + conditional screening of others

**Deliverable:** `group_interaction_screen.md`

### 4.3 Strengthen stability selection (for “don’t miss critical”)
Current “5 folds × 3 seeds” is a good start, but add:
- more seeds for the final candidate stage (e.g., 5 folds × 5–10 seeds)
- track *variance* of importance, not just mean rank

**Deliverable:** `stability_selection_report.md`

### 4.4 Ablation must use your true objective + slicing
Replace generic ΔAUC with:
- ΔBalanced Sign Accuracy (primary)
- evaluate ablations by:
  - volatility regime
  - trend/range regime
  - session (Asia/London/NY) if relevant

**Deliverable:** `ablation_by_regime.md`

---

## 5) Improve Stacking to Increase Performance *and* Persistence
### 5.1 Stack probabilities (not hard classes) for sign
Base learners should output `P(positive)`. Meta learner consumes those + regime features.

**Best default meta learner:** logistic regression / ridge (stable, low overfit).

**Deliverable:** `stack_spec.md`

### 5.2 Calibration bake-off (required)
Before gating/stacking, evaluate:
- Platt vs isotonic (and optionally beta calibration)
- using OOF-only calibration data

Track reliability plots + ECE. Adopt per-horizon calibration if needed.

**Deliverable:** `calibration_report.md`

### 5.3 Add seed-bagging inside base models (high ROI)
Train each base model with multiple seeds and average probabilities **before stacking**.

**Deliverable:** `bagging_config.yaml` + `bagging_results.md`

### 5.4 Compare against simple averaging baseline (guardrail)
Always benchmark:
- mean(probabilities)
- weighted mean (OOF weights)

If stacking doesn’t beat averaging *under walk-forward*, keep averaging.

**Deliverable:** `ensemble_baselines.md`

---

## 6) Direction-First Architecture (aligned to stakeholder priority)
### 6.1 Two-stage modeling (recommended)
- **Stage A:** Sign model (binary) → calibrated `P(+)`
- **Stage B:** Magnitude model conditional on sign

This reduces magnitude noise degrading direction performance.

**Deliverable:** `two_stage_architecture.md`

### 6.2 Confidence gating as a first-class deliverable
Define and persist:
- thresholds `τ+` and `τ−`
- accuracy–coverage curves
- threshold selection method (nested walk-forward, not tuned on the final test)

**Deliverable:** `gating_policy.md` + `coverage_curves.md`

---

## 7) Add a “Phase 4.5” Gate Before Scaling to 784 Models (required)
Your scale plan (28 pairs × 7 horizons × variants) needs a governance checkpoint.

**Insert Phase 4.5: Validation & Governance Gate**
Must pass:
- leakage audit tests
- metric + persistence contracts locked
- thresholds selected via nested evaluation
- model registry + artifact storage working
- monitoring spec implemented in staging
- pilot results stable across multiple regimes

Only then scale to full pair/horizon grid.

**Deliverable:** `phase_4_5_gate_checklist.md`

---

## 8) Operationalize Reproducibility: Model Registry + Artifacts (required)
### 8.1 Model identity schema
Standardize model IDs:
`{pair}_{horizon}_{task(sign|mag)}_{model_family}_{feature_set_hash}_{train_range}_{commit}`

### 8.2 Store artifacts for every trained model
- features list + hashes
- data ranges / splits / embargo value
- calibration parameters
- gating thresholds + expected coverage
- metrics by fold + by regime
- confusion matrices

**Deliverables:**
- `model_registry.jsonl` (or DB)
- `artifacts/` layout spec

---

## 9) Monitoring Spec (make “persistence” a product feature)
### 9.1 Monitor drift and output behavior
- feature drift (PSI/KS on key features, regime stats)
- prediction drift (distribution of `P(+)`, coverage, abstain rate)
- performance drift (sign accuracy by regime/session)

### 9.2 Alert & response policy
Define:
- thresholds for alerts
- what triggers recalibration vs retraining
- rollback rules

**Deliverable:** `monitoring_and_alerts.md`

---

## 10) Recommended Roadmap Edits (quick patch list)
### Must-change items
- Replace fixed embargo with lookback-derived embargo logic
- Add Metric Contract + Persistence Contract
- Add Feature Lineage Ledger artifact generation
- Add Leakage Audit tests milestone
- Add Phase 4.5 Validation & Governance Gate
- Update ablation to use balanced sign accuracy + regime slices
- Expand calibration to bake-off + reliability reporting

### Strongly recommended
- Add cross-group interaction screening (top-N group pairs or global model permutation)
- Strengthen stability selection seeds at final stage
- Seed-bagging of base learners; compare against averaging baseline
- Two-stage (sign then magnitude) modeling with gating policy

---

## Suggested File/Artifact Map (what “done” looks like)
- `metrics_contract.md`
- `persistence_contract.md`
- `leakage_guardrails.md`
- `feature_ledger.parquet` + `feature_ledger.md`
- `clusters.json` + `clustering_report.md`
- `stability_selection_report.md`
- `ablation_by_regime.md`
- `stack_spec.md`
- `calibration_report.md`
- `gating_policy.md` + `coverage_curves.md`
- `phase_4_5_gate_checklist.md`
- `monitoring_and_alerts.md`
- `model_registry.jsonl`

---

## Final note
These updates convert the roadmap from "good conceptual plan" into an **auditable, defensible, production-ready selection and modeling system** that can credibly claim it *accounted for all 3,813 features* and improved directional accuracy in a way that persists.
