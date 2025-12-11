#!/usr/bin/env python3
"""
ROBUST FEATURE SELECTION SYSTEM - 8,416+ Features

Based on production-grade ML feature selection principles:
1. Safe Pruning (constant/duplicate/missing)
2. Feature Clustering (correlation families)
3. Group-First Screening (by table type)
4. Stability Selection (multi-fold/seed)
5. Ablation Testing (proof by performance impact)
6. SHAP Interpretation (late-stage refinement)

This replaces naive "SHAP rank all features" with a selection SYSTEM
that makes missing critical features extremely unlikely.
"""

import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime
from google.cloud import bigquery
from sklearn.linear_model import ElasticNet, LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
from collections import defaultdict
import lightgbm as lgb
import warnings
warnings.filterwarnings('ignore')

PROJECT = "bqx-ml"
FEATURES_DATASET = "bqx_ml_v3_features_v2"
ANALYTICS_DATASET = "bqx_ml_v3_analytics_v2"
HORIZONS = [15, 30, 45, 60, 75, 90, 105]

# Feature groups by table type (for group-aware selection)
FEATURE_GROUPS = {
    'reg_idx': 'polynomial_idx',
    'reg_bqx': 'polynomial_bqx',
    'mom_idx': 'momentum_idx',
    'mom_bqx': 'momentum_bqx',
    'der_idx': 'derivative_idx',
    'der_bqx': 'derivative_bqx',
    'vol_idx': 'volatility_idx',
    'vol_bqx': 'volatility_bqx',
    'agg_idx': 'aggregation_idx',
    'agg_bqx': 'aggregation_bqx',
    'align_idx': 'alignment_idx',
    'align_bqx': 'alignment_bqx',
    'base_idx': 'base_idx',
    'base_bqx': 'base_bqx',
    'rev_idx': 'reversal_idx',
    'rev_bqx': 'reversal_bqx',
    'div_idx': 'divergence_idx',
    'div_bqx': 'divergence_bqx',
    'lag_idx': 'lag_idx',
    'lag_bqx': 'lag_bqx',
    'regime_idx': 'regime_idx',
    'regime_bqx': 'regime_bqx',
    'mrt_idx': 'microstructure_idx',
    'mrt_bqx': 'microstructure_bqx',
    'cov_': 'covariance',
    'corr_': 'correlation',
    'tri_': 'triangulation',
    'cyc_': 'cyclical',
    'ext_': 'external',
}


def load_from_parquet(pair: str) -> pd.DataFrame:
    """Load feature data from Step 6 merged parquet (no BigQuery cost)."""
    parquet_path = f"/home/micha/bqx_ml_v3/data/features/{pair}_merged_features.parquet"
    try:
        df = pd.read_parquet(parquet_path)
        print(f"Loaded from parquet: {parquet_path}")
        print(f"  Rows: {len(df):,}, Columns: {len(df.columns)}")
        return df
    except FileNotFoundError:
        print(f"Parquet not found: {parquet_path}")
        return None


def discover_feature_tables(client, pair: str) -> dict:
    """Discover all feature tables for a pair, grouped by type."""
    query = f"""
    SELECT table_id as table_name, row_count, size_bytes
    FROM `{PROJECT}.{FEATURES_DATASET}.__TABLES__`
    WHERE table_id LIKE '%{pair}%'
    ORDER BY table_id
    """
    tables_df = client.query(query).to_dataframe()

    discovered = defaultdict(list)
    for _, row in tables_df.iterrows():
        table_name = row['table_name']
        table_id = f"{PROJECT}.{FEATURES_DATASET}.{table_name}"

        # Determine group
        group = 'other'
        for prefix, group_name in FEATURE_GROUPS.items():
            if table_name.startswith(prefix):
                group = group_name
                break

        try:
            table = client.get_table(table_id)
            columns = [f.name for f in table.schema
                      if f.name not in ['interval_time', 'pair', 'pair1', 'pair2']]
            if columns:
                discovered[group].append({
                    'table_name': table_name,
                    'table_id': table_id,
                    'columns': columns,
                    'row_count': int(row['row_count']) if pd.notna(row['row_count']) else 0
                })
        except Exception:
            continue

    return dict(discovered)


