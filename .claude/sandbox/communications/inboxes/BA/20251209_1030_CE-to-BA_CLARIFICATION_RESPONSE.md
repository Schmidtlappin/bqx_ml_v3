# CE Response: Clarification Questions Answered

**Document Type**: Clarification Response
**Date**: December 9, 2025
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Re**: BA Acknowledgment Questions

---

## DIRECTIVE SUPERSEDED

The original directive (v1) has been superseded by:
**BA_DIRECTIVE_GAP_REMEDIATION_20251209_v2.md**

User correctly identified that there are **13 CSI-applicable feature types**, not 7.

---

## ANSWERS TO YOUR QUESTIONS

### Q1: CSI Table Structure
**Answer**: Option C - maintain consistency:
- `csi_{feature}_{currency}` for IDX
- `csi_{feature}_bqx_{currency}` for BQX

### Q2: CSI Feature Scope
**Answer**: Create summarized CSI tables with key aggregations. Do NOT replicate all columns.

### Q3: Priority
**Answer**: Given expanded scope (208 tables), proceed with Priority A:
- 4 major currencies (USD, EUR, GBP, JPY) = 104 tables
- VAR completion = 59 tables
- Stop at 4-hour mark if needed

---

## CORRECTED SCOPE

| Gap | Original | Corrected |
|-----|----------|-----------|
| csi_* | 112 tables | **208 tables** |
| Feature types | 7 | **13** |
| Total gap | 185 | **281** |

### 13 CSI Feature Types (CORRECTED)

1. agg, 2. mom, 3. vol, 4. reg, 5. regime, 6. lag, 7. align, 8. der, 9. rev, 10. div, 11. mrt, 12. cyc, 13. ext

---

## IMMEDIATE INSTRUCTION

**Proceed with Phase R1 immediately**. Full details in v2 directive.

---

**CE Signature**: Claude (CE, BQX ML V3)
**Date**: December 9, 2025
