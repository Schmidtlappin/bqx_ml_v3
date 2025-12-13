# BQX ML V3 NAMING STANDARD MANDATE

**Mandate ID**: BQX-ML-M008
**Status**: ACTIVE
**Priority**: P0-CRITICAL (ARCHITECTURAL FOUNDATION)
**Issued**: December 13, 2025
**Authority**: Chief Engineer (User-Mandated Standardization)
**Scope**: ALL tables, fields, features, targets, and identifiers

---

## MANDATE STATEMENT

**All naming conventions in BQX ML V3 SHALL follow standardized patterns** that:
1. Encode semantic meaning unambiguously
2. Enable programmatic parsing and validation
3. Maintain consistency across IDX and BQX variants
4. Support the 3-mandate architecture (M005, M006, M007)

**Non-compliance with this naming standard is PROHIBITED** in all new code and MUST be remediated in existing infrastructure.

---

## 1. TABLE NAMING CONVENTIONS

### 1.1 Primary Tables (Pair-Level Features)

**Pattern**: `{feature_type}_{variant}_{pair}`

**Components**:
- `feature_type`: agg, mom, vol, reg, align, der, rev, lag, regime, mrt, cyc, ext, div, tmp
- `variant`: `idx` (price-based) OR `bqx` (momentum-based)
- `pair`: lowercase, e.g., eurusd, gbpusd, usdjpy

**Examples**:
```
✅ agg_idx_eurusd          # Aggregation features from IDX for EURUSD
✅ reg_bqx_gbpusd          # Regression features from BQX for GBPUSD
✅ mom_idx_usdjpy          # Momentum features from IDX for USDJPY
✅ align_bqx_audusd        # Alignment features from BQX for AUDUSD

❌ eurusd_agg              # WRONG: pair comes last, not first
❌ reg_eurusd_bqx          # WRONG: variant comes before pair
❌ agg_EURUSD_idx          # WRONG: pair must be lowercase
```

**Count**: 28 pairs × 2 variants × ~14 feature types = **~784 primary tables**

---

### 1.2 Covariance Tables (Pair-to-Pair Comparisons)

**Pattern**: `cov_{feature_type}_{variant}_{pair1}_{pair2}`

**Components**:
- `cov`: Fixed prefix for covariance
- `feature_type`: agg, align, mom, vol, reg, lag, regime
- `variant`: `idx` OR `bqx` (MUST be same variant for both pairs - M007)
- `pair1`, `pair2`: Alphabetically sorted pairs (eurusd < gbpusd)

**Sorting Rule**: ALWAYS alphabetize pair names to avoid duplicates
- ✅ `cov_agg_bqx_audusd_nzdusd` (audusd < nzdusd alphabetically)
- ❌ `cov_agg_bqx_nzdusd_audusd` (WRONG: not alphabetized)

**Examples**:
```
✅ cov_agg_bqx_eurusd_gbpusd     # BQX aggregation comparison
✅ cov_reg_idx_audusd_nzdusd     # IDX regression comparison
✅ cov_mom_bqx_gbpusd_usdjpy     # BQX momentum comparison

❌ cov_agg_eurusd_gbpusd         # MISSING: variant identifier
❌ cov_bqx_agg_eurusd_gbpusd     # WRONG: variant position incorrect
❌ cov_agg_idx_bqx_eurusd_gbpusd # WRONG: cannot mix variants (violates M007)
```

**Count**: C(28,2) × 2 variants × 7 feature types = **2,646 COV tables** (target)

**Current**: 3,528 tables (includes additional Phase 3 variants)

---

### 1.3 Triangular Arbitrage Tables (3-Currency Relationships)

**Pattern**: `tri_{feature_type}_{variant}_{curr1}_{curr2}_{curr3}`

**Components**:
- `tri`: Fixed prefix for triangular
- `feature_type`: agg, align, mom, vol, reg
- `variant`: `idx` OR `bqx`
- `curr1`, `curr2`, `curr3`: Three-letter currency codes, alphabetically sorted

**Sorting Rule**: ALWAYS alphabetize currency codes
- ✅ `tri_agg_bqx_eur_gbp_usd` (alphabetical: e < g < u)
- ❌ `tri_agg_bqx_usd_eur_gbp` (WRONG: not alphabetized)

**Examples**:
```
✅ tri_agg_bqx_eur_gbp_usd       # EUR-GBP-USD triangle, BQX variant
✅ tri_reg_idx_aud_jpy_nzd       # AUD-JPY-NZD triangle, IDX variant
✅ tri_mom_bqx_chf_eur_usd       # CHF-EUR-USD triangle, BQX variant

❌ tri_eur_gbp_usd_agg           # WRONG: feature_type comes after variant
❌ tri_agg_eur_gbp_usd           # MISSING: variant identifier
```

