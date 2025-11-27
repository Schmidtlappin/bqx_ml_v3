# 🚀 VERTEX AI MIGRATION AND DEPLOYMENT PLAN

## Executive Summary
Migrate BQX ML V3 comprehensive testing and production deployment to Google Vertex AI for scalable, cost-effective, and managed ML operations.

**Target Completion**: 48-72 hours
**Cost Savings**: 80% reduction in compute costs
**Performance Gain**: 10x faster testing completion

---

## 📊 Phase 1: Infrastructure Setup (4 hours)

### 1.1 Enable Vertex AI APIs
```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 1.2 Create GCS Buckets
```bash
# Create buckets for data, models, and results
gsutil mb -l us-east1 gs://bqx-ml-data
gsutil mb -l us-east1 gs://bqx-ml-models
gsutil mb -l us-east1 gs://bqx-ml-results
gsutil mb -l us-east1 gs://bqx-ml-artifacts
```

### 1.3 Configure Artifact Registry
```bash
gcloud artifacts repositories create bqx-ml-docker \
    --repository-format=docker \
    --location=us-east1 \
    --description="BQX ML V3 Docker images"
```

### 1.4 Set Up Service Account
```bash
gcloud iam service-accounts create vertex-ai-bqx \
    --display-name="Vertex AI BQX ML Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding bqx-ml \
    --member="serviceAccount:vertex-ai-bqx@bqx-ml.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

---

## 📦 Phase 2: Containerization (2 hours)

### 2.1 Create Production Dockerfile
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV PYTHONPATH=/app
CMD ["python3", "run_vertex_pipeline.py"]
```

### 2.2 Build Container Images
```bash
# Testing image
docker build -t us-east1-docker.pkg.dev/bqx-ml/bqx-ml-docker/testing:latest .

# Training image
docker build -t us-east1-docker.pkg.dev/bqx-ml/bqx-ml-docker/training:latest .

# Prediction image
docker build -t us-east1-docker.pkg.dev/bqx-ml/bqx-ml-docker/prediction:latest .
```

### 2.3 Push to Artifact Registry
```bash
docker push us-east1-docker.pkg.dev/bqx-ml/bqx-ml-docker/testing:latest
docker push us-east1-docker.pkg.dev/bqx-ml/bqx-ml-docker/training:latest
docker push us-east1-docker.pkg.dev/bqx-ml/bqx-ml-docker/prediction:latest
```

---

## 🔬 Phase 3: Testing Pipeline (6 hours)

### 3.1 Create Vertex AI Pipeline for Testing
```python
from google.cloud import aiplatform
from google.cloud.aiplatform import pipeline_jobs

@component
def comprehensive_testing_component():
    """Run all feature testing in parallel"""
    # Triangulation testing
    # Correlation testing
    # Extended lags testing
    # Algorithm comparison
    pass

@pipeline
def bqx_testing_pipeline():
    testing = comprehensive_testing_component()
    return testing
```

### 3.2 Submit Testing Jobs
```python
job = aiplatform.PipelineJob(
    display_name="bqx-comprehensive-testing",
    template_path="gs://bqx-ml-artifacts/pipelines/testing.json",
    pipeline_root="gs://bqx-ml-artifacts/pipeline-runs",
    machine_type="n1-highmem-32",  # 32 vCPUs for parallel testing
)
job.submit()
```

### 3.3 Monitor Testing Progress
- Use Vertex AI console for real-time monitoring
- Set up Cloud Monitoring alerts
- Configure automated result collection

---

## 🎯 Phase 4: Model Training Pipeline (4 hours)

### 4.1 Create Training Pipeline
```python
@component
def train_model_component(pair: str, horizon: int):
    """Train individual model for pair/horizon"""
    model = XGBRegressor()
    model.fit(X_train, y_train)
    return model

@pipeline
def bqx_training_pipeline():
    models = []
    for pair in CURRENCY_PAIRS:
        for horizon in HORIZONS:
            model = train_model_component(pair, horizon)
            models.append(model)
    return models
```

### 4.2 Hyperparameter Tuning
```yaml
hyperparameterTuningJob:
  studySpec:
    algorithm: ALGORITHM_UNSPECIFIED
    metrics:
    - metricId: r2_score
      goal: MAXIMIZE
    parameters:
    - parameterId: learning_rate
      doubleValueSpec:
        minValue: 0.01
        maxValue: 0.3
    - parameterId: max_depth
      integerValueSpec:
        minValue: 3
        maxValue: 10
```

### 4.3 Model Registry
```python
model = aiplatform.Model.upload(
    display_name=f"bqx-{pair}-{horizon}",
    artifact_uri=f"gs://bqx-ml-models/{pair}/{horizon}/",
    serving_container_image_uri="us-east1-docker.pkg.dev/bqx-ml/bqx-ml-docker/prediction:latest",
)
```

---

## 🚀 Phase 5: Deployment Pipeline (4 hours)

### 5.1 Create Endpoints
```python
endpoint = aiplatform.Endpoint.create(
    display_name="bqx-ml-v3-production",
    description="Production endpoint for all 196 models",
)
```

### 5.2 Deploy Models
```python
for model in trained_models:
    endpoint.deploy(
        model=model,
        deployed_model_display_name=f"{model.display_name}-deployed",
        machine_type="n1-standard-4",
        min_replica_count=1,
        max_replica_count=10,  # Auto-scaling
        accelerator_type=None,
        traffic_percentage=100,
    )
```

### 5.3 Configure Auto-scaling
```yaml
autoscaling:
  minReplicaCount: 1
  maxReplicaCount: 10
  metrics:
  - type: RESOURCE_UTILIZATION
    target: 60
    resource: CPU
