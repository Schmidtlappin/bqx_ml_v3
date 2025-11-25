# Three-Tier QA System Deployment Guide

## 📊 Overview: The Quality Assessment Hierarchy

Based on [QA_AGENT_PROMPT_RATIONALIZED_GUIDANCE.md](QA_AGENT_PROMPT_RATIONALIZED_GUIDANCE.md), BQX ML V3 uses a **three-tier quality system** where each level has distinct requirements:

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASES: Strategic Planning (Budget, Timeline, Deliverables)     │
│ Base: 30 | Focus: $$$, Hours, "28 models" not "models"         │
├─────────────────────────────────────────────────────────────────┤
│ STAGES: Tactical Specifications (What, How, Dependencies)      │
│ Base: 35 | Focus: Named outputs, Technical methods, Task count │
├─────────────────────────────────────────────────────────────────┤
│ TASKS: Implementation Code (Python/SQL, Values, Formulas)      │
│ Base: 40 | Focus: Executable code, R²=0.35, BQX windows        │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 DEPLOYMENT INSTRUCTIONS

### 1️⃣ Deploy PHASES Prompt (Strategic Level)

**File**: [RATIONALIZED_phases_prompt.md](RATIONALIZED_phases_prompt.md)

**Deploy To**: Phases table → record_audit field

```bash
1. Open AirTable → BQX ML V3 Base → Phases table
2. Click on `record_audit` field header
3. Select "Configure AI"
4. DELETE all existing text
5. Copy lines 5-120 from RATIONALIZED_phases_prompt.md
6. Paste and Save
```

**What It Assesses**:
- ✅ Budget mentioned ($5,000)
- ✅ Timeline specified (80 hours)
- ✅ Deliverables quantified (28 models, 112 tables)
- ✅ Success metrics defined (R² > 0.30)

### 2️⃣ Deploy STAGES Prompt (Tactical Level)

**File**: [RATIONALIZED_stages_prompt.md](RATIONALIZED_stages_prompt.md)

**Deploy To**: Stages table → record_audit field

```bash
1. Open AirTable → BQX ML V3 Base → Stages table
2. Click on `record_audit` field header
3. Select "Configure AI"
4. DELETE all existing text
5. Copy lines 5-125 from RATIONALIZED_stages_prompt.md
6. Paste and Save
```

**What It Assesses**:
- ✅ Outputs named (lag_bqx_eurusd table)
- ✅ Technical approach (PurgedTimeSeriesSplit)
- ✅ Dependencies listed (Requires S02.14)
- ✅ Task count (12 tasks, 24 hours)

### 3️⃣ Deploy TASKS Prompt (Implementation Level)

**File**: [RATIONALIZED_tasks_prompt.md](RATIONALIZED_tasks_prompt.md)

**Deploy To**: Tasks table → record_audit field

```bash
1. Open AirTable → BQX ML V3 Base → Tasks table
2. Click on `record_audit` field header
3. Select "Configure AI"
4. DELETE all existing text
5. Copy lines 5-140 from RATIONALIZED_tasks_prompt.md
6. Paste and Save
```

**What It Assesses**:
- ✅ Code blocks (2+ with 5+ lines each)
- ✅ Specific values (R²=0.35, window=360)
- ✅ BQX windows [45,90,180,360,720,1440,2880]
- ✅ Complete formulas with implementations

## 📋 Key Differences Between Levels

| Aspect | PHASES | STAGES | TASKS |
|--------|--------|--------|-------|
| **Base Score** | 30 (lowest) | 35 | 40 (highest) |
| **Min Notes** | 300 chars | 400 chars | 500 chars + code |
| **Primary Focus** | Money & Time | Names & Methods | Code & Values |
| **Key Question** | "How much?" | "What exactly?" | "Show me code" |
| **Good Score** | 65-80 | 60-75 | 70-85 |

## ✅ Verification After Deployment