**Count**: 18-70 triangles × 2 variants × 5 feature types = **180-700 TRI tables**

**Current**: 194 tables (5 feature type variants, 18 triangles)

---

### 1.4 Variance/Currency Family Tables

**Pattern**: `var_{feature_type}_{variant}_{currency}`

**Components**:
- `var`: Fixed prefix for variance
- `feature_type`: agg, align, mom, vol, reg
- `variant`: `idx` OR `bqx`
- `currency`: Three-letter code (usd, eur, gbp, jpy, aud, nzd, cad, chf)

**Examples**:
```
✅ var_agg_bqx_usd               # USD currency family aggregation, BQX
✅ var_reg_idx_eur               # EUR currency family regression, IDX
✅ var_mom_bqx_gbp               # GBP currency family momentum, BQX

❌ var_usd_agg                   # MISSING: variant identifier
❌ var_agg_USD_bqx               # WRONG: currency must be lowercase
```

**Count**: 8 currencies × 2 variants × 5 feature types = **80 VAR tables**

**Current**: 63 tables (incomplete, some naming inconsistencies)

---

### 1.5 Correlation Tables (ETF/Asset Correlations)

**Pattern**: `corr_{asset_type}_{variant}_{pair}_{asset}`

**Components**:
- `corr`: Fixed prefix for correlation
- `asset_type`: `etf` (equity ETFs), `bqx` (BQX-to-BQX), `ibkr` (IDX-to-IDX)
- `variant`: `idx` OR `bqx` (for pair data)
- `pair`: Currency pair (eurusd, gbpusd, etc.)
- `asset`: ETF ticker (spy, gld, vix, etc.) OR currency for BQX/IBKR matrices

**Examples**:
```
✅ corr_etf_bqx_eurusd_spy       # EURUSD(BQX) correlation with SPY
✅ corr_etf_idx_gbpusd_gld       # GBPUSD(IDX) correlation with GLD
✅ corr_bqx_eurusd_gbpusd        # BQX-to-BQX correlation matrix
✅ corr_ibkr_eurusd_usdjpy       # IDX-to-IDX correlation matrix

❌ corr_spy_eurusd               # MISSING: asset_type and variant
❌ corr_eurusd_spy_etf           # WRONG: components out of order
```

**Count**:
- ETF: 28 pairs × 8 ETFs × 2 variants = 448 tables
- BQX matrices: 28 × 8 = 224 tables
- IBKR matrices: 28 × 8 = 224 tables
- **Total**: 896 CORR tables

**Current**: 896 tables ✅ COMPLETE

---

### 1.6 Base/Source Tables

**Pattern**: `base_{variant}_{pair}`

**Components**:
- `base`: Fixed prefix for base/source data
- `variant`: `idx` OR `bqx`
- `pair`: Currency pair

**Examples**:
```
✅ base_idx_eurusd               # Base IDX data for EURUSD
✅ base_bqx_gbpusd               # Base BQX data for GBPUSD

❌ eurusd_base                   # WRONG: pair comes last
❌ base_eurusd_idx               # WRONG: variant before pair
```

**Count**: 28 pairs × 2 variants = **56 base tables**

---

### 1.7 Market-Wide Tables

**Pattern**: `mkt_{feature_type}_{variant}`

**Components**:
- `mkt`: Fixed prefix for market-wide
- `feature_type`: agg, vol, regime, sentiment, etc.
- `variant`: `idx` OR `bqx` (aggregated across all pairs)

**Examples**:
```
✅ mkt_agg_bqx                   # Market-wide BQX aggregation
✅ mkt_vol_idx                   # Market-wide IDX volatility
✅ mkt_regime_bqx                # Market-wide BQX regime

❌ mkt_bqx_agg                   # WRONG: variant position
```

**Count**: ~6 feature types × 2 variants = **12 mkt tables**

**Current**: 12 tables ✅

---

## 1.9 LAG Table Exception (Approved 2025-12-14)

### Exception Scope

**ALL LAG tables (`lag_*`) are EXEMPT from the alphabetical sorting requirement and MAY include window suffixes.**

