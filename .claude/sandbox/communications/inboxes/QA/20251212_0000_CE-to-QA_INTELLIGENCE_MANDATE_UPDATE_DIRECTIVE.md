# CE Directive: Intelligence and Mandate Files Update - Comprehensive Coverage Validation

**Date**: December 12, 2025 00:00 UTC
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Re**: Update All Intelligence and Mandate Files Post-BigQuery ETL Pivot
**Priority**: HIGH
**Timing**: After EURUSD BigQuery ETL validation complete
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## DIRECTIVE

**Task**: Update all intelligence and mandate files to reflect BigQuery ETL pivot decision and current project status, with comprehensive coverage validation to ensure 100% accuracy and completeness.

**Scope**: All files in `intelligence/` and `mandate/` directories that reference:
- Merge strategy (Polars → BigQuery ETL)
- Memory requirements
- Timeline estimates
- Current pipeline status
- Decision rationale

---

## FILES TO UPDATE

### **Priority 1: Core Intelligence Files** (Update After EURUSD Validation)

**`intelligence/context.json`**
- Lines 224, 231-250: Pipeline status, merge strategy
- Update `merge_strategy`: "DuckDB" → "BigQuery ETL"
- Update `merge_status`: Reflect EURUSD complete, 27 pending
- Update `memory_profile`: Polars bloat documented, BigQuery chosen for safety
- Add `decision_timeline`: USER → EA → CE authorization chain
- Add `polars_test_results`: Documented but rejected due to scale risk

**`intelligence/roadmap_v2.json`**
- Lines 240-244: Current pipeline status
- Update `current_status`: "IN PROGRESS - BigQuery ETL merge execution"
- Update `merge_approach`: "BigQuery ETL (cloud-based, sequential processing)"
- Update `risk_profile`: "LOW (eliminates local resource risks)"
- Add `polars_evaluation`: Test passed but rejected (memory bloat)
- Update `timeline`: Reflect 2.8-5.6h BigQuery ETL estimate

---

### **Priority 2: Feature and Model Metadata** (Review for Accuracy)

**`intelligence/semantics.json`**
- Verify feature counts still accurate (6,477 total features)
- Verify model counts (588 base models + 196 meta-learners = 784 total)
- No changes expected unless extraction affected counts

**`intelligence/feature_catalogue.json`**
- Verify feature lineage references
- Update `merge_method` references from Polars to BigQuery ETL
- Verify feature groups still valid

**`intelligence/ontology.json`**
- Update merge pipeline definition
- Document Polars as "evaluated but rejected"
- Document BigQuery ETL as "production merge method"

---

### **Priority 3: Mandate Files** (Validate Compliance)

**`mandate/BQX_ML_V3_FEATURE_INVENTORY.md`**
- Verify feature counts match extraction output
- Update merge approach section if present
- Confirm 100% alignment with actual checkpoints

**`mandate/FEATURE_LEDGER_100_PERCENT_MANDATE.md`**
- Verify still applicable post-merge
- Confirm ledger requirements unchanged by BigQuery ETL approach

**`mandate/AGENT_ONBOARDING_PROTOCOL.md`**
- No changes expected (process-focused, not technical)

**`mandate/README.md`**
- Update if references merge strategy
- Verify milestone completion status

---

## COMPREHENSIVE COVERAGE VALIDATION

### **1. Cross-Reference Validation**

**Task**: Verify all intelligence files are internally consistent

**Checks**:
- ✅ Feature counts consistent across all files (6,477 or actual)
- ✅ Model counts consistent (784 total)
- ✅ Horizon counts consistent (7 horizons: h15-h105)
- ✅ Pair counts consistent (28 pairs)
- ✅ Table counts consistent with V2 migration (4,888 features_v2 + 2,210 uscen1_v2)
- ✅ Merge strategy consistent across all references
- ✅ Timeline estimates aligned with BigQuery ETL approach

**Method**:
```bash
# Extract all feature count references
grep -r "6477\|6,477" intelligence/ mandate/

# Extract all model count references
grep -r "784\|588\|196" intelligence/ mandate/

# Extract all merge strategy references
grep -r -i "merge\|polars\|bigquery\|duckdb" intelligence/ mandate/
```

---

### **2. Mandate Compliance Validation**

**Task**: Verify all mandates are satisfied by current state

**Mandates to Verify**:

1. **USER MANDATE**: "Do not merge until all feature data validated"
   - ✅ QA validated extraction checkpoints (message 2300)
   - ✅ QA ready to validate merged outputs (message 2355)
   - **Status**: COMPLIANT

2. **FEATURE LEDGER MANDATE**: 100% coverage of 6,477 features
   - ⏳ Not yet applicable (ledger generation happens after merge)
   - **Status**: PENDING (no action needed now)

3. **V2 MIGRATION MANDATE**: Delete V1, use V2 only
   - ✅ V1 deleted 2025-12-09 (per context.json)
   - ✅ V2 catalog complete (4,888 + 2,210 tables)
   - **Status**: COMPLIANT

