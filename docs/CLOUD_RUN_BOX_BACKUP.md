# BQ-to-Box Cloud Run Backup Service

## Overview

The BQ-to-Box Sync Service is a containerized Cloud Run service that automatically exports BigQuery tables to Box.com for disaster recovery. This creates a complete off-site backup independent of Google Cloud Platform.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BQX-ML BACKUP ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐      ┌──────────────┐      ┌──────────────────────┐     │
│   │ Cloud        │      │ Cloud Run    │      │ Box.com              │     │
│   │ Scheduler    │─────▶│ bq-to-box-   │─────▶│ bqx-ml-v3/           │     │
│   │              │      │ sync         │      │ └── GCP/             │     │
│   │ (triggers)   │      │              │      │     └── bigquery/    │     │
│   └──────────────┘      └──────┬───────┘      │         └── {dataset}│     │
│                                │              │             └── {tbl}│     │
│                                │              └──────────────────────┘     │
│                                │                         ▲                  │
│                                ▼                         │                  │
│                         ┌──────────────┐                 │                  │
│                         │ BigQuery     │                 │                  │
│                         │ Datasets     │─────────────────┘                  │
│                         │              │    (Parquet export via GCS)        │
│                         └──────────────┘                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Service Details

| Property | Value |
|----------|-------|
| **Service Name** | `bq-to-box-sync` |
| **Service URL** | `https://bq-to-box-sync-499681702492.us-central1.run.app` |
| **Region** | `us-central1` |
| **Memory** | 2 GiB |
| **CPU** | 1 vCPU |
| **Timeout** | 3600 seconds (1 hour) |
| **Concurrency** | 80 |
| **Authentication** | Required (OIDC) |
| **Service Account** | `bq-to-box-sync@bqx-ml.iam.gserviceaccount.com` |

## Container Image

- **Registry**: `gcr.io/bqx-ml/bq-to-box-sync:latest`
- **Base Image**: Python 3.10-slim
- **Key Dependencies**:
  - Flask 3.x (web framework)
  - box-sdk-gen 1.x (Box.com API)
  - google-cloud-bigquery 3.x
  - google-cloud-storage 2.x
  - google-cloud-secret-manager 2.x

## API Endpoints

### Health Check
```
GET /
Response: {"status": "healthy", "service": "bq-to-box-sync"}
```

### Sync Dataset
```
POST /sync
Body: {"dataset": "bqx_ml_v3_models", "tables": "optional,comma,separated"}
Response: {"dataset": "...", "success": N, "errors": M, "tables": [...]}
```

### Sync Specific Dataset
```
POST /sync/<dataset>
Body: {"tables": "optional,comma,separated"}  # optional
Response: {"dataset": "...", "success": N, "errors": M, "tables": [...]}
```

## Box.com Folder Structure

```
bqx-ml-v3/ (353414610676)
├── GCP/ (353418092758)
│   ├── bigquery/ (353417391696)
│   │   ├── bqx_bq_uscen1/ (353419110877)
│   │   ├── bqx_ml_v3_features/ (353419806934)
│   │   ├── bqx_ml_v3_models/ (353417980012)
│   │   ├── bqx_ml_v3_predictions/ (353419935781)
│   │   ├── bqx_ml_v3_analytics_v2/ (353419303017)
│   │   └── bqx_ml_v3_staging/ (353417344230)
│   └── storage/ (353418205951)
│       ├── bqx-ml-exports/ (353417675931)
│       ├── bqx-ml-models/ (353417637424)
│       ├── bqx-ml-artifacts/ (353417466731)
│       └── bqx-ml-results/ (353418724346)
└── [workspace files mirrored from local]
```

## Scheduled Jobs (Cloud Scheduler)

| Job Name | Schedule | Dataset | Next Run |
|----------|----------|---------|----------|
| `bq-to-box-models` | Daily 2:00 UTC | `bqx_ml_v3_models` | Every day |
| `bq-to-box-features` | Sunday 3:00 UTC | `bqx_ml_v3_features` | Weekly |
| `bq-to-box-predictions` | Monday 4:00 UTC | `bqx_ml_v3_predictions` | Weekly |
| `bq-to-box-analytics` | 1st of month 5:00 UTC | `bqx_ml_v3_analytics_v2` | Monthly |

### Cron Expressions
```bash
bq-to-box-models:      0 2 * * *    # Daily at 2 AM UTC
bq-to-box-features:    0 3 * * 0    # Sunday at 3 AM UTC
bq-to-box-predictions: 0 4 * * 1    # Monday at 4 AM UTC
bq-to-box-analytics:   0 5 1 * *    # 1st of month at 5 AM UTC
```

## Export Process

For each table export, the service:

1. **Export to GCS**: `bq extract` table to `gs://bqx-ml-exports/{dataset}/{table}/*.parquet`
2. **Download**: `gsutil cp` from GCS to local temp directory
3. **Upload to Box**: Use Box SDK to upload Parquet files
4. **Cleanup**: Delete temp files from GCS

### Data Format
- **Format**: Apache Parquet
- **Compression**: Snappy (default)
- **Advantages**:
  - 10-20x better compression than JSON
  - Preserves schema and data types exactly
  - Columnar format optimized for analytics
  - Native BigQuery support for import/export

## Service Account Permissions

The service account `bq-to-box-sync@bqx-ml.iam.gserviceaccount.com` has:

| Role | Purpose |
|------|---------|
| `roles/bigquery.dataViewer` | Read BigQuery tables |
| `roles/bigquery.jobUser` | Run export jobs |
| `roles/storage.admin` | Read/write GCS for temp exports |
| `roles/secretmanager.secretAccessor` | Access Box JWT credentials |

## Secrets

| Secret Name | Purpose |
|-------------|---------|
| `oxo-box-jwt-config` | Box.com JWT authentication config |

## Cost Estimate

### Monthly Costs (Estimated)

| Component | Cost |
|-----------|------|
| Cloud Run (compute) | $0 - $2.84 (free tier covers most usage) |
| Cloud Scheduler | $0.40 (4 jobs × $0.10) |
| Cloud Build | ~$0.02/build (negligible) |
| GCS (temp storage) | Pay-per-use (cleaned up after export) |
| **Total** | **$0.40 - $3.24/month** |

### Free Tier Coverage
- 180,000 vCPU-seconds/month
- 360,000 GiB-seconds/month
- 2 million requests/month

## Manual Operations

### Trigger Immediate Sync
```bash
# Get identity token
TOKEN=$(gcloud auth print-identity-token)

# Trigger sync for specific dataset
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dataset": "bqx_ml_v3_models"}' \
  "https://bq-to-box-sync-499681702492.us-central1.run.app/sync"

# Or use dataset-specific endpoint
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  "https://bq-to-box-sync-499681702492.us-central1.run.app/sync/bqx_ml_v3_models"
```

### View Service Logs
```bash
gcloud run services logs read bq-to-box-sync --region=us-central1 --project=bqx-ml
```

### Check Service Status
```bash
gcloud run services describe bq-to-box-sync --region=us-central1 --project=bqx-ml
```

### List Scheduler Jobs
```bash
gcloud scheduler jobs list --location=us-central1 --project=bqx-ml
```

### Manually Run Scheduler Job
```bash
gcloud scheduler jobs run bq-to-box-models --location=us-central1 --project=bqx-ml
```

## Deployment

### Build and Deploy
```bash
# Build container image
gcloud builds submit --tag gcr.io/bqx-ml/bq-to-box-sync:latest containers/bq-to-box/ --project=bqx-ml

# Deploy to Cloud Run
gcloud run deploy bq-to-box-sync \
  --image=gcr.io/bqx-ml/bq-to-box-sync:latest \
  --region=us-central1 \
  --platform=managed \
  --memory=2Gi \
  --timeout=3600 \
  --no-allow-unauthenticated \
  --service-account=bq-to-box-sync@bqx-ml.iam.gserviceaccount.com \
  --project=bqx-ml
```

### Update Scheduler Jobs
```bash
# Delete existing job
gcloud scheduler jobs delete bq-to-box-models --location=us-central1 --project=bqx-ml

# Create new job
gcloud scheduler jobs create http bq-to-box-models \
  --location=us-central1 \
  --schedule="0 2 * * *" \
  --uri="https://bq-to-box-sync-499681702492.us-central1.run.app/sync/bqx_ml_v3_models" \
  --http-method=POST \
  --oidc-service-account-email=bq-to-box-sync@bqx-ml.iam.gserviceaccount.com \
  --project=bqx-ml
```

## Relationship to Other Backup Methods

| Method | Purpose | Scope | Frequency |
|--------|---------|-------|-----------|
| **Cloud Run Service** | Automated DR for BigQuery | BQ tables only | Scheduled |
| `sync-workspace.sh` | Interactive workspace sync | Files + GDrive | On-demand |
| `sync-box-backup.py` | Manual Box file backup | Project files | On-demand |
| `export-bq-to-box.py` | Manual BQ export | BQ tables | On-demand |

## Producer-Consumer Model

The Cloud Run service implements a producer-consumer pattern:

```
BA Agent (Producer)          Cloud Run Service (Consumer)
     │                                │
     │ Creates BigQuery tables        │ Exports completed tables
     │ (async, continuous)            │ (scheduled, independent)
     │                                │
     ▼                                ▼
┌─────────────────────────────────────────────────────────────┐
│                     BigQuery (Buffer)                       │
│  bqx_ml_v3_features, bqx_ml_v3_models, etc.                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                         Box.com (DR)
```

This decoupling allows:
- BA to continue creating data without waiting for exports
- Exports to run on schedule without blocking data creation
- Independent scaling of both operations

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Verify service account has `secretmanager.secretAccessor` role
   - Check `oxo-box-jwt-config` secret exists and is valid

2. **Export Timeout**
   - Large tables may exceed 1-hour timeout
   - Consider exporting specific tables instead of full dataset
   - Increase timeout if needed (max 3600s for Cloud Run)

3. **Box API Rate Limits**
   - Box.com has API rate limits
   - Service handles this with retry logic
   - For large exports, use background mode

4. **GCS Permission Denied**
   - Verify service account has `storage.admin` role
   - Check `gs://bqx-ml-exports` bucket exists

## Files

| File | Purpose |
|------|---------|
| `containers/bq-to-box/sync_service.py` | Main Flask application |
| `containers/bq-to-box/Dockerfile` | Container definition |
| `containers/bq-to-box/requirements.txt` | Python dependencies |
| `containers/bq-to-box/deploy.sh` | Deployment script |
| `containers/bq-to-box/setup-scheduler.sh` | Scheduler setup script |
| `containers/bq-to-box/cloudbuild.yaml` | Cloud Build config |

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-29 | 1.0.0 | Initial deployment |
