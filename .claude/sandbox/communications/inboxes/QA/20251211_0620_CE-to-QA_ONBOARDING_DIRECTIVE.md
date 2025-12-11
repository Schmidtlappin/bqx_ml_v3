# CE Directive: QA Onboarding Required

**Date**: December 11, 2025 06:20 UTC
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: P0 - IMMEDIATE

---

## DIRECTIVE

**You must complete proper onboarding before any other tasks.**

---

## ONBOARDING SEQUENCE (REQUIRED - READ ALL FILES)

### Step 1: Intelligence Files
Read ALL files in order:
1. `/home/micha/bqx_ml_v3/intelligence/context.json`
2. `/home/micha/bqx_ml_v3/intelligence/ontology.json`
3. `/home/micha/bqx_ml_v3/intelligence/roadmap_v2.json`
4. `/home/micha/bqx_ml_v3/intelligence/semantics.json`
5. `/home/micha/bqx_ml_v3/intelligence/feature_catalogue.json`

### Step 2: Mandate Files
Read ALL files:
1. `/home/micha/bqx_ml_v3/mandate/README.md`
2. `/home/micha/bqx_ml_v3/mandate/BQX_ML_V3_FEATURE_INVENTORY.md`
3. `/home/micha/bqx_ml_v3/mandate/FEATURE_LEDGER_100_PERCENT_MANDATE.md`

### Step 3: Agent-Specific Files
Read ALL files:
1. `/home/micha/bqx_ml_v3/.claude/sandbox/communications/shared/QA_TODO.md`
2. `/home/micha/bqx_ml_v3/.claude/sandbox/communications/shared/AGENT_ONBOARDING_PROMPTS.md`
3. `/home/micha/bqx_ml_v3/.claude/sandbox/communications/shared/QA_SESSION_HANDOFF.md`

### Step 4: Read Your Inbox
Read recent messages in:
`/home/micha/bqx_ml_v3/.claude/sandbox/communications/inboxes/QA/`

---

## CURRENT STATE

| Item | Status |
|------|--------|
| Step 6 | RUNNING (PID 1312752, EURUSD 65%) |
| Workers | 16 per pair |
| Mode | SEQUENTIAL + CHECKPOINT |
| Session Cleanup | COMPLETE (218→3 files) |
| EA Cleanup | COMPLETE (128 items archived) |

---

## YOUR ROLE

QA - Quality Assurance Agent responsibilities:
- Validate data quality and completeness
- Audit pipeline outputs
- Review documentation consistency
- Monitor Step 6 progress and audit outputs

---

## AFTER ONBOARDING

1. Read `shared/QA_TODO.md` for current tasks
2. Monitor Step 6 progress
3. Prepare to audit EURUSD data when complete
4. Report to CE when onboarding complete

---

## REPORT FORMAT

After completing onboarding, send acknowledgment to:
`inboxes/CE/[timestamp]_QA-to-CE_ONBOARDING_COMPLETE.md`

Include:
- Files ingested (count)
- Current understanding of project state
- Ready for tasks: YES/NO

---

**Chief Engineer (CE)**