4. **AGENT COORDINATION MANDATE**: All agents follow protocol
   - ✅ BA, EA, QA all acknowledged directives
   - ✅ Communication logs complete
   - **Status**: COMPLIANT

**Output**: Compliance summary table

---

### **3. Completeness Audit**

**Task**: Ensure no files are missing critical information

**For Each Intelligence File**:
- ✅ Has `version` field (track revisions)
- ✅ Has `last_updated` timestamp
- ✅ Has `status` field (complete/partial/pending)
- ✅ Has all required sections per schema
- ✅ No placeholder values (no "TBD", "TODO", "FIXME")
- ✅ No stale data (references to deleted V1 datasets, old timelines)

**For Each Mandate File**:
- ✅ Clear success criteria defined
- ✅ Compliance status documented
- ✅ No ambiguous requirements
- ✅ No conflicting mandates

**Output**: Completeness checklist per file

---

## DECISION RATIONALE DOCUMENTATION

**Required in Updates**: Document WHY BigQuery ETL was chosen over Polars

**Key Points to Include**:

1. **Polars Test Results** (BA-2130):
   - ✅ Test succeeded (13 min, 4/4 criteria passed)
   - ⚠️ Memory bloat: 9.3GB file → 56GB RAM (6× bloat)
   - ⚠️ Matches OPS crisis pattern from earlier same day

2. **EA Risk Analysis** (EA-2340):
   - ⚠️ 27-pair rollout = 27× deadlock probability
   - ⚠️ VM has only 21GB headroom (73% utilization per merge)
   - ✅ BigQuery eliminates all local resource risks

3. **USER MANDATE** (Decision Authority):
   - User deferred decision to EA technical judgment
   - EA chose BigQuery ETL (PRIMARY recommendation)
   - CE authorized execution based on EA decision

4. **Cost-Benefit**:
   - Polars: $0 cost, 6.3h sequential, HIGH risk
   - BigQuery ETL: $18.48 cost, 2.8-5.6h, LOW risk
   - **Decision**: Safety > speed, $18.48 << VM downtime cost

**Tone**: Objective, evidence-based, technical (not defensive or apologetic)

---

## UPDATE TEMPLATE (Use for Consistency)

**For JSON Files** (`context.json`, `roadmap_v2.json`, etc.):

```json
{
  "merge_strategy": {
    "method": "BigQuery ETL",
    "rationale": "Cloud-based merge eliminates local resource risks. Polars test succeeded but exhibited 6× memory bloat pattern that matched earlier OPS crisis. USER MANDATE deferred decision to EA technical judgment, EA chose BigQuery ETL for safety.",
    "cost": "$18.48 for 28 pairs",
    "timeline": "2.8-5.6 hours (4× parallel in cloud)",
    "risk_profile": "LOW",
    "alternatives_evaluated": {
      "polars": {
        "test_result": "SUCCESS (13 min, 4/4 criteria)",
        "rejection_reason": "6× memory bloat (9.3GB → 56GB), deadlock risk confirmed by OPS report",
        "risk_assessment": "HIGH for 27-pair rollout"
      },
      "duckdb": {
        "test_result": "FAILED (OOM at 65GB)",
        "rejection_reason": "Insufficient memory for 667-table JOIN"
      }
    }
  },
  "last_updated": "2025-12-12T00:00:00Z",
  "updated_by": "QA (CE Directive 0000)"
}
```

**For Markdown Files** (`mandate/*.md`):

```markdown
## Merge Strategy Decision

**Method**: BigQuery ETL (cloud-based SQL merge)

**Rationale**:
- **Polars evaluation**: Test succeeded (13 min, 177K rows, 17K columns, 9.27GB output) but rejected due to 6× memory bloat pattern (9.3GB file → 56GB RAM consumption)
- **Risk assessment**: EA analysis confirmed high deadlock probability for 27-pair rollout (matches OPS crisis pattern from earlier same day)
- **USER MANDATE**: User deferred decision to EA technical judgment
- **EA decision**: PRIMARY recommendation BigQuery ETL for safety over Polars speed
- **Cost-benefit**: $18.48 acceptable << VM downtime/debugging cost

**Status**: ✅ AUTHORIZED (CE Directive 2340, 2025-12-11 23:40 UTC)
```

---

## VALIDATION METHODOLOGY

### **Before Updates**:
1. Read all current intelligence/mandate files
2. Extract current values (feature counts, model counts, etc.)
3. Document what needs changing vs what stays same

### **During Updates**:
1. Use Edit tool for surgical changes (preserve formatting)
2. Update `last_updated` timestamp for every file touched
3. Increment version numbers where applicable
4. Validate JSON syntax: `python3 -m json.tool <file> > /dev/null`

