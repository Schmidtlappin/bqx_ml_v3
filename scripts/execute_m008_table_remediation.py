#!/usr/bin/env python3
"""
M008 Table Remediation Execution

Executes remediation for all 475 non-compliant tables:
- DELETE 285 PATTERN_VIOLATION tables (duplicates)
- RENAME 190 ALPHABETICAL_ORDER_VIOLATION tables (wrong order)

Author: Claude (Chief Engineer)
Date: 2025-12-13
Mandate: BQX-ML-M008 (Naming Standard Mandate)
Phase: M008 Phase 4 - Execution
"""

from google.cloud import bigquery
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple


def load_violations() -> Dict:
    """Load violation patterns from Phase 1 audit."""
    with open('docs/M008_VIOLATION_PATTERNS.json') as f:
        return json.load(f)


def verify_compliant_versions_exist(client: bigquery.Client, table_name: str) -> Tuple[bool, List[str]]:
    """
    Verify that compliant BQX and IDX versions exist for a PATTERN_VIOLATION table.

    Returns:
        (has_compliant_versions, list_of_compliant_tables)
    """
    # Extract type and pair from table name
    parts = table_name.split('_')
    if len(parts) < 2:
        return False, []

    table_type = parts[0]
    pair = parts[1]

    # Generate expected compliant names
    bqx_name = f"{table_type}_bqx_{pair}"
    idx_name = f"{table_type}_idx_{pair}"

    # Check if they exist
    query = f"""
    SELECT table_name
    FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.TABLES`
    WHERE table_name IN ('{bqx_name}', '{idx_name}')
    ORDER BY table_name
    """

    result = list(client.query(query).result())
    existing = [row.table_name for row in result]

    # Both must exist for safe deletion
    return len(existing) == 2, existing


def delete_pattern_violation_tables(client: bigquery.Client, violations: List[Dict], dry_run: bool = False) -> Dict:
    """
    Delete PATTERN_VIOLATION tables (duplicates).

    Args:
        client: BigQuery client
        violations: List of PATTERN_VIOLATION tables
        dry_run: If True, only simulate (don't actually delete)

    Returns:
        Dict with execution results
    """
    print("=" * 80)
    print("PHASE 4A: DELETE PATTERN_VIOLATION TABLES (285 duplicates)")
    print("=" * 80)
    print()

    results = {
        'total': len(violations),
        'verified': 0,
        'deleted': 0,
        'skipped': 0,
        'errors': [],
        'deleted_tables': [],
        'skipped_tables': []
    }

    batch_size = 50
    batches = [violations[i:i+batch_size] for i in range(0, len(violations), batch_size)]

    for batch_num, batch in enumerate(batches, 1):
        print(f"Batch {batch_num}/{len(batches)} ({len(batch)} tables)")
        print("-" * 80)

        for item in batch:
            table_name = item['table_name']

            # Safety check: Verify compliant versions exist
            has_compliant, compliant_tables = verify_compliant_versions_exist(client, table_name)

            if not has_compliant:
                print(f"  ⚠️  SKIP: {table_name} - missing compliant versions")
                results['skipped'] += 1
                results['skipped_tables'].append({
                    'table': table_name,
                    'reason': 'Missing compliant versions'
                })
                continue

            results['verified'] += 1

            if dry_run:
                print(f"  🔍 DRY RUN: Would delete {table_name} (compliant: {compliant_tables})")
                results['deleted'] += 1
                results['deleted_tables'].append(table_name)
            else:
                try:
                    # Execute DELETE
                    drop_query = f"DROP TABLE `bqx-ml.bqx_ml_v3_features_v2.{table_name}`"
                    client.query(drop_query).result()

                    print(f"  ✅ DELETED: {table_name}")
                    results['deleted'] += 1
                    results['deleted_tables'].append(table_name)

                except Exception as e:
                    error_msg = f"Failed to delete {table_name}: {str(e)}"
                    print(f"  ❌ ERROR: {error_msg}")
                    results['errors'].append(error_msg)

        print()

        # Brief pause between batches
        if not dry_run and batch_num < len(batches):
            time.sleep(1)

    print("=" * 80)
    print(f"PHASE 4A COMPLETE: {results['deleted']}/{results['total']} deleted")
    print(f"  Verified: {results['verified']}")
    print(f"  Deleted: {results['deleted']}")
    print(f"  Skipped: {results['skipped']}")
    print(f"  Errors: {len(results['errors'])}")
    print("=" * 80)
    print()

    return results