**Rationale**:
- **ML-First Optimization**: Prioritizes ML training delivery speed over table count reduction
- **Architectural Uniqueness**: LAG tables represent time-series windows (45, 90, 180, 360, 720, 1440, 2880 days), which are semantically meaningful as table-level identifiers
- **Consolidation Trade-Off**: Accepted +168 table count (224 vs 56 consolidated) for 2-4 days faster time-to-ML-training
- **Window-Specific Access Patterns**: Each window size may be queried independently, supporting performance optimization

### Affected Tables

**Count**: 224 LAG tables
**Pattern**: `lag_{variant}_{pair}_{window}`
**Windows**: 45, 90, 180, 360, 720, 1440, 2880 (7 windows)

**Examples of COMPLIANT LAG tables with window suffix**:
```
✅ lag_idx_eurusd_45             # IDX LAG for EURUSD, 45-day window
✅ lag_bqx_gbpusd_90             # BQX LAG for GBPUSD, 90-day window
✅ lag_idx_usdjpy_180            # IDX LAG for USDJPY, 180-day window
✅ lag_bqx_audusd_360            # BQX LAG for AUDUSD, 360-day window
✅ lag_idx_nzdusd_720            # IDX LAG for NZDUSD, 720-day window
✅ lag_bqx_eurusd_1440           # BQX LAG for EURUSD, 1440-day window
✅ lag_idx_gbpusd_2880           # IDX LAG for GBPUSD, 2880-day window
```

**Full Breakdown**:
- 28 pairs × 2 variants (IDX, BQX) × 4 windows = 224 LAG tables
- Note: Not all pairs have all 7 windows (some have 4 windows per pair/variant)

### Exception Boundaries

**This exception ONLY applies to LAG tables.**

**ALL other table types MUST follow strict M008 alphabetical sorting**:
- ❌ COV tables: NO EXCEPTION (must be `cov_*_pair1_pair2` with alphabetical pairs)
- ❌ TRI tables: NO EXCEPTION (must be `tri_*_curr1_curr2_curr3` with alphabetical currencies)
- ❌ VAR tables: NO EXCEPTION
- ❌ REG tables: NO EXCEPTION
- ❌ All other categories: NO EXCEPTION

**Window Suffix Rule**:
- ✅ LAG tables MAY have `_{window}` suffix (e.g., `_45`, `_90`, `_180`)
- ❌ All other table types MUST NOT have window suffix in table name (windows belong in column names)

### Consolidation Alternative (Rejected)

**Option A (REJECTED)**: Consolidate 224 LAG tables → 56 tables
- Pattern: `lag_{variant}_{pair}` (no window suffix)
- Store all 7 windows in a single table with `window` column
- Pros: -168 tables (-75% table count), cleaner schema
- Cons: +2-4 days implementation time, delayed ML training, complex queries

**Option B (APPROVED)**: Rename 224 LAG tables in place
- Pattern: `lag_{variant}_{pair}_{window}` (keep window suffix)
- No consolidation, no schema changes
- Pros: Fast execution (1 day), simple renames, immediate ML training
- Cons: +168 table count (+75% more LAG tables)

**Decision**: **Option B approved by CE on 2025-12-14**
- Rationale: ML-first optimization - table names don't affect ML model accuracy
- Timeline savings: 2-4 days faster to ML training
- Risk reduction: Simpler execution, no schema changes, no data migration

### Exception Validity

**Status**: **PERMANENT** (unless future consolidation is explicitly approved by CE)

**Approved By**: Chief Engineer (CE), 2025-12-14
**Documented By**: Enhancement Assistant (EA), 2025-12-14
**Reviewed By**: (awaiting QA sign-off)

**Audit Trail**: See COMPREHENSIVE_REMEDIATION_PLAN_20251213.md, Phase 4C, LAG Strategy Decision

---

## 2. FIELD/COLUMN NAMING CONVENTIONS

### 2.1 Feature Column Pattern

**Pattern**: `{feature_type}_{metric}_{window}`

**Components**:
- `feature_type`: Prefix matching table type (reg, agg, mom, vol, etc.)
- `metric`: Specific measurement (mean, std, lin_term, bqx, atr, etc.)
- `window`: Lookback period in intervals (45, 90, 180, 360, 720, 1440, 2880)

**Examples**:
```
✅ agg_mean_45                   # Mean aggregation, 45-interval window
✅ reg_lin_term_180              # Linear term from regression, 180-interval window
✅ vol_atr_720                   # Average True Range, 720-interval window
✅ mom_bqx_2880                  # BQX momentum, 2880-interval window

❌ mean_45_agg                   # WRONG: feature_type comes first
❌ reg_lin_term                  # MISSING: window identifier
❌ agg_mean_45min                # WRONG: window must be interval count, not time unit
```

