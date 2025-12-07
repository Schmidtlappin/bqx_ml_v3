#!/usr/bin/env python3
"""
Migrate P4 Cross-market Tables to new dataset with partitioning.
Tables: corr_ibkr, tri, var, csi, mkt
"""

from google.cloud import bigquery
import sys

PROJECT = 'bqx-ml'
OLD_DATASET = 'bqx_ml_v3_features'
NEW_DATASET = 'bqx_ml_v3_features_v2'

PAIRS = [
    'audcad', 'audchf', 'audjpy', 'audnzd', 'audusd',
    'cadchf', 'cadjpy', 'chfjpy',
    'euraud', 'eurcad', 'eurchf', 'eurgbp', 'eurjpy', 'eurnzd', 'eurusd',
    'gbpaud', 'gbpcad', 'gbpchf', 'gbpjpy', 'gbpnzd', 'gbpusd',
    'nzdcad', 'nzdchf', 'nzdjpy', 'nzdusd',
    'usdcad', 'usdchf', 'usdjpy'
]

CURRENCIES = ['aud', 'cad', 'chf', 'eur', 'gbp', 'jpy', 'nzd', 'usd']
ETFS = ['spy', 'vix', 'gld', 'uup', 'ewa', 'ewg', 'ewj', 'ewu']


def get_table_info(client, dataset, table_name):
    """Get row count and size for a table."""
    query = f"""
    SELECT row_count, size_bytes
    FROM `{PROJECT}.{dataset}.__TABLES__`
    WHERE table_id = '{table_name}'
    """
    result = list(client.query(query).result())
    if result:
        return result[0].row_count, result[0].size_bytes
    return 0, 0


def migrate_table(client, old_table, new_table, dry_run=False):
    """Migrate a single table with partitioning."""

    try:
        client.get_table(f"{PROJECT}.{NEW_DATASET}.{new_table}")
        return True, "already_exists"
    except:
        pass

    old_rows, old_bytes = get_table_info(client, OLD_DATASET, old_table)
    if old_rows == 0:
        return True, "empty"

    sql = f"""
    CREATE TABLE `{PROJECT}.{NEW_DATASET}.{new_table}`
    PARTITION BY DATE(interval_time)
    AS SELECT * FROM `{PROJECT}.{OLD_DATASET}.{old_table}`
    """

    if dry_run:
        print(f"  DRY: {new_table} ({old_rows:,} rows, {old_bytes/1024/1024:.1f} MB)")
        return True, "dry_run"

    try:
        job = client.query(sql)
        job.result()
        new_rows, _ = get_table_info(client, NEW_DATASET, new_table)

        if new_rows == old_rows:
            print(f"  OK: {new_table} ({new_rows:,} rows)")
            return True, "success"
        else:
            print(f"  MISMATCH: {new_table} ({old_rows} vs {new_rows})")
            return False, f"row_mismatch_{old_rows}_{new_rows}"

    except Exception as e:
        print(f"  ERROR: {new_table}: {e}")
        return False, str(e)


