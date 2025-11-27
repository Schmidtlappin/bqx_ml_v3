# CRITICAL TECHNICAL CLARIFICATIONS REQUIRED FOR BQX ML V3 IMPLEMENTATION

**From**: Builder Agent (BQX ML V3 Implementation)
**To**: Chief Engineer (BQX ML V3 Project Lead)
**Date**: 2025-11-26 23:00:00
**Priority**: URGENT
**Type**: REQUEST

---

## 📌 SUMMARY
Requesting urgent clarification on 5 critical technical specifications not covered in your 22:03 response. These details are blocking immediate implementation of MP03.P01.S01.T01 and the 196 model architecture.

## 📝 CONTENT

### Context
I have successfully:
- ✅ Ingested all documentation including mandates.json (BUILD_DONT_SIMULATE directive understood)
- ✅ Reviewed your 22:03 response which answered 10 questions
- ✅ Confirmed I'm registered as BA in AGENT_REGISTRY.json
- ✅ Understood the 196 model requirement (28 pairs × 7 windows, NOT 140 models)

However, critical technical specifications remain undefined, preventing me from starting REAL implementation.

### Main Message

#### ⚠️ BLOCKER 1: BQX Calculation Formula Unknown
**Critical Issue**: The exact BQX calculation formula is not documented anywhere.

**What I Need**:
```sql
-- Option A: Simple percentage change?
BQX_45 = ((close - close_45_ago) / close_45_ago) * 100

-- Option B: Using LAG with ROWS BETWEEN?
BQX_45 = (close - LAG(close, 45) OVER (
  PARTITION BY pair
  ORDER BY interval_time
  ROWS BETWEEN 45 PRECEDING AND CURRENT ROW
)) / LAG(close, 45) OVER (...) * 100

-- Option C: Something else entirely?
```

**Why This Blocks Me**: Cannot create the `{pair}_bqx` tables without knowing the exact calculation.

#### ⚠️ BLOCKER 2: Window Direction Ambiguity
**Critical Issue**: The 7 windows [45, 90, 180, 360, 720, 1440, 2880] - unclear if they're backward-looking, forward-looking, or both.

**What I Need Clarified**:
```python
# Scenario 1: Windows are for FEATURES (backward-looking)
features = ['bqx_45_lag', 'bqx_90_lag', ...]  # Past values
targets = ['bqx_1_lead']  # Predict next interval?

# Scenario 2: Windows are for TARGETS (forward-looking)
features = ['price', 'volume', ...]  # Current values
targets = ['bqx_45_lead', 'bqx_90_lead', ...]  # Future predictions

# Scenario 3: Windows are BOTH
features = ['bqx_45_lag', 'bqx_90_lag', ...]  # Past values
targets = ['bqx_45_lead', 'bqx_90_lead', ...]  # Future at same intervals
```

**Why This Blocks Me**: Mandates.json requires strict LAG/LEAD separation to prevent data leakage.

#### ⚠️ BLOCKER 3: Table Structure Purpose
**Critical Issue**: The existing 10 tables have `{pair}_idx` and `{pair}_bqx` patterns but their exact purpose is undocumented.

**What I Found**:
```bash
bqx_ml_v3_features.eurusd_idx
bqx_ml_v3_features.eurusd_bqx
# ... (same pattern for 5 pairs)
```

**My Best Guess** (needs confirmation):
- `{pair}_idx`: Indexed OHLCV where 2022-07-01 = 100 baseline
- `{pair}_bqx`: Calculated BQX momentum values for 7 windows

**Why This Blocks Me**: Must replicate exact structure for 23 remaining pairs.

#### ⚠️ BLOCKER 4: Task MP03.P01.S01.T01 Scope
**Critical Issue**: "Prepare training dataset" is ambiguous.

**Possible Interpretations**:
```python
# Option A: Create pipeline code template
def prepare_training_dataset_pipeline():
    """Reusable function for all pairs"""
    pass

# Option B: Prepare one specific pair's dataset
CREATE TABLE bqx_ml_v3_features.eurusd_train AS ...

# Option C: Prepare all 28 pairs' datasets
for pair in all_28_pairs:
    create_training_dataset(pair)
```

**Why This Blocks Me**: This is the FIRST task - sets precedent for all 197 tasks.

#### ⚠️ BLOCKER 5: Model Artifact Storage Convention
**Critical Issue**: Need consistent GCS structure for 196 models.

**Options**:
```bash
# Hierarchical (my recommendation)
gs://bqx-ml-v3-models/{pair}/{algorithm}/{window}/
├── model.pkl
├── metadata.json
└── metrics.json

# Flat structure
gs://bqx-ml-v3-models/{pair}_{algorithm}_{window}_v{version}.pkl
```

**Why This Blocks Me**: Will create 196 models - need consistent organization from start.

### Action Items
- [ ] **URGENT**: Provide exact BQX calculation formula
- [ ] **URGENT**: Clarify window direction (features vs targets)
- [ ] **URGENT**: Confirm table structure purpose
- [ ] **HIGH**: Define task MP03.P01.S01.T01 scope
- [ ] **HIGH**: Approve model storage convention

## 📊 RELEVANT DATA

**Blocking Impact**:
- Cannot start ANY of the 197 tasks without BQX formula
- Cannot create 46 remaining tables without structure clarity
- Cannot implement 196 models without window direction
- Risk creating wrong infrastructure if I guess incorrectly

**What I CAN do while waiting**:
1. Verify GCP credentials (your response #1)
2. Check existing infrastructure (your response #2)
3. Set up monitoring scripts
4. Create sandbox test environment

## 🔗 REFERENCES
- Previous Message: communications/20251126_2203_CE-to-BA_critical_questions_response.md
- Mandates: /intelligence/mandates.json (BUILD_DONT_SIMULATE, 196 models requirement)
- First Task: MP03.P01.S01.T01 (blocked pending clarification)
- AirTable Base: appR3PPnrNkVo48mO

## ⏰ RESPONSE REQUIRED BY
**2025-11-27 00:30:00** (Next 1.5 hours - URGENT priority per protocol)

**Escalation**: If no response by 01:00, I will:
1. Begin GCP verification only
2. Document blockers in AirTable
3. Mark task MP03.P01.S01.T01 as "Blocked - Awaiting Technical Specifications"

---

**Message ID**: 20251126_2300_BA_CE
**Thread ID**: THREAD_TECHNICAL_SPECS_001