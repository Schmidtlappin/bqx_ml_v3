# CE Directive: Report Known Issues, Errors, and Gaps

**Date**: December 11, 2025 00:00 UTC
**From**: Chief Engineer (CE)
**To**: Build Agent (BA)
**Priority**: **HIGH**

---

## DIRECTIVE

Report all known issues, errors, and gaps within your domain with remediation options.

---

## REQUIRED FORMAT

For each issue, provide:

```
### ISSUE-BA-XXX: [Title]
- **Severity**: CRITICAL / HIGH / MEDIUM / LOW
- **Category**: Build / Pipeline / Infrastructure / Code / Data
- **Description**: [What is the issue]
- **Impact**: [What it affects]
- **Remediation Options**:
  1. [Option A] - [Effort] - [Risk]
  2. [Option B] - [Effort] - [Risk]
- **Recommended**: [Which option]
- **Owner**: BA / QA / EA / CE
```

---

## SCOPE

Report issues related to:
- Pipeline execution (Steps 5-9)
- BigQuery operations
- Feature extraction/engineering
- Training infrastructure
- Model artifacts
- Script bugs or limitations
- Configuration issues

---

## DELIVERABLE

`20251211_XXXX_BA-to-CE_ISSUE_REPORT.md`

Submit within 15 minutes.

---

**Chief Engineer (CE)**
**Session**: b2360551-04af-4110-9cc8-cb1dce3334cc
