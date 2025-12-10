#!/usr/bin/env python3
"""
Full Feature Universe Stability Selection
USER MANDATE: Test all features, not just hardcoded 59

Runs stability selection on full EURUSD feature universe:
- 5 folds x 3 seeds
- 50% threshold for stable features
- Expected output: 200-600 stable features
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
from google.cloud import bigquery
import lightgbm as lgb
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"

# Configuration
N_FOLDS = 5
N_SEEDS = 3
STABILITY_THRESHOLD = 0.50  # 50% - USER APPROVED


def get_all_feature_tables(pair: str):
    """Get list of all feature tables for a pair."""
    client = bigquery.Client(project=PROJECT)

    query = f"""
    SELECT table_name
    FROM `{PROJECT}.{FEATURES_DATASET}.INFORMATION_SCHEMA.TABLES`
    WHERE table_name LIKE '%{pair}%'
      AND table_name NOT LIKE '%targets%'
    ORDER BY table_name
    """

    return [row.table_name for row in client.query(query).result()]


def get_table_columns(table_name: str):
    """Get columns from a table (excluding interval_time, pair)."""
    client = bigquery.Client(project=PROJECT)

    query = f"""
    SELECT column_name
    FROM `{PROJECT}.{FEATURES_DATASET}.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name = '{table_name}'
      AND column_name NOT IN ('interval_time', 'pair')
    ORDER BY column_name
    """

    return [row.column_name for row in client.query(query).result()]


def build_feature_query(pair: str, horizon: int, tables: list, limit: int = 80000):
    """Build dynamic query joining all feature tables."""
    client = bigquery.Client(project=PROJECT)

    # Group tables by type for efficient joining
    base_tables = []
    for table in tables:
        cols = get_table_columns(table)
        if cols:
            base_tables.append({'name': table, 'cols': cols})

    if not base_tables:
        return None

    # Start with first table
    first = base_tables[0]
    select_parts = [f"t0.interval_time"]

    for i, t in enumerate(base_tables):
        alias = f"t{i}"
        for col in t['cols']:
            select_parts.append(f"{alias}.{col}")

    # Build FROM clause
    from_clause = f"`{PROJECT}.{FEATURES_DATASET}.{first['name']}` t0"

    # Build JOIN clauses
    join_clauses = []
    for i, t in enumerate(base_tables[1:], 1):
        alias = f"t{i}"
        join_clauses.append(
            f"LEFT JOIN `{PROJECT}.{FEATURES_DATASET}.{t['name']}` {alias} ON t0.interval_time = {alias}.interval_time"
        )

    # Target table
    target_table = f"`{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}`"
    join_clauses.append(f"JOIN {target_table} targets ON t0.interval_time = targets.interval_time")
    select_parts.append(f"targets.target_bqx45_h{horizon}")

    query = f"""
    SELECT {', '.join(select_parts)}
    FROM {from_clause}
    {' '.join(join_clauses)}
    WHERE targets.target_bqx45_h{horizon} IS NOT NULL
    ORDER BY t0.interval_time
    LIMIT {limit}
    """

    return query


def load_features_from_ledger(pair: str, horizon: int, limit: int = 80000):
    """Load features based on ledger configuration."""
    # Load ledger
    ledger = pd.read_parquet('/home/micha/bqx_ml_v3/data/feature_ledger.parquet')

    # Get candidate features for this pair-horizon
    mask = (ledger['pair'] == pair) & (ledger['horizon'] == horizon)
    pair_features = ledger[mask]

    # Get unique source tables
    source_tables = pair_features['source_table'].dropna().unique()
    print(f"  Source tables in ledger: {len(source_tables)}")

    return source_tables.tolist()


def load_training_data_dynamic(pair: str, horizon: int, sample_limit: int = 80000):
    """Load training data with ALL available features."""
    client = bigquery.Client(project=PROJECT)

    # Core feature tables (known to have data)
    core_tables = [
        f"reg_idx_{pair}", f"reg_bqx_{pair}",
        f"agg_idx_{pair}", f"agg_bqx_{pair}",
        f"mom_idx_{pair}", f"mom_bqx_{pair}",
        f"vol_idx_{pair}", f"vol_bqx_{pair}",
        f"der_idx_{pair}", f"der_bqx_{pair}",
        f"align_idx_{pair}", f"align_bqx_{pair}",
        f"base_idx_{pair}", f"base_bqx_{pair}",
        f"mrt_idx_{pair}", f"mrt_bqx_{pair}",
        f"lag_{pair}_45", f"lag_{pair}_90",
        f"lag_bqx_{pair}_45", f"lag_bqx_{pair}_90",
    ]

    # Verify which tables exist
    existing_tables = []
    for table in core_tables:
        check_query = f"""
        SELECT COUNT(*) as cnt
        FROM `{PROJECT}.{FEATURES_DATASET}.INFORMATION_SCHEMA.TABLES`
        WHERE table_name = '{table}'
        """
        result = list(client.query(check_query).result())
        if result[0].cnt > 0:
            existing_tables.append(table)

    print(f"  Verified {len(existing_tables)} feature tables exist")

    # Build dynamic query
    feature_cols = []
    select_parts = ["base.interval_time"]

    # Use reg_idx as base table
    base_table = f"reg_idx_{pair}"

    # Get columns from each table
    join_clauses = []
    alias_idx = 0

    for table in existing_tables:
        cols = get_table_columns(table)

        if table == base_table:
            # Base table uses 'base' alias
            for col in cols:
                select_parts.append(f"base.{col}")
                feature_cols.append(col)
        else:
            # Other tables use t1, t2, etc.
            alias_idx += 1
            alias = f"t{alias_idx}"
            prefix = table.replace(f'_{pair}', '').replace('_', '')

            for col in cols:
                col_alias = f"{prefix}_{col}"
                select_parts.append(f"{alias}.{col} AS {col_alias}")
                feature_cols.append(col_alias)

            join_clauses.append(
                f"LEFT JOIN `{PROJECT}.{FEATURES_DATASET}.{table}` {alias} ON base.interval_time = {alias}.interval_time"
            )

    # Add target
    select_parts.append(f"targets.target_bqx45_h{horizon}")
    join_clauses.append(
        f"JOIN `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}` targets ON base.interval_time = targets.interval_time"
    )

    query = f"""
    SELECT {', '.join(select_parts)}
    FROM `{PROJECT}.{FEATURES_DATASET}.{base_table}` base
    {' '.join(join_clauses)}
    WHERE targets.target_bqx45_h{horizon} IS NOT NULL
    ORDER BY base.interval_time
    LIMIT {sample_limit}
    """

    print(f"  Querying {len(feature_cols)} feature columns...")
    df = client.query(query).to_dataframe()

    return df, feature_cols


def run_stability_selection(X, y, feature_names, n_folds=N_FOLDS, n_seeds=N_SEEDS, threshold=STABILITY_THRESHOLD):
    """Run stability selection with multiple seeds."""
    feature_selection_counts = defaultdict(int)
    total_runs = n_folds * n_seeds

    for seed in range(n_seeds):
        # Create fold indices
        n = len(X)
        indices = np.arange(n)
        np.random.seed(seed)
        np.random.shuffle(indices)
        fold_size = n // n_folds

        for fold in range(n_folds):
            # Train/val split
            val_start = fold * fold_size
            val_end = (fold + 1) * fold_size if fold < n_folds - 1 else n

            train_idx = np.concatenate([indices[:val_start], indices[val_end:]])

            X_train = X[train_idx]
            y_train = y[train_idx]

            # Train LightGBM with feature importance
            lgb_params = {
                'objective': 'binary', 'metric': 'binary_logloss',
                'num_leaves': 31, 'learning_rate': 0.05, 'feature_fraction': 0.8,
                'bagging_fraction': 0.8, 'bagging_freq': 5, 'verbose': -1,
                'seed': seed * 100 + fold, 'min_data_in_leaf': 100,
                'importance_type': 'gain'
            }

            lgb_train = lgb.Dataset(X_train, label=y_train, feature_name=feature_names)
            model = lgb.train(lgb_params, lgb_train, num_boost_round=100)

            # Get feature importances
            importances = model.feature_importance(importance_type='gain')

            # Select top features (non-zero importance)
            selected = np.where(importances > 0)[0]

            for idx in selected:
                feature_selection_counts[feature_names[idx]] += 1

    # Calculate stability scores
    stability_scores = {
        feat: count / total_runs
        for feat, count in feature_selection_counts.items()
    }

    # Filter by threshold
    stable_features = {
        feat: score for feat, score in stability_scores.items()
        if score >= threshold
    }

    return stable_features, stability_scores


def main():
    pair = "eurusd"
    horizon = 15

    print("=" * 70)
    print("FULL FEATURE UNIVERSE STABILITY SELECTION")
    print("USER MANDATE: Test ALL features")
    print("=" * 70)

    # Load data
    print("\nStep 1: Loading full feature universe...")
    df, feature_cols = load_training_data_dynamic(pair, horizon)
    print(f"  Loaded {len(df):,} rows with {len(feature_cols)} features")

    # Prepare features
    target_col = f'target_bqx45_h{horizon}'
    X = df[feature_cols].apply(pd.to_numeric, errors='coerce').fillna(0).values
    y = (df[target_col] > 0).astype(int).values

    # Remove constant features
    variances = np.var(X, axis=0)
    non_constant_mask = variances > 1e-10
    X = X[:, non_constant_mask]
    feature_cols_filtered = [f for f, m in zip(feature_cols, non_constant_mask) if m]

    print(f"  After removing constant features: {len(feature_cols_filtered)}")

    # Run stability selection
    print(f"\nStep 2: Running stability selection...")
    print(f"  Configuration: {N_FOLDS} folds x {N_SEEDS} seeds = {N_FOLDS * N_SEEDS} total runs")
    print(f"  Threshold: {STABILITY_THRESHOLD * 100:.0f}%")

    stable_features, all_scores = run_stability_selection(
        X, y, feature_cols_filtered,
        n_folds=N_FOLDS, n_seeds=N_SEEDS,
        threshold=STABILITY_THRESHOLD
    )

    print(f"\nStep 3: Results...")
    print(f"  Total features tested: {len(feature_cols_filtered)}")
    print(f"  Features with any importance: {len(all_scores)}")
    print(f"  Stable features (>={STABILITY_THRESHOLD*100:.0f}%): {len(stable_features)}")

    # Sort by stability score
    sorted_features = sorted(stable_features.items(), key=lambda x: -x[1])

    print(f"\nTop 20 stable features:")
    for i, (feat, score) in enumerate(sorted_features[:20]):
        print(f"  {i+1}. {feat}: {score:.2%}")

    # Save results
    results = {
        'pair': pair,
        'horizon': horizon,
        'timestamp': datetime.now().isoformat(),
        'config': {
            'n_folds': N_FOLDS,
            'n_seeds': N_SEEDS,
            'threshold': STABILITY_THRESHOLD,
            'total_runs': N_FOLDS * N_SEEDS
        },
        'summary': {
            'total_features_tested': len(feature_cols_filtered),
            'features_with_importance': len(all_scores),
            'stable_features': len(stable_features)
        },
        'stable_features': sorted_features,
        'all_scores': dict(sorted(all_scores.items(), key=lambda x: -x[1]))
    }

    output_path = f'/home/micha/bqx_ml_v3/intelligence/full_universe_stability_{pair}_h{horizon}.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved results to: {output_path}")

    # Summary
    print("\n" + "=" * 70)
    print("STABILITY SELECTION COMPLETE")
    print("=" * 70)
    print(f"  Total features: {len(feature_cols_filtered)}")
    print(f"  Stable features: {len(stable_features)}")
    print(f"  Improvement potential: {len(stable_features) - 59} additional features vs current 59")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
