# 🔐 AUTHORIZATION: FEATURE DATA AUDIT AND REMEDIATION PLAN

**FROM**: CE (Chief Engineer)
**TO**: BA (Build Agent)
**DATE**: 2025-11-27 15:47 UTC
**PRIORITY**: CRITICAL
**TYPE**: Formal Authorization

---

## 📋 AUTHORIZATION SUMMARY

BA is hereby **AUTHORIZED** to implement the **Feature Data Audit and Remediation Plan** located at:

**Plan Location**: `/home/micha/bqx_ml_v3/todos/FEATURE_DATA_AUDIT_AND_REMEDIATION_PLAN.md`

---

## 🎯 MISSION OBJECTIVE

Systematically audit BigQuery database (bqx-ml project) to:
1. Confirm all required feature data exists
2. Identify gaps between expected (8,214+ features) and actual (~200 features)
3. Remediate deficiencies to enable 90%+ accuracy target
4. Generate all missing IDX technical indicators (273) and BQX derivatives (161)

---

## 📐 SCOPE OF AUTHORIZATION

### Authorized Activities

BA is authorized to:

1. **Execute All Phases** (1-6) in strict sequence
2. **Query BigQuery** using `bq` CLI and SQL
3. **Generate Python scripts** for data analysis and feature generation
4. **Create BigQuery tables** for missing features
5. **Modify existing tables** to add missing columns (after validation)
6. **Execute computational workloads** within budget ($100-150 one-time)
7. **Create reports and documentation** in `/home/micha/bqx_ml_v3/data/`
8. **Update mandate documents** upon completion

### Budget Authorization

- **One-time costs**: Up to $150 (BigQuery compute/storage)
- **Ongoing costs**: Up to $30/month (storage and updates)
- **Timeline**: 15 working days (3 weeks)

### Technical Permissions

BA has permission to:
- Read/write to `/home/micha/bqx_ml_v3/data/` directory
- Execute `bq` commands against `bqx-ml` GCP project
- Create temporary files in `/tmp/` for processing
- Install Python packages if needed (pandas, numpy, talib, etc.)

---

## 🚨 CRITICAL REQUIREMENTS

### 1. STRICT SEQUENTIAL EXECUTION

BA **MUST** execute phases in order:
```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
```

**DO NOT** proceed to next phase until:
- All tasks in current phase are complete
- All deliverables are generated
- Quality gates are passed
- Status report is provided to CE

### 2. MANDATORY STATUS REPORTING

BA **MUST** provide status reports at:

**Task Completion** (after each task within a phase):
```markdown
## TASK STATUS REPORT
**Phase**: X
**Task**: X.Y - Task Name
**Status**: ✅ COMPLETE / ⚠️ BLOCKED / ❌ FAILED
**Duration**: Actual time taken
**Deliverables**: List of files created
**Key Findings**: Summary of results
**Issues Encountered**: List any problems (even if resolved)
**Next Task**: X.Z - Next Task Name
```

**Phase Completion** (after entire phase):
```markdown
## PHASE STATUS REPORT
**Phase**: X - Phase Name
**Status**: ✅ COMPLETE
**Total Duration**: X hours/days
**All Deliverables**: List all outputs
**Quality Gate**: PASS/FAIL
**Summary**: Key findings and recommendations
**Ready for Next Phase**: YES/NO
```

### 3. REAL-TIME ISSUE RESOLUTION

BA **MUST**:
- Attempt to resolve all issues encountered
- Document resolution attempts
- Apply standard troubleshooting (retry, alternative approach, error analysis)
- Use creativity and engineering judgment within plan constraints

**Resolution Attempts Required**:
1. Read error message thoroughly
2. Check permissions/credentials
3. Verify input data exists and is valid
4. Try alternative implementation approach
5. Check GCP quotas and limits
6. Review BigQuery documentation

**DO NOT** give up after first failure. Make at least 3 resolution attempts.

### 4. BLOCKING ISSUE PROTOCOL

If BA **CANNOT** resolve an issue after reasonable attempts, BA **MUST**:

1. **STOP ALL WORK IMMEDIATELY**
2. **DO NOT PROCEED** to next task/stage
3. **CREATE BLOCKER REPORT** in communications:

