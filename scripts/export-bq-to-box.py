#!/usr/bin/env python3
"""
BigQuery to Box.com Export Script for BQX-ML-V3 Disaster Recovery

Exports BigQuery tables to GCS, downloads them, and uploads to Box.com.
Designed to run as a long-running background process.

Usage:
    python3 export-bq-to-box.py --dataset <dataset_name> [--tables <table1,table2>] [--background]

Examples:
    # Export all tables from a dataset
    python3 export-bq-to-box.py --dataset bqx_ml_v3_features

    # Export specific tables
    python3 export-bq-to-box.py --dataset bqx_ml_v3_models --tables eurusd_rf_45,eurusd_rf_90

    # Run in background
    python3 export-bq-to-box.py --dataset bqx_bq_uscen1 --background

Note: This is a LONG-RUNNING process (4-8 hours for full datasets).
      Use --background to run without blocking.
"""

import sys
sys.path.insert(0, '/home/micha/.local/lib/python3.10/site-packages')

import os
import json
import argparse
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
import time

from box_sdk_gen import BoxClient, BoxJWTAuth, JWTConfig, CreateFolderParent
from box_sdk_gen import UploadFileAttributes, UploadFileAttributesParentField

# Configuration
BOX_JWT_CONFIG = '/home/micha/.secrets/box_jwt_config.json'
BOX_BQX_FOLDER_ID = '353414610676'  # bqx-ml-v3 folder
GCP_PROJECT = 'bqx-ml'
GCS_BUCKET = 'gs://bqx-ml-exports'  # Temporary bucket for exports
LOG_DIR = '/home/micha/bqx_ml_v3/logs'

# Datasets to export
DATASETS = {
    'bqx_bq_uscen1': {
        'description': 'Raw OHLCV data',
        'priority': 'HIGH',
        'estimated_size': '2TB'
    },
    'bqx_ml_v3_features': {
        'description': 'Engineered features',
        'priority': 'HIGH',
        'estimated_size': '500GB'
    },
    'bqx_ml_v3_models': {
        'description': 'Trained models',
        'priority': 'CRITICAL',
        'estimated_size': '50GB'
    },
    'bqx_ml_v3_predictions': {
        'description': 'Model predictions',
        'priority': 'MEDIUM',
        'estimated_size': '100GB'
    },
    'bqx_ml_v3_analytics': {
        'description': 'Analytics metrics',
        'priority': 'LOW',
        'estimated_size': '10GB'
    }
}

def setup_logging(dataset):
    """Setup logging for the export process."""
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(LOG_DIR, f'bq_export_{dataset}_{timestamp}.log')
    return log_file

def log(message, log_file=None):
    """Log message to console and optionally to file."""
    timestamp = datetime.now().isoformat()
    formatted = f"[{timestamp}] {message}"
    print(formatted)
    if log_file:
        with open(log_file, 'a') as f:
            f.write(formatted + '\n')

def get_box_client():
    """Initialize Box client with JWT auth."""
    with open(BOX_JWT_CONFIG, 'r') as f:
        config_data = json.load(f)
    jwt_config = JWTConfig.from_config_json_string(json.dumps(config_data))
    auth = BoxJWTAuth(config=jwt_config)
    return BoxClient(auth=auth)

def get_or_create_folder(client, parent_id, folder_name):
    """Get existing folder or create new one."""
    items = client.folders.get_folder_items(folder_id=parent_id, limit=1000)
    for item in items.entries:
        if item.type == 'folder' and item.name == folder_name:
            return item.id

    parent = CreateFolderParent(id=parent_id)
    new_folder = client.folders.create_folder(name=folder_name, parent=parent)
    return new_folder.id

def list_tables(dataset):
    """List all tables in a BigQuery dataset."""
    cmd = f"bq ls --format=json {GCP_PROJECT}:{dataset}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Failed to list tables: {result.stderr}")

    tables = json.loads(result.stdout)
    return [t['tableReference']['tableId'] for t in tables]

def export_table_to_gcs(dataset, table, log_file):
    """Export a BigQuery table to GCS as Parquet format.

    Why Parquet:
    - 10-20x better compression than JSON
    - Preserves schema and data types exactly
    - Columnar format optimized for analytics
    - Native BigQuery support for import/export
    - Faster read/write operations
    """
    gcs_path = f"{GCS_BUCKET}/{dataset}/{table}/*.parquet"

    log(f"Exporting {dataset}.{table} to GCS (Parquet format)...", log_file)

    # Use PARQUET format with SNAPPY compression (default, excellent balance)
    cmd = f"""bq extract --destination_format=PARQUET \
        {GCP_PROJECT}:{dataset}.{table} \
        {gcs_path}"""

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"ERROR exporting {table}: {result.stderr}", log_file)
        return None

    log(f"Exported {table} to {gcs_path}", log_file)
    return gcs_path

