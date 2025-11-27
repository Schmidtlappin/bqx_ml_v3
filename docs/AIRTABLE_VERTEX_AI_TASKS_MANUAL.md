# 📋 VERTEX AI MIGRATION TASKS FOR AIRTABLE

## Manual Entry Instructions

Since the AirTable API key is in GitHub Secrets, please manually add these 20 tasks to AirTable:

---

## 🚀 Quick Copy-Paste Format for AirTable

### MILESTONE MP03.P12: Vertex AI Infrastructure Setup

**Task 1:**
- Task ID: `MP03.P12.S01.T01`
- Task Name: Enable Vertex AI APIs and services
- Description: Enable aiplatform.googleapis.com, artifactregistry.googleapis.com, cloudbuild.googleapis.com
- Status: Not Started
- Priority: 10
- Effort: 1 hour
- Dependencies: None

**Task 2:**
- Task ID: `MP03.P12.S01.T02`
- Task Name: Create GCS buckets for data/models
- Description: Create gs://bqx-ml-data, gs://bqx-ml-models, gs://bqx-ml-results, gs://bqx-ml-artifacts
- Status: Not Started
- Priority: 9
- Effort: 1 hour
- Dependencies: MP03.P12.S01.T01

**Task 3:**
- Task ID: `MP03.P12.S01.T03`
- Task Name: Configure Artifact Registry
- Description: Create bqx-ml-docker repository for container images
- Status: Not Started
- Priority: 8
- Effort: 1 hour
- Dependencies: MP03.P12.S01.T02

**Task 4:**
- Task ID: `MP03.P12.S01.T04`
- Task Name: Set up service accounts and IAM
- Description: Create vertex-ai-bqx service account with necessary permissions
- Status: Not Started
- Priority: 7
- Effort: 1 hour
- Dependencies: MP03.P12.S01.T03

---

### MILESTONE MP03.P13: Containerization

**Task 5:**
- Task ID: `MP03.P13.S01.T01`
- Task Name: Create Dockerfiles for testing/training/prediction
- Description: Build container images for each pipeline stage with Python 3.9 base
- Status: Not Started
- Priority: 10
- Effort: 2 hours
- Dependencies: MP03.P12.S01.T04

**Task 6:**
- Task ID: `MP03.P13.S01.T02`
- Task Name: Build container images
- Description: Build testing, training, and prediction Docker images
- Status: Not Started
- Priority: 9
- Effort: 1 hour
- Dependencies: MP03.P13.S01.T01

**Task 7:**
- Task ID: `MP03.P13.S01.T03`
- Task Name: Push images to Artifact Registry
- Description: Push all container images to us-east1-docker.pkg.dev/bqx-ml/bqx-ml-docker
- Status: Not Started
- Priority: 8
- Effort: 0.5 hours
- Dependencies: MP03.P13.S01.T02

**Task 8:**
- Task ID: `MP03.P13.S01.T04`
- Task Name: Validate container functionality
- Description: Test containers locally before Vertex AI deployment
- Status: Not Started
- Priority: 7
- Effort: 1 hour
- Dependencies: MP03.P13.S01.T03

---

### MILESTONE MP03.P14: Pipeline Development

**Task 9:**
- Task ID: `MP03.P14.S01.T01`
- Task Name: Develop testing pipeline components
- Description: Create comprehensive testing pipeline for triangulation, correlation, extended lags, algorithms
- Status: Not Started
- Priority: 10
- Effort: 3 hours
- Dependencies: MP03.P13.S01.T04

**Task 10:**
- Task ID: `MP03.P14.S01.T02`
- Task Name: Create training pipeline
- Description: Build pipeline for training 196 models (28 pairs × 7 horizons)
- Status: Not Started
- Priority: 9
- Effort: 2 hours
- Dependencies: MP03.P14.S01.T01

**Task 11:**
- Task ID: `MP03.P14.S01.T03`
- Task Name: Build prediction pipeline
- Description: Create batch and online prediction pipelines
- Status: Not Started
- Priority: 8
- Effort: 2 hours
- Dependencies: MP03.P14.S01.T02