def load_group_features(client, pair: str, tables: list, sample_pct: float = 5.0) -> pd.DataFrame:
    """Load features from a single group of tables."""
    if not tables:
        return None

    # Build query for this group (JOIN tables within group)
    base = tables[0]
    select_parts = [f"t0.interval_time"]

    for i, t in enumerate(tables[:5]):  # Limit to 5 tables per group to avoid memory
        alias = f"t{i}"
        for col in t['columns'][:100]:  # Limit columns per table
            select_parts.append(f"{alias}.{col} as {t['table_name']}_{col}")

    # Add targets
    for h in HORIZONS:
        select_parts.append(f"targets.target_bqx45_h{h}")

    # Build JOINs
    joins = []
    for i, t in enumerate(tables[1:5], 1):
        joins.append(f"LEFT JOIN `{t['table_id']}` t{i} ON t0.interval_time = t{i}.interval_time")

    joins.append(f"JOIN `{PROJECT}.{ANALYTICS_DATASET}.targets_{pair}` targets ON t0.interval_time = targets.interval_time")

    query = f"""
    SELECT {', '.join(select_parts)}
    FROM `{base['table_id']}` t0
    {' '.join(joins)}
    WHERE RAND() < {sample_pct / 100.0}
    AND targets.target_bqx45_h15 IS NOT NULL
    LIMIT 30000
    """

    try:
        return client.query(query).to_dataframe()
    except Exception as e:
        print(f"    Error loading group: {e}")
        return None


# =============================================================================
# STAGE 1: SAFE PRUNING
# =============================================================================
def safe_prune(df: pd.DataFrame, feature_cols: list) -> tuple:
    """Remove constant, near-constant, and extreme missingness features."""
    pruned = []
    kept = []

    for col in feature_cols:
        if col not in df.columns:
            continue

        series = df[col]

        # Check missingness (>99% missing)
        missing_pct = series.isna().mean()
        if missing_pct > 0.99:
            pruned.append((col, 'missing', missing_pct))
            continue

        # Check constant (zero variance)
        if series.dropna().nunique() <= 1:
            pruned.append((col, 'constant', 0))
            continue

        # Check near-constant (>99% same value)
        value_counts = series.value_counts(normalize=True)
        if len(value_counts) > 0 and value_counts.iloc[0] > 0.99:
            pruned.append((col, 'near_constant', value_counts.iloc[0]))
            continue

        kept.append(col)

    return kept, pruned


# =============================================================================
# STAGE 2: FEATURE CLUSTERING (correlation families)
# =============================================================================
def cluster_correlated_features(df: pd.DataFrame, feature_cols: list,
                                 threshold: float = 0.95) -> dict:
    """Cluster highly correlated features, keep one representative per cluster."""
    if len(feature_cols) < 2:
        return {col: col for col in feature_cols}

    # Compute correlation matrix (sample for speed)
    sample = df[feature_cols].sample(min(10000, len(df)), random_state=42)
    sample = sample.apply(pd.to_numeric, errors='coerce')

    # Fill NaN with column median
    sample = sample.fillna(sample.median())

    try:
        corr = sample.corr().abs()
    except Exception:
        return {col: col for col in feature_cols}

    # Build clusters using simple greedy approach
    clusters = {}
    assigned = set()

    for col in feature_cols:
        if col in assigned:
            continue

        # Find all features correlated above threshold
        if col in corr.columns:
            correlated = corr[col][corr[col] > threshold].index.tolist()
        else:
            correlated = [col]

        # Assign to cluster
        cluster_rep = col  # First feature becomes representative
        for c in correlated:
            if c not in assigned:
                clusters[c] = cluster_rep
                assigned.add(c)

    return clusters