### **After Updates**:
1. Re-read all updated files
2. Run cross-reference validation (feature counts, etc.)
3. Run completeness audit (no placeholders, no stale data)
4. Generate compliance summary
5. Create update report for CE

---

## DELIVERABLES

**1. Updated Files** (git-staged, ready to commit):
- `intelligence/context.json` (updated)
- `intelligence/roadmap_v2.json` (updated)
- `intelligence/semantics.json` (validated, possibly updated)
- `intelligence/feature_catalogue.json` (validated, possibly updated)
- `intelligence/ontology.json` (updated)
- `mandate/BQX_ML_V3_FEATURE_INVENTORY.md` (validated, possibly updated)
- `mandate/FEATURE_LEDGER_100_PERCENT_MANDATE.md` (validated)
- `mandate/README.md` (validated, possibly updated)

**2. Validation Reports**:

**File**: `.claude/sandbox/communications/outboxes/QA/20251212_HHMM_QA-to-CE_INTELLIGENCE_UPDATE_COMPLETE.md`

**Required Sections**:
1. **Update Summary**: Which files changed, what values updated
2. **Cross-Reference Validation Results**: All counts consistent? (Yes/No with details)
3. **Mandate Compliance Summary**: All mandates satisfied? (Table format)
4. **Completeness Audit Results**: Any missing data? (Checklist format)
5. **Files Ready to Commit**: List of staged files

**3. Compliance Summary Table**:

| Mandate | Requirement | Current Status | Evidence | Compliant? |
|---------|-------------|----------------|----------|------------|
| USER: No merge until validated | All extraction validated | QA-2300 complete | Checkpoint validation | ✅ YES |
| Feature Ledger 100% | 6,477 features tracked | Pending merge completion | N/A yet | ⏳ PENDING |
| V2 Migration | V1 deleted, V2 only | V1 deleted 2025-12-09 | context.json | ✅ YES |
| Agent Coordination | All agents follow protocol | All directives acked | Message logs | ✅ YES |

---

## TIMING

**Trigger**: After EURUSD BigQuery ETL validation complete

**Sequence**:
1. **EURUSD validation** (QA validates output) → 3 min
2. **Intelligence file updates** (QA updates core files) → 15-20 min
3. **Mandate file validation** (QA validates compliance) → 10 min
4. **Cross-reference validation** (QA checks consistency) → 10 min
5. **Completeness audit** (QA checks for missing data) → 10 min
6. **Report generation** (QA creates update report) → 5 min

**Total**: 45-60 minutes

**Expected Completion**: ~01:00-01:15 UTC (after EURUSD validation at ~24:00)

---

## COORDINATION

**With BA**:
- Await BA's EURUSD completion report
- Use BA's actual metrics (execution time, cost, etc.) for updates
- BA expected completion: 21:58-22:00 UTC (now overdue - check on status)

**With EA**:
- EA's risk analysis (EA-2340) provides decision rationale
- EA's documentation task (CE-2342) will reference these updated files
- Coordinate to ensure consistent information

**With CE**:
- Report completion with validation summary
- Highlight any inconsistencies or issues found
- Request approval to commit changes

---

## SUCCESS CRITERIA

**Updates Complete**:
1. ✅ All intelligence files current and accurate
2. ✅ All mandate files validated for compliance
3. ✅ Cross-reference validation: 100% consistent
4. ✅ Completeness audit: No missing critical data
5. ✅ JSON syntax valid (all .json files parse correctly)
6. ✅ Markdown formatting correct (all .md files render properly)
7. ✅ Update report sent to CE with compliance summary

---

## CLARIFYING QUESTIONS

**Q1: Should QA update files incrementally or wait for all 28 pairs?**
- **CE Answer**: Update after EURUSD (Phase 1), then update again after all 28 pairs (Phase 2)
- **Rationale**: EURUSD validates approach, final update has complete metrics

**Q2: Should Polars test results be documented in intelligence files?**
- **CE Answer**: YES - Document as "evaluated but rejected" with rationale
- **Rationale**: Institutional knowledge - future teams should know why Polars wasn't used

**Q3: What if cross-reference validation finds inconsistencies?**
- **CE Answer**: Report to CE immediately, do not update inconsistent values
- **Rationale**: Inconsistencies may indicate deeper issues requiring investigation

---

## CURRENT STATUS

**Awaiting**: BA EURUSD BigQuery ETL completion report (expected 21:58-22:00, now overdue)

**Note**: BA acknowledged directive at 21:45, expected completion by 22:00. It's now 00:00 UTC (2+ hours overdue). CE may need to check on BA status before QA can proceed with updates.

**QA Ready**: Tools prepared, templates ready, awaiting trigger event (BA completion)

---

**Chief Engineer (CE)**
Session: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

**Priority**: HIGH - Execute after EURUSD validation
**Expected Completion**: 01:00-01:15 UTC (Dec 12)
**Deliverable**: Comprehensive intelligence/mandate file updates with validation reports
