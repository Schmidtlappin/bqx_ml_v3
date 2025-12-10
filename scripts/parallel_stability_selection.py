#!/usr/bin/env python3
"""
Parallel Stability Selection - Optimized for Memory and Speed
USER MANDATE: Test ALL features with parallel batch processing

Strategy:
- Smaller sample size (40K instead of 80K)
- Process feature groups in parallel
- Combine results at end
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
from google.cloud import bigquery
import lightgbm as lgb
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"

# Optimized configuration
N_FOLDS = 5
N_SEEDS = 3
STABILITY_THRESHOLD = 0.50
SAMPLE_LIMIT = 40000  # Reduced for memory


def get_client():
    return bigquery.Client(project=PROJECT)


def load_base_data(pair: str, horizon: int):
    """Load targets and base interval_time index."""
    client = get_client()
    query = f"""
    SELECT interval_time, target_bqx45_h{horizon}
    FROM `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}`
    WHERE target_bqx45_h{horizon} IS NOT NULL
    ORDER BY interval_time
    LIMIT {SAMPLE_LIMIT}
    """
    df = client.query(query).to_dataframe()
    return df


def load_feature_group(pair: str, tables: list, intervals: set):
    """Load a group of feature tables."""
    client = get_client()
    features = {}

    for table in tables:
        try:
            # Get columns
            col_query = f"""
            SELECT column_name
            FROM `{PROJECT}.{FEATURES_DATASET}.INFORMATION_SCHEMA.COLUMNS`
            WHERE table_name = '{table}' AND column_name NOT IN ('interval_time', 'pair')
            """
            cols = [r.column_name for r in client.query(col_query).result()]

            if not cols:
                continue

            # Load data
            query = f"""
            SELECT interval_time, {', '.join(cols)}
            FROM `{PROJECT}.{FEATURES_DATASET}.{table}`
            ORDER BY interval_time
            LIMIT {SAMPLE_LIMIT * 2}
            """
            df = client.query(query).to_dataframe()

            # Filter to matching intervals
            df = df[df['interval_time'].isin(intervals)]

            # Prefix columns
            prefix = table.replace(f'_{pair}', '').replace('_', '')
            for col in cols:
                new_name = f"{prefix}_{col}"
                features[new_name] = df.set_index('interval_time')[col]

        except Exception as e:
            print(f"    Skip {table}: {e}")

    return features


def run_stability_on_features(X, y, feature_names):
    """Run stability selection on feature matrix."""
    selection_counts = defaultdict(int)
    total_runs = N_FOLDS * N_SEEDS

    for seed in range(N_SEEDS):
        n = len(X)
        indices = np.arange(n)
        np.random.seed(seed * 42)
        np.random.shuffle(indices)
        fold_size = n // N_FOLDS

        for fold in range(N_FOLDS):
            val_start = fold * fold_size
            val_end = (fold + 1) * fold_size if fold < N_FOLDS - 1 else n
            train_idx = np.concatenate([indices[:val_start], indices[val_end:]])

            X_train = X[train_idx]
            y_train = y[train_idx]

            lgb_params = {
                'objective': 'binary', 'metric': 'binary_logloss',
                'num_leaves': 31, 'learning_rate': 0.05,
                'feature_fraction': 0.8, 'bagging_fraction': 0.8,
                'bagging_freq': 5, 'verbose': -1,
                'seed': seed * 100 + fold, 'min_data_in_leaf': 100,
            }

            lgb_train = lgb.Dataset(X_train, label=y_train, feature_name=feature_names)
            model = lgb.train(lgb_params, lgb_train, num_boost_round=100)

            importances = model.feature_importance(importance_type='gain')
            for i in np.where(importances > 0)[0]:
                selection_counts[feature_names[i]] += 1

    return {f: c / total_runs for f, c in selection_counts.items()}


def process_batch(batch_name, tables, base_df, pair):
    """Process a single batch of feature tables."""
    print(f"  Processing batch: {batch_name}...")

    intervals = set(base_df['interval_time'])
    features = load_feature_group(pair, tables, intervals)

    if not features:
        return batch_name, {}

    # Build feature matrix
    feature_df = pd.DataFrame(features, index=base_df['interval_time'])
    feature_df = feature_df.reindex(base_df['interval_time']).fillna(0)

    feature_cols = list(feature_df.columns)
    X = feature_df.values
    y = (base_df['target_bqx45_h15'] > 0).astype(int).values

    # Remove constant features
    variances = np.var(X, axis=0)
    non_constant = variances > 1e-10
    X = X[:, non_constant]
    feature_cols = [f for f, nc in zip(feature_cols, non_constant) if nc]

    if len(feature_cols) == 0:
        return batch_name, {}

    print(f"    {batch_name}: {len(feature_cols)} features")

    # Run stability selection
    scores = run_stability_on_features(X, y, feature_cols)

    return batch_name, scores


def main():
    pair = "eurusd"
    horizon = 15

    print("=" * 70)
    print("PARALLEL STABILITY SELECTION")
    print("USER MANDATE: Test ALL features")
    print("=" * 70)

    # Load base data
    print("\nStep 1: Loading base data...")
    base_df = load_base_data(pair, horizon)
    print(f"  Samples: {len(base_df)}")

    # Define batches
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
        'rev': [f'rev_idx_{pair}', f'rev_bqx_{pair}'],
    }

    # Process batches in parallel
    print(f"\nStep 2: Processing {len(batches)} batches in parallel...")

    all_scores = {}

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(process_batch, name, tables, base_df.copy(), pair): name
            for name, tables in batches.items()
        }

        for future in as_completed(futures):
            batch_name = futures[future]
            try:
                name, scores = future.result()
                all_scores.update(scores)
                print(f"    Completed: {name} ({len(scores)} features)")
            except Exception as e:
                print(f"    Failed: {batch_name}: {e}")

    # Filter stable features
    stable_features = {f: s for f, s in all_scores.items() if s >= STABILITY_THRESHOLD}
    sorted_stable = sorted(stable_features.items(), key=lambda x: -x[1])

    print(f"\nStep 3: Results")
    print(f"  Total features tested: {len(all_scores)}")
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
            'sample_size': SAMPLE_LIMIT,
            'total_runs': N_FOLDS * N_SEEDS
        },
        'summary': {
            'features_tested': len(all_scores),
            'stable_features': len(stable_features),
            'current_features': 59,
            'improvement': len(stable_features) - 59
        },
        'stable_features': sorted_stable,
        'all_scores': dict(sorted(all_scores.items(), key=lambda x: -x[1]))
    }

    output_path = f'/home/micha/bqx_ml_v3/intelligence/parallel_stability_{pair}_h{horizon}.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {output_path}")

    print("\n" + "=" * 70)
    print("PARALLEL STABILITY SELECTION COMPLETE")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
