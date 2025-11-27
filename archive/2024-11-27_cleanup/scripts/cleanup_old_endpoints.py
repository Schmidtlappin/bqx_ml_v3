#!/usr/bin/env python3
"""
Cleanup old single-horizon endpoints from Vertex AI.
These endpoints use the old naming convention and need to be removed
before deploying the new multi-horizon architecture.
"""

import subprocess
import time

# Old endpoints to delete (single-horizon naming)
OLD_ENDPOINTS = [
    ('bqx-EUR_JPY_90-endpoint-sklearn', '1469113560964530176'),
    ('bqx-EUR_GBP_90-endpoint-sklearn', '7458901065367289856'),
    ('bqx-USD_JPY_90-endpoint-sklearn', '4160014338318401536'),
    ('bqx-GBP_USD_90-endpoint-sklearn', '3376950953109356544'),
    ('bqx-EUR_USD_90-endpoint-sklearn', '7233721083998765056'),
    ('bqx-USD_JPY_90-endpoint', '8945088942399553536'),
    ('bqx-GBP_USD_90-endpoint', '8233520201275015168'),
    ('bqx-EUR_USD_90-endpoint', '3007092833711554560'),
    ('bqx-EUR_USD_45-endpoint', '6343134257686249472'),
    ('bqx-EUR_USD_45-endpoint', '2471164478054465536'),
]

def delete_endpoint(endpoint_id, name):
    """Delete a Vertex AI endpoint."""
    print(f"\n🗑️  Deleting endpoint: {name} (ID: {endpoint_id})")

    cmd = [
        'gcloud', 'ai', 'endpoints', 'delete', endpoint_id,
        '--region=us-central1',
        '--project=bqx-ml',
        '--quiet'  # Skip confirmation
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Successfully deleted {name}")
            return True
        else:
            print(f"   ❌ Failed to delete {name}")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Error deleting {name}: {e}")
        return False

def main():
    print("=" * 80)
    print("🧹 CLEANING UP OLD SINGLE-HORIZON ENDPOINTS")
    print("=" * 80)
    print(f"\n📋 Found {len(OLD_ENDPOINTS)} old endpoints to delete")

    success_count = 0
    failed_count = 0

    for name, endpoint_id in OLD_ENDPOINTS:
        if delete_endpoint(endpoint_id, name):
            success_count += 1
        else:
            failed_count += 1

        # Small delay to avoid rate limiting
        time.sleep(2)

    print("\n" + "=" * 80)
    print("📊 CLEANUP SUMMARY")
    print("=" * 80)
    print(f"✅ Successfully deleted: {success_count} endpoints")
    print(f"❌ Failed to delete: {failed_count} endpoints")

    if failed_count == 0:
        print("\n🎉 All old endpoints cleaned up successfully!")
        print("Ready for multi-horizon deployment.")
    else:
        print("\n⚠️  Some endpoints could not be deleted.")
        print("Please check the errors and try again.")

    # Verify final state
    print("\n📋 Verifying final state...")
    cmd = ['gcloud', 'ai', 'endpoints', 'list', '--region=us-central1', '--project=bqx-ml', '--format=json']
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        import json
        endpoints = json.loads(result.stdout) if result.stdout else []
        if endpoints:
            print(f"⚠️  {len(endpoints)} endpoints still exist")
            for ep in endpoints:
                print(f"   - {ep.get('displayName', 'Unknown')}")
        else:
            print("✅ No endpoints remaining - workspace is clean!")

if __name__ == "__main__":
    main()