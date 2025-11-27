#!/usr/bin/env python3
"""
Test regression-based features (lin_term, quad_term, residual)
Authorization: ALPHA-2B-COMPREHENSIVE
"""

import numpy as np
import pandas as pd
from google.cloud import bigquery
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Initialize BigQuery client
client = bigquery.Client(project='bqx-ml')

# Currency pairs
PAIRS = ['eurusd', 'gbpusd', 'usdjpy', 'audusd', 'usdcad']  # Test on 5 major pairs first

def create_regression_features(idx_data, bqx_data, pair, windows=[15, 30, 60, 120, 240]):
    """Create regression-based features from price data"""

    features = pd.DataFrame(index=idx_data.index)

    for window in windows:
        # Linear regression features (trend)
        for i in range(len(idx_data)):
            if i >= window:
                # Get window of data
                window_data = idx_data['close_idx'].iloc[i-window:i].values
                x = np.arange(window)

                # Fit polynomial regression
                coeffs = np.polyfit(x, window_data, 2)  # 2nd degree polynomial

                # Extract features
                features.loc[idx_data.index[i], f'idx_lin_term_w{window}'] = coeffs[1]  # Linear term
                features.loc[idx_data.index[i], f'idx_quad_term_w{window}'] = coeffs[0]  # Quadratic term

                # Calculate residuals
                fitted = np.polyval(coeffs, x)
                residuals = window_data - fitted
                features.loc[idx_data.index[i], f'idx_residual_var_w{window}'] = np.var(residuals)

                # R-squared
                ss_tot = np.sum((window_data - np.mean(window_data))**2)
                ss_res = np.sum(residuals**2)
                r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                features.loc[idx_data.index[i], f'idx_r2_w{window}'] = r2

        # Same for BQX data
        bqx_col = f'{pair}_bqx'
        for i in range(len(bqx_data)):
            if i >= window:
                window_data = bqx_data[bqx_col].iloc[i-window:i].values
                x = np.arange(window)

                coeffs = np.polyfit(x, window_data, 2)

                features.loc[bqx_data.index[i], f'bqx_lin_term_w{window}'] = coeffs[1]
                features.loc[bqx_data.index[i], f'bqx_quad_term_w{window}'] = coeffs[0]

                fitted = np.polyval(coeffs, x)
                residuals = window_data - fitted
                features.loc[bqx_data.index[i], f'bqx_residual_var_w{window}'] = np.var(residuals)

                ss_tot = np.sum((window_data - np.mean(window_data))**2)
                ss_res = np.sum(residuals**2)
                r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                features.loc[bqx_data.index[i], f'bqx_r2_w{window}'] = r2

    # Forward fill NaN values
    features = features.fillna(method='ffill').fillna(0)

    return features

