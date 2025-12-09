#!/usr/bin/env python3
"""
Comprehensive SHAP Feature Selection for BQX ML V3

Joins ALL available V2 feature tables and selects top 500-1000 features.
Prioritizes IDX features per user mandate:
  #1 IDX polynomial (reg_idx)
  #2 IDX derived (mom, der, align, etc.)
  #3 BQX polynomial (reg_bqx)
  #4 BQX derived
  #5 Other
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

# Feature windows
WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]
HORIZONS = [15, 30, 45, 60, 75, 90, 105]

# Feature table prefixes in priority order (IDX first)
FEATURE_TABLES = {
    'reg_idx': {'priority': 1, 'pattern': 'reg_idx_{pair}', 'desc': 'IDX polynomial regression'},
    'reg_bqx': {'priority': 3, 'pattern': 'reg_bqx_{pair}', 'desc': 'BQX polynomial regression'},
    'mom_idx': {'priority': 2, 'pattern': 'mom_idx_{pair}', 'desc': 'IDX momentum'},
    'mom_bqx': {'priority': 4, 'pattern': 'mom_bqx_{pair}', 'desc': 'BQX momentum'},
    'der_idx': {'priority': 2, 'pattern': 'der_idx_{pair}', 'desc': 'IDX derivatives'},
    'der_bqx': {'priority': 4, 'pattern': 'der_bqx_{pair}', 'desc': 'BQX derivatives'},
    'vol_idx': {'priority': 2, 'pattern': 'vol_idx_{pair}', 'desc': 'IDX volatility'},
    'vol_bqx': {'priority': 4, 'pattern': 'vol_bqx_{pair}', 'desc': 'BQX volatility'},
    'align_idx': {'priority': 2, 'pattern': 'align_idx_{pair}', 'desc': 'IDX alignment'},
    'align_bqx': {'priority': 4, 'pattern': 'align_bqx_{pair}', 'desc': 'BQX alignment'},
    'agg_idx': {'priority': 2, 'pattern': 'agg_idx_{pair}', 'desc': 'IDX aggregation'},
    'agg_bqx': {'priority': 4, 'pattern': 'agg_bqx_{pair}', 'desc': 'BQX aggregation'},
    'base_idx': {'priority': 2, 'pattern': 'base_idx_{pair}', 'desc': 'IDX base'},
    'base_bqx': {'priority': 4, 'pattern': 'base_bqx_{pair}', 'desc': 'BQX base'},
    'lag_idx': {'priority': 2, 'pattern': 'lag_idx_{pair}', 'desc': 'IDX lag'},
    'lag_bqx': {'priority': 4, 'pattern': 'lag_bqx_{pair}', 'desc': 'BQX lag'},
    'regime_idx': {'priority': 2, 'pattern': 'regime_idx_{pair}', 'desc': 'IDX regime'},
    'regime_bqx': {'priority': 4, 'pattern': 'regime_bqx_{pair}', 'desc': 'BQX regime'},
    'rev_idx': {'priority': 2, 'pattern': 'rev_idx_{pair}', 'desc': 'IDX reversal'},
    'rev_bqx': {'priority': 4, 'pattern': 'rev_bqx_{pair}', 'desc': 'BQX reversal'},
    'div_idx': {'priority': 2, 'pattern': 'div_idx_{pair}', 'desc': 'IDX divergence'},
    'div_bqx': {'priority': 4, 'pattern': 'div_bqx_{pair}', 'desc': 'BQX divergence'},
}


def get_table_columns(client, table_id: str) -> list:
    """Get column names from a BigQuery table."""
    try:
        table = client.get_table(table_id)
        return [field.name for field in table.schema if field.name != 'interval_time' and field.name != 'pair']
    except Exception as e:
        return []


def build_comprehensive_query(pair: str, sample_pct: float = 5.0) -> str:
    """Build query joining all available feature tables."""
    client = bigquery.Client(project=PROJECT)

    # Discover available tables and their columns
    tables_found = {}
    all_columns = []

    for prefix, info in FEATURE_TABLES.items():
        table_name = info['pattern'].format(pair=pair)
        table_id = f"{PROJECT}.{FEATURES_DATASET}.{table_name}"

        cols = get_table_columns(client, table_id)
        if cols:
            tables_found[prefix] = {
                'table': table_name,
                'columns': cols,
                'priority': info['priority']
            }
            # Add prefix to column names
            for col in cols:
                all_columns.append({
                    'table': prefix,
                    'column': col,
                    'alias': f"{prefix}_{col}",
                    'priority': info['priority']
                })

    print(f"  Found {len(tables_found)} feature tables with {len(all_columns)} total columns")

    # Build select columns
    select_parts = ["base.interval_time"]
    for col_info in all_columns:
        select_parts.append(f"{col_info['table']}.{col_info['column']} as {col_info['alias']}")

    # Add targets
    for h in HORIZONS:
        select_parts.append(f"targets.target_bqx45_h{h}")

    # Build FROM and JOINs
    from_clause = f"`{PROJECT}.{FEATURES_DATASET}.{tables_found['base_idx']['table']}` base"
    join_clauses = []

    for prefix, info in tables_found.items():
        if prefix != 'base_idx':
            join_clauses.append(
                f"LEFT JOIN `{PROJECT}.{FEATURES_DATASET}.{info['table']}` {prefix} "
                f"ON base.interval_time = {prefix}.interval_time"
            )

    # Add targets join
    join_clauses.append(
        f"JOIN `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}` targets "
        f"ON base.interval_time = targets.interval_time"
    )

    query = f"""
    SELECT
        {', '.join(select_parts)}
    FROM {from_clause}
    {' '.join(join_clauses)}
    WHERE RAND() < {sample_pct / 100.0}
    AND targets.target_bqx45_h15 IS NOT NULL
    """

    return query, all_columns


def load_comprehensive_features(pair: str, sample_pct: float = 5.0) -> tuple:
    """Load comprehensive feature set from BigQuery."""
    print(f"Loading {sample_pct}% sample of ALL {pair.upper()} features...")

    client = bigquery.Client(project=PROJECT)
    query, column_info = build_comprehensive_query(pair, sample_pct)

    print("  Executing query...")
    df = client.query(query).to_dataframe()
    print(f"  Loaded {len(df):,} rows with {len(df.columns)} columns")

    return df, column_info


def train_lightgbm_importance(X: pd.DataFrame, y: pd.Series, target_name: str) -> dict:
    """Train LightGBM and extract feature importance."""
    # Convert to numeric and handle NaN
    X = X.apply(pd.to_numeric, errors='coerce')
    y = pd.to_numeric(y, errors='coerce')

    mask = ~(X.isna().any(axis=1) | y.isna())
    X_clean = X[mask].values
    y_clean = y[mask].values

    if len(X_clean) < 1000:
        print(f"  Warning: Only {len(X_clean)} rows, skipping...")
        return {}

    # Binary classification target
    y_binary = (y_clean > 0).astype(int)

    print(f"  Training on {len(X_clean):,} rows, class balance: {y_binary.mean():.2%}")

    # Train LightGBM for classification
    params = {
        'objective': 'binary',
        'metric': 'binary_logloss',
        'num_leaves': 63,
        'learning_rate': 0.05,
        'feature_fraction': 0.6,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'verbose': -1,
        'seed': 42,
        'min_data_in_leaf': 50
    }

    feature_names = list(X.columns)
    train_data = lgb.Dataset(X_clean, label=y_binary, feature_name=feature_names)
    model = lgb.train(params, train_data, num_boost_round=200)

    # Get feature importance
    importance = model.feature_importance()
    feature_importance = dict(zip(feature_names, importance))

    return feature_importance


def main():
    pair = sys.argv[1] if len(sys.argv) > 1 else "eurusd"
    sample_pct = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
    top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 500

    print("=" * 70)
    print(f"COMPREHENSIVE Feature Selection for {pair.upper()}")
    print(f"Sample: {sample_pct}%, Target: top {top_n} features")
    print("Priority: IDX poly > IDX derived > BQX poly > BQX derived")
    print("=" * 70)

    # Load features
    df, column_info = load_comprehensive_features(pair, sample_pct)

    # Identify feature and target columns
    target_cols = [c for c in df.columns if c.startswith('target_')]
    feature_cols = [c for c in df.columns if c not in target_cols and c != 'interval_time']

    print(f"\nFeatures: {len(feature_cols)}")
    print(f"Targets: {len(target_cols)}")

    X = df[feature_cols]

    # Train for each horizon and collect importance
    all_importance = {}

    for horizon in HORIZONS:
        target_col = f"target_bqx45_h{horizon}"
        if target_col not in df.columns:
            continue

        print(f"\n--- Horizon h{horizon} ---")
        y = df[target_col]
        importance = train_lightgbm_importance(X, y, target_col)

        for feat, imp in importance.items():
            if feat not in all_importance:
                all_importance[feat] = []
            all_importance[feat].append(imp)

    # Average importance across horizons
    avg_importance = {feat: np.mean(imps) for feat, imps in all_importance.items()}

    # Create priority map for tiebreaking
    priority_map = {}
    for col_info in column_info:
        priority_map[col_info['alias']] = col_info['priority']

    # Sort by importance, then by priority (lower = better)
    sorted_features = sorted(
        avg_importance.items(),
        key=lambda x: (-x[1], priority_map.get(x[0], 5))
    )

    # Select top N features
    top_features = sorted_features[:top_n]

    # Categorize results
    idx_poly_count = sum(1 for f, _ in top_features if f.startswith('reg_idx'))
    idx_derived_count = sum(1 for f, _ in top_features if any(f.startswith(p) for p in ['mom_idx', 'der_idx', 'vol_idx', 'align_idx', 'agg_idx', 'lag_idx', 'regime_idx', 'rev_idx', 'div_idx', 'base_idx']))
    bqx_poly_count = sum(1 for f, _ in top_features if f.startswith('reg_bqx'))
    bqx_derived_count = sum(1 for f, _ in top_features if any(f.startswith(p) for p in ['mom_bqx', 'der_bqx', 'vol_bqx', 'align_bqx', 'agg_bqx', 'lag_bqx', 'regime_bqx', 'rev_bqx', 'div_bqx', 'base_bqx']))

    # Save results
    output = {
        "pair": pair,
        "sample_pct": sample_pct,
        "total_features_analyzed": len(feature_cols),
        "top_n_selected": top_n,
        "timestamp": datetime.now().isoformat(),
        "category_breakdown": {
            "idx_polynomial": idx_poly_count,
            "idx_derived": idx_derived_count,
            "bqx_polynomial": bqx_poly_count,
            "bqx_derived": bqx_derived_count
        },
        "top_features": [
            {"feature": f, "importance": float(v), "priority": priority_map.get(f, 5)}
            for f, v in top_features
        ],
        "feature_list": [f for f, _ in top_features]
    }

    output_file = f"/tmp/comprehensive_features_{pair}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    # Print results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Total features analyzed: {len(feature_cols)}")
    print(f"Top {top_n} selected")
    print(f"\nCategory breakdown:")
    print(f"  IDX Polynomial: {idx_poly_count}")
    print(f"  IDX Derived:    {idx_derived_count}")
    print(f"  BQX Polynomial: {bqx_poly_count}")
    print(f"  BQX Derived:    {bqx_derived_count}")

    print(f"\nTop 30 features:")
    for i, (feat, imp) in enumerate(top_features[:30], 1):
        priority = priority_map.get(feat, 5)
        prefix = "IDX" if "idx" in feat else "BQX" if "bqx" in feat else "OTH"
        print(f"  {i:2d}. [{prefix}] {feat}: {imp:.0f} (p{priority})")

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
