#!/usr/bin/env python3
"""
BQ-to-Box Sync Service
Containerized service for exporting BigQuery tables to Box.com

Designed to run as:
- Cloud Run service (triggered by Cloud Scheduler)
- Cloud Functions (for lighter workloads)
- Standalone container

Environment Variables:
- BOX_JWT_CONFIG_SECRET: GCP Secret Manager secret name for Box JWT config
- GCP_PROJECT: GCP project ID (default: bqx-ml)
- DATASET: BigQuery dataset to export (required)
- TABLES: Comma-separated table names (optional, default: all)
- BOX_FOLDER_ID: Box.com folder ID for uploads
"""

import os
import sys
import json
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify

# Box SDK
from box_sdk_gen import BoxClient, BoxJWTAuth, JWTConfig, CreateFolderParent
from box_sdk_gen import UploadFileAttributes, UploadFileAttributesParentField

# Configuration
GCP_PROJECT = os.environ.get('GCP_PROJECT', 'bqx-ml')

# Box.com directory structure (mirrors GCP)
BOX_ROOT_FOLDER_ID = '353414610676'  # bqx-ml-v3/
BOX_GCP_FOLDER_ID = '353418092758'   # bqx-ml-v3/GCP/
BOX_BQ_FOLDER_ID = '353417391696'    # bqx-ml-v3/GCP/bigquery/
BOX_STORAGE_FOLDER_ID = '353418205951'  # bqx-ml-v3/GCP/storage/

# Box.com folder IDs for each BigQuery dataset (under GCP/bigquery/)
DATASET_FOLDERS = {
    'bqx_bq_uscen1': '353419110877',
    'bqx_ml_v3_features': '353419806934',
    'bqx_ml_v3_models': '353417980012',
    'bqx_ml_v3_predictions': '353419935781',
    'bqx_ml_v3_analytics': '353419303017',
    'bqx_ml_v3_staging': '353417344230',
}

# Box.com folder IDs for GCS buckets (under GCP/storage/)
STORAGE_FOLDERS = {
    'bqx-ml-exports': '353417675931',
    'bqx-ml-models': '353417637424',
    'bqx-ml-artifacts': '353417466731',
    'bqx-ml-results': '353418724346',
}

app = Flask(__name__)

def get_box_client():
    """Initialize Box client from Secret Manager or environment."""
    # Try to get from Secret Manager
    secret_name = os.environ.get('BOX_JWT_CONFIG_SECRET', 'oxo-box-jwt-config')

    try:
        from google.cloud import secretmanager
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{GCP_PROJECT}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        config_data = json.loads(response.payload.data.decode('UTF-8'))
    except Exception as e:
        # Fallback to local file (for testing)
        config_path = os.environ.get('BOX_JWT_CONFIG', '/secrets/box_jwt_config.json')
        with open(config_path, 'r') as f:
            config_data = json.load(f)

    jwt_config = JWTConfig.from_config_json_string(json.dumps(config_data))
    auth = BoxJWTAuth(config=jwt_config)
    return BoxClient(auth=auth)

def list_tables(dataset):
    """List all tables in a BigQuery dataset."""
    cmd = f"bq ls --format=json {GCP_PROJECT}:{dataset}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Failed to list tables: {result.stderr}")

    tables = json.loads(result.stdout)
    return [t['tableReference']['tableId'] for t in tables]

def export_table_to_gcs(dataset, table):
    """Export a BigQuery table to GCS as Parquet."""
    gcs_bucket = f"gs://bqx-ml-exports/{dataset}/{table}"
    gcs_path = f"{gcs_bucket}/*.parquet"

    # Export to GCS
    cmd = f"""bq extract --destination_format=PARQUET \
        {GCP_PROJECT}:{dataset}.{table} \
        {gcs_path}"""

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return None, f"Export failed: {result.stderr}"

    return gcs_bucket, None

def download_from_gcs(gcs_path, local_dir):
    """Download files from GCS to local directory."""
    cmd = f"gsutil -m cp -r {gcs_path}/* {local_dir}/"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0