### 2.2 Regression Feature Columns (M005 Compliance)

**Coefficient Columns** (raw polynomial coefficients):
```
reg_lin_coef_{W}                 # β₁ (linear coefficient)
reg_quad_coef_{W}                # β₂ (quadratic coefficient)
reg_const_{W}                    # β₀ (constant/intercept)
```

**Term Columns** (evaluated at endpoint x = W):
```
reg_lin_term_{W}                 # β₁ × W (linear contribution at endpoint)
reg_quad_term_{W}                # β₂ × W² (quadratic contribution at endpoint)
reg_residual_{W}                 # Actual - (quad_term + lin_term + const)
```

**Goodness-of-Fit Columns**:
```
reg_r2_{W}                       # R² score [0, 1]
reg_rmse_{W}                     # Root mean squared error
```

**Windows**: {45, 90, 180, 360, 720, 1440, 2880}

**Example (Window 180)**:
```
✅ reg_lin_coef_180              # Linear coefficient, 180-interval window
✅ reg_quad_term_180             # Quadratic term evaluated at x=180
✅ reg_residual_180              # Residual at endpoint
✅ reg_r2_180                    # R² for 180-interval fit

❌ lin_coef_180                  # MISSING: reg_ prefix
❌ reg_180_lin_coef              # WRONG: window position
```

### 2.3 Comparison Table Feature Columns

**COV Tables** - Include features from BOTH pairs:

**Pair 1 Features**:
```
pair1_lin_term_{W}               # Pair 1 linear term
pair1_quad_term_{W}              # Pair 1 quadratic term
pair1_residual_{W}               # Pair 1 residual
pair1_mean_{W}                   # Pair 1 mean (if using agg features)
```

**Pair 2 Features**:
```
pair2_lin_term_{W}               # Pair 2 linear term
pair2_quad_term_{W}              # Pair 2 quadratic term
pair2_residual_{W}               # Pair 2 residual
pair2_mean_{W}                   # Pair 2 mean (if using agg features)
```

**TRI Tables** - Include features from ALL THREE pairs:
```
pair1_lin_term_{W}               # First pair in triangle
pair2_lin_term_{W}               # Second pair in triangle
pair3_lin_term_{W}               # Third pair in triangle
... (repeat for all regression features)
```

### 2.4 Reserved Column Names (Non-Feature Columns)

**Metadata Columns** (do NOT follow feature naming pattern):
```
interval_time                    # Timestamp (PRIMARY KEY, PARTITION KEY)
pair                            # Pair identifier (CLUSTER KEY)
pair1, pair2                    # For COV tables
curr1, curr2, curr3             # For TRI tables
base_curr, quote_curr, cross_curr  # For TRI tables (alternative)
```

**Target Columns** (see Section 3):
```
target_bqx{W}_h{H}              # BQX targets
target_idx{W}_h{H}              # IDX targets (if used)
```

---

## 3. TARGET NAMING CONVENTIONS

### 3.1 Target Column Pattern

**Pattern**: `target_{variant}{window}_h{horizon}`

**Components**:
- `target_`: Fixed prefix
- `variant`: `bqx` OR `idx`
- `window`: BQX/IDX lookback window (45, 90, 180, 360, 720, 1440, 2880)
- `h{horizon}`: Prediction horizon (h15, h30, h45, h60, h75, h90, h105)

**Examples**:
```
✅ target_bqx45_h15              # Predict bqx_45 value 15 intervals ahead
✅ target_bqx180_h30             # Predict bqx_180 value 30 intervals ahead
✅ target_idx720_h60             # Predict idx_720 value 60 intervals ahead

❌ target_h15_bqx45              # WRONG: horizon before window
❌ bqx45_target_h15              # WRONG: target_ prefix missing
❌ target_bqx_45_h_15            # WRONG: underscores in window/horizon
```

### 3.2 Target Matrix

**Full Matrix**: 7 windows × 7 horizons = **49 target columns per variant**

**BQX Targets** (PRIMARY - user mandated):
```
target_bqx45_h15, target_bqx45_h30, target_bqx45_h45, ..., target_bqx45_h105
target_bqx90_h15, target_bqx90_h30, ..., target_bqx90_h105
target_bqx180_h15, ..., target_bqx180_h105
target_bqx360_h15, ..., target_bqx360_h105
target_bqx720_h15, ..., target_bqx720_h105
target_bqx1440_h15, ..., target_bqx1440_h105
target_bqx2880_h15, ..., target_bqx2880_h105
```