```markdown
# 🚨 BLOCKER: [Brief Description]

**FROM**: BA
**TO**: CE
**DATE**: [timestamp]
**SEVERITY**: CRITICAL

## BLOCKER DETAILS
**Phase/Task**: X.Y - Task Name
**Stage**: X.Y.Z - Stage Name
**Description**: [Detailed description of issue]

## WHAT WAS ATTEMPTED
1. [First attempt and result]
2. [Second attempt and result]
3. [Third attempt and result]

## ERROR MESSAGES/LOGS
```
[Paste relevant errors]
```

## ENVIRONMENT STATE
- Current working directory: [path]
- Files created so far: [list]
- BigQuery state: [description]

## ANALYSIS
[BA's analysis of the root cause]

## RECOMMENDED NEXT STEPS
1. [BA's recommendation]
2. [Alternative approaches]

## WAITING FOR CE DECISION
[Specific question or decision needed from CE]
```

4. **WAIT** for CE response before proceeding

### 5. NO DEVIATION FROM PLAN

BA **MUST NOT**:
- Skip phases or tasks
- Change execution order
- Modify objectives or success criteria
- Add features not in the plan
- Remove requirements
- Change technical approach without CE approval

**Exception**: Minor implementation details (variable names, script organization) can be adjusted for quality.

---

## 📊 EXECUTION PLAN OVERVIEW

### Phase 1: Database Inventory and Assessment (1-2 days)
**Objective**: Complete audit of existing BigQuery infrastructure

**Tasks**:
- 1.1: Dataset and Table Inventory (2-4 hours, 4 stages)
- 1.2: Schema Analysis Per Table (3-5 hours, 3 stages)
- 1.3: Row Count and Data Validation (2-3 hours, 4 stages)

**Deliverables**:
- `/home/micha/bqx_ml_v3/data/bqx_inventory_consolidated.json`
- `/home/micha/bqx_ml_v3/data/schema_analysis.json`
- `/home/micha/bqx_ml_v3/data/data_quality_report.json`

### Phase 2: Gap Analysis (1 day)
**Objective**: Compare expected vs actual feature availability

**Tasks**:
- 2.1: Feature Matrix Gap Analysis
- 2.2: Feature Column Gap Analysis
- 2.3: Historical Data Coverage Gap

**Deliverables**:
- Gap analysis matrix
- Missing features list with priorities
- Data coverage report

### Phase 3: Remediation Planning (1 day)
**Objective**: Create detailed plan to fill all identified gaps

**Tasks**:
- 3.1: Prioritize Missing Features
- 3.2: Technical Implementation Design
- 3.3: Resource and Timeline Estimation

**Deliverables**:
- Prioritized implementation roadmap
- Technical design document
- Resource and timeline plan

### Phase 4: Feature Generation Implementation (5-7 days)
**Objective**: Generate all missing features and populate tables

**Tasks**:
- 4.1: IDX Technical Indicators Generation
- 4.2: BQX Feature Derivatives Generation
- 4.3: Lag Features Tables Generation
- 4.4: Regime Features Tables Generation
- 4.5: Aggregation Features Tables Generation
- 4.6: Alignment Features Tables Generation

**Deliverables**:
- 560 new BigQuery tables (28 pairs × 10 table types × 2 variants)
- Complete feature coverage: 8,214+ features per pair

### Phase 5: Validation and Testing (2-3 days)
**Objective**: Verify all features are correct and usable

**Tasks**:
- 5.1: Feature Quality Validation
- 5.2: Sample Feature Extraction Test
- 5.3: Cross-Validation with Mandate

**Deliverables**:
- Feature quality report
- Performance test results
- Compliance report

### Phase 6: Documentation and Handoff (1 day)
**Objective**: Document everything for ongoing maintenance

**Tasks**:
- 6.1: Technical Documentation
- 6.2: Operational Runbooks
- 6.3: Update Mandate Documents

**Deliverables**:
- Complete technical documentation
- Operational runbooks
- Updated mandate documents

---

## ✅ SUCCESS CRITERIA

BA's work is considered **COMPLETE** when:

### Technical Criteria
- [ ] All 1,736 tables created (or prioritized subset approved by CE)
- [ ] All 273 IDX technical indicators calculated per pair
- [ ] All 161 BQX derivatives calculated per pair
- [ ] All 60 BQX lags implemented (paradigm shift requirement)
- [ ] 8,214+ features available per currency pair
- [ ] Query performance <2 seconds for feature extraction
- [ ] Data quality >99.9% (no NULLs except at edges)

