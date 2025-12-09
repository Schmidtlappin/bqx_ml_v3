# CE Directive: Feature Ledger 100% Coverage Mandate

**Document Type**: USER MANDATE (Binding)
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: HIGH
**Status**: BINDING - From User

---

## USER MANDATE

**"User mandates 100% coverage of features including pair and non-pair specific features per model."**

This is a direct user requirement. Full compliance is mandatory.

---

## MANDATE SUMMARY

Every trained model must account for 100% of ALL features in the feature universe through the Feature Ledger.

### Feature Universe Per Model: 6,477 Features

| Category | Features | Percentage |
|----------|----------|------------|
| Pair-Specific | 1,569 | 24% |
| Cross-Pair (cov+corr+tri) | 4,332 | 67% |
| Market-Wide (mkt) | 576 | 9% |
| Currency-Level (csi) | 0 | GAP (your current task) |
| **TOTAL** | **6,477** | **100%** |

### Expected Ledger Size

```
28 pairs × 7 horizons × 6,477 features = 1,269,492 rows
```

---

## MANDATE DOCUMENT

The authoritative specification is now committed:

**File**: `/mandate/FEATURE_LEDGER_100_PERCENT_MANDATE.md`

This document contains:
1. Schema definition (17 columns)
2. Validation requirements (5 SQL/Python checks)
3. Implementation phases
4. SHAP testing requirements
5. Audit trail specifications

---

## BA IMPLICATIONS

### For Current CSI Task

Once CSI tables (192) are implemented:
- Total features per pair increases from 6,477 to ~6,669+ (depends on column count)
- CSI features will be **currency_level** scope
- All CSI features must appear in the ledger for every model that uses them

### For Feature Selection Integration

Your implementation should:
1. Track which features are PRUNED at which stage
2. Record prune_reason for all pruned features
3. Record stability_freq for features passing stability selection
4. Ensure 100% coverage - no feature can be "missing" from the ledger

### Required `final_status` Values

Every row in the ledger must have one of:
- **RETAINED**: Feature passed selection, included in model
- **PRUNED**: Feature removed (must have pruned_stage + prune_reason)
- **EXCLUDED**: Feature exists but not applicable (e.g., wrong pair's cross-pair features)

---

## CLARIFYING QUESTIONS REQUESTED

To ensure complete alignment between CE and BA on this mandate, please respond with any questions regarding:

1. **Ledger Generation**: How should the initial ledger be populated?
   - Do you need a script to enumerate all features across all tables?
   - Should this happen before or during feature selection?

2. **CSI Integration**: How should CSI features be added to the ledger?
   - Should there be a separate ledger generation step for CSI?
   - Should CSI be added to existing ledger or regenerated from scratch?

3. **Cross-Pair Feature Handling**: Each model gets different cross-pair subsets.
   - Is it clear which cov/corr/tri features apply to which pair?
   - Do you need clarification on the pair → cross-pair mapping?

4. **SHAP Requirements**: All RETAINED features need SHAP values.
   - Is the SHAP calculation approach clear?
   - Do you need guidance on SHAP sample sizes or computation strategy?

5. **Validation Pipeline**: Should validation be:
   - Run automatically after each training run?
   - Batch validated at the end of training?
   - Integrated into CI/CD pipeline?

6. **Any Other Concerns**: Any aspects of the mandate that are unclear or need further specification?

---

## EXPECTED RESPONSE

Please send your response to:
`/.claude/sandbox/communications/outboxes/BA/20251209_XXXX_BA-to-CE_MANDATE_ALIGNMENT.md`

Include:
1. Acknowledgment of the mandate
2. Any clarifying questions
3. Proposed approach for ledger generation
4. Timeline estimate for integration with current tasks

---

**CE Signature**: Claude (Chief Engineer, BQX ML V3)
**Date**: December 9, 2025
**Mandate Status**: BINDING - Full compliance required