**Current Model Training**: Uses 7 horizons per model (one BQX window)
- Example: EURUSD h15 model uses 7 targets: target_bqx45_h15 through target_bqx2880_h15

---

## 4. IDENTIFIER NAMING CONVENTIONS

### 4.1 Currency Pair Identifiers

**Format**: Lowercase, no separators, base currency first

**Standard Pairs** (28 total):
```
eurusd, gbpusd, usdjpy, usdchf, audusd, usdcad, nzdusd
eurgbp, eurjpy, eurchf, euraud, eurcad, eurnzd
gbpjpy, gbpchf, gbpaud, gbpcad, gbpnzd
audjpy, audchf, audcad, audnzd
nzdjpy, nzdchf, nzdcad
cadjpy, cadchf
chfjpy
```

**Rules**:
- ✅ Always lowercase: `eurusd` not `EURUSD`
- ✅ No separator: `eurusd` not `eur_usd` or `eur-usd`
- ✅ Base currency first: `eurusd` not `usdeur`

### 4.2 Currency Identifiers

**Format**: Three-letter lowercase codes

**Standard Currencies** (8 total):
```
usd, eur, gbp, jpy, aud, nzd, cad, chf
```

### 4.3 Variant Identifiers

**Format**: Lowercase, 3-letter codes

**Standard Variants** (2 total):
```
idx    # Indexed price data (OHLCV)
bqx    # BQX momentum oscillator
```

**Rules**:
- ✅ NEVER mix variants in same table (M007 compliance)
- ✅ Always explicit (no default assumption)
- ✅ Consistent position in naming pattern

### 4.4 Window Identifiers

**Format**: Integer interval count (NOT time duration)

**Standard Windows** (7 total):
```
45, 90, 180, 360, 720, 1440, 2880
```

**Rules**:
- ✅ Use interval count: `45` not `45min` or `45m`
- ✅ No leading zeros: `45` not `045`
- ✅ Always use standard windows (no custom windows without approval)

### 4.5 Horizon Identifiers

**Format**: `h{interval_count}`

**Standard Horizons** (7 total):
```
h15, h30, h45, h60, h75, h90, h105
```

**Rules**:
- ✅ Include `h` prefix: `h15` not `15`
- ✅ No separator: `h15` not `h_15` or `h-15`
- ✅ Always use standard horizons

---

## 5. COMPLIANCE ENFORCEMENT MECHANISMS

### 5.1 Schema Validation Scripts

**File**: `/scripts/validate_naming_compliance.py`

**Function**: Validate all table and column names against M008 standard

```python
def validate_table_name(table_name: str) -> dict:
    """
    Validate table name against M008 naming standard.

    Returns:
        {
            'valid': bool,
            'table_type': str,  # 'primary', 'cov', 'tri', 'var', etc.
            'components': dict,  # Parsed components
            'errors': list[str]  # Validation errors
        }
    """
    # Patterns for each table type
    patterns = {
        'primary': r'^(agg|mom|vol|reg|align|der|rev|lag|regime|mrt|cyc|ext|div|tmp)_(idx|bqx)_([a-z]{6})$',
        'cov': r'^cov_(agg|align|mom|vol|reg|lag|regime)_(idx|bqx)_([a-z]{6})_([a-z]{6})$',
        'tri': r'^tri_(agg|align|mom|vol|reg)_(idx|bqx)_([a-z]{3})_([a-z]{3})_([a-z]{3})$',
        'var': r'^var_(agg|align|mom|vol|reg)_(idx|bqx)_([a-z]{3})$',
        'corr': r'^corr_(etf|bqx|ibkr)_(idx|bqx)_([a-z]{6})_([a-z]{3,6})$',
        'base': r'^base_(idx|bqx)_([a-z]{6})$',
        'mkt': r'^mkt_(agg|vol|regime|sentiment)_(idx|bqx)$'
    }

    # Validate against patterns...
    # Check alphabetical sorting for COV/TRI...
    # Validate component values against allowed lists...

    return validation_result

def validate_column_name(column_name: str, table_type: str) -> dict:
    """
    Validate column name against M008 naming standard.

    Returns:
        {
            'valid': bool,
            'column_type': str,  # 'feature', 'target', 'metadata'
            'components': dict,
            'errors': list[str]
        }
    """
    # Feature pattern: {prefix}_{metric}_{window}
    feature_pattern = r'^([a-z]+)_([a-z0-9_]+)_(\d+)$'

    # Target pattern: target_{variant}{window}_h{horizon}
    target_pattern = r'^target_(bqx|idx)(\d+)_h(\d+)$'

    # Metadata columns (whitelist)
    metadata = ['interval_time', 'pair', 'pair1', 'pair2', 'curr1', 'curr2', 'curr3']

    # Validate...

    return validation_result
```

