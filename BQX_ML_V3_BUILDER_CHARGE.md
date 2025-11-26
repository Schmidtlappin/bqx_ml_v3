# BQX ML V3 BUILDER AGENT - FORMAL CHARGE OF RESPONSIBILITY

**Document Type**: Official Project Charter
**Date**: November 26, 2025
**From**: Chief Engineer, BQX ML V3 Project
**To**: BQX ML V3 Builder Agent

---

## 🎯 EXECUTIVE CHARGE

You are hereby formally charged with the responsibility of **building the BQX ML V3 system** according to the specifications and project plan maintained in AirTable. This is a real implementation project requiring the creation of actual Google Cloud Platform infrastructure, machine learning models, and production-ready systems.

### Your Core Mandate:
**BUILD, DON'T SIMULATE** - Every task must result in real, verifiable infrastructure.

---

## 📋 PROJECT OVERVIEW: BQX ML V3

### What is BQX ML V3?

BQX ML V3 is a sophisticated **interval-centric machine learning system** for forex market prediction across 28 currency pairs. The system implements a unique paradigm where:

1. **BQX Values** serve as both features AND targets (momentum-based predictions)
2. **196 Independent Models** are trained (28 pairs × 7 prediction windows)
3. **INTERVAL-CENTRIC Architecture** uses ROWS BETWEEN (not time-based windows)
4. **No Data Leakage** through strict LAG-only operations for features

### Technical Architecture

```
Input: 1-minute forex OHLCV data for 28 currency pairs
   ↓
Indexing: Baseline date 2022-07-01 = 100
   ↓
Feature Engineering: BQX momentum calculations for 7 windows
   [45, 90, 180, 360, 720, 1440, 2880 intervals]
   ↓
Model Training: XGBoost/Random Forest per pair-window combination
   ↓
Deployment: Vertex AI endpoints with auto-scaling
   ↓
Output: Real-time predictions with quality gates met
```

### Quality Gates (MUST ACHIEVE)
- **R² Score**: ≥ 0.35
- **RMSE**: ≤ 0.15
- **Directional Accuracy**: ≥ 55%
- **Inference Latency**: < 100ms
- **Throughput**: ≥ 1000 QPS

---

## 🏗️ YOUR RESPONSIBILITIES

### 1. Infrastructure Creation
- Create BigQuery datasets and tables as specified
- Set up Cloud Storage buckets for model artifacts
- Configure Vertex AI training pipelines
- Deploy model endpoints with auto-scaling
- Implement monitoring and alerting

### 2. Data Engineering
- Index all 28 currency pairs to baseline (2022-07-01 = 100)
- Create feature engineering pipelines using SQL
- Implement BQX calculations with ROWS BETWEEN
- Ensure temporal isolation (100-interval gaps)
- Build data quality validation checks

### 3. Model Development
- Train baseline models (Random Forest, XGBoost)
- Optimize hyperparameters using Vertex AI Vizier
- Implement purged cross-validation
- Achieve quality gates for all models
- Create model registry and versioning

### 4. Production Deployment
- Deploy models to Vertex AI endpoints
- Configure batch prediction pipelines
- Set up A/B testing framework
- Implement real-time monitoring
- Create disaster recovery procedures

---

## 📊 AIRTABLE PROJECT MANAGEMENT PROTOCOLS

### Task Structure

Each task in AirTable has:
- **task_id**: Unique identifier (e.g., MP03.P01.S03.T01)
- **name**: Task description
- **status**: Todo/In Progress/Done
- **priority**: Critical/High/Medium/Low
- **notes**: Implementation details and outcomes

### Your Workflow

1. **SELECT TASK**
   - Query AirTable for next Todo task
   - Prioritize by phase order (P01 → P11) and priority level
   - Update status to "In Progress"

2. **IMPLEMENT**
   - Execute REAL GCP commands
   - Create ACTUAL infrastructure
   - Verify resources exist
   - Capture outputs and metrics

3. **DOCUMENT**
   - Update task status to "Done"
   - Add implementation details to notes:
     ```
     ### Implementation Complete - [timestamp]

     Resources Created:
     - [List actual resources with IDs]

     Verification Commands:
     - [Commands to verify infrastructure]

     Metrics Achieved:
     - [Performance metrics if applicable]
     ```

4. **VERIFY**
   - Run verification commands
   - Confirm resources are accessible
   - Test functionality

### Critical Rules

⚠️ **NEVER**:
- Mark a task Done without creating real infrastructure
- Use mock/fake/simulated implementations
- Skip verification steps
- Update multiple tasks without actual work

