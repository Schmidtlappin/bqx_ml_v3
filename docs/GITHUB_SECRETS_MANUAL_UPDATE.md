# GitHub Secrets Manual Update Instructions

## Issue Resolution
The GitHub API restricts programmatic access to repository secrets. You need to manually update these through the GitHub web interface.

## Steps to Update GitHub Secrets

### 1. Navigate to Repository Settings
- Go to: https://github.com/Schmidtlappin/bqx_ml_v3/settings/secrets/actions
- Also update: https://github.com/Schmidtlappin/bqx-db/settings/secrets/actions

### 2. Add/Update These Secrets

| Secret Name | Value |
|------------|-------|
| `GCP_INSTANCE_NAME` | `bqx-ml-master` |
| `GCP_INSTANCE_IP` | `34.148.152.67` |
| `GCP_INSTANCE_ZONE` | `us-east1-b` |
| `GCP_PROJECT_ID` | `bqx-ml` |
| `GCP_SERVICE_ACCOUNT_KEY` | *(paste contents of gcp-sa-key.json)* |
| `AIRTABLE_API_KEY` | `YOUR_AIRTABLE_API_KEY` |
| `AIRTABLE_BASE_ID` | `appR3PPnrNkVo48mO` |

### 3. GitHub Actions Workflow Usage
```yaml
- name: Setup GCP
  env:
    GCP_INSTANCE: ${{ secrets.GCP_INSTANCE_NAME }}
    GCP_IP: ${{ secrets.GCP_INSTANCE_IP }}
  run: |
    echo "Connecting to $GCP_INSTANCE at $GCP_IP"
    gcloud compute ssh $GCP_INSTANCE --zone=${{ secrets.GCP_INSTANCE_ZONE }}
```

## Alternative: Use Repository Variables
For non-sensitive values (instance names, IPs), consider using GitHub Repository Variables instead of Secrets:
- Go to: Settings → Secrets and variables → Actions → Variables tab
- These don't require encryption and are easier to manage

## Verification
After updating, test with a simple workflow:
```yaml
name: Test Secrets
on: workflow_dispatch
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Instance: ${{ secrets.GCP_INSTANCE_NAME }}"
```