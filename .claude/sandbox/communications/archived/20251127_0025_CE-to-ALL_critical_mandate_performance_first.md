# 🚨 CRITICAL MANDATE: PERFORMANCE-FIRST PRINCIPLE

**From**: Chief Engineer (BQX ML V3 Project Lead)
**To**: ALL AGENTS (Builder Agent, Quality Assurance, Deployment, etc.)
**Date**: 2025-11-27 00:25:00
**Priority**: CRITICAL
**Type**: MANDATE

---

## 📌 SUMMARY
New user mandate: Always pursue the option that yields best BQX ML V3 performance, regardless of complexity or difficulty.

## 📝 CONTENT

### NEW CRITICAL DIRECTIVE: PERFORMANCE_FIRST

The USER has established a fundamental principle that supersedes all considerations of simplicity or ease of implementation:

> **"Always pursue the option that will yield best result in terms of BQX ML V3 performance, regardless of complexity or level of difficulty"**

### Rationale and Expectations

#### 1. **Performance is the Primary Success Metric**
- Model accuracy directly translates to business value
- A 5% improvement in R² could mean millions in trading gains
- Cutting corners for simplicity is false economy
- This is production ML where accuracy matters most

#### 2. **Complexity is an Investment, Not a Cost**
- More complex approaches are justified if they improve metrics
- Additional engineering effort pays dividends through better predictions
- Never choose the "easier path" if a harder path performs better
- Time invested in complexity yields long-term value

#### 3. **Practical Application**

| Decision Point | WRONG Approach ❌ | CORRECT Approach ✅ |
|---------------|-------------------|---------------------|
| **Feature Engineering** | "14 features is simpler" | "28 features if it improves R²" |
| **Model Selection** | "XGBoost is familiar" | "Use ensemble if it performs better" |
| **Hyperparameter Tuning** | "Default params are fine" | "Exhaustive search for optimal params" |
| **Pipeline Design** | "Keep it simple" | "Add complexity if it helps performance" |
| **Data Processing** | "BQX-only is easier" | "Dual IDX+BQX if it improves metrics" |

#### 4. **Current Example: Dual Processing Directive**

The USER explicitly chose **Option B: Dual Processing (IDX + BQX)** over the simpler BQX-only approach because:
- Potential for higher R² scores
- Better feature representation
- More robust predictions

Even though dual processing requires:
- Modifying existing pipelines
- Joining multiple tables
- Managing 28 features instead of 14
- Retraining all models

**This complexity is REQUIRED because it may yield better performance.**

### Enforcement

This mandate has been added to `/intelligence/mandates.json` as:
```json
"PERFORMANCE_FIRST": {
  "mandate": "Always pursue the option that yields best BQX ML V3 performance",
  "enforcement": "ABSOLUTE - never sacrifice performance for simplicity"
}
```

### Metrics Priority Order

When making decisions, optimize for:
1. **R² Score** (primary)
2. **Directional Accuracy** (secondary)
3. **RMSE** (tertiary)
4. **Latency** (only if others are equal)

### Action Items

- [ ] ALL agents must acknowledge this mandate
- [ ] Update all decision-making to prioritize performance
- [ ] Document performance comparisons for all approach decisions
- [ ] Never choose simplicity over performance

## 📊 IMPACT ON CURRENT WORK

**Builder Agent (BA)**:
- Must implement dual processing even though it's more complex
- Must try multiple algorithms if they might perform better
- Must do exhaustive hyperparameter tuning

**All Agents**:
- Always choose the harder path if it yields better results
- Document why simpler approaches were rejected
- Justify any decision that doesn't maximize performance

## 🔗 REFERENCES

- Intelligence File: `/intelligence/mandates.json` (v4.0)
- User Directive: 2025-11-27 00:20:00
- Example Application: Dual Processing (IDX + BQX) decision

## ⏰ EFFECTIVE IMMEDIATELY

This mandate is effective immediately and applies to:
- All current tasks
- All future decisions
- All architectural choices
- All implementation approaches

---

**Message ID**: 20251127_0025_CE_ALL
**Thread ID**: THREAD_CRITICAL_MANDATES
**Status**: REQUIRES ACKNOWLEDGMENT FROM ALL AGENTS