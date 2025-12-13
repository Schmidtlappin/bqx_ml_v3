#!/usr/bin/env python3
"""
M008 Phase 4B: Rename TRI Tables with Wrong Alphabetical Order

Renames TRI tables where the three currencies are not in alphabetical order.

Author: Claude (Chief Engineer)
Date: 2025-12-13
Mandate: BQX-ML-M008 (Naming Standard Mandate)
Phase: M008 Phase 4B - TRI Table Renaming
"""

from google.cloud import bigquery
import re
import sys
from datetime import datetime


def get_tri_tables_needing_rename(client: bigquery.Client):
    """Get all TRI tables that violate alphabetical order."""

    query = """
    SELECT table_name
    FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.TABLES`
    WHERE table_name LIKE 'tri_%'
    ORDER BY table_name
    """

    tables = [row.table_name for row in client.query(query).result()]

    violations = []
    for table in tables:
        parts = table.split('_')
        if len(parts) >= 6:
            # tri_{type}_{variant}_{curr1}_{curr2}_{curr3}
            curr1, curr2, curr3 = parts[-3], parts[-2], parts[-1]
            currencies = [curr1, curr2, curr3]
            sorted_currencies = sorted(currencies)

            if currencies != sorted_currencies:
                # Generate correct name
                new_parts = parts[:-3] + sorted_currencies
                new_name = '_'.join(new_parts)

                violations.append({
                    'old_name': table,
                    'new_name': new_name,
                    'currencies_old': '_'.join(currencies),
                    'currencies_new': '_'.join(sorted_currencies)
                })

    return violations


def rename_table(client: bigquery.Client, old_name: str, new_name: str, dry_run: bool = False):
    """Rename a table using ALTER TABLE."""

    # Check if new name already exists
    check_query = f"""
    SELECT COUNT(*) as count
    FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.TABLES`
    WHERE table_name = '{new_name}'
    """

    result = list(client.query(check_query).result())[0]
    if result.count > 0:
        return {'status': 'SKIP', 'reason': f'Target name {new_name} already exists'}

    if dry_run:
        return {'status': 'DRY_RUN', 'old': old_name, 'new': new_name}

    try:
        # Execute rename
        rename_query = f"""
        ALTER TABLE `bqx-ml.bqx_ml_v3_features_v2.{old_name}`
        RENAME TO `{new_name}`
        """

        client.query(rename_query).result()
        return {'status': 'SUCCESS', 'old': old_name, 'new': new_name}

    except Exception as e:
        return {'status': 'ERROR', 'old': old_name, 'new': new_name, 'error': str(e)}


def main():
    print("=" * 80)
    print("M008 PHASE 4B: RENAME TRI TABLES (ALPHABETICAL ORDER)")
    print("=" * 80)
    print()
    print("Mandate: BQX-ML-M008 (Naming Standard Mandate)")
    print("Date:", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
    print()

    # Get mode from command-line args or default to asking
    if len(sys.argv) > 1:
        mode = sys.argv[1].strip().lower()
        print(f"Mode: {mode} (from command-line argument)")
        print()
    else:
        mode = input("Execute remediation? (yes/no/dry-run): ").strip().lower()

    if mode not in ['yes', 'no', 'dry-run']:
        print("Invalid input. Exiting.")
        print("Usage: python3 rename_tri_tables_m008.py [yes|no|dry-run]")
        return

    if mode == 'no':
        print("Aborted by user.")
        return

    dry_run = (mode == 'dry-run')
    if dry_run:
        print("⚠️  DRY RUN MODE - No tables will be renamed")
    else:
        print("⚠️  LIVE MODE - Tables will be renamed")

    print()

    client = bigquery.Client(project='bqx-ml', location='us-central1')

    # Step 1: Get tables needing rename
    print("Step 1: Finding TRI tables with wrong alphabetical order...")
    violations = get_tri_tables_needing_rename(client)

    print(f"  Found {len(violations)} tables needing rename")
    print()

    if len(violations) == 0:
        print("✅ No TRI tables need renaming - all are already in alphabetical order!")
        return

    # Step 2: Show sample
    print("Sample tables to be renamed (first 10):")
    for i, item in enumerate(violations[:10], 1):
        print(f"  {i}. {item['old_name']}")
        print(f"     → {item['new_name']}")

    if len(violations) > 10:
        print(f"  ... and {len(violations) - 10} more")
    print()

    # Step 3: Execute renames
    print("=" * 80)
    print("EXECUTING RENAMES")
    print("=" * 80)
    print()

    results = {
        'total': len(violations),
        'success': 0,
        'skip': 0,
        'error': 0,
        'renamed': [],
        'skipped': [],
        'errors': []
    }

    batch_size = 25
    batches = [violations[i:i+batch_size] for i in range(0, len(violations), batch_size)]

    for batch_num, batch in enumerate(batches, 1):
        print(f"Batch {batch_num}/{len(batches)} ({len(batch)} tables)")
        print("-" * 80)

        for item in batch:
            result = rename_table(client, item['old_name'], item['new_name'], dry_run)

            if result['status'] == 'SUCCESS' or result['status'] == 'DRY_RUN':
                results['success'] += 1
                results['renamed'].append(item)
                status_icon = "🔄" if dry_run else "✅"
                print(f"  {status_icon} RENAMED: {item['old_name']} → {item['new_name']}")
            elif result['status'] == 'SKIP':
                results['skip'] += 1
                results['skipped'].append({'item': item, 'reason': result['reason']})
                print(f"  ⚠️  SKIP: {item['old_name']} - {result['reason']}")
            else:
                results['error'] += 1
                results['errors'].append({'item': item, 'error': result.get('error', 'Unknown error')})
                print(f"  ❌ ERROR: {item['old_name']} - {result.get('error', 'Unknown error')[:100]}")

        print()

        # Pause between batches (not in dry-run)
        if not dry_run and batch_num < len(batches):
            import time
            time.sleep(1)

    # Step 4: Summary
    print("=" * 80)
    print("✅ M008 PHASE 4B COMPLETE")
    print("=" * 80)
    print()
    print(f"Total Tables:      {results['total']:>6}")
    print(f"Renamed:           {results['success']:>6}")
    print(f"Skipped:           {results['skip']:>6}")
    print(f"Errors:            {results['error']:>6}")
    print()

    if results['errors']:
        print("Errors encountered:")
        for err in results['errors'][:10]:
            print(f"  - {err['item']['old_name']}: {err['error'][:100]}")
        if len(results['errors']) > 10:
            print(f"  ... and {len(results['errors']) - 10} more")
        print()

    if results['skipped']:
        print("Tables skipped:")
        for skip in results['skipped'][:10]:
            print(f"  - {skip['item']['old_name']}: {skip['reason']}")
        if len(results['skipped']) > 10:
            print(f"  ... and {len(results['skipped']) - 10} more")
        print()

    if not dry_run:
        print("Next Step: M008 Phase 6 - Final Verification")
    else:
        print("Run with 'yes' to execute live renames")

    print("=" * 80)

    return results


if __name__ == '__main__':
    main()