### 5.2 Generation Script Templates

**All table generation scripts MUST**:
1. Import naming validation module
2. Validate table names before creation
3. Validate column names in SELECT clauses
4. Log any non-compliance for remediation

**Example Integration**:
```python
from scripts.validate_naming_compliance import validate_table_name, validate_column_name

def generate_cov_table(client, feature_type, variant, pair1, pair2):
    # Construct table name
    table_name = f"cov_{feature_type}_{variant}_{pair1}_{pair2}"

    # VALIDATE BEFORE CREATION
    validation = validate_table_name(table_name)
    if not validation['valid']:
        raise ValueError(f"Invalid table name: {validation['errors']}")

    # Validate all column names in SQL
    columns = extract_columns_from_sql(sql_query)
    for col in columns:
        col_validation = validate_column_name(col, 'cov')
        if not col_validation['valid']:
            raise ValueError(f"Invalid column '{col}': {col_validation['errors']}")

    # Proceed with table creation...
```

### 5.3 BigQuery Naming Enforcement

**Project-Level Policies**:
1. All table names validated before `CREATE TABLE`
2. Column names validated in schema definitions
3. Automated linting in CI/CD pipeline
4. Pre-commit hooks for SQL files

**Enforcement Script**: `/scripts/pre_commit_naming_check.sh`
```bash
#!/bin/bash
# Pre-commit hook: Validate all SQL files for naming compliance

for sql_file in $(git diff --cached --name-only --diff-filter=ACM | grep '\.sql$'); do
    python3 scripts/validate_naming_compliance.py --file "$sql_file"
    if [ $? -ne 0 ]; then
        echo "❌ Naming compliance failed for $sql_file"
        exit 1
    fi
done

echo "✅ All SQL files comply with M008 naming standard"
exit 0
```

### 5.4 Documentation Standards

**Every table generation script MUST include**:
1. Table name construction logic (commented)
2. Column naming conventions (docstring)
3. Example valid names
4. Common mistakes to avoid

**Example**:
```python
"""
Generate COV tables for pair-to-pair comparisons.

Table Naming Convention (M008):
    cov_{feature_type}_{variant}_{pair1}_{pair2}

    Example: cov_agg_bqx_eurusd_gbpusd

    CRITICAL: Pairs must be alphabetically sorted!
    ✅ eurusd_gbpusd (correct)
    ❌ gbpusd_eurusd (WRONG - not alphabetized)

Column Naming Convention (M008):
    Feature columns: {feature_type}_{metric}_{window}
    Example: agg_mean_45, reg_lin_term_180

    Pair-specific columns: pair1_{feature}_{window}, pair2_{feature}_{window}
    Example: pair1_lin_term_45, pair2_lin_term_45
"""
```

---

## 6. REMEDIATION PLAN FOR EXISTING INFRASTRUCTURE

### 6.1 Audit Current State

**Step 1**: Run compliance audit across all 6,069 tables

```bash
python3 scripts/audit_naming_compliance.py \
    --dataset bqx-ml.bqx_ml_v3_features_v2 \
    --output /tmp/naming_compliance_audit_20251213.json
```

**Expected Output**:
```json
{
  "total_tables": 6069,
  "compliant_tables": 5800,
  "non_compliant_tables": 269,
  "compliance_rate": "95.6%",
  "issues": [
    {
      "table": "var_corr_usd",
      "error": "Missing variant identifier - should be var_corr_idx_usd or var_corr_bqx_usd",
      "severity": "CRITICAL"
    },
    ...
  ]
}
```

### 6.2 Categorize Non-Compliance

**Priority 1 - CRITICAL** (Blocks M005/M006/M007):
- Missing variant identifiers (affects semantic compatibility)
- Incorrect component ordering (breaks programmatic parsing)
- Non-standard separators (affects downstream scripts)

**Priority 2 - HIGH** (Inconsistency issues):
- Non-alphabetized pair/currency order in COV/TRI
- Uppercase vs lowercase inconsistencies
- Non-standard window/horizon identifiers

**Priority 3 - MEDIUM** (Documentation gaps):
- Tables compliant but undocumented
- Column descriptions missing
- Metadata incomplete

### 6.3 Remediation Strategy

**Option A: Rename Tables** (for small batches < 50 tables)
```sql
-- Example: Fix VAR naming
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_features_v2.var_agg_idx_usd` AS
SELECT * FROM `bqx-ml.bqx_ml_v3_features_v2.var_agg_usd`;

