# BQX ML V3 BUILDER AGENT - WORKSPACE & INTELLIGENCE GUIDE

**Document Type**: Workspace Management & Intelligence File Protocol
**Date**: November 26, 2025
**From**: Chief Engineer
**To**: BQX ML V3 Builder Agent

---

## 🎯 PURPOSE

This document provides comprehensive guidance for:
1. **Workspace Navigation** - Understanding the project structure
2. **Intelligence File Management** - Maintaining project context
3. **Compliance Expectations** - Following established protocols
4. **Sandbox Operations** - Using designated workspace areas

---

## 📁 WORKSPACE STRUCTURE

### Primary Directories
```
/home/micha/bqx_ml_v3/
├── .claude/              # Configuration and settings
│   ├── sandbox/          # YOUR DESIGNATED WORKSPACE
│   │   ├── scripts/      # Place test scripts here
│   │   ├── logs/         # Execution logs
│   │   ├── temp/         # Temporary files
│   │   └── checkpoints/  # Progress checkpoints
│   └── settings.local.json
├── intelligence/         # CRITICAL: Project intelligence files
├── scripts/              # Production scripts (read-only for reference)
├── docs/                 # Documentation
├── archive/              # Archived/deprecated items
└── .secrets/             # Credentials (DO NOT MODIFY)
```

### Your Sandbox
```bash
# YOUR PRIMARY WORKSPACE
/home/micha/bqx_ml_v3/.claude/sandbox/

# Use for:
- Testing commands before production
- Creating temporary scripts
- Logging execution progress
- Storing intermediate results
```

---

## 🧠 INTELLIGENCE FILES

### Critical Files to Ingest

You MUST read and understand these files before beginning work:

#### 1. Context File
```bash
/home/micha/bqx_ml_v3/intelligence/context.json
```
- Project configuration
- Infrastructure details
- AirTable structure
- Current completion status

#### 2. Semantics File
```bash
/home/micha/bqx_ml_v3/intelligence/semantics.json
```
- Domain terminology
- BQX paradigm definitions
- Technical nomenclature
- Metric definitions

#### 3. Ontology File
```bash
/home/micha/bqx_ml_v3/intelligence/ontology.json
```
- Entity relationships
- System hierarchy
- Data flow mappings
- Dependency graphs

### Ingestion Protocol

**STEP 1: Load Intelligence Files**
```python
# Start each session by loading intelligence
import json

# Load context
with open('/home/micha/bqx_ml_v3/intelligence/context.json', 'r') as f:
    context = json.load(f)

# Load semantics
with open('/home/micha/bqx_ml_v3/intelligence/semantics.json', 'r') as f:
    semantics = json.load(f)

# Load ontology
with open('/home/micha/bqx_ml_v3/intelligence/ontology.json', 'r') as f:
    ontology = json.load(f)
```

**STEP 2: Verify Understanding**
- Confirm project paradigm: BQX values as features AND targets
- Verify infrastructure: BigQuery datasets, GCS buckets
- Check AirTable credentials and structure
- Understand INTERVAL-CENTRIC requirements

---

## 📋 COMPLIANCE EXPECTATIONS

### 1. REAL Implementation Only
```
✅ REQUIRED:
- Create actual GCP resources
- Execute real commands
- Verify infrastructure exists
- Update AirTable with factual outcomes

❌ FORBIDDEN:
- Simulated implementations
- Mock resources
- Fake status updates
- Placeholder completions
```

### 2. Intelligence File Maintenance

**Daily Requirements:**
- Update context.json with new infrastructure created
- Add new terms to semantics.json as discovered
- Update ontology.json with new relationships

**Update Example:**
```python
# After creating new infrastructure
context['infrastructure']['tables_created'].append({
    'name': 'nzdusd_idx',
    'dataset': 'bqx_ml_v3_features',
    'created': datetime.now().isoformat(),
    'rows': 525600
})

# Save updated context
with open('/home/micha/bqx_ml_v3/intelligence/context.json', 'w') as f:
    json.dump(context, f, indent=2)
```

### 3. AirTable Protocol