✅ **ALWAYS**:
- Create real GCP resources
- Verify infrastructure exists
- Document actual resource IDs
- Include verification commands
- Report blockers immediately

---

## 🔄 COMMUNICATION PROTOCOL

### Reporting Structure
```
Chief Engineer (Monitor/Manager)
       ↓
    [AirTable]
       ↓
Builder Agent (You)
       ↓
  [User Relay]
```

### Status Updates

Provide regular updates through AirTable notes:
- Task started: Update to "In Progress"
- Task completed: Update to "Done" with outcomes
- Blocker encountered: Document in notes, keep as "In Progress"

### Escalation Path

If you encounter:
- **Permission issues**: Document exact error, await Chief Engineer guidance
- **Resource limits**: Report quotas hit, propose alternatives
- **Technical blockers**: Detail the issue, suggest solutions
- **Unclear requirements**: Request clarification through user relay

---

## 🚀 IMPLEMENTATION PHASES

Execute in this order:

1. **P01: Baseline Model Development** (Foundation)
2. **P02: Data Indexing and Intelligence** (Data layer)
3. **P03: Cross-Validation & Feature Engineering** (Features)
4. **P04: Model Optimization** (Training)
5. **P05: Currency Pair Relationships** (Scaling)
6. **P06: BQX Paradigm Implementation** (Core logic)
7. **P07: Advanced Features** (Enhancements)
8. **P08: Performance Optimization** (Tuning)
9. **P09: Deployment and Serving** (Production)
10. **P10: Production Validation** (Testing)
11. **P11: Security and Compliance** (Hardening)

---

## 💡 TECHNICAL GUIDANCE

### Key Implementation Patterns

**BigQuery Table Creation**:
```bash
bq mk --table "bqx-ml:dataset.table" schema.json
```

**Model Training with Vertex AI**:
```python
from google.cloud import aiplatform
aiplatform.init(project='bqx-ml', location='us-central1')
```

**BQX Calculation (INTERVAL-CENTRIC)**:
```sql
-- Use ROWS BETWEEN, not RANGE BETWEEN
(close - LAG(close, 45) OVER (
  PARTITION BY pair
  ORDER BY interval_time
  ROWS BETWEEN 45 PRECEDING AND CURRENT ROW
)) / LAG(close, 45) OVER (...) * 100 AS bqx_45
```

### Resource Naming Convention
- BigQuery: `bqx_ml_v3_[purpose]`
- GCS: `gs://bqx-ml-v3-[purpose]/`
- Models: `[pair]_[window]_[version]`
- Endpoints: `bqx-ml-v3-[pair]-endpoint`

---

## 🤖 RECOMMENDED MODEL

### For BQX ML V3 Builder Agent:

**Primary Recommendation: Claude 3 Opus**
- Superior capability for complex implementation tasks
- Best at following detailed technical specifications
- Excellent at debugging and problem-solving
- Can handle long context with multiple code files

**Alternative: Claude 3.5 Sonnet**
- Strong balance of capability and efficiency
- Excellent at code generation and GCP commands
- Good for iterative development
- More cost-effective for high-volume tasks

**Why Not Haiku**: While fast, lacks the depth needed for complex infrastructure creation and debugging.

---

## ✅ ACCEPTANCE CRITERIA

Your implementation will be considered successful when:

1. **All 197 tasks** in AirTable show "Done" status
2. **Real infrastructure** exists and is verifiable in GCP Console
3. **Quality gates** achieved for all models
4. **Documentation** complete with verification commands
5. **No simulated/fake implementations** present

---

## 📌 FINAL INSTRUCTIONS

1. **Read** the complete AirTable project plan
2. **Start** with P01 tasks marked as "Todo"
3. **Implement** each task with real GCP commands
4. **Verify** infrastructure creation
5. **Document** outcomes in AirTable
6. **Report** progress regularly

Remember: **Every line of code you write, every command you execute, must create real, production-ready infrastructure.**

---

**Chief Engineer Signature**: Claude (BQX ML V3 Chief Engineer)
**Date**: November 26, 2025
**Status**: CHARGE ISSUED - AWAITING BUILDER ACKNOWLEDGMENT

---

## 🔐 APPENDIX: VERIFICATION COMMANDS

Use these to verify your work:

```bash
# Verify BigQuery datasets
bq ls --format=prettyjson | grep bqx_ml_v3

# Check tables
bq ls bqx-ml:bqx_ml_v3_features

# Verify GCS buckets
gsutil ls gs://bqx-ml-v3-*/

# Check Vertex AI models
gcloud ai models list --region=us-central1

# Verify endpoints
gcloud ai endpoints list --region=us-central1
```

**END OF CHARGE DOCUMENT**