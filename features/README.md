# BQX ML V3 Feature Specifications

**Directory**: `/features/`
**Purpose**: Detailed feature specifications for all polynomial regression and derived features
**Last Updated**: 2025-11-29

---

## Feature Specification Files

| File | Feature Type | Tables | Description |
|------|--------------|--------|-------------|
| [POLYNOMIAL_REG_FEATURES.md](POLYNOMIAL_REG_FEATURES.md) | REG | 56 | Primary polynomial regression features |
| [COV_REG_FEATURES.md](COV_REG_FEATURES.md) | COV_REG | 336 | Covariance between reg_ features |
| [VAR_REG_FEATURES.md](VAR_REG_FEATURES.md) | VAR_REG | 28 | Variance aggregation per currency |
| [CSI_REG_FEATURES.md](CSI_REG_FEATURES.md) | CSI_REG | 32 | Currency Strength Index from reg_ |
| [TRI_REG_FEATURES.md](TRI_REG_FEATURES.md) | TRI_REG | 36 | Triangular arbitrage analysis |
| [MKT_REG_FEATURES.md](MKT_REG_FEATURES.md) | MKT_REG | 4 | Market-wide aggregation |

**Total Tables**: 492

---

## Dependency Hierarchy

```
reg_{pair}                    ← Primary polynomial features (56 tables)
    │
    ├── cov_reg_{p1}_{p2}     ← Pair-pair covariance (336 tables)
    │
    ├── var_reg_{currency}    ← Per-currency variance (28 tables)
    │       │
    │       └── csi_reg_{currency}  ← Currency strength (32 tables)
    │
    ├── tri_reg_{c1}_{c2}_{c3}  ← Triangular analysis (36 tables)
    │
    └── mkt_reg               ← Market-wide (4 tables)
```

---

## Polynomial Regression Overview

All features are derived from quadratic polynomial fits:

```python
y = ax² + bx + c

Where:
- x = np.arange(W)   # [0, 1, 2, ..., W-1]
- y = values[-W:]    # Last W source values
- a = quad_term      # Curvature/acceleration
- b = lin_term       # Slope/velocity
- c = const_term     # Intercept
```

### Windows

| Window | Intervals | ~Time (15-min bars) |
|--------|-----------|---------------------|
| 45 | 45 | ~11 hours |
| 90 | 90 | ~22 hours |
| 180 | 180 | ~45 hours |
| 360 | 360 | ~90 hours |
| 720 | 720 | ~180 hours |
| 1440 | 1440 | ~360 hours |
| 2880 | 2880 | ~720 hours |

### Variants

| Variant | Source | Table Pattern | Interpretation |
|---------|--------|---------------|----------------|
| IDX | Close price | `reg_{pair}` | Price trends |
| BQX | BQX oscillator | `reg_bqx_{pair}` | Momentum trends |

---

## Column Summary

### Per reg_ Table (Primary)
- 18 new polynomial columns per window
- 7 windows = 126 new columns
- 10 existing columns retained
- **Total: 196 columns**

### Per cov_reg_ Table
- 14 covariance columns per window
- 3 cross-correlation columns per window
- 7 windows
- **Total: 123 columns**

### Per var_reg_ Table
- Variance, aggregation, derived metrics
- **Total: 122 columns**

### Per csi_reg_ Table
- Strength, ranking, momentum metrics
- **Total: 107 columns**

### Per tri_reg_ Table
- Triangular sum, divergence, arbitrage signals
- **Total: 119 columns**

### Per mkt_reg Table
- Market-wide aggregation, regime classification
- **Total: 155 columns**

---

## Implementation Status

| Feature Type | Specified | Implemented | Gap |
|--------------|-----------|-------------|-----|
| REG (polynomial) | ✓ | ✗ | 56 tables |
| COV_REG | ✓ | ✗ | 336 tables |
| VAR_REG | ✓ | ✗ | 28 tables |
| CSI_REG | ✓ | ✗ | 32 tables |
| TRI_REG | ✓ | ✗ | 36 tables |
| MKT_REG | ✓ | ✗ | 4 tables |

**All features specified. BA implementation pending.**

---

## Related Documents

- [/mandate/POLYNOMIAL_REGRESSION_FEATURE_GAP_ANALYSIS.md](../mandate/POLYNOMIAL_REGRESSION_FEATURE_GAP_ANALYSIS.md) - Gap analysis
- [/mandate/BQX_ML_V3_FEATURE_INVENTORY.md](../mandate/BQX_ML_V3_FEATURE_INVENTORY.md) - Full feature inventory
- [/mandate/FEATURE_TABLE_DIRECTORY.md](../mandate/FEATURE_TABLE_DIRECTORY.md) - Complete table directory

---

*Specification created: 2025-11-29*
