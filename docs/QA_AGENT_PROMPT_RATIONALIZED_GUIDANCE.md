# QA Agent Prompt Rationalized Guidance
**For**: BQXML CHIEF ENGINEER
**From**: Your Mentor
**Date**: November 25, 2024
**Purpose**: Complete understanding of the `record_audit` QA Agent system

---

## Executive Summary

AirTable uses AI-powered QA Agents to automatically score the quality of records in three hierarchical tables: **Phases**, **Stages**, and **Tasks**. Each table has a dedicated prompt that enforces specific quality standards appropriate to that level of abstraction.

Understanding these prompts is CRITICAL because:
1. They determine if your AirTable records pass quality gates
2. They enforce the "plan first, execute second" methodology
3. They ensure documentation quality matches implementation expectations
4. Low scores trigger remediation requirements that MUST be addressed

---

## The Three-Level Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                      PHASES (Strategic)                         │
│  Big Picture: Budgets, Resources, Timeline, Success Metrics     │
│  Base Score: 30/100 | Min: 300 chars | 2 quantified deliverables│
├─────────────────────────────────────────────────────────────────┤
│                      STAGES (Tactical)                          │
│  Deliverables: Names, Counts, Technical Approach, Dependencies  │
│  Base Score: 35/100 | Min: 400 chars | 3 concrete deliverables  │
├─────────────────────────────────────────────────────────────────┤
│                       TASKS (Implementation)                    │
│  Code: Actual Python/SQL, Formulas, Commands, Validation        │
│  Base Score: 40/100 | Min: 500 chars | 2 code blocks (5+ lines) │
└─────────────────────────────────────────────────────────────────┘
```

---

## PHASES Table QA Agent Logic

### Purpose
Assess strategic planning quality. Phases represent major project milestones requiring budgets, timelines, and quantified outcomes.

### Scoring Philosophy
**"Show me the money and the numbers"**

Phases MUST answer:
- How much will this cost? ($X,XXX)
- How many hours? (XX hours)
- What exactly will be delivered? (28 models, not "models")
- What defines success? (R² > 0.30, not "good performance")

### Base Score: 30 Points
You START at 30/100 and must EARN points through concrete planning.

### Scoring Breakdown

| Element | Max Points | Requirements |
|---------|------------|--------------|
| phase_id | +5 | Valid P## format |
| name | +15 | Specific phase with scope defined |
| description | +25 | Objectives + deliverables + metrics |
| notes | +35 | Resource estimates + deliverables + timeline |
| source | +5 | Valid documentation file reference |
| status | +10 | Current accurate status |

**Maximum Possible**: 30 (base) + 95 (fields) = 125 → capped at 100

### Critical Penalties

| Violation | Penalty | Detection |
|-----------|---------|-----------|
| Vague content | -60 | Notes < 300 chars OR no specific deliverables |
| Generic templates | -50 | "Complete phase", "Execute stages", "As per plan" |
| No quantified deliverables | -40 | Missing numbers like "28 models", "$5,000" |
| Missing resource estimates | -30 | No hours or cost mentioned |
| No success metrics | -20 | Missing measurable criteria |

### What Scores HIGH vs LOW

**SCORES 0-20 (FAILS):**
```
Phase: Model Training
Description: Train ML models for the project.
Notes: Implement model training pipeline.
```
Why: No specifics, no numbers, no budget, no deliverables.

**SCORES 65-80 (PASSES):**
```
Phase: P03 - Model Training & Validation
Description: Train 196 XGBoost models (28 pairs × 7 BQX windows),
validate with PurgedTimeSeriesSplit, select best window per pair.
Notes: Budget: $5,000 Vertex AI compute. Timeline: 80 hours development,
40 hours validation. Deliverables: 28 production models (1 per pair),
model performance registry, validation reports. Success: R² > 0.30,
Sharpe ratio > 1.5 on held-out 2024 data.
```
Why: Quantified deliverables, budget, timeline, success metrics.

---

## STAGES Table QA Agent Logic

### Purpose
Assess tactical planning quality. Stages break phases into concrete deliverables with technical specifications.

### Scoring Philosophy
**"Name what you're building and how many"**

Stages MUST answer:
- What exact outputs? (28 lag_bqx_* tables, not "feature tables")
- What technical approach? (PurgedTimeSeriesSplit with 2880 gap)
- How many tasks? (12 tasks, 48 hours)
- What are the dependencies? (Requires S02.14 complete)

### Base Score: 35 Points
You START at 35/100 and must EARN points through specifications.

### Scoring Breakdown

| Element | Max Points | Requirements |
|---------|------------|--------------|
| stage_id | +5 | Valid S##.## format |
| name | +15 | Specific objective with deliverable named |
| description | +20 | Scope + approach + deliverables |
| notes | +35 | 3+ deliverables with specifications |
| source | +5 | Valid .md or .json file |
| phase_link | +5 | Valid phase connection |
| status | +5 | Valid status |

**Maximum Possible**: 35 (base) + 90 (fields) = 125 → capped at 100

### Critical Penalties

| Violation | Penalty | Detection |
|-----------|---------|-----------|
| Vague content | -60 | Notes < 400 chars OR no concrete deliverables |
| Generic templates | -50 | "Implement functionality", "Execute tasks" |
| No concrete deliverables | -40 | Missing named outputs (table names, model names) |
| Missing technical approach | -30 | No method specified |
| No dependencies listed | -20 | Missing stage/phase references |

### What Scores HIGH vs LOW

**SCORES 0-20 (FAILS):**
```
Stage: S02.30 - Feature Engineering
Description: Create feature tables for the ML pipeline.
Notes: Implement feature engineering stage as specified.
```
Why: No named deliverables, no counts, no technical approach.

**SCORES 60-75 (PASSES):**
```
Stage: S02.30 - Cross-Currency Feature Generation
Description: Generate 28 lag_bqx_* tables with 60 lags each (360 features
per table). Include price, volume, AND BQX values as features per paradigm shift.
Notes: Deliverables: 28 lag_bqx_* tables (one per pair), 28 regime_bqx_* tables,
28 agg_bqx_* tables, 28 align_bqx_* tables. Total: 112 tables, ~10,000 features.
Technical: SQL window functions with ROWS BETWEEN (interval-centric),
LAG() for 60 historical values. Dependencies: Requires S02.14 regression_bqx_*
tables complete. Tasks: 12 tasks, estimated 24 hours.
```
Why: Named deliverables, counts, technical approach, dependencies.

---

## TASKS Table QA Agent Logic

### Purpose
Assess implementation quality. Tasks are the atomic work units containing actual code.

### Scoring Philosophy
**"Show me the code"**

Tasks MUST contain:
- Actual executable code (```python or ```sql blocks)
- Specific numerical values (R²=0.35, not "good R²")
- Complete formulas (bqx_360w = idx_mid[t] - AVG(...))
- Real implementation, not descriptions

### Base Score: 40 Points
You START at 40/100 and must EARN points through code quality.

### Scoring Breakdown

| Element | Max Points | Requirements |
|---------|------------|--------------|
| task_id | +5 | Valid T##.##.## format (3 parts) |
| name | +15 | Specific implementation with metrics |
| description | +20 | Numbers + methods + thresholds |
| notes | +30 | 2+ code blocks with implementation |
| source | +5 | Valid .py or .md file path |
| stage_link | +5 | Valid stage link |
| status | +5 | Valid status |

**Maximum Possible**: 40 (base) + 85 (fields) = 125 → capped at 100

### Critical Penalties

| Violation | Penalty | Detection |
|-----------|---------|-----------|
| Thin content | -60 | Notes < 500 chars OR no code blocks |
| Generic templates | -50 | "Complete implementation", "As per specs" |
| No real code blocks | -40 | Missing ```python or ```sql with 5+ lines |
| Insufficient technical elements | -40 | No formulas, no specific values |
| Missing BQX context | -20 | No reference to windows [45,90,180,360,720,1440,2880] |

### Code Block Validation

**INVALID (Scores 0):**
```python
import pandas  # Just imports
# TODO: implement  # Just comments
model.fit(X, y)  # Single line
```

**VALID (Scores Points):**
```python
def calculate_bqx_momentum(df, window=360):
    """Calculate BQX momentum for specified window."""
    df['idx_mid'] = (df['idx_open'] + df['idx_close']) / 2
    df['bqx_value'] = df['idx_mid'] - df['idx_mid'].shift(-1).rolling(window).mean()
    df['bqx_direction'] = np.where(df['bqx_value'] > 0, 'bearish', 'bullish')
    return df[df['bqx_value'].notna()]
