# BA Session Handoff (Context Recovery)

**Date**: December 11, 2025 05:15 UTC
**Purpose**: Resume BA session after context limit

---

## ONBOARDING SEQUENCE (REQUIRED)

**You are BA - Build Agent for BQX ML V3 project.**

### Step 1: Ingest Intelligence Files (READ ALL)
```
/intelligence/context.json        # Project context and current state
/intelligence/ontology.json       # Data model and entity definitions
/intelligence/roadmap_v2.json     # Current roadmap and milestones
/intelligence/semantics.json      # Feature semantics and naming
/intelligence/feature_catalogue.json  # Feature inventory
```

### Step 2: Ingest Mandate Files (READ ALL)
```
/mandate/README.md                # Project mandate overview
/mandate/BQX_ML_V3_FEATURE_INVENTORY.md  # Feature coverage requirements
/mandate/FEATURE_LEDGER_100_PERCENT_MANDATE.md  # Feature tracking mandate
```

### Step 3: Ingest Agent-Specific Files (READ ALL)
```
/.claude/sandbox/communications/shared/BA_TODO.md           # Your current tasks
/.claude/sandbox/communications/shared/AGENT_ONBOARDING_PROMPTS.md  # Role definition
/.claude/sandbox/communications/inboxes/BA/                 # Your inbox (all .md files)
```

### Step 4: Read This Handoff Context Below

---

## CURRENT TASK: Step 6 Optimization

### Active Directive
`inboxes/BA/20251211_0510_CE-to-BA_WORKER_OPTIMIZATION_APPROVED.md`

### Task Summary
1. **APPROVED**: Increase workers from 12 to 16 per pair
2. **Mode**: SEQUENTIAL pairs (USER MANDATE - do NOT change)
3. **Current Process**: PID 1272452 running EURUSD

### Implementation Options

**Option A** (Recommended if EURUSD >50%):
- Let EURUSD complete
- Stop process after EURUSD saves
- Modify MAX_WORKERS to 16
- Restart

**Option B** (if EURUSD <50%):
- Stop process now
- Modify MAX_WORKERS to 16
- Restart (checkpoints preserved)

### Code Change Required
File: `pipelines/training/parallel_feature_testing.py`
```python
# Line ~15
MAX_WORKERS = 16  # Was 12
```

### Current Progress
```
EURUSD: ~230/669 tables (34%)
Checkpoints: data/features/checkpoints/eurusd/
```

### Commands
```bash
# Check progress
tail -10 logs/step6_sequential_*.log

# Stop process
pkill -f parallel_feature_testing

# Restart
nohup python3 pipelines/training/parallel_feature_testing.py full > logs/step6_sequential_$(date +%Y%m%d_%H%M%S).log 2>&1 &
```

---

## USER MANDATES (BINDING)

1. **Sequential pairs**: All workers on ONE pair at a time
2. **Checkpoint/resume**: Parquet files per table
3. **12→16 workers**: APPROVED optimization

---

## TODO
Read: `shared/BA_TODO.md`
Inbox: `inboxes/BA/`

---

**To resume**: Start new session, paste this context, continue task.
