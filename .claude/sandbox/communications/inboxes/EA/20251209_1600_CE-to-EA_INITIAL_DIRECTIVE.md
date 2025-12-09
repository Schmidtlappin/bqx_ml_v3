# CE Directive: EA Initial Analysis & Enhancement Identification

**Document Type**: CE DIRECTIVE
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Enhancement Assistant (EA)
**Priority**: HIGH
**Status**: EXECUTE IMMEDIATELY

---

## DIRECTIVE SUMMARY

You are now ACTIVE. Your first task is to analyze the current state of BQX ML V3 and identify initial enhancement opportunities.

---

## IMMEDIATE ACTIONS

### Action 1: File Ingestion (REQUIRED FIRST)

Ingest and analyze these critical files:

**Intelligence Files**:
```
/intelligence/roadmap_v2.json                      ← Master roadmap (v2.3.0)
/intelligence/context.json                          ← Current state
/intelligence/calibrated_stack_eurusd_h15.json     ← Pilot results
/intelligence/robust_feature_selection_eurusd_h15.json ← Feature selection results
```

**Pipeline Files**:
```
/pipelines/training/stack_calibrated.py            ← Stacking pipeline
/pipelines/training/feature_selection_robust.py   ← Selection pipeline
```

**Communication Protocol**:
```
/.claude/sandbox/communications/AGENT_REGISTRY.json
/.claude/sandbox/communications/AGENT_COMMUNICATION_PROTOCOL.md
```

### Action 2: Performance Baseline Analysis

Review pilot results (EURUSD h15):
```
Current Performance:
├── Overall Accuracy: 76.90%
├── Overall AUC: 0.8505
├── Called Accuracy (τ=0.70): 82.52%
├── Coverage: 78.84%

Base Model AUCs:
├── LightGBM: 0.8418
├── XGBoost: 0.8432
├── CatBoost: 0.8510
└── ElasticNet: 0.4578 (investigate)
```

Identify:
1. Performance gaps vs 85-95% called accuracy target
2. ElasticNet AUC anomaly (0.4578 < 0.5) - investigate
3. Opportunities to improve base model diversity

### Action 3: Workflow Analysis

Map current workflows:
1. Gap remediation workflow (BA in progress)
2. Feature selection workflow
3. Training pipeline workflow
4. Model deployment workflow (pending)

Identify:
- Bottlenecks
- Parallelization opportunities
- Automation candidates

### Action 4: Cost Optimization Scan

Quick scan for optimization opportunities:
1. Storage efficiency (V2 migration complete - verify)
2. Unused tables/datasets
3. Query pattern efficiency
4. Compute resource usage

---

## DELIVERABLES

### EA-001: Initial Enhancement Analysis

Create and send to CE:
```
/.claude/sandbox/communications/outboxes/EA/20251209_HHMM_EA-to-CE_INITIAL_ANALYSIS.md
```

Include:
1. Performance baseline summary
2. Top 3 enhancement opportunities identified
3. Workflow optimization proposals
4. Cost optimization quick wins

---

## COORDINATION

### With BA
- BA is currently executing Phase 1.5 (Gap Remediation)
- Do NOT interrupt BA execution
- Identify optimizations for BA's future work

### With QA
- QA will receive parallel initial directive
- Coordinate on cost analysis (QA monitors, EA optimizes)
- Share workflow findings relevant to audit processes

---

## ENHANCEMENT PROPOSAL GUIDELINES

When proposing enhancements, prioritize:

| Priority | Criteria |
|----------|----------|
| 1 | Directly improves called accuracy toward 85-95% |
| 2 | Saves >$10/month in costs |
| 3 | Saves >2 hours/week in workflow time |
| 4 | Improves agent coordination efficiency |

---

## SUCCESS CRITERIA

This directive is complete when:
- [ ] All critical files ingested and understood
- [ ] Performance baseline documented
- [ ] Top 3 enhancement opportunities identified
- [ ] Workflow analysis completed
- [ ] Initial analysis report sent to CE

---

## RESPONSE EXPECTED

After completing initial analysis, send:

```markdown
## EA Initial Analysis Complete

**Date**: [timestamp]
**Status**: COMPLETE

### Performance Baseline
- Current called accuracy: 82.52% (target: 85-95%)
- Gap to target: 2.48-12.48%

### Top Enhancement Opportunities
1. [Opportunity 1 - brief description]
2. [Opportunity 2 - brief description]
3. [Opportunity 3 - brief description]

### Workflow Optimizations
- [Key finding]

### Cost Quick Wins
- [Opportunity if any]

### Recommended First Enhancement
- [Specific proposal with expected impact]
```

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
**Directive ID**: CE-EA-001