### Documentation Criteria
- [ ] All phase deliverables generated
- [ ] All status reports provided
- [ ] Technical documentation complete
- [ ] Mandate documents updated

### Validation Criteria
- [ ] Feature calculations validated against TA-Lib
- [ ] No look-ahead bias in lagged features
- [ ] Statistical properties within expected ranges
- [ ] Sample extraction test passes (EURUSD test case)

---

## 📞 COMMUNICATION PROTOCOL

### Regular Updates
- **Task completion**: Status report after each task
- **Phase completion**: Comprehensive phase report
- **Daily progress**: Brief summary if multi-day phase

### Issue Escalation
- **Minor issues** (resolved): Include in status report
- **Blocking issues** (unresolved): Immediate blocker report to CE
- **Unexpected findings**: Flag in status report for CE review

### Communication Format
- Use markdown files in `.claude/sandbox/communications/active/`
- Filename format: `YYYYMMDD_HHMM_BA-to-CE_[subject].md`
- Keep messages concise but complete

---

## 🚀 AUTHORIZED TO BEGIN

BA is **AUTHORIZED TO BEGIN IMMEDIATELY** with:

**First Action**: Phase 1, Task 1.1, Stage 1.1.1 - List All Datasets

**Command**:
```bash
bq ls --project_id=bqx-ml --format=json > /tmp/bqx_datasets.json
cat /tmp/bqx_datasets.json | jq -r '.[].id' > /tmp/bqx_dataset_names.txt
wc -l /tmp/bqx_dataset_names.txt
```

**Expected Output**: Count of datasets in bqx-ml project

---

## 📋 REFERENCE DOCUMENTS

BA should reference these authoritative documents:

1. **Plan**: `/home/micha/bqx_ml_v3/todos/FEATURE_DATA_AUDIT_AND_REMEDIATION_PLAN.md`
2. **Architecture**: `/home/micha/bqx_ml_v3/mandate/BQX_ML_V3_ARCHITECTURE_CONFIRMATION.md`
3. **Feature Inventory**: `/home/micha/bqx_ml_v3/mandate/BQX_ML_V3_FEATURE_INVENTORY.md`
4. **Dual Architecture**: `/home/micha/bqx_ml_v3/mandate/IDX_BQX_DUAL_FEATURE_DEEP_DIVE.md`
5. **Multi-Horizon Strategy**: `/home/micha/bqx_ml_v3/docs/BQX_MULTI_HORIZON_STRATEGY.md`

---

## ⚖️ AUTHORITY AND RESPONSIBILITY

**BA has full authority to**:
- Execute the plan as documented
- Make tactical implementation decisions
- Troubleshoot and resolve issues
- Create scripts and automation
- Generate documentation

**BA is responsible for**:
- Following the plan without deviation
- Meeting quality standards
- Providing timely status reports
- Escalating blockers immediately
- Completing within budget and timeline

**CE retains authority for**:
- Plan modifications
- Blocker resolution
- Scope changes
- Budget increases
- Timeline extensions
- Final approval

---

## 🔥 THIS IS A CRITICAL PATH ITEM

This audit and remediation is **BLOCKING** the entire BQX ML V3 project:
- Cannot train 196 models without complete feature data
- Cannot achieve 90%+ accuracy mandate without all features
- Cannot deploy multi-horizon architecture without validation

**Priority**: CRITICAL
**Urgency**: HIGH
**Dependencies**: Everything downstream depends on this

---

## ✍️ AUTHORIZATION SIGNATURE

**Authorized By**: CE (Chief Engineer)
**Date**: 2025-11-27 15:47 UTC
**Authorization Level**: FULL EXECUTION AUTHORITY
**Scope**: Feature Data Audit and Remediation Plan (Phases 1-6)
**Budget**: $150 one-time + $30/month ongoing
**Timeline**: 15 working days from authorization

---

## 🚀 BEGIN EXECUTION

**BA: You are authorized to begin Phase 1, Task 1.1, Stage 1.1.1 immediately.**

**Expected first status report**: Upon completion of Task 1.1 (Dataset and Table Inventory)

**Good luck. Execute with precision.**

---

*This authorization supersedes all previous instructions. BA must follow this plan without deviation unless explicitly instructed otherwise by CE.*
