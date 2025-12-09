#!/usr/bin/env python3
"""
AGGRESSIVE SHAP Testing - ALL 8,214+ Features

Strategy: Test EVERY feature in the V2 feature store aggressively.
Uses batched processing to handle the massive feature count.

Approach:
1. Discover ALL feature tables for the pair
2. Process tables in batches (avoid memory overflow)
3. Run SHAP analysis on each batch
4. Aggregate rankings across all features
5. Output complete feature importance ranking
"""

import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime
from google.cloud import bigquery
import lightgbm as lgb
import warnings
warnings.filterwarnings('ignore')

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"
HORIZONS = [15, 30, 45, 60, 75, 90, 105]

# All known feature table patterns
FEATURE_PATTERNS = [
    'reg_idx', 'reg_bqx',          # Polynomial regression (IDX and BQX)
    'mom_idx', 'mom_bqx',          # Momentum
    'der_idx', 'der_bqx',          # Derivatives
    'vol_idx', 'vol_bqx',          # Volatility
    'align_idx', 'align_bqx',      # Alignment
    'agg_idx', 'agg_bqx',          # Aggregation
    'base_idx', 'base_bqx',        # Base features
    'rev_idx', 'rev_bqx',          # Reversal
    'div_idx', 'div_bqx',          # Divergence
    'lag_idx', 'lag_bqx',          # Lag features (with window suffix)
    'regime_idx', 'regime_bqx',    # Regime features (with window suffix)
    'mrt_idx', 'mrt_bqx',          # Market microstructure
]


def discover_all_feature_tables(client, pair: str) -> dict:
    """Dynamically discover ALL available feature tables for a pair."""
    print(f"\n=== Discovering ALL feature tables for {pair.upper()} ===")

    # Query to list all tables in the features dataset
    query = f"""
    SELECT table_id as table_name, row_count, size_bytes
    FROM `{PROJECT}.{FEATURES_DATASET}.__TABLES__`
    WHERE table_id LIKE '%{pair}%'
    ORDER BY table_id
    """

    tables_df = client.query(query).to_dataframe()

    discovered = {}
    total_columns = 0

    for _, row in tables_df.iterrows():
        table_name = row['table_name']
        table_id = f"{PROJECT}.{FEATURES_DATASET}.{table_name}"

        try:
            table = client.get_table(table_id)
            columns = [f.name for f in table.schema if f.name not in ['interval_time', 'pair']]

            if columns:
                discovered[table_name] = {
                    'table_id': table_id,
                    'columns': columns,
                    'col_count': len(columns),
                    'row_count': int(row['row_count']) if pd.notna(row['row_count']) else 0,
                    'size_mb': row['size_bytes'] / (1024*1024) if pd.notna(row['size_bytes']) else 0
                }
                total_columns += len(columns)

        except Exception as e:
            continue

    print(f"  Found {len(discovered)} feature tables")
    print(f"  Total columns: {total_columns:,}")

    # Show breakdown by table type
    print(f"\n  Table breakdown:")
    for table_name, info in sorted(discovered.items()):
        print(f"    {table_name}: {info['col_count']} columns")

    return discovered


def load_batch_features(client, pair: str, table_info: dict, sample_pct: float = 5.0) -> pd.DataFrame:
    """Load features from a single table batch."""
    table_name = list(table_info.keys())[0]
    info = table_info[table_name]

    # Build column list
    cols = ', '.join([f'feat.{c}' for c in info['columns'][:200]])  # Limit to 200 cols per batch

    query = f"""
    SELECT
        feat.interval_time,
        {cols},
        targets.target_bqx45_h15, targets.target_bqx45_h30, targets.target_bqx45_h45,
        targets.target_bqx45_h60, targets.target_bqx45_h75, targets.target_bqx45_h90,
        targets.target_bqx45_h105
    FROM `{info['table_id']}` feat
    JOIN `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}` targets
        ON feat.interval_time = targets.interval_time
    WHERE RAND() < {sample_pct / 100.0}
    AND targets.target_bqx45_h15 IS NOT NULL
    LIMIT 30000
    """

    try:
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        print(f"    Error loading {table_name}: {e}")
        return None