def main():
    dry_run = '--dry-run' in sys.argv

    if dry_run:
        print("DRY RUN MODE - No tables will be created")

    client = bigquery.Client(project=PROJECT, location='us-central1')

    results = {'success': 0, 'failed': [], 'skipped': 0}

    # CORR_IBKR tables (ETF correlations) - rename ibkr to etf
    print(f"\n{'='*60}\nMigrating CORR_IBKR (ETF correlation) tables\n{'='*60}")
    for pair in PAIRS:
        for etf in ETFS:
            # IDX variant
            old = f"corr_ibkr_{pair}_{etf}"
            new = f"corr_etf_idx_{pair}_{etf}"
            s, st = migrate_table(client, old, new, dry_run)
            if s:
                results['skipped' if st in ['already_exists', 'empty'] else 'success'] += 1
            else:
                results['failed'].append((new, st))

            # BQX variant
            old = f"corr_bqx_ibkr_{pair}_{etf}"
            new = f"corr_etf_bqx_{pair}_{etf}"
            s, st = migrate_table(client, old, new, dry_run)
            if s:
                results['skipped' if st in ['already_exists', 'empty'] else 'success'] += 1
            else:
                results['failed'].append((new, st))

    # TRI tables (triangular arbitrage)
    print(f"\n{'='*60}\nMigrating TRI (triangular arbitrage) tables\n{'='*60}")
    query = f"""
    SELECT table_id FROM `{PROJECT}.{OLD_DATASET}.__TABLES__`
    WHERE table_id LIKE 'tri_%'
    ORDER BY table_id
    """
    tri_tables = [r.table_id for r in client.query(query).result()]

    for old in tri_tables:
        # Parse: tri_{source}_{bqx?}_{pair1}_{pair2}_{pair3}
        parts = old.split('_')
        if 'bqx' in parts:
            new = old  # Keep BQX as is
        else:
            # Insert idx after source
            source = parts[1]
            rest = '_'.join(parts[2:])
            new = f"tri_{source}_idx_{rest}"

        s, st = migrate_table(client, old, new, dry_run)
        if s:
            results['skipped' if st in ['already_exists', 'empty'] else 'success'] += 1
        else:
            results['failed'].append((new, st))

    # VAR tables (currency variance)
    print(f"\n{'='*60}\nMigrating VAR (variance) tables\n{'='*60}")
    query = f"""
    SELECT table_id FROM `{PROJECT}.{OLD_DATASET}.__TABLES__`
    WHERE table_id LIKE 'var_%'
    ORDER BY table_id
    """
    var_tables = [r.table_id for r in client.query(query).result()]

    for old in var_tables:
        parts = old.split('_')
        if 'bqx' in parts:
            new = old
        else:
            source = parts[1]
            currency = parts[2]
            new = f"var_{source}_idx_{currency}"

        s, st = migrate_table(client, old, new, dry_run)
        if s:
            results['skipped' if st in ['already_exists', 'empty'] else 'success'] += 1
        else:
            results['failed'].append((new, st))

    # CSI tables (currency strength index)
    print(f"\n{'='*60}\nMigrating CSI (currency strength) tables\n{'='*60}")
    query = f"""
    SELECT table_id FROM `{PROJECT}.{OLD_DATASET}.__TABLES__`
    WHERE table_id LIKE 'csi_%'
    ORDER BY table_id
    """
    csi_tables = [r.table_id for r in client.query(query).result()]

    for old in csi_tables:
        parts = old.split('_')
        if 'bqx' in parts:
            new = old
        else:
            source = parts[1]
            currency = parts[2]
            new = f"csi_{source}_idx_{currency}"

        s, st = migrate_table(client, old, new, dry_run)
        if s:
            results['skipped' if st in ['already_exists', 'empty'] else 'success'] += 1
        else:
            results['failed'].append((new, st))

    # MKT tables (market-wide)
    print(f"\n{'='*60}\nMigrating MKT (market-wide) tables\n{'='*60}")
    query = f"""
    SELECT table_id FROM `{PROJECT}.{OLD_DATASET}.__TABLES__`
    WHERE table_id LIKE 'mkt_%'
    ORDER BY table_id
    """
    mkt_tables = [r.table_id for r in client.query(query).result()]

    for old in mkt_tables:
        parts = old.split('_')
        if 'bqx' in parts:
            new = old
        else:
            source = parts[1]
            new = f"mkt_{source}_idx_all"

        s, st = migrate_table(client, old, new, dry_run)
        if s:
            results['skipped' if st in ['already_exists', 'empty'] else 'success'] += 1
        else:
            results['failed'].append((new, st))

    # Summary
    print(f"\n{'='*60}")
    print("CROSS-MARKET MIGRATION SUMMARY")
    print(f"{'='*60}")
    print(f"Successful: {results['success']}")
    print(f"Skipped: {results['skipped']}")
    print(f"Failed: {len(results['failed'])}")

    if results['failed']:
        print("\nFailed tables:")
        for name, error in results['failed'][:20]:
            print(f"  - {name}: {error}")

    return results


if __name__ == "__main__":
    main()