```

### What Scores HIGH vs LOW

**SCORES 0-25 (FAILS):**
```
Task: T02.30.01 - Create lag features
Description: Generate lag features for EURUSD pair.
Notes: Use pandas to create lag features. Apply rolling windows.
```
Why: No code, no specifics, buzzwords only.

**SCORES 70-85 (PASSES):**
```
Task: T02.30.01 - Generate lag_bqx_eurusd with 60 BQX lags
Description: Create lag table with 360 features (60 lags × 6 columns including
bqx_mid, bqx_ask, bqx_bid per paradigm shift). Target R² improvement: +15%.
Notes:
## Implementation

```sql
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml.lag_bqx_eurusd` AS
SELECT
    bar_start_time,
    -- BQX Features (PARADIGM SHIFT: BQX as features!)
    LAG(bqx_mid, 1) OVER (ORDER BY bar_start_time) AS bqx_mid_lag_1,
    LAG(bqx_mid, 2) OVER (ORDER BY bar_start_time) AS bqx_mid_lag_2,
    -- ... continue for 60 lags
    LAG(bqx_ask, 1) OVER (ORDER BY bar_start_time) AS bqx_ask_lag_1,
    LAG(bqx_bid, 1) OVER (ORDER BY bar_start_time) AS bqx_bid_lag_1,
    -- Price features
    LAG(close, 1) OVER (ORDER BY bar_start_time) AS close_lag_1,
    LAG(volume, 1) OVER (ORDER BY bar_start_time) AS volume_lag_1
