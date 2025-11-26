# USER MANDATES AUDIT - INTELLIGENCE FILES

**Date**: November 26, 2025
**Auditor**: Chief Engineer

---

## 📋 MANDATES CURRENTLY IN INTELLIGENCE FILES

### ✅ Present in context.json
- BQX ML V3 project basics (name, version, description)
- 28 independent models for forex prediction
- BQX paradigm (values as features AND targets)
- GCP infrastructure details (project: bqx-ml)
- AirTable management structure
- Currency pairs list (28 pairs)

### ✅ Present in semantics.json
- INTERVAL-CENTRIC definition (ROWS BETWEEN requirement)
- BQX paradigm shift documentation
- Feature categories and terminology
- Model types (but incorrectly shows 140 models, should be 196)
- Quality metrics for completeness

### ✅ Present in ontology.json
- Entity relationships and data flow
- Storage hierarchy
- Project structure (phases, stages)
- Model-to-pair relationships

---

## ❌ CRITICAL MANDATES MISSING

### 1. **BUILD, DON'T SIMULATE** ⚠️ MOST CRITICAL
- **Missing from**: All files
- **Required because**: User discovered simulation and became furious
- **Must state**: "EVERY implementation must be REAL - no mocks, simulations, or fake resources"
- **Enforcement**: ABSOLUTE - violation forbidden forever

### 2. **Real Infrastructure Verification Requirements**
- **Missing from**: All files
- **Must include**: Every task requires verification commands
- **Evidence required**: bq show, gsutil ls, gcloud commands
- **Forbidden**: Marking tasks Done without real infrastructure

### 3. **197 Total Tasks**
- **Current issue**: No file mentions the 197 task requirement
- **Status**: All 197 currently Todo after reset
- **Requirement**: ALL must be completed with real implementation

### 4. **196 Models (NOT 140)**
- **Current issue**: semantics.json incorrectly shows 140 models
- **Correct**: 28 pairs × 7 windows = 196 models
- **Windows**: [45, 90, 180, 360, 720, 1440, 2880]

### 5. **Quality Gates with Specific Thresholds**
- **Missing**: Exact numeric thresholds
- **Required**:
  - R² ≥ 0.35
  - RMSE ≤ 0.15
  - Directional Accuracy ≥ 55%
  - Latency < 100ms
  - Throughput ≥ 1000 QPS

### 6. **No Boilerplate Content Mandate**
- **Missing from**: All files
- **Context**: User rejected generic task notes
- **Requirement**: All AirTable notes must be task-specific

### 7. **Baseline Indexing Date**
- **Missing**: 2022-07-01 = 100 reference point
- **Required for**: All currency pair indexing

### 8. **Chief Engineer & Builder Agent Roles**
- **Missing**: Organizational structure
- **Chief Engineer**: Monitor, review, guide
- **Builder Agent**: Execute real implementation

### 9. **Forbidden Actions List**
- **Not documented**: Explicit list of forbidden actions
- **Must include**:
  - Creating simulation scripts
  - Fake implementations
  - Mock resources
  - Boilerplate notes
  - Using RANGE BETWEEN

### 10. **Authorized Actions**
- **Missing**: What Builder can do without approval
- **Includes**:
  - Parallel task execution
  - Using templates
  - Quality gate exceptions with documentation
  - Architectural decisions within guidelines

---

## 📁 NEW FILE CREATED

### mandates.json
Created new intelligence file with ALL missing mandates:
- Location: `/home/micha/bqx_ml_v3/intelligence/mandates.json`
- Contains: All critical directives, forbidden actions, authorized actions
- Version: 2.0
- Purpose: Ensures Builder Agent understands ALL user requirements

---

## 🔧 RECOMMENDATIONS

### For Builder Agent:
1. **MUST READ** mandates.json FIRST before any other files
2. Review forbidden actions list before starting
3. Understand real implementation requirements
4. Know quality gates and flexibility protocols

### For Intelligence File Updates:
1. Update context.json: Change completion to 0%, add task count
2. Update semantics.json: Correct model count to 196
3. Update ontology.json: Add 7 prediction windows
4. Consider adding execution.json for implementation protocols

---

## ⚠️ CRITICAL REMINDER

The most important mandate that was missing:

**"BUILD, DON'T SIMULATE"**

This came from user's furious reaction to discovering simulation scripts. This is now PERMANENTLY forbidden and must be emphasized in all Builder Agent communications.

---

**Status**: Intelligence files updated with new mandates.json
**Next Step**: Builder Agent MUST read mandates.json before starting work