def test_regression_features(pair):
    """Test regression features for a pair"""

    print(f"\n  Testing {pair.upper()} regression features...")

    try:
        # Load data
        idx_query = f"""
        SELECT
            interval_time,
            close_idx
        FROM `bqx-ml.bqx_ml_v3_features.{pair}_idx`
        ORDER BY interval_time
        """

        bqx_query = f"""
        SELECT
            interval_time,
            {pair}_bqx
        FROM `bqx-ml.bqx_ml_v3_features.{pair}_bqx`
        ORDER BY interval_time
        """

        idx_data = client.query(idx_query).to_dataframe()
        bqx_data = client.query(bqx_query).to_dataframe()

        if len(idx_data) < 10000:
            print(f"    ⚠️ Insufficient data: {len(idx_data)} rows")
            return None

        # Set index
        idx_data.set_index('interval_time', inplace=True)
        bqx_data.set_index('interval_time', inplace=True)

        # Merge data
        data = idx_data.join(bqx_data, how='inner')

        # Create base features (from Smart Dual Processing)
        features = pd.DataFrame(index=data.index)

        # IDX features (leading indicators)
        features['idx_lag_1'] = data['close_idx'].shift(1)
        features['idx_lag_2'] = data['close_idx'].shift(2)
        features['idx_lag_3'] = data['close_idx'].shift(3)
        features['idx_lag_5'] = data['close_idx'].shift(5)
        features['idx_lag_8'] = data['close_idx'].shift(8)
        features['idx_lag_13'] = data['close_idx'].shift(13)

        # BQX features (lagging indicators)
        features[f'bqx_lag_1'] = data[f'{pair}_bqx'].shift(1)
        features[f'bqx_lag_2'] = data[f'{pair}_bqx'].shift(2)
        features[f'bqx_lag_3'] = data[f'{pair}_bqx'].shift(3)
        features[f'bqx_lag_5'] = data[f'{pair}_bqx'].shift(5)
        features[f'bqx_lag_8'] = data[f'{pair}_bqx'].shift(8)
        features[f'bqx_lag_13'] = data[f'{pair}_bqx'].shift(13)

        # Drop NaN rows
        features = features.dropna()
        y = data[f'{pair}_bqx'].loc[features.index]

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, y, test_size=0.2, shuffle=False
        )

        # Train baseline model
        baseline_model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        baseline_model.fit(X_train, y_train)
        baseline_pred = baseline_model.predict(X_test)
        baseline_r2 = r2_score(y_test, baseline_pred)

        print(f"    Baseline R²: {baseline_r2:.4f}")

        # Now add regression features
        regression_features = create_regression_features(
            idx_data,
            bqx_data,
            pair,
            windows=[15, 30, 60, 120, 240]
        )

        # Merge regression features
        enhanced_features = features.join(regression_features, how='inner')
        enhanced_features = enhanced_features.dropna()
        y_enhanced = data[f'{pair}_bqx'].loc[enhanced_features.index]

        # Split enhanced data
        X_train_enh, X_test_enh, y_train_enh, y_test_enh = train_test_split(
            enhanced_features, y_enhanced, test_size=0.2, shuffle=False
        )

        # Train enhanced model
        enhanced_model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        enhanced_model.fit(X_train_enh, y_train_enh)
        enhanced_pred = enhanced_model.predict(X_test_enh)
        enhanced_r2 = r2_score(y_test_enh, enhanced_pred)

        print(f"    Enhanced R²: {enhanced_r2:.4f}")

        improvement = enhanced_r2 - baseline_r2
        improvement_pct = (improvement / baseline_r2) * 100

        if improvement > 0.01:  # Keep if improves by 1% or more
            print(f"    ✅ KEPT: Improvement {improvement:.4f} ({improvement_pct:.2f}%)")

            # Get feature importance
            feature_importance = enhanced_model.get_score(importance_type='gain')
            regression_features_used = [f for f in feature_importance.keys()
                                       if 'lin_term' in f or 'quad_term' in f or 'residual' in f or 'r2' in f]

            return {
                'pair': pair,
                'baseline_r2': baseline_r2,
                'enhanced_r2': enhanced_r2,
                'improvement': improvement,
                'improvement_pct': improvement_pct,
                'kept': True,
                'num_features': len(regression_features.columns),
                'top_regression_features': regression_features_used[:10]
            }
        else:
            print(f"    ❌ DROPPED: Improvement {improvement:.4f} ({improvement_pct:.2f}%)")
            return {
                'pair': pair,
                'baseline_r2': baseline_r2,
                'enhanced_r2': enhanced_r2,
                'improvement': improvement,
                'improvement_pct': improvement_pct,
                'kept': False,
                'num_features': len(regression_features.columns)
            }

    except Exception as e:
        print(f"    ❌ Error: {str(e)}")
        return None

def main():
    """Main testing function"""

    print("\n" + "="*70)
    print("COMPREHENSIVE REGRESSION FEATURES TESTING")
    print("Authorization: ALPHA-2B-COMPREHENSIVE")
    print("="*70)

    print("\n📊 TESTING REGRESSION FEATURES (lin_term, quad_term, residual)")
    print("Testing on 5 major pairs with multiple window sizes")

    results = []
    total_kept = 0

    for pair in PAIRS:
        result = test_regression_features(pair)
        if result:
            results.append(result)
            if result['kept']:
                total_kept += 1

    # Save results
    output = {
        'timestamp': datetime.now().isoformat(),
        'authorization': 'ALPHA-2B-COMPREHENSIVE',
        'feature_type': 'regression_features',
        'total_tested': len(PAIRS),
        'total_kept': total_kept,
        'results': results
    }

    with open('/home/micha/bqx_ml_v3/regression_features_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "="*70)
    print("REGRESSION FEATURES TEST COMPLETE")
    print(f"Tested: {len(PAIRS)} pairs")
    print(f"Kept: {total_kept} feature sets")

    if total_kept > 0:
        avg_improvement = np.mean([r['improvement_pct'] for r in results if r['kept']])
        print(f"Average improvement: {avg_improvement:.2f}%")

    print("Results saved to: regression_features_results.json")
    print("="*70)

if __name__ == "__main__":
    main()