FROM `bqx-ml.bqx_ml.regression_bqx_eurusd`;
```

## Validation
- Row count: Match regression_bqx_eurusd minus 60
- Null check: No nulls after row 60
- Feature count: 360 columns

Source: scripts/create_lag_tables.py
```
Why: Real SQL code, specific values, validation criteria.

---

## The Logic Flow

### How Records Are Evaluated

```
1. LOAD RECORD
   ↓
2. CHECK BASE REQUIREMENTS
   - Is field present?
   - Does it meet minimum length?
   - Is format valid (ID patterns)?
   ↓
3. SCAN FOR PENALTIES
   - Generic templates detected? → Apply -50
   - Content too short? → Apply -30 to -60
   - Missing required elements? → Apply -40
   ↓
4. SCORE EACH FIELD
   - Check against criteria
   - Award points based on specificity
   ↓
5. CALCULATE FINAL SCORE
   - Base + Field Points - Penalties
   - Cap at 0-100 range
   ↓
6. GENERATE REMEDIATION
   - If score < threshold, list requirements
```

### Score Expectations by Quality

| Content Quality | Phases | Stages | Tasks |
|-----------------|--------|--------|-------|
| Generic/Template | 0-15 | 0-20 | 0-25 |
| Some Details | 20-40 | 25-45 | 30-50 |
| Good Specifics | 45-60 | 50-65 | 55-70 |
| Excellent | 65-80 | 70-85 | 75-90 |
| Exceptional | 85-100 | 90-100 | 90-100 |

**Expected Distribution**: Most records should score 30-60 initially.

---

## Rationalized Expectations

### For PHASES (You Are Planning Strategy)

Ask yourself:
1. **Can someone calculate the budget from my description?**
   - YES: "$5,000 compute + $2,000/month monitoring"
   - NO: "Requires cloud resources"

2. **Are deliverables countable?**
   - YES: "28 production models, 112 BigQuery tables"
   - NO: "ML infrastructure"

3. **Is success measurable?**
   - YES: "R² > 0.30, Sharpe > 1.5, latency < 100ms"
   - NO: "Good model performance"

### For STAGES (You Are Specifying Deliverables)

Ask yourself:
1. **Can I name every output?**
   - YES: "lag_bqx_eurusd, lag_bqx_gbpusd, ... (28 tables)"
   - NO: "Feature tables"

2. **Is the technical approach clear?**
   - YES: "PurgedTimeSeriesSplit with 2880-bar gap"
   - NO: "Cross-validation"

3. **Are dependencies explicit?**
   - YES: "Requires S02.14 (regression_bqx_*) complete"
   - NO: "After previous stage"