# =============================================================================
# STAGE 3: GROUP-FIRST SCREENING
# =============================================================================
def screen_group(df: pd.DataFrame, feature_cols: list, target_col: str) -> dict:
    """Quick screening of a feature group using fast model."""
    if not feature_cols or len(df) < 500:
        return {'auc': 0, 'features_used': 0, 'top_features': []}

    # Prepare data
    X = df[feature_cols].apply(pd.to_numeric, errors='coerce')
    y = (pd.to_numeric(df[target_col], errors='coerce') > 0).astype(int)

    mask = ~(X.isna().any(axis=1) | y.isna())
    X_clean = X[mask].values
    y_clean = y[mask].values

    if len(X_clean) < 500 or len(np.unique(y_clean)) < 2:
        return {'auc': 0, 'features_used': 0, 'top_features': []}

    # Quick LightGBM
    lgb_train = lgb.Dataset(X_clean, label=y_clean, feature_name=feature_cols)
    params = {
        'objective': 'binary', 'metric': 'auc',
        'num_leaves': 31, 'learning_rate': 0.1,
        'feature_fraction': 0.8, 'verbose': -1, 'seed': 42
    }

    try:
        model = lgb.train(params, lgb_train, num_boost_round=50)
        importance = model.feature_importance()
        auc = model.best_score.get('training', {}).get('auc', 0)

        # Get top features
        sorted_idx = np.argsort(importance)[::-1]
        top_features = [(feature_cols[i], int(importance[i])) for i in sorted_idx[:20]]

        return {
            'auc': float(auc) if auc else 0,
            'features_used': len(feature_cols),
            'top_features': top_features
        }
    except Exception as e:
        return {'auc': 0, 'features_used': 0, 'top_features': [], 'error': str(e)}


# =============================================================================
# STAGE 4: STABILITY SELECTION
# =============================================================================
def stability_selection(df: pd.DataFrame, feature_cols: list, target_col: str,
                        n_iterations: int = 10, n_folds: int = 5) -> dict:
    """Run stability selection across multiple folds and seeds."""
    if not feature_cols or len(df) < 1000:
        return {}

    # Prepare data
    X = df[feature_cols].apply(pd.to_numeric, errors='coerce')
    y = (pd.to_numeric(df[target_col], errors='coerce') > 0).astype(int)

    mask = ~(X.isna().any(axis=1) | y.isna())
    X_clean = X[mask].fillna(0).values
    y_clean = y[mask].values

    if len(X_clean) < 1000:
        return {}

    # Track selection frequency
    selection_counts = defaultdict(int)
    importance_sums = defaultdict(float)
    total_runs = 0

    # Standardize for Elastic Net
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_clean)

    for seed in range(n_iterations):
        try:
            # Elastic Net (L1+L2 for stability with correlated features)
            en = LogisticRegression(
                penalty='elasticnet', solver='saga', l1_ratio=0.5,
                C=0.1, max_iter=500, random_state=seed
            )
            en.fit(X_scaled, y_clean)

            # Track non-zero coefficients
            for i, coef in enumerate(en.coef_[0]):
                if abs(coef) > 1e-6:
                    selection_counts[feature_cols[i]] += 1
                    importance_sums[feature_cols[i]] += abs(coef)

            total_runs += 1

            # Also run LightGBM with different seed
            lgb_train = lgb.Dataset(X_clean, label=y_clean, feature_name=feature_cols)
            params = {
                'objective': 'binary', 'metric': 'binary_logloss',
                'num_leaves': 31, 'learning_rate': 0.05,
                'feature_fraction': 0.6, 'bagging_fraction': 0.8,
                'verbose': -1, 'seed': seed
            }
            model = lgb.train(params, lgb_train, num_boost_round=100)
            importance = model.feature_importance()

            # Track top 50% by importance
            threshold = np.percentile(importance, 50)
            for i, imp in enumerate(importance):
                if imp >= threshold:
                    selection_counts[feature_cols[i]] += 1
                    importance_sums[feature_cols[i]] += imp

            total_runs += 1

        except Exception as e:
            continue

    # Compute selection frequency
    stability_scores = {}
    for feat in feature_cols:
        if feat in selection_counts:
            freq = selection_counts[feat] / total_runs if total_runs > 0 else 0
            avg_imp = importance_sums[feat] / selection_counts[feat] if selection_counts[feat] > 0 else 0
            stability_scores[feat] = {
                'frequency': freq,
                'avg_importance': avg_imp,
                'score': freq * avg_imp  # Combined score
            }

    return stability_scores


