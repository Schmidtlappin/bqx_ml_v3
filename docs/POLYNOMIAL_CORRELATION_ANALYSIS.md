# Polynomial Feature Correlation Analysis

## Summary
- 28 currency pairs analyzed
- 8,624 polynomial feature correlations computed
- 7 windows x 7 horizons = 49 correlations per feature

## Top Features
1. reg_residual_1440 (EURUSD): 0.9248
2. reg_forecast_5_1440 (EURUSD): 0.9246
3. reg_resid_last_2880 (EURUSD): 0.9238

## Tiers
- TIER 1 (>=0.70): EURUSD, USDCHF
- TIER 2 (0.50-0.70): GBPUSD, NZDUSD, AUDUSD, USDCAD
- TIER 3 (0.30-0.50): Cross pairs
- TIER 4 (<0.30): Exotic crosses

## BigQuery Tables
- all_pairs_poly_correlation_matrix
- poly_feature_ranking  
- poly_window_horizon_analysis
- optimal_feature_slate

Generated: 2025-11-30
