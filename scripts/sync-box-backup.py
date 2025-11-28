#!/usr/bin/env python3
"""
Box.com Backup Script for BQX-ML-V3
Syncs project files and BigQuery table exports to Box.com

Usage:
    python3 sync-box-backup.py [--full] [--tables-only] [--files-only]

Options:
    --full          Full backup including BQ table exports
    --tables-only   Only export and upload BigQuery tables
    --files-only    Only upload project files (default)
"""

import sys
sys.path.insert(0, '/home/micha/.local/lib/python3.10/site-packages')

import os
import json
import argparse
from datetime import datetime
from pathlib import Path

from box_sdk_gen import BoxClient, BoxJWTAuth, JWTConfig, CreateFolderParent, PreflightFileUploadCheckParent

# Configuration
BOX_JWT_CONFIG = '/home/micha/.secrets/box_jwt_config.json'
BOX_BQX_FOLDER_ID = '353414610676'  # bqx-ml-v3 folder
PROJECT_ROOT = '/home/micha/bqx_ml_v3'

# Exclusions
EXCLUDE_PATTERNS = [
    '.git',
    '.secrets',
    '__pycache__',
    '*.pyc',
    '.env',
    'venv',
    'node_modules',
    '*.pkl',
    '*.model',
]

def get_box_client():
    """Initialize Box client with JWT auth."""
    with open(BOX_JWT_CONFIG, 'r') as f:
        config_data = json.load(f)

    jwt_config = JWTConfig.from_config_json_string(json.dumps(config_data))
    auth = BoxJWTAuth(config=jwt_config)
    return BoxClient(auth=auth)

def should_exclude(path):
    """Check if path should be excluded from backup."""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith('*'):
            if path_str.endswith(pattern[1:]):
                return True
        elif pattern in path_str:
            return True
    return False

def get_or_create_folder(client, parent_id, folder_name):
    """Get existing folder or create new one."""
    # List items in parent
    items = client.folders.get_folder_items(folder_id=parent_id, limit=1000)

    for item in items.entries:
        if item.type == 'folder' and item.name == folder_name:
            return item.id

    # Create if not exists
    parent = CreateFolderParent(id=parent_id)
    new_folder = client.folders.create_folder(name=folder_name, parent=parent)
    return new_folder.id

def upload_file(client, folder_id, file_path):
    """Upload a file to Box folder."""
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    # Check if file exists
    items = client.folders.get_folder_items(folder_id=folder_id, limit=1000)
    existing_file_id = None

    for item in items.entries:
        if item.type == 'file' and item.name == file_name:
            existing_file_id = item.id
            break

    if existing_file_id:
        # Update existing file - use upload_new_version
        with open(file_path, 'rb') as f:
            from box_sdk_gen import UploadFileVersionAttributes
            client.uploads.upload_file_version(
                file_id=existing_file_id,
                file=f,
                attributes=UploadFileVersionAttributes(name=file_name)
            )
        print(f"  Updated: {file_name}")
    else:
        # Upload new file
        with open(file_path, 'rb') as f:
            from box_sdk_gen import UploadFileAttributes, UploadFileAttributesParentField
            parent = UploadFileAttributesParentField(id=folder_id)
            attributes = UploadFileAttributes(name=file_name, parent=parent)
            client.uploads.upload_file(
                attributes=attributes,
                file=f
            )
        print(f"  Uploaded: {file_name}")

def sync_directory(client, parent_folder_id, local_path, box_folder_name=None):
    """Recursively sync a directory to Box."""
    if box_folder_name:
        folder_id = get_or_create_folder(client, parent_folder_id, box_folder_name)
    else:
        folder_id = parent_folder_id

    local_path = Path(local_path)

    for item in local_path.iterdir():
        if should_exclude(item):
            continue

        if item.is_file():
            try:
                upload_file(client, folder_id, str(item))
            except Exception as e:
                print(f"  Error uploading {item.name}: {e}")
        elif item.is_dir():
            sync_directory(client, folder_id, item, item.name)

def main():
    parser = argparse.ArgumentParser(description='Box.com Backup for BQX-ML-V3')
    parser.add_argument('--full', action='store_true', help='Full backup including BQ exports')
    parser.add_argument('--tables-only', action='store_true', help='Only export BQ tables')
    parser.add_argument('--files-only', action='store_true', help='Only sync project files')
    args = parser.parse_args()

    print("=" * 60)
    print(f"BQX-ML-V3 Box.com Backup")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    client = get_box_client()
    print("✅ Connected to Box.com")

    if args.files_only or (not args.tables_only and not args.full):
        print("\n📁 Syncing project files...")

        # Sync key directories
        directories = [
            ('intelligence', 'intelligence'),
            ('docs', 'docs'),
            ('scripts', 'scripts'),
            ('configs', 'configs'),
            ('.claude/sandbox/communications', 'communications'),
            ('archive', 'archive'),
        ]

        for local_dir, box_name in directories:
            local_path = os.path.join(PROJECT_ROOT, local_dir)
            if os.path.exists(local_path):
                print(f"\n  → {box_name}/")
                try:
                    sync_directory(client, BOX_BQX_FOLDER_ID, local_path, box_name)
                except Exception as e:
                    print(f"    Error: {e}")

    if args.tables_only or args.full:
        print("\n📊 BigQuery table export not yet implemented")
        print("   (Requires BQ export to GCS, then download and upload)")

    print("\n" + "=" * 60)
    print(f"Backup complete: {datetime.now().isoformat()}")
    print("=" * 60)

if __name__ == '__main__':
    main()