-- Verify row count match
-- Drop old table after verification
DROP TABLE `bqx-ml.bqx_ml_v3_features_v2.var_agg_usd`;
```

**Option B: Regenerate Tables** (for large batches > 50 tables)
- Update generation scripts with M008 compliance
- Regenerate all non-compliant tables
- Validate new tables
- Drop old tables

**Recommended Approach**:
1. Fix VAR family (63 tables) - Option A (rename)
2. Fix any COV/TRI ordering issues - Option B (regenerate)
3. Update all generation scripts - Mandatory
4. Add pre-commit validation - Mandatory

### 6.4 Timeline

| Phase | Action | Tables | Duration | Priority |
|-------|--------|--------|----------|----------|
| **Phase 1** | Audit + categorize | 6,069 | 1 hour | P0 |
| **Phase 2** | Fix VAR naming | ~63 | 2 hours | P0 |
| **Phase 3** | Update generation scripts | All | 4 hours | P0 |
| **Phase 4** | Add validation hooks | N/A | 2 hours | P1 |
| **Phase 5** | Regenerate remaining | ~200 | 6 hours | P2 |
| **Total** | | | **15 hours** | |

---

## 7. COMPLIANCE VALIDATION CHECKLIST

Before ANY new table is created, validate:

### 7.1 Table Name Checklist
- [ ] Follows correct pattern for table type (primary, COV, TRI, VAR, etc.)
- [ ] Includes variant identifier (idx OR bqx)
- [ ] All components are lowercase
- [ ] No underscores within component names (only between components)
- [ ] Pairs/currencies are alphabetically sorted (for COV/TRI/VAR)
- [ ] Uses standard feature type prefixes (agg, mom, vol, reg, etc.)

### 7.2 Column Name Checklist
- [ ] Feature columns follow {prefix}_{metric}_{window} pattern
- [ ] Target columns follow target_{variant}{window}_h{horizon} pattern
- [ ] Metadata columns use reserved names (interval_time, pair, etc.)
- [ ] Window identifiers are interval counts (45, 90, etc.), not time units
- [ ] Horizon identifiers include 'h' prefix (h15, h30, etc.)
- [ ] No mixed variants in same table (M007 compliance)

### 7.3 Semantic Compliance Checklist (M007)
- [ ] Comparison tables (COV/TRI) only compare features from same semantic group
- [ ] No cross-variant comparisons (idx vs bqx in same calculation)
- [ ] Regression features (Group 1) only compared with other Group 1 features
- [ ] Prohibited features excluded (raw prices, categorical features)

---

## 8. INTEGRATION WITH OTHER MANDATES

### 8.1 M005 (Regression Feature Architecture)

**M008 Ensures**:
- Regression coefficient columns named consistently: `reg_lin_coef_{W}`, `reg_quad_coef_{W}`
- Regression term columns named consistently: `reg_lin_term_{W}`, `reg_quad_term_{W}`
- Easy programmatic identification of regression features in COV/TRI/VAR tables

**Example M005 + M008 Compliance**:
```sql
-- COV table with M005 regression features (M008 compliant naming)
CREATE TABLE cov_reg_bqx_eurusd_gbpusd AS
SELECT
  interval_time,
  'eurusd' as pair1,
  'gbpusd' as pair2,

  -- M005: Pair 1 regression features (M008: pair1_{feature}_{window})
  pair1_lin_coef_45, pair1_lin_coef_90, ..., pair1_lin_coef_2880,
  pair1_quad_coef_45, ..., pair1_quad_coef_2880,
  pair1_lin_term_45, ..., pair1_lin_term_2880,

  -- M005: Pair 2 regression features (M008: pair2_{feature}_{window})
  pair2_lin_coef_45, ..., pair2_lin_coef_2880,
  pair2_quad_coef_45, ..., pair2_quad_coef_2880,
  pair2_lin_term_45, ..., pair2_lin_term_2880
FROM ...
```

### 8.2 M006 (Maximize Feature Comparisons)

**M008 Ensures**:
- Alphabetical sorting prevents duplicate COV/TRI tables
- Variant separation enforced in table names
- Programmatic generation of all valid combinations

**Example M006 + M008 Compliance**:
```python
# Generate ALL valid COV combinations (M006)
# Using M008 naming standard

pairs = get_all_pairs()  # 28 pairs
variants = ['idx', 'bqx']
feature_types = ['agg', 'align', 'mom', 'vol', 'reg', 'lag', 'regime']