def download_from_gcs(gcs_path, local_dir, log_file):
    """Download exported files from GCS."""
    log(f"Downloading from {gcs_path}...", log_file)

    cmd = f"gsutil -m cp -r {gcs_path} {local_dir}/"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"ERROR downloading: {result.stderr}", log_file)
        return False

    log(f"Downloaded to {local_dir}", log_file)
    return True

def upload_to_box(client, folder_id, local_path, log_file):
    """Upload a file to Box."""
    file_name = os.path.basename(local_path)
    file_size = os.path.getsize(local_path)

    log(f"Uploading {file_name} ({file_size / 1024 / 1024:.2f} MB)...", log_file)

    # Check if file exists
    items = client.folders.get_folder_items(folder_id=folder_id, limit=1000)
    existing_id = None
    for item in items.entries:
        if item.type == 'file' and item.name == file_name:
            existing_id = item.id
            break

    with open(local_path, 'rb') as f:
        if existing_id:
            from box_sdk_gen import UploadFileVersionAttributes
            client.uploads.upload_file_version(
                file_id=existing_id,
                file=f,
                attributes=UploadFileVersionAttributes(name=file_name)
            )
            log(f"Updated: {file_name}", log_file)
        else:
            parent = UploadFileAttributesParentField(id=folder_id)
            attributes = UploadFileAttributes(name=file_name, parent=parent)
            client.uploads.upload_file(attributes=attributes, file=f)
            log(f"Uploaded: {file_name}", log_file)

    return True

def cleanup_gcs(gcs_path, log_file):
    """Clean up exported files from GCS."""
    log(f"Cleaning up {gcs_path}...", log_file)
    cmd = f"gsutil -m rm -r {gcs_path}"
    subprocess.run(cmd, shell=True, capture_output=True)

def export_dataset(dataset, tables=None, log_file=None):
    """Export a dataset to Box.com."""
    log(f"=== Starting export of {dataset} ===", log_file)

    # Initialize Box client
    client = get_box_client()
    log("Connected to Box.com", log_file)

    # Create dataset folder in Box
    bigquery_folder = get_or_create_folder(client, BOX_BQX_FOLDER_ID, 'bigquery')
    dataset_folder = get_or_create_folder(client, bigquery_folder, dataset)
    log(f"Box folder ready: bigquery/{dataset}", log_file)

    # Get list of tables
    if tables:
        table_list = tables
    else:
        table_list = list_tables(dataset)

    log(f"Found {len(table_list)} tables to export", log_file)

    # Process each table
    success_count = 0
    error_count = 0

    for i, table in enumerate(table_list):
        log(f"\n[{i+1}/{len(table_list)}] Processing {table}...", log_file)

        try:
            # Create temp directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Export to GCS
                gcs_path = export_table_to_gcs(dataset, table, log_file)
                if not gcs_path:
                    error_count += 1
                    continue

                # Download from GCS
                if not download_from_gcs(gcs_path, temp_dir, log_file):
                    error_count += 1
                    continue

                # Create table folder in Box
                table_folder = get_or_create_folder(client, dataset_folder, table)

                # Upload all Parquet files
                for file_path in Path(temp_dir).rglob('*.parquet'):
                    upload_to_box(client, table_folder, str(file_path), log_file)

                # Cleanup GCS
                cleanup_gcs(gcs_path, log_file)

                success_count += 1
                log(f"Completed {table}", log_file)

        except Exception as e:
            log(f"ERROR processing {table}: {e}", log_file)
            error_count += 1
            continue

    log(f"\n=== Export Summary ===", log_file)
    log(f"Dataset: {dataset}", log_file)
    log(f"Successful: {success_count}/{len(table_list)}", log_file)
    log(f"Errors: {error_count}/{len(table_list)}", log_file)
    log(f"======================", log_file)

    return success_count, error_count

def main():
    parser = argparse.ArgumentParser(description='Export BigQuery to Box.com')
    parser.add_argument('--dataset', required=True, help='Dataset to export')
    parser.add_argument('--tables', help='Comma-separated list of tables (default: all)')
    parser.add_argument('--background', action='store_true', help='Run in background')
    args = parser.parse_args()

    log_file = setup_logging(args.dataset)

    tables = args.tables.split(',') if args.tables else None

    log(f"BQX-ML-V3 BigQuery to Box.com Export", log_file)
    log(f"Dataset: {args.dataset}", log_file)
    log(f"Tables: {tables if tables else 'ALL'}", log_file)
    log(f"Log file: {log_file}", log_file)

    if args.background:
        log("Running in background mode...", log_file)
        # Fork to background
        pid = os.fork()
        if pid > 0:
            print(f"Export started in background. PID: {pid}")
            print(f"Log file: {log_file}")
            sys.exit(0)

    start_time = time.time()
    success, errors = export_dataset(args.dataset, tables, log_file)
    elapsed = time.time() - start_time

    log(f"\nTotal time: {elapsed/3600:.2f} hours", log_file)

if __name__ == '__main__':
    main()