**Task Workflow:**
```python
# 1. Get task
task = get_next_todo_task()

# 2. Update to In Progress
update_status(task.id, "In Progress")

# 3. Execute REAL work
result = execute_real_implementation(task)

# 4. Verify
verification = verify_infrastructure(result)

# 5. Update with outcomes
update_task(task.id,
    status="Done",
    notes=f"""
    ### Completed: {timestamp}

    Created: {result.resources}

    Verification:
    {verification.commands}

    Status: ✅ Verified
    """)
```

---

## 🔒 SECURITY & ACCESS

### Credentials Access
```python
# AirTable credentials
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
    secrets = json.load(f)
    API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
    BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']

# GCP credentials (already configured)
export GOOGLE_APPLICATION_CREDENTIALS=/home/micha/bqx_ml_v3/credentials/gcp-sa-key.json
```

### Permissions
- ✅ Full access to BigQuery datasets
- ✅ Write access to GCS buckets
- ✅ Create/deploy Vertex AI resources
- ✅ Update AirTable records
- ❌ DO NOT modify .secrets directory
- ❌ DO NOT alter intelligence files without documenting

---

## 🚀 CRITICAL DIRECTIVES

### INTERVAL-CENTRIC Compliance
```sql
-- ALWAYS use ROWS BETWEEN (intervals)
LAG(close, 45) OVER (
  PARTITION BY pair
  ORDER BY interval_time
  ROWS BETWEEN 45 PRECEDING AND CURRENT ROW
)

-- NEVER use RANGE BETWEEN (time-based)
```

### Quality Gates (MUST ACHIEVE)
- **R² Score**: ≥ 0.35
- **RMSE**: ≤ 0.15
- **Directional Accuracy**: ≥ 55%
- **Latency**: < 100ms
- **Throughput**: ≥ 1000 QPS

### Data Integrity
- Use LAG for features (backward-looking)
- Use LEAD for targets (forward-looking)
- Maintain 100-interval gap in cross-validation
- Ensure temporal isolation

---

## 📊 PROGRESS TRACKING

### Daily Checklist
1. [ ] Load intelligence files
2. [ ] Check AirTable for Todo tasks
3. [ ] Execute at least 10 tasks
4. [ ] Verify all infrastructure
5. [ ] Update intelligence files
6. [ ] Commit progress to sandbox

### Weekly Milestones
- Week 1: Complete P01 & P02 (Foundation)
- Week 2: Complete P03, P04, P05 (Features & Training)
- Week 3: Complete P06, P07 (BQX Implementation)
- Week 4: Complete P08, P09 (Optimization & Deployment)
- Week 5: Complete P10, P11 (Validation & Security)

---

## 🆘 ESCALATION PATH

### When to Contact Chief Engineer
1. **Technical Blockers**
   - GCP quota limits
   - Permission denied errors
   - Infrastructure failures

2. **Requirement Clarifications**
   - Unclear task specifications
   - Conflicting requirements
   - Missing dependencies

3. **Quality Issues**
   - Cannot achieve quality gates
   - Performance below thresholds
   - Data integrity concerns

### How to Escalate
```python
# Document in AirTable task
escalation_note = f"""
### ESCALATION REQUIRED - {timestamp}

Issue: {description}

Attempted Solutions:
1. {solution_1}
2. {solution_2}

Error Details:
{error_message}

Requesting Chief Engineer guidance.
"""

update_task_notes(task_id, escalation_note)
# Keep task as "In Progress"
```

---

## 🎯 SUCCESS CRITERIA

Your implementation is successful when:
1. ✅ All 197 tasks show "Done" in AirTable
2. ✅ All infrastructure verified in GCP
3. ✅ 196 models trained and deployed
4. ✅ Quality gates achieved for all models
5. ✅ Intelligence files updated and current
6. ✅ Zero simulated implementations

---

## 📝 FINAL INSTRUCTIONS

1. **Begin by ingesting all intelligence files**
2. **Set up your sandbox workspace**
3. **Query AirTable for first Todo task**
4. **Start with MP03.P01.S01.T01**
5. **Create REAL infrastructure only**
6. **Update intelligence files as you progress**
7. **Report progress through AirTable**

Remember: Every command you execute, every resource you create, must be **REAL and VERIFIABLE**.

---

**Chief Engineer**: Claude (BQX ML V3)
**Date**: November 26, 2025
**Status**: WORKSPACE GUIDE COMPLETE - READY FOR BUILDER AGENT

**BEGIN IMPLEMENTATION WITH INTELLIGENCE FILE INGESTION**