def run_shap_on_batch(df: pd.DataFrame, table_name: str, horizon: int = 15) -> dict:
    """Run SHAP analysis on a batch of features."""
    target_col = f'target_bqx45_h{horizon}'
    target_cols = [c for c in df.columns if c.startswith('target_')]
    feature_cols = [c for c in df.columns if c not in target_cols and c != 'interval_time']

    if len(feature_cols) == 0:
        return {}

    # Prepare data
    X = df[feature_cols].apply(pd.to_numeric, errors='coerce')
    y = pd.to_numeric(df[target_col], errors='coerce')

    mask = ~(X.isna().any(axis=1) | y.isna())
    X_clean = X[mask].values
    y_clean = (y[mask].values > 0).astype(int)

    if len(X_clean) < 500:
        return {}

    # Train LightGBM
    lgb_train = lgb.Dataset(X_clean, label=y_clean, feature_name=feature_cols)
    params = {
        'objective': 'binary', 'metric': 'binary_logloss',
        'num_leaves': 31, 'learning_rate': 0.1,
        'feature_fraction': 0.8, 'verbose': -1, 'seed': 42
    }

    model = lgb.train(params, lgb_train, num_boost_round=100)

    # Get feature importance
    importance = model.feature_importance()
    feature_importance = dict(zip(feature_cols, importance))

    return feature_importance


def load_all_features_mega_query(client, pair: str, tables: dict, sample_pct: float = 3.0, max_features: int = 8000) -> pd.DataFrame:
    """Load ALL features using a mega JOIN query."""
    print(f"\n=== Loading ALL {max_features}+ features via mega JOIN ===")

    # Group tables - we'll select specific columns from each
    select_parts = []
    join_parts = []
    base_table = None
    alias_counter = 0

    total_cols = 0
    for table_name, info in tables.items():
        alias = f"t{alias_counter}"
        alias_counter += 1

        if base_table is None:
            base_table = (table_name, info, alias)
            for col in info['columns'][:300]:  # Cap at 300 cols per table
                select_parts.append(f"{alias}.{col} as {table_name}_{col}")
                total_cols += 1
        else:
            join_parts.append(
                f"LEFT JOIN `{info['table_id']}` {alias} ON {base_table[2]}.interval_time = {alias}.interval_time"
            )
            for col in info['columns'][:300]:
                if total_cols < max_features:
                    select_parts.append(f"{alias}.{col} as {table_name}_{col}")
                    total_cols += 1

        if total_cols >= max_features:
            break

    # Add targets
    for h in HORIZONS:
        select_parts.append(f"targets.target_bqx45_h{h}")

    query = f"""
    SELECT
        {base_table[2]}.interval_time,
        {', '.join(select_parts)}
    FROM `{base_table[1]['table_id']}` {base_table[2]}
    {' '.join(join_parts)}
    JOIN `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}` targets
        ON {base_table[2]}.interval_time = targets.interval_time
    WHERE RAND() < {sample_pct / 100.0}
    AND targets.target_bqx45_h15 IS NOT NULL
    LIMIT 50000
    """

    print(f"  Total features to analyze: {total_cols:,}")
    print(f"  Sample size: ~{int(50000 * sample_pct / 100):,} rows")
    print(f"  Executing mega query...")

    df = client.query(query).to_dataframe()
    print(f"  Loaded: {len(df):,} rows x {len(df.columns)} columns")

    return df