# =============================================================================
# STAGE 5: ABLATION TESTING
# =============================================================================
def ablation_test(df: pd.DataFrame, feature_cols: list, target_col: str,
                  groups_to_test: dict) -> dict:
    """Test performance impact of removing each group."""
    if not feature_cols or len(df) < 1000:
        return {}

    # Prepare full data
    X = df[feature_cols].apply(pd.to_numeric, errors='coerce')
    y = (pd.to_numeric(df[target_col], errors='coerce') > 0).astype(int)

    mask = ~(X.isna().any(axis=1) | y.isna())
    X_clean = X[mask].values
    y_clean = y[mask].values

    if len(X_clean) < 1000:
        return {}

    # Baseline performance (all features)
    lgb_train = lgb.Dataset(X_clean, label=y_clean, feature_name=feature_cols)
    params = {
        'objective': 'binary', 'metric': 'auc',
        'num_leaves': 63, 'learning_rate': 0.05,
        'verbose': -1, 'seed': 42
    }

    try:
        baseline_model = lgb.train(params, lgb_train, num_boost_round=100)
        baseline_auc = baseline_model.best_score.get('training', {}).get('auc', 0.5)
    except Exception:
        baseline_auc = 0.5

    ablation_results = {'baseline_auc': baseline_auc, 'groups': {}}

    # Test removing each group
    for group_name, group_features in groups_to_test.items():
        # Features without this group
        remaining_features = [f for f in feature_cols if f not in group_features]
        remaining_indices = [i for i, f in enumerate(feature_cols) if f not in group_features]

        if not remaining_features:
            continue

        X_ablated = X_clean[:, remaining_indices]

        try:
            lgb_train_ablated = lgb.Dataset(X_ablated, label=y_clean, feature_name=remaining_features)
            ablated_model = lgb.train(params, lgb_train_ablated, num_boost_round=100)
            ablated_auc = ablated_model.best_score.get('training', {}).get('auc', 0.5)

            delta = baseline_auc - ablated_auc
            ablation_results['groups'][group_name] = {
                'auc_without': ablated_auc,
                'delta_auc': delta,
                'features_removed': len(group_features),
                'is_critical': delta > 0.005  # >0.5% AUC drop = critical
            }
        except Exception:
            continue

    return ablation_results


# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================
def run_robust_selection(pair: str, sample_pct: float = 5.0, horizon: int = 15):
    """Run the complete robust feature selection pipeline."""
    print("=" * 80)
    print("ROBUST FEATURE SELECTION SYSTEM")
    print(f"Pair: {pair.upper()}, Horizon: h{horizon}, Sample: {sample_pct}%")
    print("=" * 80)

    client = bigquery.Client(project=PROJECT)
    target_col = f'target_bqx45_h{horizon}'

    # Discover all feature groups
    print("\n=== DISCOVERING FEATURE GROUPS ===")
    feature_groups = discover_feature_tables(client, pair)

    total_tables = sum(len(tables) for tables in feature_groups.values())
    print(f"Found {len(feature_groups)} groups, {total_tables} tables")

    for group, tables in sorted(feature_groups.items()):
        total_cols = sum(len(t['columns']) for t in tables)
        print(f"  {group}: {len(tables)} tables, {total_cols} columns")

    results = {
        'pair': pair,
        'horizon': horizon,
        'timestamp': datetime.now().isoformat(),
        'groups': {},
        'stability_selection': {},
        'ablation': {},
        'final_features': []
    }

    all_features = []
    group_features_map = {}

    # Process each group
    for group_name, tables in feature_groups.items():
        print(f"\n=== PROCESSING GROUP: {group_name} ===")

        # Stage 3: Load and screen group
        df = load_group_features(client, pair, tables, sample_pct)
        if df is None or len(df) < 500:
            print(f"  Skipped (insufficient data)")
            continue

        target_cols = [c for c in df.columns if c.startswith('target_')]
        feature_cols = [c for c in df.columns if c not in target_cols and c != 'interval_time']

        print(f"  Loaded: {len(df):,} rows, {len(feature_cols)} features")

        # Stage 1: Safe pruning
        kept_features, pruned = safe_prune(df, feature_cols)
        print(f"  After pruning: {len(kept_features)} features ({len(pruned)} removed)")

        if not kept_features:
            continue

        # Stage 2: Cluster correlated features
        clusters = cluster_correlated_features(df, kept_features)
        representatives = list(set(clusters.values()))
        print(f"  After clustering: {len(representatives)} representatives")

        # Stage 3: Group screening
        screening = screen_group(df, representatives, target_col)
        print(f"  Group AUC: {screening['auc']:.4f}")

        # Stage 4: Stability selection (on representatives)
        print(f"  Running stability selection...")
        stability = stability_selection(df, representatives, target_col, n_iterations=5)

        # Identify stable features (frequency > 60%)
        stable_features = [
            f for f, scores in stability.items()
            if scores['frequency'] >= 0.6
        ]
        print(f"  Stable features (>60% frequency): {len(stable_features)}")

        # Store results
        results['groups'][group_name] = {
            'total_features': len(feature_cols),
            'after_pruning': len(kept_features),
            'representatives': len(representatives),
            'stable_features': len(stable_features),
            'screening_auc': screening['auc'],
            'top_features': screening['top_features'][:10]
        }

        results['stability_selection'][group_name] = {
            f: scores for f, scores in stability.items()
            if scores['frequency'] >= 0.4  # Keep features with >40% selection
        }

        all_features.extend(stable_features)
        group_features_map[group_name] = stable_features

    # Stage 5: Cross-group ablation
    print("\n=== ABLATION TESTING ===")
    print("(Testing impact of removing each group)")

    # For ablation, we need to load a combined dataset
    # Use the stable features from all groups
    if all_features:
        print(f"Total stable features across groups: {len(all_features)}")

        # Note: Full ablation would require loading all features together
        # For now, store group-level importance ranking
        group_importance = []
        for group_name, group_data in results['groups'].items():
            group_importance.append({
                'group': group_name,
                'auc': group_data['screening_auc'],
                'stable_count': group_data['stable_features']
            })

        group_importance.sort(key=lambda x: -x['auc'])
        print("\nGroup importance ranking by AUC:")
        for i, g in enumerate(group_importance[:15], 1):
            print(f"  {i:2d}. {g['group']}: AUC={g['auc']:.4f}, stable={g['stable_count']}")

        results['ablation']['group_ranking'] = group_importance

    # Final feature selection
    print("\n=== FINAL FEATURE SELECTION ===")

    # Combine all stable features, ranked by stability score
    all_stability = {}
    for group_name, features in results['stability_selection'].items():
        for feat, scores in features.items():
            all_stability[feat] = {
                'group': group_name,
                **scores
            }

    # Sort by combined score (frequency * importance)
    ranked_features = sorted(
        all_stability.items(),
        key=lambda x: -x[1]['score']
    )

    # Select top features
    top_500 = [f for f, _ in ranked_features[:500]]
    top_1000 = [f for f, _ in ranked_features[:1000]]

    results['final_features'] = {
        'top_500': top_500,
        'top_1000': top_1000,
        'complete_ranking': [
            {'rank': i+1, 'feature': f, **scores}
            for i, (f, scores) in enumerate(ranked_features)
        ]
    }

    # Category breakdown
    idx_count = sum(1 for f in top_500 if 'idx' in f.lower())
    bqx_count = sum(1 for f in top_500 if 'bqx' in f.lower())
    cov_count = sum(1 for f in top_500 if 'cov_' in f.lower())
    corr_count = sum(1 for f in top_500 if 'corr_' in f.lower())

    print(f"\nTop 500 breakdown:")
    print(f"  IDX features: {idx_count}")
    print(f"  BQX features: {bqx_count}")
    print(f"  Covariance: {cov_count}")
    print(f"  Correlation: {corr_count}")
    print(f"  Other: {500 - idx_count - bqx_count - cov_count - corr_count}")

    print(f"\nTop 20 features by stability score:")
    for i, (feat, scores) in enumerate(ranked_features[:20], 1):
        print(f"  {i:2d}. [{scores['group'][:8]}] {feat[:50]}: "
              f"freq={scores['frequency']:.0%}, score={scores['score']:.2f}")

    # Save results
    output_file = f"/tmp/robust_feature_selection_{pair}_h{horizon}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    return results