for variant in variants:
    for ft in feature_types:
        for pair1, pair2 in itertools.combinations(sorted(pairs), 2):
            # M008: Alphabetize pairs
            if pair1 > pair2:
                pair1, pair2 = pair2, pair1

            # M008: Construct standard name
            table_name = f"cov_{ft}_{variant}_{pair1}_{pair2}"

            # Validate against M008
            if not validate_table_name(table_name)['valid']:
                raise ValueError(f"M008 violation: {table_name}")

            generate_cov_table(client, ft, variant, pair1, pair2)
```

### 8.3 M007 (Semantic Feature Compatibility)

**M008 Ensures**:
- Feature group membership identifiable from column name prefix
- Variant separation (idx/bqx) enforced to prevent invalid comparisons
- Regression features easily identified (reg_ prefix)

**Example M007 + M008 Compliance**:
```python
# Identify semantic group from column name (M008 enables M007)

def get_semantic_group(column_name: str) -> int:
    """
    Determine semantic compatibility group from M008-compliant column name.

    Returns: Group number (1-9) or 0 if incompatible
    """
    # M008: Parse column name
    if column_name.startswith('reg_'):
        # Group 1: Regression Features
        if 'lin_term' in column_name or 'quad_term' in column_name or 'residual' in column_name:
            return 1

    elif column_name.startswith('agg_'):
        # Group 2: Statistical Aggregates
        if any(m in column_name for m in ['mean', 'std', 'min', 'max', 'range']):
            return 2

    # ... (map other M008 prefixes to M007 groups)

    return 0  # Incompatible/unknown

# Use for validation
def validate_comparison(col1: str, col2: str) -> bool:
    """M007: Only compare within same semantic group"""
    group1 = get_semantic_group(col1)
    group2 = get_semantic_group(col2)

    return group1 == group2 and group1 > 0
```

---

## 9. ENFORCEMENT AND GOVERNANCE

### 9.1 Code Review Requirements

**Before ANY PR is merged**:
1. Run `validate_naming_compliance.py` on all SQL files
2. Pass pre-commit naming checks
3. Update naming documentation if introducing new patterns
4. Get approval from Chief Engineer for any naming exceptions

### 9.2 Exception Process

**To request a naming exception**:
1. File issue documenting:
   - Proposed exception name
   - Reason standard pattern doesn't apply
   - Impact analysis (how many tables, downstream effects)
   - Alternative considered
2. Get user approval (if architectural change)
3. Update M008 mandate with approved exception
4. Add exception to validation whitelist

**Exceptions MUST be rare** - architectural consistency is critical.

### 9.3 Quarterly Audit

**Every quarter**:
1. Run full naming compliance audit
2. Identify any drift from standards
3. Remediate non-compliant tables
4. Update validation scripts if new patterns emerge

---

## 10. SUMMARY

### 10.1 Key Principles

1. **Semantic Encoding**: Names carry meaning, not just identifiers
2. **Programmatic Parsability**: Names follow patterns machines can parse
3. **Variant Separation**: IDX and BQX never mix (M007 compliance)
4. **Alphabetical Ordering**: Prevents duplicates in multi-entity tables
5. **Consistency Over Brevity**: Explicit is better than implicit

### 10.2 Compliance Status

| Component | Compliance | Action Required |
|-----------|------------|-----------------|
| Table names | ~95% | Fix VAR family (63 tables) |
| Column names | ~98% | Update generation scripts |
| Target names | 100% | None (already compliant) |
| Documentation | 80% | Add M008 references to all scripts |

### 10.3 Next Steps

1. ✅ **Immediate**: Run naming compliance audit
2. ⏳ **Priority 1**: Fix VAR naming inconsistencies (2 hours)
3. ⏳ **Priority 1**: Update all generation scripts with validation (4 hours)
4. ⏸️ **Priority 2**: Add pre-commit hooks (2 hours)
5. ⏸️ **Priority 3**: Regenerate remaining non-compliant tables (6 hours)

---

**This naming standard is now ACTIVE and BINDING.**

All new code MUST comply with M008.
All existing non-compliant infrastructure MUST be remediated.

**Signed**: Chief Engineer, BQX ML V3
**Date**: December 13, 2025
**Mandate Status**: ACTIVE

---

## RELATED MANDATES

- **M005**: Regression Feature Architecture (provides reg_ feature definitions)
- **M006**: Maximize Feature Comparisons (defines scope of table generation)
- **M007**: Semantic Feature Compatibility (constrains valid feature comparisons)
- **M001**: Feature Ledger 100% Coverage (requires consistent feature identification)