def upload_to_box(client, folder_id, file_path):
    """Upload a file to Box.com."""
    file_name = os.path.basename(file_path)

    # Check if file exists
    items = client.folders.get_folder_items(folder_id=folder_id, limit=1000)
    existing_id = None
    for item in items.entries:
        if item.type == 'file' and item.name == file_name:
            existing_id = item.id
            break

    with open(file_path, 'rb') as f:
        if existing_id:
            from box_sdk_gen import UploadFileVersionAttributes
            client.uploads.upload_file_version(
                file_id=existing_id,
                file=f,
                attributes=UploadFileVersionAttributes(name=file_name)
            )
        else:
            parent = UploadFileAttributesParentField(id=folder_id)
            attributes = UploadFileAttributes(name=file_name, parent=parent)
            client.uploads.upload_file(attributes=attributes, file=f)

    return True

def get_or_create_folder(client, parent_id, folder_name):
    """Get existing folder or create new one in Box."""
    items = client.folders.get_folder_items(folder_id=parent_id, limit=1000)
    for item in items.entries:
        if item.type == 'folder' and item.name == folder_name:
            return item.id

    parent = CreateFolderParent(id=parent_id)
    new_folder = client.folders.create_folder(name=folder_name, parent=parent)
    return new_folder.id

def cleanup_gcs(gcs_path):
    """Clean up exported files from GCS."""
    cmd = f"gsutil -m rm -r {gcs_path}"
    subprocess.run(cmd, shell=True, capture_output=True)

def sync_dataset(dataset, tables=None):
    """Sync a BigQuery dataset to Box.com."""
    results = {
        'dataset': dataset,
        'started': datetime.now().isoformat(),
        'tables': [],
        'success': 0,
        'errors': 0,
    }

    # Get Box client
    client = get_box_client()

    # Get dataset folder ID
    if dataset not in DATASET_FOLDERS:
        return {'error': f'Unknown dataset: {dataset}'}

    dataset_folder_id = DATASET_FOLDERS[dataset]

    # Get list of tables
    if tables:
        table_list = tables if isinstance(tables, list) else tables.split(',')
    else:
        table_list = list_tables(dataset)

    results['total_tables'] = len(table_list)

    # Process each table
    for table in table_list:
        table_result = {'table': table, 'status': 'pending'}

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Export to GCS
                gcs_path, error = export_table_to_gcs(dataset, table)
                if error:
                    table_result['status'] = 'error'
                    table_result['error'] = error
                    results['errors'] += 1
                    results['tables'].append(table_result)
                    continue

                # Download from GCS
                if not download_from_gcs(gcs_path, temp_dir):
                    table_result['status'] = 'error'
                    table_result['error'] = 'Download failed'
                    results['errors'] += 1
                    results['tables'].append(table_result)
                    continue

                # Create table folder in Box
                table_folder_id = get_or_create_folder(client, dataset_folder_id, table)

                # Upload all parquet files
                for file_path in Path(temp_dir).rglob('*.parquet'):
                    upload_to_box(client, table_folder_id, str(file_path))

                # Cleanup GCS
                cleanup_gcs(gcs_path)

                table_result['status'] = 'success'
                results['success'] += 1

        except Exception as e:
            table_result['status'] = 'error'
            table_result['error'] = str(e)
            results['errors'] += 1

        results['tables'].append(table_result)

    results['completed'] = datetime.now().isoformat()
    return results

@app.route('/', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'bq-to-box-sync'})

@app.route('/sync', methods=['POST'])
def sync():
    """Trigger sync for a dataset."""
    data = request.get_json() or {}

    dataset = data.get('dataset') or os.environ.get('DATASET')
    if not dataset:
        return jsonify({'error': 'dataset is required'}), 400

    tables = data.get('tables')

    results = sync_dataset(dataset, tables)
    return jsonify(results)

@app.route('/sync/<dataset>', methods=['POST'])
def sync_specific(dataset):
    """Trigger sync for a specific dataset."""
    data = request.get_json() or {}
    tables = data.get('tables')

    results = sync_dataset(dataset, tables)
    return jsonify(results)

if __name__ == '__main__':
    # Check if running as CLI or web service
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        # CLI mode
        dataset = os.environ.get('DATASET')
        tables = os.environ.get('TABLES')

        if not dataset:
            print("DATASET environment variable required")
            sys.exit(1)

        results = sync_dataset(dataset, tables)
        print(json.dumps(results, indent=2))
    else:
        # Web service mode
        port = int(os.environ.get('PORT', 8080))
        app.run(host='0.0.0.0', port=port)
