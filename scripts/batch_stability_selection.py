#!/usr/bin/env python3
"""
Batch Stability Selection for Full Feature Universe
USER MANDATE: Test ALL features via batch processing

Strategy: Process features in batches by table type to avoid memory/timeout issues.
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
SAMPLE_LIMIT = 80000


def load_targets(pair: str, horizon: int, limit: int = SAMPLE_LIMIT):
    """Load target variable."""
    client = bigquery.Client(project=PROJECT)
    query = f"""
    SELECT interval_time, target_bqx45_h{horizon}
    FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}`
    WHERE target_bqx45_h{horizon} IS NOT NULL
    ORDER BY interval_time
    LIMIT {limit}
    """
    return client.query(query).to_dataframe()


def load_feature_batch(table_name: str, intervals: pd.Series, limit: int = SAMPLE_LIMIT):
    """Load features from a single table, filtered by intervals."""
    client = bigquery.Client(project=PROJECT)

    # Get columns
    col_query = f"""
    SELECT column_name
    FROM `{PROJECT}.{FEATURES_DATASET}.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name = '{table_name}'
      AND column_name NOT IN ('interval_time', 'pair')
    """
    cols = [r.column_name for r in client.query(col_query).result()]

    if not cols:
        return None, []

    # Load data
    query = f"""
    SELECT interval_time, {', '.join(cols)}
    FROM `{PROJECT}.{FEATURES_DATASET}.{table_name}`
    ORDER BY interval_time
    LIMIT {limit * 2}
    """

    try:
        df = client.query(query).to_dataframe()
        # Filter to matching intervals
        df = df[df['interval_time'].isin(intervals)]
        return df, cols
    except Exception as e:
        print(f"    Warning: {table_name}: {e}")
        return None, []


def run_stability_fold(X, y, feature_names, seed, fold, n_folds):
    """Run single stability selection fold."""
    n = len(X)
    indices = np.arange(n)
    np.random.seed(seed * 42)
    np.random.shuffle(indices)
    fold_size = n // n_folds

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
    }

    lgb_train = lgb.Dataset(X_train, label=y_train, feature_name=feature_names)
    model = lgb.train(lgb_params, lgb_train, num_boost_round=100)

    importances = model.feature_importance(importance_type='gain')
    selected = set(feature_names[i] for i in np.where(importances > 0)[0])

    return selected


def main():
    pair = "eurusd"
    horizon = 15

    print("=" * 70)
    print("BATCH STABILITY SELECTION")
    print("USER MANDATE: Test ALL features")
    print("=" * 70)

    # Load targets first
    print("\nStep 1: Loading targets...")
    targets_df = load_targets(pair, horizon)
    intervals = targets_df['interval_time']
    y = (targets_df[f'target_bqx45_h{horizon}'] > 0).astype(int).values
    print(f"  Samples: {len(targets_df)}")

    # Define feature table batches
    batches = {
        'reg': [f'reg_idx_{pair}', f'reg_bqx_{pair}'],
        'agg': [f'agg_idx_{pair}', f'agg_bqx_{pair}'],
        'mom': [f'mom_idx_{pair}', f'mom_bqx_{pair}'],
        'vol': [f'vol_idx_{pair}', f'vol_bqx_{pair}'],
        'der': [f'der_idx_{pair}', f'der_bqx_{pair}'],
        'align': [f'align_idx_{pair}', f'align_bqx_{pair}'],
        'base': [f'base_idx_{pair}', f'base_bqx_{pair}'],
        'mrt': [f'mrt_idx_{pair}', f'mrt_bqx_{pair}'],
        'lag': [f'lag_{pair}_45', f'lag_{pair}_90', f'lag_bqx_{pair}_45', f'lag_bqx_{pair}_90'],
    }

    # Load all features
    print("\nStep 2: Loading feature batches...")
    all_features = {}
    merged = targets_df[['interval_time']].copy()

    for batch_name, tables in batches.items():
        print(f"  Batch: {batch_name}")
        for table in tables:
            df, cols = load_feature_batch(table, intervals)
            if df is not None and len(cols) > 0:
                # Prefix columns
                prefix = table.replace(f'_{pair}', '').replace('_', '')
                renamed = {c: f"{prefix}_{c}" for c in cols}
                df = df.rename(columns=renamed)

                # Merge
                merged = merged.merge(df, on='interval_time', how='left')
                for new_col in renamed.values():
                    all_features[new_col] = batch_name
                print(f"    {table}: {len(cols)} cols → {len(renamed)} features")

    # Prepare feature matrix
    feature_cols = list(all_features.keys())
    print(f"\nTotal features loaded: {len(feature_cols)}")

    X = merged[feature_cols].apply(pd.to_numeric, errors='coerce').fillna(0).values

    # Remove constant features
    variances = np.var(X, axis=0)
    non_constant = variances > 1e-10
    X = X[:, non_constant]
    feature_cols = [f for f, nc in zip(feature_cols, non_constant) if nc]
    print(f"After removing constants: {len(feature_cols)}")

    # Run stability selection
    print(f"\nStep 3: Running stability selection ({N_FOLDS}x{N_SEEDS}={N_FOLDS*N_SEEDS} runs)...")

    selection_counts = defaultdict(int)
    total_runs = N_FOLDS * N_SEEDS

    for seed in range(N_SEEDS):
        for fold in range(N_FOLDS):
            selected = run_stability_fold(X, y, feature_cols, seed, fold, N_FOLDS)
            for f in selected:
                selection_counts[f] += 1
        print(f"  Seed {seed+1}/{N_SEEDS} complete")

    # Calculate stability scores
    stability_scores = {f: c / total_runs for f, c in selection_counts.items()}
    stable_features = {f: s for f, s in stability_scores.items() if s >= STABILITY_THRESHOLD}

    # Sort
    sorted_stable = sorted(stable_features.items(), key=lambda x: -x[1])

    print(f"\nStep 4: Results")
    print(f"  Features tested: {len(feature_cols)}")
    print(f"  Features with importance: {len(selection_counts)}")
    print(f"  Stable features (≥{STABILITY_THRESHOLD*100:.0f}%): {len(stable_features)}")

    print(f"\nTop 30 stable features:")
    for i, (f, s) in enumerate(sorted_stable[:30]):
        print(f"  {i+1}. {f}: {s:.1%}")

    # Save results
    results = {
        'pair': pair,
        'horizon': horizon,
        'timestamp': datetime.now().isoformat(),
        'config': {
            'n_folds': N_FOLDS,
            'n_seeds': N_SEEDS,
            'threshold': STABILITY_THRESHOLD,
            'total_runs': total_runs
        },
        'summary': {
            'features_tested': len(feature_cols),
            'features_with_importance': len(selection_counts),
            'stable_features': len(stable_features),
            'current_features': 59,
            'improvement': len(stable_features) - 59
        },
        'stable_features': sorted_stable,
        'all_scores': dict(sorted(stability_scores.items(), key=lambda x: -x[1]))
    }

    output_path = f'/home/micha/bqx_ml_v3/intelligence/batch_stability_{pair}_h{horizon}.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {output_path}")

    print("\n" + "=" * 70)
    print("BATCH STABILITY SELECTION COMPLETE")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