def rename_alphabetical_violation_tables(client: bigquery.Client, violations: List[Dict], dry_run: bool = False) -> Dict:
    """
    Rename ALPHABETICAL_ORDER_VIOLATION tables (wrong currency order).

    Args:
        client: BigQuery client
        violations: List of ALPHABETICAL_ORDER_VIOLATION tables
        dry_run: If True, only simulate (don't actually rename)

    Returns:
        Dict with execution results
    """
    print("=" * 80)
    print("PHASE 4B: RENAME ALPHABETICAL_ORDER_VIOLATION TABLES (190 tables)")
    print("=" * 80)
    print()

    results = {
        'total': len(violations),
        'verified': 0,
        'renamed': 0,
        'skipped': 0,
        'errors': [],
        'renamed_tables': []
    }

    batch_size = 50
    batches = [violations[i:i+batch_size] for i in range(0, len(violations), batch_size)]

    for batch_num, batch in enumerate(batches, 1):
        print(f"Batch {batch_num}/{len(batches)} ({len(batch)} tables)")
        print("-" * 80)

        for item in batch:
            old_name = item['table_name']
            new_name = item['suggested_fix']

            # Skip if already compliant (suggested_fix == table_name)
            if old_name == new_name:
                print(f"  ⚠️  SKIP: {old_name} - already compliant")
                results['skipped'] += 1
                continue

            # Safety check: Verify new name doesn't already exist
            check_query = f"""
            SELECT COUNT(*) as count
            FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.TABLES`
            WHERE table_name = '{new_name}'
            """

            check_result = list(client.query(check_query).result())[0]
            if check_result.count > 0:
                print(f"  ⚠️  SKIP: {old_name} - {new_name} already exists")
                results['skipped'] += 1
                continue

            results['verified'] += 1

            if dry_run:
                print(f"  🔍 DRY RUN: Would rename {old_name} → {new_name}")
                results['renamed'] += 1
                results['renamed_tables'].append({
                    'old': old_name,
                    'new': new_name
                })
            else:
                try:
                    # Execute RENAME
                    rename_query = f"""
                    ALTER TABLE `bqx-ml.bqx_ml_v3_features_v2.{old_name}`
                    RENAME TO `{new_name}`
                    """
                    client.query(rename_query).result()

                    print(f"  ✅ RENAMED: {old_name} → {new_name}")
                    results['renamed'] += 1
                    results['renamed_tables'].append({
                        'old': old_name,
                        'new': new_name
                    })

                except Exception as e:
                    error_msg = f"Failed to rename {old_name}: {str(e)}"
                    print(f"  ❌ ERROR: {error_msg}")
                    results['errors'].append(error_msg)

        print()

        # Brief pause between batches
        if not dry_run and batch_num < len(batches):
            time.sleep(1)

    print("=" * 80)
    print(f"PHASE 4B COMPLETE: {results['renamed']}/{results['total']} renamed")
    print(f"  Verified: {results['verified']}")
    print(f"  Renamed: {results['renamed']}")
    print(f"  Skipped: {results['skipped']}")
    print(f"  Errors: {len(results['errors'])}")
    print("=" * 80)
    print()

    return results


