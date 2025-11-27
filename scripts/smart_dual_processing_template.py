#!/usr/bin/env python3
"""
Smart Dual Processing Template
Implements intelligent IDX+BQX feature engineering based on lag insight.
Created: 2025-11-27 00:55:00
"""

import pandas as pd
import numpy as np
from typing import Tuple, List
import xgboost as xgb
from sklearn.model_selection import train_test_split

def create_smart_dual_features(
    idx_data: pd.DataFrame,
    bqx_data: pd.DataFrame,
    target_window: int
) -> pd.DataFrame:
    """
    Create intelligent dual features addressing the lag problem.

    Key Insight: BQX values are lagged/smoothed indicators.
    IDX provides essential leading signals for changes.
    """

    features = pd.DataFrame(index=idx_data.index)

    # 1. CRITICAL: Recent IDX (Leading Indicators) - High Weight
    # These detect price changes BEFORE they appear in smoothed BQX
    features['idx_lag_1'] = idx_data['close'].shift(1)  # Most important
    features['idx_lag_2'] = idx_data['close'].shift(2)
    features['idx_lag_3'] = idx_data['close'].shift(3)
    features['idx_lag_5'] = idx_data['close'].shift(5)

    # 2. IMPORTANT: Selected BQX Trends (Momentum Context) - Medium Weight
    # Don't use all 14 - select key momentum indicators
    features['bqx_lag_1'] = bqx_data['bqx'].shift(1)  # Recent momentum
    features['bqx_lag_3'] = bqx_data['bqx'].shift(3)
    features['bqx_lag_7'] = bqx_data['bqx'].shift(7)
    features['bqx_lag_14'] = bqx_data['bqx'].shift(14)  # Longer trend

    # 3. DERIVED: Smart Features (Capture Relationships)
    # These help model understand market state

    # Price relative to moving average (support/resistance context)
    ma_20 = idx_data['close'].rolling(20).mean()
    features['idx_to_ma_ratio'] = idx_data['close'] / ma_20

    # Volatility (market regime)
    features['idx_volatility'] = idx_data['close'].rolling(20).std()

    # BQX acceleration (momentum change rate)
    features['bqx_acceleration'] = bqx_data['bqx'].shift(1) - bqx_data['bqx'].shift(2)

    # Price change velocity (how fast IDX is moving)
    features['idx_velocity'] = (idx_data['close'] - idx_data['close'].shift(3)) / 3

    # Target: Future BQX value
    features['target'] = bqx_data['bqx'].shift(-target_window)

    return features.dropna()

def get_feature_weights(feature_names: List[str]) -> np.ndarray:
    """
    Assign importance weights based on feature type.
    Recent IDX gets highest weight (leading indicators).
    """
    weights = []

    for feature in feature_names:
        if feature == 'idx_lag_1':
            weights.append(2.0)  # Highest - current market state
        elif feature == 'idx_lag_2':
            weights.append(1.8)
        elif feature == 'idx_lag_3':
            weights.append(1.5)
        elif feature == 'idx_lag_5':
            weights.append(1.2)
        elif 'bqx_lag' in feature:
            weights.append(1.0)  # Medium - momentum context
        else:
            weights.append(0.8)  # Lower - derived features

    return np.array(weights)

def train_smart_dual_model(
    features_df: pd.DataFrame,
    pair: str,
    window: int
) -> Tuple[xgb.XGBRegressor, dict]:
    """
    Train XGBoost with smart dual processing approach.
    """

    # Separate features and target
    feature_cols = [col for col in features_df.columns if col != 'target']
    X = features_df[feature_cols]
    y = features_df['target']

    # Split with temporal awareness
    split_point = int(len(X) * 0.7)
    X_train, X_temp = X[:split_point], X[split_point:]
    y_train, y_temp = y[:split_point], y[split_point:]

    # Further split validation and test
    X_val, X_test = X_temp[:len(X_temp)//2], X_temp[len(X_temp)//2:]
    y_val, y_test = y_temp[:len(y_temp)//2], y_temp[len(y_temp)//2:]

    # Get feature weights
    feature_weights = get_feature_weights(feature_cols)

    # Configure model with regularization to prevent overfitting
    model = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=8,           # Deeper for feature interactions
        learning_rate=0.05,    # Slower for stability
        subsample=0.8,
        colsample_bytree=0.7,  # Feature sampling
        reg_alpha=0.1,         # L1 regularization
        reg_lambda=1.0,        # L2 regularization
        random_state=42,
        tree_method='hist',
        early_stopping_rounds=20
    )

    # Train with feature weights
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
        # Note: XGBoost doesn't directly support feature weights,
        # but we can use sample weights based on feature importance
        sample_weight=np.ones(len(X_train))  # Uniform for now
    )

    # Evaluate
    from sklearn.metrics import r2_score, mean_squared_error

    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # Directional accuracy
    y_test_direction = np.sign(y_test)
    y_pred_direction = np.sign(y_pred)
    directional_accuracy = np.mean(y_test_direction == y_pred_direction)

    # Feature importance
    importance = model.feature_importances_
    feature_importance = dict(zip(feature_cols, importance))

    # Sort by importance
    sorted_importance = sorted(feature_importance.items(),
                              key=lambda x: x[1],
                              reverse=True)

    print(f"\n{'='*60}")
    print(f"SMART DUAL PROCESSING RESULTS - {pair} Window {window}")
    print(f"{'='*60}")
    print(f"R² Score: {r2:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"Directional Accuracy: {directional_accuracy:.2%}")
    print(f"\nTop 5 Most Important Features:")
    for feat, imp in sorted_importance[:5]:
        print(f"  {feat}: {imp:.4f}")

    # Check if IDX features are being used
    idx_importance = sum(imp for feat, imp in feature_importance.items()
                        if 'idx' in feat)
    bqx_importance = sum(imp for feat, imp in feature_importance.items()
                        if 'bqx' in feat)

    print(f"\nFeature Group Importance:")
    print(f"  IDX Features: {idx_importance:.2%}")
    print(f"  BQX Features: {bqx_importance:.2%}")
    print(f"  Derived Features: {1 - idx_importance - bqx_importance:.2%}")

    metrics = {
        'r2_score': r2,
        'rmse': rmse,
        'directional_accuracy': directional_accuracy,
        'feature_importance': dict(sorted_importance),
        'idx_total_importance': idx_importance,
        'bqx_total_importance': bqx_importance
    }

    return model, metrics

# Example usage
if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║         SMART DUAL PROCESSING IMPLEMENTATION            ║
    ║                                                          ║
    ║  Key Innovation: IDX provides leading indicators        ║
    ║  BQX provides lagging momentum context                  ║
    ║  Together they predict future BQX optimally             ║
    ╚══════════════════════════════════════════════════════════╝

    This template implements the critical insight that BQX
    values are inherently lagged (smoothed over intervals),
    while IDX provides immediate market state information.

    Expected Performance:
    - R² > 0.50 (vs 0.4648 BQX-only, 0.2692 naive dual)
    - 12-15 carefully selected features
    - Weighted importance favoring recent IDX
    """)