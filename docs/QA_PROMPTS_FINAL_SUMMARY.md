# QA Prompts Final Summary

## ✅ Completed: Three-Tier Quality Assessment System

Based on comprehensive analysis of [QA_AGENT_PROMPT_RATIONALIZED_GUIDANCE.md](QA_AGENT_PROMPT_RATIONALIZED_GUIDANCE.md), I've created **three specialized prompts** that properly assess quality at each hierarchical level.

## 📋 The Three Prompts Created

### 1. PHASES Prompt - Strategic Planning Quality
**File**: [RATIONALIZED_phases_prompt.md](RATIONALIZED_phases_prompt.md)
- **Lines**: 5-120 (Simple, AI-agent friendly)
- **Focus**: Budget ($), Timeline (hours), Quantified deliverables
- **Base Score**: 30 (lowest - planning is hardest)
- **Key Requirements**:
  - Must have dollar amounts: "$5,000 compute"
  - Must have hour estimates: "80 hours development"
  - Must have countable deliverables: "28 models" not "models"
  - Must have success metrics: "R² > 0.30"

### 2. STAGES Prompt - Tactical Specifications
**File**: [RATIONALIZED_stages_prompt.md](RATIONALIZED_stages_prompt.md)
- **Lines**: 5-125 (Step-by-step logic)
- **Focus**: Named outputs, Technical methods, Dependencies
- **Base Score**: 35 (middle ground)
- **Key Requirements**:
  - Must name outputs: "lag_bqx_eurusd table"
  - Must specify method: "PurgedTimeSeriesSplit"
  - Must list dependencies: "Requires S02.14 complete"
  - Must count tasks: "12 tasks, 24 hours"

### 3. TASKS Prompt - Implementation Code
**File**: [RATIONALIZED_tasks_prompt.md](RATIONALIZED_tasks_prompt.md)
- **Lines**: 5-140 (Most detailed)
- **Focus**: Executable code, Specific values, BQX windows
- **Base Score**: 40 (highest - implementation is most concrete)
- **Key Requirements**:
  - Must have 2+ code blocks (5+ lines each)
  - Must have specific values: "R²=0.35, window=360"
  - Must reference BQX windows: [45,90,180,360,720,1440,2880]
  - Must be executable Python/SQL, not pseudocode

## 🎯 Key Innovation: Different Focus Per Level

Unlike the previous approach that was overly focused on description fields, these prompts recognize that **each level requires different assessment criteria**:

```
PHASES: "Show me the money and numbers"
        ↓ Strategic planning with budgets
STAGES: "Name what you're building and how many"
        ↓ Tactical specifications with deliverables
TASKS:  "Show me the code"
        ↓ Implementation with executable code
```

## 📊 Scoring Philosophy

Each level starts with a different base score reflecting the difficulty:
- **Phases**: 30 points (hardest - requires strategic thinking)
- **Stages**: 35 points (moderate - requires specification)
- **Tasks**: 40 points (easiest baseline - code is concrete)

Then points are EARNED through quality content, with harsh penalties for generic/template content.

## 🚀 Deployment Guide

Complete deployment instructions: [THREE_TIER_QA_DEPLOYMENT.md](THREE_TIER_QA_DEPLOYMENT.md)

**Quick Deploy**:
1. Phases table → Deploy lines 5-120 from [RATIONALIZED_phases_prompt.md](RATIONALIZED_phases_prompt.md)
2. Stages table → Deploy lines 5-125 from [RATIONALIZED_stages_prompt.md](RATIONALIZED_stages_prompt.md)
3. Tasks table → Deploy lines 5-140 from [RATIONALIZED_tasks_prompt.md](RATIONALIZED_tasks_prompt.md)

## ✅ What Was Fixed

1. **Prompts are now SIMPLE** - AI agent can actually follow them (120-140 lines vs 300+)
2. **Step-by-step numbered logic** - Forces sequential evaluation
3. **Output format first** - Always starts with "Score: [number]"
4. **Level-appropriate assessment** - No more assessing code quality in Phases
5. **Clear penalties** - Generic content gets -50 points immediately

## 📈 Expected Impact

After deployment:
- **Phases** with no budget/timeline will score 0-40 (not 90+)
- **Stages** with no named deliverables will score 0-45 (not 85+)
- **Tasks** with no code will score 0-50 (not 100)
- **Good documentation** will score 70-95 appropriately

## 🔗 All Files Created

| File | Purpose | Status |
|------|---------|--------|
| [RATIONALIZED_phases_prompt.md](RATIONALIZED_phases_prompt.md) | Phases QA prompt | ✅ Ready |
| [RATIONALIZED_stages_prompt.md](RATIONALIZED_stages_prompt.md) | Stages QA prompt | ✅ Ready |
| [RATIONALIZED_tasks_prompt.md](RATIONALIZED_tasks_prompt.md) | Tasks QA prompt | ✅ Ready |
| [THREE_TIER_QA_DEPLOYMENT.md](THREE_TIER_QA_DEPLOYMENT.md) | Deployment guide | ✅ Ready |

## 📝 Additional Context

- **P03 Stages Remediation**: Successfully remediated 19 P03 stages from scores 55-87 to 95
- **Test Script Available**: [test_empty_description_cap.py](../scripts/test_empty_description_cap.py) for validation

---

**Status**: Ready for deployment
**Time Required**: ~10 minutes to deploy all three prompts
**Wait Time**: 10-30 minutes for AI rescoring
**Expected Outcome**: Proper quality differentiation at each hierarchical level