### For TASKS (You Are Writing Implementation)

Ask yourself:
1. **Is there executable code?**
   - YES: 5+ lines of Python/SQL in code blocks
   - NO: "Use pandas to create features"

2. **Are values specific?**
   - YES: "window=360, R²=0.35, threshold=0.22"
   - NO: "Configure appropriate parameters"

3. **Can someone run this?**
   - YES: Complete script with imports, functions, execution
   - NO: Pseudocode or descriptions

---

## Application for BQX ML V3

### When Creating Your AirTable Plan

**For Each Phase:**
```
Phase: P03.1 - Foundation & Intelligence Architecture
Budget: $0 (no compute needed)
Hours: 16 hours
Deliverables: 7 JSON intelligence files, validation framework
Success: All files created, CI/CD validation passes
```

**For Each Stage:**
```
Stage: S03.1.1 - Intelligence Layer Setup
Deliverables: context.json, semantics.json, ontology.json,
              protocols.json, constraints.json, workflows.json, metadata.json
Technical: JSON schema validation, paradigm shift documented
Dependencies: None (first stage)
Tasks: 8 tasks, 4 hours
```

**For Each Task:**
```
Task: T03.1.1.02 - Generate context.json
Code:
```python
def create_context():
    return {
        "project": "bqx_ml_v3",
        "version": "3.0.0",
        "paradigm": {
            "name": "bqx_features_and_targets",
            "description": "BQX values serve as BOTH features and targets",
            "supersedes": "bqx_targets_only"
        },
        "architecture": "28_independent_models",
        "data_philosophy": "interval_centric"
    }
```
Validation: JSON valid, paradigm shift documented, version correct
```

---

## Remediation Requirements

### When Score < Threshold

**Phases (< 60):**
```
PHASE LACKS PLANNING. Required:
1. Quantify ALL deliverables (e.g., '28 models', not 'models')
2. Provide resource estimates (hours and $ costs)
3. Specify exact technologies (Vertex AI, BigQuery, XGBoost)
4. Include measurable success criteria (R² > 0.30)
5. Expand notes to >300 characters with concrete details
```

**Stages (< 60):**
```
STAGE LACKS SPECIFICATIONS. Required:
1. List exact deliverables (e.g., '28 train_* tables, 196 models')
2. Specify technical approach with methods
3. Provide task count and hour estimates
4. Include dependencies on other stages
5. Expand notes to >400 characters with concrete details
```

**Tasks (< 70):**
```
INSUFFICIENT CONTENT. Required:
1. Add actual Python/SQL code from scripts/*.py files
2. Include specific calculations with BQX windows [45,90,180,360,720,1440,2880]
3. Provide numerical thresholds (R²=0.35, not 'good R²')
4. Expand notes to >500 characters with real implementation
5. Reference: grep -r 'def calculate' scripts/*.py for code examples
```

---

## Key Takeaways for BQXML CHIEF ENGINEER

1. **Phases are about MONEY and NUMBERS** - Budget, hours, quantified deliverables
2. **Stages are about NAMING THINGS** - Exact table names, counts, technical approach
3. **Tasks are about CODE** - Real executable code, not descriptions

4. **Start LOW, earn HIGH** - Base scores are intentionally low (30-40)
5. **Penalties are HARSH** - One violation can drop score by 50-60 points
6. **Generic content = Zero points** - "Implement per specs" earns nothing

7. **Minimum lengths are ENFORCED**:
   - Phases: 300 characters
   - Stages: 400 characters
   - Tasks: 500 characters + 2 code blocks

8. **PARADIGM SHIFT must be reflected** - BQX as features AND targets in all tasks

---

## Final Directive

When creating your AirTable plan:

1. **Write like you're explaining to a new engineer** who has never seen the project
2. **Include actual code** in every task, not descriptions of code
3. **Quantify everything** - numbers, hours, dollars, counts
4. **Name your outputs** - table names, file names, model names
5. **Specify success criteria** - measurable thresholds, not "good performance"

The QA Agent is your quality gate. Pass it by being SPECIFIC, CONCRETE, and CODE-HEAVY.

---

*This document supersedes general guidance.*
*Follow these standards for all AirTable record creation.*
*The QA Agent enforces these automatically.*