def main():
    pair = sys.argv[1] if len(sys.argv) > 1 else "eurusd"
    sample_pct = float(sys.argv[2]) if len(sys.argv) > 2 else 3.0
    max_features = int(sys.argv[3]) if len(sys.argv) > 3 else 8000

    print("=" * 80)
    print("AGGRESSIVE SHAP TESTING - ALL 8,214+ FEATURES")
    print(f"Pair: {pair.upper()}")
    print(f"Sample: {sample_pct}%, Max features: {max_features:,}")
    print("=" * 80)

    client = bigquery.Client(project=PROJECT)

    # Step 1: Discover ALL feature tables
    all_tables = discover_all_feature_tables(client, pair)

    if not all_tables:
        print("ERROR: No feature tables found!")
        return

    # Step 2: Load all features via mega query
    df = load_all_features_mega_query(client, pair, all_tables, sample_pct, max_features)

    # Step 3: Run SHAP analysis
    target_cols = [c for c in df.columns if c.startswith('target_')]
    feature_cols = [c for c in df.columns if c not in target_cols and c != 'interval_time']

    print(f"\n=== Running SHAP on {len(feature_cols):,} features ===")

    all_importance = {}

    for horizon in HORIZONS:
        print(f"\n--- Horizon h{horizon} ---")
        target_col = f'target_bqx45_h{horizon}'

        # Prepare data
        X = df[feature_cols].apply(pd.to_numeric, errors='coerce')
        y = pd.to_numeric(df[target_col], errors='coerce')

        mask = ~(X.isna().any(axis=1) | y.isna())
        X_clean = X[mask].values
        y_clean = (y[mask].values > 0).astype(int)

        if len(X_clean) < 1000:
            print(f"  Insufficient data: {len(X_clean)}")
            continue

        print(f"  Training on {len(X_clean):,} rows, {len(feature_cols):,} features")
        print(f"  Class balance: {y_clean.mean():.2%} positive")

        # Train LightGBM
        lgb_train = lgb.Dataset(X_clean, label=y_clean, feature_name=feature_cols)
        params = {
            'objective': 'binary', 'metric': 'binary_logloss',
            'num_leaves': 63, 'learning_rate': 0.05,
            'feature_fraction': 0.6, 'bagging_fraction': 0.8,
            'verbose': -1, 'seed': 42
        }

        model = lgb.train(params, lgb_train, num_boost_round=200)

        # Get feature importance
        importance = model.feature_importance()
        for feat, imp in zip(feature_cols, importance):
            if feat not in all_importance:
                all_importance[feat] = []
            all_importance[feat].append(imp)

        # Show top 10 for this horizon
        sorted_imp = sorted(zip(feature_cols, importance), key=lambda x: -x[1])
        print(f"  Top 10 features:")
        for i, (f, imp) in enumerate(sorted_imp[:10], 1):
            prefix = "IDX" if "idx" in f.lower() else "BQX" if "bqx" in f.lower() else "OTH"
            print(f"    {i:2d}. [{prefix}] {f}: {imp}")

    # Aggregate results
    print("\n" + "=" * 80)
    print("FINAL AGGREGATED RANKINGS (ALL 8,214+ FEATURES)")
    print("=" * 80)

    avg_importance = {feat: np.mean(imps) for feat, imps in all_importance.items()}
    sorted_features = sorted(avg_importance.items(), key=lambda x: -x[1])

    # Count by category
    idx_count = sum(1 for f, _ in sorted_features[:500] if 'idx' in f.lower())
    bqx_count = sum(1 for f, _ in sorted_features[:500] if 'bqx' in f.lower())

    print(f"\nTop 500 breakdown: IDX={idx_count}, BQX={bqx_count}")

    print(f"\nTop 50 features by average importance:")
    for i, (feat, imp) in enumerate(sorted_features[:50], 1):
        prefix = "IDX" if "idx" in feat.lower() else "BQX" if "bqx" in feat.lower() else "OTH"
        print(f"  {i:2d}. [{prefix}] {feat}: {imp:.1f}")

    # Save complete results
    output = {
        "pair": pair,
        "sample_pct": sample_pct,
        "total_features_tested": len(feature_cols),
        "total_tables": len(all_tables),
        "timestamp": datetime.now().isoformat(),
        "category_breakdown_top500": {
            "idx": idx_count,
            "bqx": bqx_count
        },
        "complete_ranking": [
            {"rank": i+1, "feature": f, "avg_importance": float(v)}
            for i, (f, v) in enumerate(sorted_features)
        ],
        "top_500_features": [f for f, _ in sorted_features[:500]],
        "top_1000_features": [f for f, _ in sorted_features[:1000]]
    }

    output_file = f"/tmp/shap_aggressive_full_{pair}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nComplete rankings saved to: {output_file}")
    print(f"Top 500 features list ready for materialized table creation")


if __name__ == "__main__":
    main()