Wait 10-30 minutes for AI rescoring, then run:

```python
# Check all three tables
python3 -c "
from pyairtable import Api
import json

with open('.secrets/github_secrets.json') as f:
    secrets = json.load(f)['secrets']

api = Api(secrets['AIRTABLE_API_KEY']['value'])
base_id = secrets['AIRTABLE_BASE_ID']['value']

# Check Phases
phases = api.table(base_id, 'Phases').all()
phases_scores = [p['fields'].get('record_score', 0) for p in phases]
print(f'PHASES: Avg score: {sum(phases_scores)/len(phases_scores):.1f}')
print(f'  Low scores (<60): {len([s for s in phases_scores if s < 60])}')

# Check Stages
stages = api.table(base_id, 'Stages').all()
stages_scores = [s['fields'].get('record_score', 0) for s in stages]
print(f'STAGES: Avg score: {sum(stages_scores)/len(stages_scores):.1f}')
print(f'  Low scores (<60): {len([s for s in stages_scores if s < 60])}')

# Check Tasks
tasks = api.table(base_id, 'Tasks').all()
tasks_scores = [t['fields'].get('record_score', 0) for t in tasks]
print(f'TASKS: Avg score: {sum(tasks_scores)/len(tasks_scores):.1f}')
print(f'  Low scores (<70): {len([s for s in tasks_scores if s < 70])}')
"
```

## 🎯 What Success Looks Like

### PHASES Should Have:
```
Budget: $5,000 Vertex AI compute + $2,000/month monitoring
Hours: 80 development, 40 validation, 20 deployment
Deliverables: 28 production models, 112 BigQuery tables, 7 JSON files
Success: R² > 0.30, Sharpe > 1.5, latency < 100ms
```

### STAGES Should Have:
```
Outputs: lag_bqx_eurusd, lag_bqx_gbpusd, ... (28 tables)
Method: PurgedTimeSeriesSplit with 2880-bar gap
Dependencies: Requires S02.14 regression_bqx_* tables complete
Tasks: 12 tasks, estimated 24 hours
```

### TASKS Should Have:
```python
def calculate_bqx_360w(df):
    """Calculate 360-interval BQX momentum."""
    window = 360
    df['idx_mid'] = (df['idx_open'] + df['idx_close']) / 2
    df['bqx_360w'] = df['idx_mid'] - df['idx_mid'].rolling(window).mean()
    return df[df['bqx_360w'].notna()]
```

## ⚠️ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Scores all 100 | Prompt too complex, use these simplified versions |
| Scores all 0 | Check field references match your table structure |
| No "Score:" output | Ensure prompt starts with output format instruction |
| Generic content not penalized | Check Step 3 penalties are applied |

## 📝 Quick Reference

**All Prompts Created**:
1. [RATIONALIZED_phases_prompt.md](RATIONALIZED_phases_prompt.md) - **Phases** (120 lines)
2. [RATIONALIZED_stages_prompt.md](RATIONALIZED_stages_prompt.md) - **Stages** (125 lines)
3. [RATIONALIZED_tasks_prompt.md](RATIONALIZED_tasks_prompt.md) - **Tasks** (140 lines)

**Key Principle**: Each level assesses different aspects:
- **Phases** = Planning (budget, timeline)
- **Stages** = Specification (deliverables, methods)
- **Tasks** = Implementation (code, values)

## 🔴 CRITICAL REMINDERS

1. **Prompts are SIMPLE** - AI agents can't handle complexity
2. **Output format FIRST** - Always starts with "Score: [number]"
3. **Step-by-step logic** - Numbered steps ensure correct execution
4. **Focus differs by level** - Don't assess code in Phases, don't assess budget in Tasks

---

**Deployment Time**: ~10 minutes (3-4 minutes per table)
**Wait Time**: 10-30 minutes for AI rescoring
**Expected Result**: Proper differentiation between good and poor documentation at each level