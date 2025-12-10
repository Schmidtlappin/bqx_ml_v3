#!/usr/bin/env python3
"""
Full Feature Universe Stability Selection V2
USER MANDATE: Test all features, not just hardcoded 59

Simplified approach: Query tables incrementally, merge locally.
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
STABILITY_THRESHOLD = 0.50


def load_table_data(table_name: str, pair: str, limit: int = 80000):
    """Load data from a single table."""
    client = bigquery.Client(project=PROJECT)

    query = f"""
    SELECT *
    FROM `{PROJECT}.{FEATURES_DATASET}.{table_name}`
    ORDER BY interval_time
    LIMIT {limit}
    """

    try:
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        print(f"  Warning: Could not load {table_name}: {e}")
        return None


def load_all_features(pair: str, horizon: int, limit: int = 80000):
    """Load all features by querying tables individually and merging."""
    client = bigquery.Client(project=PROJECT)

    # Core tables to load
    tables_to_load = [
        f"reg_idx_{pair}",
        f"reg_bqx_{pair}",
        f"agg_idx_{pair}",
        f"agg_bqx_{pair}",
        f"mom_idx_{pair}",
        f"mom_bqx_{pair}",
        f"vol_idx_{pair}",
        f"vol_bqx_{pair}",
        f"der_idx_{pair}",
        f"der_bqx_{pair}",
        f"align_idx_{pair}",
        f"align_bqx_{pair}",
        f"base_idx_{pair}",
        f"base_bqx_{pair}",
        f"mrt_idx_{pair}",
        f"mrt_bqx_{pair}",
        f"rev_idx_{pair}",
        f"rev_bqx_{pair}",
    ]

    # Load targets first
    print("  Loading targets...")
    target_query = f"""
    SELECT interval_time, target_bqx45_h{horizon}
    FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}`
    WHERE target_bqx45_h{horizon} IS NOT NULL
    ORDER BY interval_time
    LIMIT {limit}
    """
    merged = client.query(target_query).to_dataframe()
    print(f"  Targets: {len(merged)} rows")

    # Load each feature table
    for table in tables_to_load:
        print(f"  Loading {table}...")
        df = load_table_data(table, pair, limit * 2)

        if df is not None and len(df) > 0:
            # Remove pair column if present
            if 'pair' in df.columns:
                df = df.drop(columns=['pair'])

            # Prefix columns (except interval_time)
            prefix = table.replace(f'_{pair}', '').replace('_', '')
            df = df.rename(columns={
                c: f"{prefix}_{c}" if c != 'interval_time' else c
                for c in df.columns
            })

            # Merge
            merged = merged.merge(df, on='interval_time', how='left')
            print(f"    Merged: {merged.shape}")

    return merged


def run_stability_selection(X, y, feature_names, n_folds=N_FOLDS, n_seeds=N_SEEDS, threshold=STABILITY_THRESHOLD):
    """Run stability selection with multiple seeds."""
    feature_selection_counts = defaultdict(int)
    total_runs = n_folds * n_seeds

    print(f"  Running {total_runs} stability selection runs...")

    for seed in range(n_seeds):
        # Create fold indices
        n = len(X)
        indices = np.arange(n)
        np.random.seed(seed * 42)
        np.random.shuffle(indices)
        fold_size = n // n_folds

        for fold in range(n_folds):
            # Train/val split
            val_start = fold * fold_size
            val_end = (fold + 1) * fold_size if fold < n_folds - 1 else n

            train_idx = np.concatenate([indices[:val_start], indices[val_end:]])

            X_train = X[train_idx]
            y_train = y[train_idx]

            # Train LightGBM
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

            # Select features with non-zero importance
            selected = np.where(importances > 0)[0]

            for idx in selected:
                feature_selection_counts[feature_names[idx]] += 1

        print(f"    Seed {seed+1}/{n_seeds} complete")

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
    print("FULL FEATURE UNIVERSE STABILITY SELECTION V2")
    print("USER MANDATE: Test ALL features")
    print("=" * 70)

    # Load data
    print("\nStep 1: Loading feature tables...")
    df = load_all_features(pair, horizon)
    print(f"  Final dataset: {df.shape}")

    # Prepare features
    target_col = f'target_bqx45_h{horizon}'
    exclude_cols = [target_col, 'interval_time']
    feature_cols = [c for c in df.columns if c not in exclude_cols]

    print(f"\nStep 2: Preparing features...")
    X = df[feature_cols].apply(pd.to_numeric, errors='coerce').fillna(0).values
    y = (df[target_col] > 0).astype(int).values

    # Remove constant features
    variances = np.var(X, axis=0)
    non_constant_mask = variances > 1e-10
    X = X[:, non_constant_mask]
    feature_cols_filtered = [f for f, m in zip(feature_cols, non_constant_mask) if m]

    print(f"  Total features: {len(feature_cols)}")
    print(f"  After removing constants: {len(feature_cols_filtered)}")
    print(f"  Samples: {len(X)}")

    # Run stability selection
    print(f"\nStep 3: Running stability selection...")
    print(f"  Config: {N_FOLDS} folds x {N_SEEDS} seeds = {N_FOLDS * N_SEEDS} runs")
    print(f"  Threshold: {STABILITY_THRESHOLD * 100:.0f}%")

    stable_features, all_scores = run_stability_selection(
        X, y, feature_cols_filtered,
        n_folds=N_FOLDS, n_seeds=N_SEEDS,
        threshold=STABILITY_THRESHOLD
    )

    print(f"\nStep 4: Results...")
    print(f"  Total features tested: {len(feature_cols_filtered)}")
    print(f"  Features with any importance: {len(all_scores)}")
    print(f"  Stable features (>={STABILITY_THRESHOLD*100:.0f}%): {len(stable_features)}")

    # Sort by stability score
    sorted_features = sorted(stable_features.items(), key=lambda x: -x[1])

    print(f"\nTop 30 stable features:")
    for i, (feat, score) in enumerate(sorted_features[:30]):
        print(f"  {i+1}. {feat}: {score:.1%}")

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
            'stable_features': len(stable_features),
            'current_features': 59,
            'improvement': len(stable_features) - 59
        },
        'stable_features': sorted_features,
        'all_scores': dict(sorted(all_scores.items(), key=lambda x: -x[1]))
    }

    output_path = f'/home/micha/bqx_ml_v3/intelligence/full_universe_stability_{pair}_h{horizon}.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {output_path}")

    # Summary
    print("\n" + "=" * 70)
    print("STABILITY SELECTION COMPLETE")
    print("=" * 70)
    print(f"  Features tested: {len(feature_cols_filtered)}")
    print(f"  Stable features: {len(stable_features)}")
    print(f"  Current h15 features: 59")
    print(f"  Potential improvement: +{len(stable_features) - 59} features")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
