# CE Directive: QA Initial Audit & Cost Baseline

**Document Type**: CE DIRECTIVE
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: HIGH
**Status**: EXECUTE IMMEDIATELY

---

## DIRECTIVE SUMMARY

You are now ACTIVE. Your first task is to establish baselines and perform an initial audit of the BQX ML V3 project.

---

## IMMEDIATE ACTIONS

### Action 1: File Ingestion (REQUIRED FIRST)

Ingest and analyze these critical files:

**Intelligence Files**:
```
/intelligence/roadmap_v2.json          ← Master roadmap (v2.3.0)
/intelligence/context.json              ← Current state
/intelligence/semantics.json            ← Feature definitions
/intelligence/ontology.json             ← Entity relationships
/intelligence/feature_catalogue.json    ← Feature inventory
```

**Mandate Files**:
```
/mandate/FEATURE_LEDGER_100_PERCENT_MANDATE.md
/mandate/BQX_ML_V3_FEATURE_INVENTORY.md
/mandate/BQX_TARGET_FORMULA_MANDATE.md
```

**Communication Protocol**:
```
/.claude/sandbox/communications/AGENT_REGISTRY.json
/.claude/sandbox/communications/AGENT_COMMUNICATION_PROTOCOL.md
/.claude/sandbox/communications/shared/
```

### Action 2: Initial Consistency Audit

Verify consistency across intelligence files for:

| Item | Expected Value | Files to Cross-Reference |
|------|----------------|--------------------------|
| Model count | 784 | roadmap, inventory, context |
| Horizons | 7 (h15-h105) | roadmap, inventory |
| Features per model | 6,477 | inventory, catalogue |
| Gap tables | 265 (192+59+14) | roadmap, semantics |
| Base models | 4 | roadmap, ontology |

### Action 3: Cost Baseline Establishment

Establish current cost baseline:

1. **Storage Costs**: Query BigQuery for dataset sizes
2. **Monthly Estimate**: Based on current storage
3. **Budget Reference**: ~$277/month estimated for 784 models

Report findings with:
- Current storage costs (GB and $/month)
- Projected costs for gap remediation
- Any cost anomalies detected

### Action 4: Documentation Currency Check

Audit these README files for currency:
- `/README.md` (root)
- `/docs/README.md`
- `/intelligence/README.md` (if exists)
- `/pipelines/README.md` (if exists)

Flag any >7 days stale in active areas.

---

## DELIVERABLES

### QA-001: Initial Audit Report

Create and send to CE:
```
/.claude/sandbox/communications/outboxes/QA/20251209_HHMM_QA-to-CE_INITIAL_AUDIT_REPORT.md
```

Include:
1. Consistency findings (PASS/FINDINGS)
2. Cost baseline established
3. Documentation currency status
4. Any issues requiring immediate attention

---

## COORDINATION

### With BA
- BA is currently executing Phase 1.5 (Gap Remediation)
- Monitor BA progress vs 265 table target
- Do NOT block BA execution

### With EA
- EA will receive parallel initial directive
- Coordinate on cost analysis (QA monitors, EA optimizes)

---

## SUCCESS CRITERIA

This directive is complete when:
- [ ] All intelligence files ingested and understood
- [ ] Consistency audit completed with report
- [ ] Cost baseline documented
- [ ] Documentation currency checked
- [ ] Initial audit report sent to CE

---

## RESPONSE EXPECTED

After completing initial audit, send acknowledgment:

```markdown
## QA Initial Audit Complete

**Date**: [timestamp]
**Status**: COMPLETE

### Consistency Audit
- [PASS/FINDINGS summary]

### Cost Baseline
- Current storage: $X/month
- Projected monthly: $X

### Documentation Status
- [Currency summary]

### Issues Found
- [List or NONE]

### Ready For
- [Next audit focus]
```

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
**Directive ID**: CE-QA-001