def verify_remediation(client: bigquery.Client) -> Dict:
    """
    Verify table remediation success.

    Returns:
        Dict with verification results
    """
    print("=" * 80)
    print("PHASE 4C: VERIFICATION")
    print("=" * 80)
    print()

    # Re-run compliance check
    from scripts.audit_m008_table_compliance import validate_m008_table_name

    tables_query = """
    SELECT table_name
    FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.TABLES`
    WHERE table_type = 'BASE TABLE'
    ORDER BY table_name
    """

    tables = [row.table_name for row in client.query(tables_query).result()]

    compliant = 0
    violations = []

    for table in tables:
        is_valid, violation_type, violation_details = validate_m008_table_name(table)
        if is_valid:
            compliant += 1
        else:
            violations.append({
                'table': table,
                'type': violation_type,
                'details': violation_details
            })

    total = len(tables)
    compliance_pct = (compliant / total * 100) if total > 0 else 0

    print(f"Total Tables:     {total:>6}")
    print(f"Compliant:        {compliant:>6} ({compliance_pct:.2f}%)")
    print(f"Non-Compliant:    {len(violations):>6} ({(100-compliance_pct):.2f}%)")
    print()

    if len(violations) > 0:
        print("Remaining Violations:")
        for v in violations[:10]:
            print(f"  - {v['table']}: {v['type']}")
        if len(violations) > 10:
            print(f"  ... and {len(violations) - 10} more")
    else:
        print("🎉 100% TABLE COMPLIANCE ACHIEVED!")

    print()
    print("=" * 80)

    return {
        'total_tables': total,
        'compliant_tables': compliant,
        'non_compliant_tables': len(violations),
        'compliance_percentage': compliance_pct,
        'remaining_violations': violations
    }


def main():
    print("=" * 80)
    print("M008 TABLE REMEDIATION EXECUTION")
    print("=" * 80)
    print()
    print("Mandate: BQX-ML-M008 (Naming Standard Mandate)")
    print("Phase: M008 Phase 4 - Table Remediation")
    print("Date:", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
    print()
    print("Strategy:")
    print("  - DELETE 285 PATTERN_VIOLATION tables (duplicates)")
    print("  - RENAME 190 ALPHABETICAL_ORDER_VIOLATION tables (wrong order)")
    print()

    # Ask for confirmation
    response = input("Execute remediation? (yes/no/dry-run): ").strip().lower()

    if response not in ['yes', 'y', 'dry-run', 'dry']:
        print("Remediation cancelled.")
        return

    dry_run = response in ['dry-run', 'dry']

    if dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made\n")
    else:
        print("\n⚠️  LIVE MODE - Tables will be deleted/renamed\n")

    client = bigquery.Client(project='bqx-ml', location='us-central1')

    # Step 1: Load violations
    print("Step 1: Loading violation patterns...")
    violations = load_violations()

    pattern_violations = violations['violations_by_type'].get('PATTERN_VIOLATION', [])
    alphabetical_violations = violations['violations_by_type'].get('ALPHABETICAL_ORDER_VIOLATION', [])

    print(f"  PATTERN_VIOLATION: {len(pattern_violations)} tables")
    print(f"  ALPHABETICAL_ORDER_VIOLATION: {len(alphabetical_violations)} tables")
    print()

    # Step 2: Delete PATTERN_VIOLATION tables
    delete_results = delete_pattern_violation_tables(client, pattern_violations, dry_run)

    # Step 3: Rename ALPHABETICAL_ORDER_VIOLATION tables
    rename_results = rename_alphabetical_violation_tables(client, alphabetical_violations, dry_run)

    # Step 4: Verify if not dry run
    if not dry_run:
        verification_results = verify_remediation(client)
    else:
        verification_results = None

    # Step 5: Generate execution log
    log = {
        'generated': datetime.utcnow().isoformat() + 'Z',
        'dry_run': dry_run,
        'delete_results': delete_results,
        'rename_results': rename_results,
        'verification_results': verification_results
    }

    log_path = 'docs/M008_REMEDIATION_LOG.json'
    with open(log_path, 'w') as f:
        json.dump(log, f, indent=2)

    print()
    print("=" * 80)
    print("✅ M008 TABLE REMEDIATION COMPLETE")
    print("=" * 80)
    print()
    print("Results:")
    print(f"  Deleted: {delete_results['deleted']}/{delete_results['total']} PATTERN_VIOLATION tables")
    print(f"  Renamed: {rename_results['renamed']}/{rename_results['total']} ALPHABETICAL_ORDER_VIOLATION tables")
    print()

    if verification_results:
        print(f"  Final Compliance: {verification_results['compliance_percentage']:.2f}%")
        print(f"  Remaining Violations: {verification_results['non_compliant_tables']}")
        print()

    print(f"Execution log: {log_path}")
    print()

    if not dry_run and verification_results and verification_results['compliance_percentage'] == 100.0:
        print("🎉 100% TABLE COMPLIANCE ACHIEVED!")

    return log


if __name__ == '__main__':
    main()