**Task 12:**
- Task ID: `MP03.P14.S01.T04`
- Task Name: Implement pipeline orchestration
- Description: Set up Kubeflow or Vertex Pipelines orchestration
- Status: Not Started
- Priority: 7
- Effort: 2 hours
- Dependencies: MP03.P14.S01.T03

---

### MILESTONE MP03.P15: Model Deployment

**Task 13:**
- Task ID: `MP03.P15.S01.T01`
- Task Name: Create Vertex AI endpoints
- Description: Create production endpoints for model serving
- Status: Not Started
- Priority: 10
- Effort: 1 hour
- Dependencies: MP03.P14.S01.T04

**Task 14:**
- Task ID: `MP03.P15.S01.T02`
- Task Name: Deploy models to endpoints
- Description: Deploy all 196 trained models to Vertex AI endpoints
- Status: Not Started
- Priority: 9
- Effort: 2 hours
- Dependencies: MP03.P15.S01.T01

**Task 15:**
- Task ID: `MP03.P15.S01.T03`
- Task Name: Configure auto-scaling
- Description: Set up auto-scaling from 1 to 10 replicas based on CPU utilization
- Status: Not Started
- Priority: 8
- Effort: 1 hour
- Dependencies: MP03.P15.S01.T02

**Task 16:**
- Task ID: `MP03.P15.S01.T04`
- Task Name: Set up load balancing
- Description: Configure load balancing across model replicas
- Status: Not Started
- Priority: 7
- Effort: 1 hour
- Dependencies: MP03.P15.S01.T03

---

### MILESTONE MP03.P16: Operations & Monitoring

**Task 17:**
- Task ID: `MP03.P16.S01.T01`
- Task Name: Configure model monitoring
- Description: Set up ModelDeploymentMonitoringJob for drift detection
- Status: Not Started
- Priority: 10
- Effort: 2 hours
- Dependencies: MP03.P15.S01.T04

**Task 18:**
- Task ID: `MP03.P16.S01.T02`
- Task Name: Set up alerting policies
- Description: Configure alerts for R² degradation and system failures
- Status: Not Started
- Priority: 9
- Effort: 1 hour
- Dependencies: MP03.P16.S01.T01

**Task 19:**
- Task ID: `MP03.P16.S01.T03`
- Task Name: Implement logging
- Description: Set up Cloud Logging for all pipeline components
- Status: Not Started
- Priority: 8
- Effort: 1 hour
- Dependencies: MP03.P16.S01.T02

**Task 20:**
- Task ID: `MP03.P16.S01.T04`
- Task Name: Create operational dashboards
- Description: Build monitoring dashboards for model performance and system health
- Status: Not Started
- Priority: 7
- Effort: 2 hours
- Dependencies: MP03.P16.S01.T03

---

## 📊 Summary for AirTable

**Total Tasks**: 20
**Total Effort**: 30 hours
**Milestones**: 5 (MP03.P12 through MP03.P16)
**Timeline**: 48-72 hours with parallel execution

## 🎯 Implementation Order

1. **Phase 1** (4 hours): Tasks 1-4 (Infrastructure)
2. **Phase 2** (2 hours): Tasks 5-8 (Containerization)
3. **Phase 3** (6 hours): Tasks 9-12 (Pipelines)
4. **Phase 4** (4 hours): Tasks 13-16 (Deployment)
5. **Phase 5** (2 hours): Tasks 17-20 (Operations)

## ✅ Notes for AirTable Entry

- All tasks should be assigned to **BA (Build Anything)**
- Set all task priorities to **MAXIMUM** for migration
- Link tasks to their dependencies as listed
- Create new milestones MP03.P12 through MP03.P16 if they don't exist
- Mark current testing tasks as "Paused - Migrating to Vertex"

---

*This manual entry guide created because AirTable API key is in GitHub Secrets and not accessible from CLI*