```

---

## 📊 Phase 6: Batch Prediction Pipeline (2 hours)

### 6.1 Create Batch Prediction Jobs
```python
batch_prediction_job = model.batch_predict(
    job_display_name="bqx-daily-predictions",
    gcs_source="gs://bqx-ml-data/input/",
    gcs_destination="gs://bqx-ml-results/predictions/",
    machine_type="n1-standard-16",
    starting_replica_count=1,
    max_replica_count=10,
)
```

### 6.2 Schedule Regular Predictions
```python
from google.cloud import scheduler

scheduler_client = scheduler.CloudSchedulerClient()
job = {
    "name": "bqx-hourly-predictions",
    "schedule": "0 * * * *",  # Every hour
    "http_target": {
        "uri": "https://aiplatform.googleapis.com/v1/projects/bqx-ml/locations/us-east1/batchPredictionJobs",
        "http_method": "POST",
    },
}
```

---

## 📈 Phase 7: Monitoring & Operations (2 hours)

### 7.1 Set Up Monitoring
```python
# Model performance monitoring
aiplatform.ModelDeploymentMonitoringJob.create(
    display_name="bqx-model-monitoring",
    endpoint=endpoint,
    prediction_sampling_rate=0.1,
    monitoring_interval_hours=1,
    drift_thresholds={
        "r2_score": 0.05,  # Alert if R² drops by 5%
    },
)
```

### 7.2 Configure Alerts
```yaml
alertPolicy:
  displayName: "BQX Model Performance Alert"
  conditions:
  - displayName: "R² Score Below Threshold"
    conditionThreshold:
      filter: 'metric.type="aiplatform.googleapis.com/prediction/r2_score"'
      comparison: COMPARISON_LT
      thresholdValue: 0.90
```

### 7.3 Logging Configuration
```python
import logging
from google.cloud import logging as cloud_logging

logging_client = cloud_logging.Client()
logging_client.setup_logging()
```

---

## 💰 Cost Analysis

### Current VM Approach
- **VM Cost**: $95/month (always running)
- **Testing Time**: 48-72 hours
- **Total Monthly**: $95

### Vertex AI Approach
- **Testing**: $15 per complete test run (3-6 hours)
- **Training**: $10 per training cycle
- **Prediction**: $0.006 per 1000 predictions
- **Total Monthly**: ~$20-30 (80% savings)

---

## 🔄 Migration Timeline

### Day 1 (Today)
- [ ] Complete current testing on VM
- [ ] Set up Vertex AI infrastructure
- [ ] Build and push Docker containers

### Day 2
- [ ] Migrate testing pipeline to Vertex AI
- [ ] Run parallel testing (3-6 hours)
- [ ] Validate results match VM testing

### Day 3
- [ ] Deploy production models
- [ ] Set up batch prediction
- [ ] Configure monitoring

### Day 4
- [ ] Production validation
- [ ] Performance testing
- [ ] Decommission VM

---

## ✅ Success Criteria

### Testing Phase
- [ ] All 6000+ features tested in < 6 hours
- [ ] Results match current VM testing
- [ ] Cost < $20 per test run

### Training Phase
- [ ] All 196 models trained in < 2 hours
- [ ] R² > 95% maintained
- [ ] Automatic retraining on schedule

### Deployment Phase
- [ ] < 100ms prediction latency
- [ ] 99.9% uptime SLA
- [ ] Auto-scaling functional

### Operations Phase
- [ ] Automated monitoring active
- [ ] Alerts configured
- [ ] Logging operational

---

## 📋 AirTable Tasks to Add

### New Milestone: MP03.P12 - Vertex AI Migration
1. **MP03.P12.S01.T01**: Enable Vertex AI APIs and services
2. **MP03.P12.S01.T02**: Create GCS buckets for data/models
3. **MP03.P12.S01.T03**: Configure Artifact Registry
4. **MP03.P12.S01.T04**: Set up service accounts and IAM

### New Milestone: MP03.P13 - Containerization
5. **MP03.P13.S01.T01**: Create Dockerfiles for testing/training/prediction
6. **MP03.P13.S01.T02**: Build container images
7. **MP03.P13.S01.T03**: Push images to Artifact Registry
8. **MP03.P13.S01.T04**: Validate container functionality

### New Milestone: MP03.P14 - Pipeline Development
9. **MP03.P14.S01.T01**: Develop testing pipeline components
10. **MP03.P14.S01.T02**: Create training pipeline
11. **MP03.P14.S01.T03**: Build prediction pipeline
12. **MP03.P14.S01.T04**: Implement pipeline orchestration

### New Milestone: MP03.P15 - Model Deployment
13. **MP03.P15.S01.T01**: Create Vertex AI endpoints
14. **MP03.P15.S01.T02**: Deploy models to endpoints
15. **MP03.P15.S01.T03**: Configure auto-scaling
16. **MP03.P15.S01.T04**: Set up load balancing

### New Milestone: MP03.P16 - Operations
17. **MP03.P16.S01.T01**: Configure model monitoring
18. **MP03.P16.S01.T02**: Set up alerting policies
19. **MP03.P16.S01.T03**: Implement logging
20. **MP03.P16.S01.T04**: Create operational dashboards

---

## 🚀 Immediate Next Steps

1. **Complete documentation** of migration plan
2. **Update AirTable** with new tasks
3. **Charge BA** with implementation
4. **Begin Phase 1** infrastructure setup

---

*Migration plan created: 2025-11-27*
*Estimated completion: 72 hours*
*Expected cost savings: 80%*
*Performance improvement: 10x*