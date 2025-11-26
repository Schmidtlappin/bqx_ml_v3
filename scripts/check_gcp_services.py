#!/usr/bin/env python3
"""
Check if all required GCP services are activated for BQX ML V3 project.
"""

import subprocess
import json
from datetime import datetime

# List of required GCP services for BQX ML V3
REQUIRED_SERVICES = [
    'aiplatform.googleapis.com',           # Vertex AI
    'bigquery.googleapis.com',             # BigQuery
    'bigquerystorage.googleapis.com',      # BigQuery Storage API
    'bigqueryconnection.googleapis.com',   # BigQuery Connection API
    'storage-component.googleapis.com',    # Cloud Storage
    'storage-api.googleapis.com',          # Cloud Storage API
    'compute.googleapis.com',              # Compute Engine
    'cloudscheduler.googleapis.com',       # Cloud Scheduler
    'cloudfunctions.googleapis.com',       # Cloud Functions
    'pubsub.googleapis.com',              # Pub/Sub
    'logging.googleapis.com',             # Cloud Logging
    'monitoring.googleapis.com',           # Cloud Monitoring
    'cloudtrace.googleapis.com',          # Cloud Trace
    'clouderrorreporting.googleapis.com', # Error Reporting
    'ml.googleapis.com',                  # AI Platform Training & Prediction
    'notebooks.googleapis.com',           # AI Platform Notebooks
    'dataflow.googleapis.com',            # Dataflow
    'iam.googleapis.com',                 # Identity and Access Management
    'iamcredentials.googleapis.com',      # IAM Service Account Credentials
    'cloudresourcemanager.googleapis.com', # Cloud Resource Manager
    'secretmanager.googleapis.com',       # Secret Manager
    'cloudkms.googleapis.com',            # Cloud Key Management Service
    'artifactregistry.googleapis.com',    # Artifact Registry
    'containerregistry.googleapis.com',   # Container Registry
    'cloudbuild.googleapis.com'           # Cloud Build
]

def check_service_status(service_name):
    """Check if a specific service is enabled."""
    try:
        # Try to get the service status
        cmd = f'gcloud services list --filter="name:{service_name}" --format=json 2>/dev/null'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0 and result.stdout:
            services = json.loads(result.stdout)
            if services and len(services) > 0:
                return True, "Enabled"
        return False, "Not enabled"
    except Exception as e:
        return False, f"Error checking: {str(e)}"

def enable_service(service_name):
    """Enable a GCP service."""
    try:
        print(f"  🔄 Enabling {service_name}...")
        cmd = f'gcloud services enable {service_name} --quiet 2>&1'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            return True, "Successfully enabled"
        else:
            return False, f"Failed: {result.stderr or result.stdout}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Main function to check and enable all required services."""
    print("=" * 80)
    print("🔍 GCP SERVICES STATUS CHECK FOR BQX ML V3")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)

    # Get current project
    try:
        result = subprocess.run('gcloud config get-value project',
                              shell=True, capture_output=True, text=True)
        project_id = result.stdout.strip()
        print(f"\n📋 Current Project: {project_id}")
    except:
        print("⚠️  Could not determine current project")
        print("Please ensure you're authenticated: gcloud auth login")
        return 1

    print(f"\n📊 Checking {len(REQUIRED_SERVICES)} required services...")
    print("-" * 80)

    enabled_services = []
    disabled_services = []
    error_services = []

    # Check each service
    for service in REQUIRED_SERVICES:
        is_enabled, status = check_service_status(service)

        service_short = service.replace('.googleapis.com', '')

        if is_enabled:
            enabled_services.append(service)
            print(f"✅ {service_short:30} : {status}")
        else:
            if "Error" in status:
                error_services.append(service)
                print(f"❌ {service_short:30} : {status}")
            else:
                disabled_services.append(service)
                print(f"⚠️  {service_short:30} : {status}")

    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"  ✅ Enabled:  {len(enabled_services)}/{len(REQUIRED_SERVICES)}")
    print(f"  ⚠️  Disabled: {len(disabled_services)}/{len(REQUIRED_SERVICES)}")
    print(f"  ❌ Errors:   {len(error_services)}/{len(REQUIRED_SERVICES)}")

    # List disabled services
    if disabled_services:
        print("\n⚠️  SERVICES THAT NEED TO BE ENABLED:")
        for service in disabled_services:
            print(f"  • {service}")

        print("\n🔧 Would you like to enable all disabled services? (y/n): ", end='')
        # Auto-confirm for automation
        response = 'y'
        print(response)

        if response.lower() == 'y':
            print("\n🚀 Enabling disabled services...")
            successfully_enabled = []
            failed_to_enable = []

            for service in disabled_services:
                success, message = enable_service(service)
                if success:
                    successfully_enabled.append(service)
                    print(f"  ✅ {service} - {message}")
                else:
                    failed_to_enable.append((service, message))
                    print(f"  ❌ {service} - {message}")

            # Final status
            print("\n" + "=" * 80)
            print("🎯 ENABLEMENT RESULTS")
            print("=" * 80)
            print(f"  ✅ Successfully enabled: {len(successfully_enabled)}")
            print(f"  ❌ Failed to enable:     {len(failed_to_enable)}")

            if failed_to_enable:
                print("\n❌ Failed services:")
                for service, error in failed_to_enable:
                    print(f"  • {service}: {error}")

    # Check for critical services
    print("\n" + "=" * 80)
    print("🔍 CRITICAL SERVICES CHECK")
    print("=" * 80)

    critical_services = [
        'aiplatform.googleapis.com',
        'bigquery.googleapis.com',
        'storage-component.googleapis.com',
        'compute.googleapis.com'
    ]

    all_critical_enabled = True
    for service in critical_services:
        service_short = service.replace('.googleapis.com', '')
        if service in enabled_services:
            print(f"  ✅ {service_short:25} : Required for core functionality")
        else:
            print(f"  ❌ {service_short:25} : CRITICAL - Must be enabled!")
            all_critical_enabled = False

    # Final verdict
    print("\n" + "=" * 80)
    print("🎯 FINAL STATUS")
    print("=" * 80)

    if len(enabled_services) == len(REQUIRED_SERVICES):
        print("✅ ALL GCP SERVICES ARE ACTIVATED!")
        print("The BQX ML V3 project has all required services enabled.")
        return 0
    elif all_critical_enabled:
        print("⚠️  PARTIAL ACTIVATION")
        print(f"{len(enabled_services)}/{len(REQUIRED_SERVICES)} services are activated.")
        print("Critical services are enabled, but some optional services are missing.")
        return 0
    else:
        print("❌ CRITICAL SERVICES MISSING")
        print("Some critical services are not activated.")
        print("The project cannot run without these services.")
        return 1

if __name__ == "__main__":
    exit(main())