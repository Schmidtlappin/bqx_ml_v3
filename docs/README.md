# BQX ML V3 Documentation Hub

**Last Updated**: 2025-12-09 (QA Audit)
**Roadmap Version**: v2.3.0
**Current Phase**: Phase 1.5 - Gap Remediation

---

## 📊 Project Status

| Metric | Value | Status |
|--------|-------|--------|
| V2 Migration | COMPLETE | 4,888 tables |
| Gap Tables | 265 remaining | 192 CSI + 59 VAR + 14 MKT |
| Models | 784 planned | 28 pairs × 7 horizons × 4 ensemble |
| Features | 6,477 per model | 607 stable (50% threshold) |
| Storage Cost | $33.88/month | GREEN (budget: $277) |

---

## 🤖 Multi-Agent Coordination

BQX ML V3 uses a multi-agent architecture:

| Agent | Role | Status |
|-------|------|--------|
| **CE** | Chief Engineer - Project oversight | ACTIVE |
| **BA** | Builder Agent - Implementation | ACTIVE |
| **QA** | Quality Assurance - Audit & cost | ACTIVE |
| **EA** | Enhancement Assistant - Optimization | ACTIVE |

### Communication Structure
```
/.claude/sandbox/communications/
├── inboxes/     # Agent inboxes (CE, BA, QA, EA)
├── outboxes/    # Agent outboxes
├── active/      # Charge documents
└── shared/      # Protocols and onboarding
```

---

## 🧠 Intelligence Files

Located in `/intelligence/`:

| File | Purpose | Version |
|------|---------|---------|
| `roadmap_v2.json` | Master roadmap | v2.3.0 |
| `context.json` | Project context | v3.1.0 |
| `semantics.json` | Terminology | Updated 2025-12-09 |
| `ontology.json` | Entity relationships | Updated 2025-12-09 |
| `feature_catalogue.json` | Feature inventory | v2.1.0 |

---

## 📋 Mandate Files

Located in `/mandate/`:

| File | Purpose |
|------|---------|
| `FEATURE_LEDGER_100_PERCENT_MANDATE.md` | 100% feature coverage requirement |
| `BQX_TARGET_FORMULA_MANDATE.md` | Target calculation specification |
| `BQX_ML_V3_FEATURE_INVENTORY.md` | Feature specifications |

---

## 📚 Key Documentation

### Architecture
- `roadmap_v2.json` - Enhanced Stacking Architecture
- `GCP_COST_ESTIMATE_784_MODELS.md` - Cost breakdown

### Implementation
- `pipelines/training/stack_calibrated.py` - Training pipeline
- `pipelines/training/feature_selection_robust.py` - Feature selection

---

## 🚀 Quick Start for Agents

### For BA (Builder Agent)
1. Read charge: `/.claude/sandbox/communications/active/BA_CHARGE_*.md`
2. Check inbox: `/.claude/sandbox/communications/inboxes/BA/`
3. Ingest: `/intelligence/roadmap_v2.json`

### For QA (Quality Assurance)
1. Read charge: `/.claude/sandbox/communications/active/QA_CHARGE_*.md`
2. Check inbox: `/.claude/sandbox/communications/inboxes/QA/`
3. Monitor: Cost, data quality, documentation

### For EA (Enhancement Assistant)
1. Read charge: `/.claude/sandbox/communications/active/EA_CHARGE_*.md`
2. Check inbox: `/.claude/sandbox/communications/inboxes/EA/`
3. Optimize: Performance, cost, workflows

---

## ⚠️ Critical Mandates

1. **784 Models**: 28 pairs × 7 horizons × 4 ensemble (USER MANDATE)
2. **SHAP Samples**: 100,000+ minimum (USER MANDATE)
3. **Stability Threshold**: 50% (USER APPROVED 2025-12-09)
4. **CSI Tables**: 192 (regime excluded - CE AUTHORIZED 2025-12-09)
5. **Interval-Centric**: ROWS BETWEEN only, never time-based

---

*Maintained by: QA Agent*
*Last Audit: 2025-12-09*
