# API Enablement Resolution Guide

## Issue Summary
**Error**: Cloud Dataproc API has not been used in project bqx-ml before or it is disabled.

## Investigation Results

### 1. Root Cause
- The service account `bqx-ml-ibgateway@bqx-ml.iam.gserviceaccount.com` lacks permissions to enable APIs
- Current permissions are limited to BigQuery and storage operations only

### 2. Dataproc Assessment
**Finding**: Cloud Dataproc is NOT required for BQX ML V3

Evidence:
- Zero mentions of Dataproc in all documentation
- No Dataproc references in codebase
- Architecture uses BigQuery + Vertex AI, not Dataproc

### 3. Required APIs for BQX ML V3

Based on the architecture documentation, these APIs are required:

| API | Purpose | Status |
|-----|---------|--------|
| bigquery.googleapis.com | Data storage and processing | Required |
| aiplatform.googleapis.com | Model training and deployment | Required |
| storage.googleapis.com | Model artifacts and data files | Required |
| compute.googleapis.com | Vertex AI infrastructure | Required |
| iam.googleapis.com | Service account management | Required |
| logging.googleapis.com | System monitoring | Required |
| monitoring.googleapis.com | Performance tracking | Required |

### 4. Resolution Steps

#### For Project Owner/Admin:

1. **Option A: Enable via Console**
   ```
   https://console.cloud.google.com/apis/library?project=bqx-ml
   ```
   Enable only the APIs listed above.

2. **Option B: Enable via CLI**
   ```bash
   chmod +x /home/micha/bqx_ml_v3/scripts/enable_required_apis.sh
   ./scripts/enable_required_apis.sh
   ```
   Note: Requires Owner or Editor role

3. **Option C: Grant Service Account Permissions**
   ```bash
   gcloud projects add-iam-policy-binding bqx-ml \
     --member="serviceAccount:bqx-ml-ibgateway@bqx-ml.iam.gserviceaccount.com" \
     --role="roles/serviceusage.serviceUsageAdmin"
   ```

#### For Current Service Account:

The current service account cannot enable APIs due to permission restrictions. This is by design for security.

### 5. Verification

Once APIs are enabled, verify with:
```bash
# Test BigQuery access
bq ls -d --project_id=bqx-ml

# Test Vertex AI access
gcloud ai models list --region=us-east1 --project=bqx-ml

# Test Storage access
gsutil ls -p bqx-ml
```

### 6. Important Notes

1. **Dataproc is NOT needed** - The error about Dataproc can be ignored
2. **Permission restrictions are intentional** - Service accounts should have minimal permissions
3. **Manual enablement required** - A project owner must enable these APIs

## Conclusion

The Dataproc API error is a red herring. BQX ML V3 does not use Dataproc. The required APIs should be enabled by a project administrator using the provided script or console.

---
*Generated: 2024-11-24*
*Status: Investigation Complete*