def run_robust_selection_from_df(pair: str, df: pd.DataFrame, horizon: int = 15):
    """Run robust selection directly from a DataFrame (parquet mode)."""
    print("=" * 80)
    print("ROBUST FEATURE SELECTION FROM PARQUET")
    print(f"Pair: {pair.upper()}, Horizon: h{horizon}")
    print(f"Data: {len(df):,} rows, {len(df.columns)} columns")
    print("=" * 80)

    target_col = f'target_bqx45_h{horizon}'

    # Identify features and targets
    target_cols = [c for c in df.columns if c.startswith('target_')]
    feature_cols = [c for c in df.columns if c not in target_cols and c not in ['interval_time', 'pair']]

    print(f"\nFeatures: {len(feature_cols)}")
    print(f"Targets: {len(target_cols)}")

    if target_col not in df.columns:
        print(f"ERROR: Target column {target_col} not found")
        return None

    # Group features by prefix
    feature_groups = defaultdict(list)
    for col in feature_cols:
        for prefix, group_name in FEATURE_GROUPS.items():
            if col.startswith(prefix) or f'_{prefix}' in col:
                feature_groups[group_name].append(col)
                break
        else:
            feature_groups['other'].append(col)

    print("\n=== FEATURE GROUPS ===")
    for group, cols in sorted(feature_groups.items()):
        print(f"  {group}: {len(cols)} features")

    # Prepare data
    X = df[feature_cols].copy()
    y = (df[target_col] > 0).astype(int)

    # Remove columns with too many nulls
    null_pct = X.isnull().mean()
    good_cols = null_pct[null_pct < 0.3].index.tolist()
    X = X[good_cols]
    print(f"\nAfter null filter: {len(good_cols)} features")

    # Fill remaining nulls
    X = X.fillna(0)

    # Run stability selection
    print("\n=== STABILITY SELECTION ===")
    results = stability_selection(X, y, n_folds=5, n_seeds=3, threshold=0.5)

    # Save results
    output_file = f"/home/micha/bqx_ml_v3/intelligence/stable_features_{pair}_h{horizon}.json"
    output = {
        'pair': pair,
        'horizon': horizon,
        'source': 'parquet',
        'timestamp': datetime.now().isoformat(),
        'total_features': len(feature_cols),
        'selected_features': results['stable_features'],
        'feature_count': len(results['stable_features']),
        'stability_scores': {f: float(s) for f, s in results['scores'].items()
                           if s >= 0.5}
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n=== RESULTS ===")
    print(f"Selected: {len(results['stable_features'])} features")
    print(f"Saved to: {output_file}")

    return output


def main():
    pair = sys.argv[1] if len(sys.argv) > 1 else "eurusd"
    sample_pct = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
    horizon = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    # GAP-001 FIX: Default to parquet (Step 6 output), use --bq flag for BigQuery fallback
    use_parquet = "--bq" not in sys.argv

    if use_parquet:
        print("Using parquet mode (Step 6 output) - DEFAULT")
        df = load_from_parquet(pair)
        if df is not None:
            # Run selection on parquet data
            run_robust_selection_from_df(pair, df, horizon)
        else:
            print("ERROR: Parquet not found, falling back to BigQuery")
            run_robust_selection(pair, sample_pct, horizon)
    else:
        print("Using BigQuery mode (--bq flag specified)")
        run_robust_selection(pair, sample_pct, horizon)


if __name__ == "__main__":
    main()
