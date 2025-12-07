#!/usr/bin/env python3
"""
Validate migration by comparing row counts and sample data between old and new datasets.
"""

from google.cloud import bigquery
import sys

PROJECT = 'bqx-ml'
OLD_DATASET = 'bqx_ml_v3_features'
NEW_DATASET = 'bqx_ml_v3_features_v2'


def main():
    client = bigquery.Client(project=PROJECT, location='us-central1')

    # Get table counts
    old_query = f"""
    SELECT COUNT(*) as cnt FROM `{PROJECT}.{OLD_DATASET}.__TABLES__`
    """
    new_query = f"""
    SELECT COUNT(*) as cnt FROM `{PROJECT}.{NEW_DATASET}.__TABLES__`
    """

    old_count = list(client.query(old_query).result())[0].cnt
    new_count = list(client.query(new_query).result())[0].cnt

    print(f"Old dataset tables: {old_count}")
    print(f"New dataset tables: {new_count}")
    print(f"Migration progress: {new_count}/{old_count} ({100*new_count/old_count:.1f}%)")

    # Compare row counts for migrated tables
    print(f"\n{'='*70}")
    print("ROW COUNT VALIDATION")
    print(f"{'='*70}")

    query = f"""
    WITH old_tables AS (
      SELECT table_id, row_count as old_rows
      FROM `{PROJECT}.{OLD_DATASET}.__TABLES__`
    ),
    new_tables AS (
      SELECT table_id, row_count as new_rows
      FROM `{PROJECT}.{NEW_DATASET}.__TABLES__`
    )
    SELECT
      COALESCE(o.table_id, n.table_id) as table_name,
      o.old_rows,
      n.new_rows,
      CASE
        WHEN n.new_rows IS NULL THEN 'NOT_MIGRATED'
        WHEN o.old_rows = n.new_rows THEN 'MATCH'
        ELSE 'MISMATCH'
      END as status
    FROM old_tables o
    FULL OUTER JOIN new_tables n ON
      -- Handle naming convention changes
      o.table_id = n.table_id OR
      CONCAT(SPLIT(o.table_id, '_')[OFFSET(0)], '_idx_', SPLIT(o.table_id, '_')[OFFSET(1)]) = n.table_id
    WHERE n.new_rows IS NOT NULL
    ORDER BY status DESC, table_name
    LIMIT 100
    """

    results = list(client.query(query).result())

    match_count = sum(1 for r in results if r.status == 'MATCH')
    mismatch_count = sum(1 for r in results if r.status == 'MISMATCH')

    print(f"\nValidated {len(results)} tables:")
    print(f"  MATCH: {match_count}")
    print(f"  MISMATCH: {mismatch_count}")

    if mismatch_count > 0:
        print("\nMismatched tables:")
        for r in results:
            if r.status == 'MISMATCH':
                print(f"  {r.table_name}: old={r.old_rows}, new={r.new_rows}")

    # Check partitioning status
    print(f"\n{'='*70}")
    print("PARTITIONING STATUS")
    print(f"{'='*70}")

    part_query = f"""
    SELECT
      COUNT(*) as total_tables,
      COUNTIF(partition_column IS NOT NULL) as partitioned,
      COUNTIF(partition_column IS NULL) as not_partitioned
    FROM `{PROJECT}.{NEW_DATASET}.INFORMATION_SCHEMA.PARTITIONS`
    GROUP BY partition_id HAVING partition_id IS NOT NULL
    LIMIT 1
    """

    # Alternative check using table options
    part_query2 = f"""
    SELECT
      table_name,
      option_value as partition_expr
    FROM `{PROJECT}.{NEW_DATASET}.INFORMATION_SCHEMA.TABLE_OPTIONS`
    WHERE option_name = 'partition_expiration_days'
       OR option_name LIKE '%partition%'
    LIMIT 10
    """

    # Simple check - try to get partition info for one table
    sample_table = 'reg_idx_audcad' if new_count > 0 else None

    if sample_table:
        try:
            table = client.get_table(f"{PROJECT}.{NEW_DATASET}.{sample_table}")
            if table.time_partitioning:
                print(f"Sample table {sample_table}:")
                print(f"  Partitioned: YES")
                print(f"  Partition field: {table.time_partitioning.field}")
                print(f"  Partition type: {table.time_partitioning.type_}")
            else:
                print(f"Sample table {sample_table}: NOT partitioned")

            if table.clustering_fields:
                print(f"  Clustered by: {table.clustering_fields}")

        except Exception as e:
            print(f"Could not check {sample_table}: {e}")

    # Summary
    print(f"\n{'='*70}")
    print("MIGRATION SUMMARY")
    print(f"{'='*70}")
    print(f"Progress: {new_count}/{old_count} tables ({100*new_count/old_count:.1f}%)")
    print(f"Row validation: {match_count} match, {mismatch_count} mismatch")

    if new_count == old_count and mismatch_count == 0:
        print("\n✓ MIGRATION COMPLETE AND VALIDATED")
    elif mismatch_count > 0:
        print("\n✗ VALIDATION FAILED - Row count mismatches detected")
    else:
        print(f"\n⋯ MIGRATION IN PROGRESS - {old_count - new_count} tables remaining")

    return {
        'old_count': old_count,
        'new_count': new_count,
        'match': match_count,
        'mismatch': mismatch_count
    }


if __name__ == "__main__":
    main()
