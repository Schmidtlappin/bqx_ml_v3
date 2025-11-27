# 📋 FEATURE DATA AUDIT AND REMEDIATION PLAN
**Project**: BQX ML V3
**Objective**: Confirm feature data availability, identify gaps, remediate deficiencies
**Status**: AWAITING USER APPROVAL
**Created**: 2025-11-27

---

## 🎯 EXECUTIVE SUMMARY

### Purpose
Systematically audit BigQuery database (bqx-ml project) to:
1. Confirm all required feature data exists
2. Identify gaps between expected and actual data
3. Create remediation plan to fill gaps
4. Implement missing features for 90%+ accuracy target

### Expected State
Per [mandate/BQX_ML_V3_FEATURE_INVENTORY.md](../mandate/BQX_ML_V3_FEATURE_INVENTORY.md):
- 1,736 BigQuery tables
- 8,214+ features per currency pair
- 273 IDX technical indicators per pair
- 161 BQX derivatives per pair

### Current State (Known Issues)
- IDX tables: 3 columns only (interval_time, pair, close_idx)
- BQX tables: 16 columns (7 BQX windows + 7 targets + metadata)
- Technical indicators: NOT pre-calculated
- Gap: ~99% of expected features missing

---

## 📊 PHASED IMPLEMENTATION PLAN

### PHASE 1: DATABASE INVENTORY AND ASSESSMENT
**Duration**: 1-2 days
**Priority**: CRITICAL
**Objective**: Complete audit of existing BigQuery infrastructure

#### Task 1.1: Dataset and Table Inventory
**Owner**: BA
**Duration**: 2-4 hours
**Deliverables**:
- [ ] List all datasets in bqx-ml project
- [ ] Count tables per dataset
- [ ] Document table naming conventions
- [ ] Identify which datasets contain feature data

**Execution Stages**:

**Stage 1.1.1: List All Datasets** (30 min)
```bash
# Export dataset list to JSON
bq ls --project_id=bqx-ml --format=json > /tmp/bqx_datasets.json
cat /tmp/bqx_datasets.json | jq -r '.[].id' > /tmp/bqx_dataset_names.txt

# Count datasets
wc -l /tmp/bqx_dataset_names.txt
```

**Stage 1.1.2: Enumerate Tables Per Dataset** (1 hour)
```bash
# For each dataset, list tables
for dataset in $(cat /tmp/bqx_dataset_names.txt); do
  echo "Dataset: $dataset"
  bq ls --project_id=bqx-ml $dataset --format=json > "/tmp/tables_${dataset}.json"
  echo "Table count: $(cat /tmp/tables_${dataset}.json | jq length)"
done
```

**Stage 1.1.3: Consolidate Inventory** (30 min)
```bash
# Create consolidated JSON inventory
python3 << 'EOF'
import json
import glob

inventory = {"datasets": {}}
for file in glob.glob("/tmp/tables_*.json"):
    dataset = file.split("_")[1].replace(".json", "")
    with open(file) as f:
        tables = json.load(f)
    inventory["datasets"][dataset] = {
        "table_count": len(tables),
        "tables": [t["tableReference"]["tableId"] for t in tables]
    }

with open("/tmp/bqx_inventory_consolidated.json", "w") as f:
    json.dump(inventory, f, indent=2)

print(f"Total datasets: {len(inventory['datasets'])}")
print(f"Total tables: {sum(d['table_count'] for d in inventory['datasets'].values())}")
EOF
```

**Stage 1.1.4: Copy to Workspace** (15 min)
```bash
# Copy inventory to workspace
cp /tmp/bqx_inventory_consolidated.json /home/micha/bqx_ml_v3/data/
```

**Output**: `/home/micha/bqx_ml_v3/data/bqx_inventory_consolidated.json`

**Status Report**: Report total datasets, total tables, naming patterns observed

---

#### Task 1.2: Schema Analysis Per Table
**Owner**: BA
**Duration**: 3-5 hours
**Deliverables**:
- [ ] Extract schema for all existing tables
- [ ] Document column names, types, and descriptions
- [ ] Identify IDX tables and their columns
- [ ] Identify BQX tables and their columns
- [ ] Identify any feature tables (lag, regime, agg, align, etc.)

**Execution Stages**:

**Stage 1.2.1: Extract All Schemas** (2 hours)
```bash
# Create schema export script
cat > /tmp/export_schemas.sh << 'EOF'
#!/bin/bash
mkdir -p /tmp/schemas
for dataset in $(cat /tmp/bqx_dataset_names.txt); do
  echo "Processing dataset: $dataset"
  mkdir -p "/tmp/schemas/$dataset"

  for table in $(bq ls --project_id=bqx-ml $dataset --format=json | jq -r '.[].tableReference.tableId'); do
    echo "  Exporting schema: $table"
    bq show --schema --format=prettyjson "bqx-ml:$dataset.$table" > "/tmp/schemas/$dataset/${table}.json" 2>/dev/null || echo "    ERROR: Failed to export $table"
  done
done
EOF

chmod +x /tmp/export_schemas.sh
/tmp/export_schemas.sh
```

**Stage 1.2.2: Analyze Schemas** (1 hour)
```python
# Create schema analysis script
cat > /tmp/analyze_schemas.py << 'EOF'
import json
import glob
import os

schema_analysis = {
    "idx_tables": [],
    "bqx_tables": [],
    "feature_tables": {"lag": [], "regime": [], "agg": [], "align": [], "correlation": [], "momentum": [], "volatility": []},
    "unknown_tables": []
}

for schema_file in glob.glob("/tmp/schemas/*/*.json"):
    dataset = os.path.basename(os.path.dirname(schema_file))
    table_name = os.path.basename(schema_file).replace(".json", "")

    try:
        with open(schema_file) as f:
            schema = json.load(f)

        column_count = len(schema)
        columns = [col["name"] for col in schema]

        table_info = {
            "dataset": dataset,
            "table": table_name,
            "column_count": column_count,
            "columns": columns
        }

        # Classify table
        if "idx" in table_name.lower() and "lag" not in table_name.lower():
            schema_analysis["idx_tables"].append(table_info)
        elif "bqx" in table_name.lower() and "lag" not in table_name.lower():
            schema_analysis["bqx_tables"].append(table_info)
        elif "lag" in table_name.lower():
            schema_analysis["feature_tables"]["lag"].append(table_info)
        elif "regime" in table_name.lower():
            schema_analysis["feature_tables"]["regime"].append(table_info)
        elif "agg" in table_name.lower():
            schema_analysis["feature_tables"]["agg"].append(table_info)
        elif "align" in table_name.lower():
            schema_analysis["feature_tables"]["align"].append(table_info)
        elif "correlation" in table_name.lower() or "corr" in table_name.lower():
            schema_analysis["feature_tables"]["correlation"].append(table_info)
        elif "momentum" in table_name.lower():
            schema_analysis["feature_tables"]["momentum"].append(table_info)
        elif "volatility" in table_name.lower() or "vol" in table_name.lower():
            schema_analysis["feature_tables"]["volatility"].append(table_info)
        else:
            schema_analysis["unknown_tables"].append(table_info)
    except Exception as e:
        print(f"Error processing {schema_file}: {e}")

# Save analysis
with open("/tmp/schema_analysis.json", "w") as f:
    json.dump(schema_analysis, f, indent=2)

# Print summary
print(f"\n=== SCHEMA ANALYSIS SUMMARY ===")
print(f"IDX Tables: {len(schema_analysis['idx_tables'])}")
print(f"BQX Tables: {len(schema_analysis['bqx_tables'])}")
print(f"Lag Feature Tables: {len(schema_analysis['feature_tables']['lag'])}")
print(f"Regime Feature Tables: {len(schema_analysis['feature_tables']['regime'])}")
print(f"Aggregation Feature Tables: {len(schema_analysis['feature_tables']['agg'])}")
print(f"Alignment Feature Tables: {len(schema_analysis['feature_tables']['align'])}")
print(f"Unknown Tables: {len(schema_analysis['unknown_tables'])}")
EOF

python3 /tmp/analyze_schemas.py
```

**Stage 1.2.3: Copy Analysis to Workspace** (15 min)
```bash
cp /tmp/schema_analysis.json /home/micha/bqx_ml_v3/data/
```

**Output**: `/home/micha/bqx_ml_v3/data/schema_analysis.json`

**Status Report**: Report table classification counts, column counts for IDX/BQX tables, any anomalies

---

#### Task 1.3: Row Count and Data Validation
**Owner**: BA
**Duration**: 2-3 hours
**Deliverables**:
- [ ] Count rows in each table
- [ ] Validate data completeness (NULL checks)
- [ ] Check date ranges covered
- [ ] Identify data quality issues

**Execution Stages**:

**Stage 1.3.1: Generate Row Count Queries** (30 min)
```python
cat > /tmp/generate_rowcount_queries.py << 'EOF'
import json

with open("/tmp/schema_analysis.json") as f:
    analysis = json.load(f)

queries = []
for category in ["idx_tables", "bqx_tables"]:
    for table_info in analysis[category]:
        dataset = table_info["dataset"]
        table = table_info["table"]

        query = f"""
SELECT
  '{dataset}.{table}' as table_name,
  COUNT(*) as total_rows,
  MIN(interval_time) as earliest_data,
  MAX(interval_time) as latest_data,
  COUNT(DISTINCT pair) as unique_pairs
FROM `bqx-ml.{dataset}.{table}`
"""
        queries.append(query)

# Save queries
with open("/tmp/rowcount_queries.sql", "w") as f:
    for i, query in enumerate(queries):
        f.write(f"-- Query {i+1}\n")
        f.write(query)
        f.write(";\n\n")

print(f"Generated {len(queries)} row count queries")
EOF

python3 /tmp/generate_rowcount_queries.py
```

**Stage 1.3.2: Execute Row Count Queries** (1 hour)
```bash
# Execute queries and collect results
cat > /tmp/execute_rowcount.sh << 'EOF'
#!/bin/bash
mkdir -p /tmp/rowcount_results

# Read schema analysis to get table list
python3 << 'PYEOF'
import json
import subprocess

with open("/tmp/schema_analysis.json") as f:
    analysis = json.load(f)

results = []
for category in ["idx_tables", "bqx_tables"]:
    for table_info in analysis[category]:
        dataset = table_info["dataset"]
        table = table_info["table"]

        print(f"Querying: {dataset}.{table}")

        query = f"""
SELECT
  COUNT(*) as total_rows,
  MIN(interval_time) as earliest_data,
  MAX(interval_time) as latest_data,
  COUNT(DISTINCT pair) as unique_pairs
FROM `bqx-ml.{dataset}.{table}`
"""

        try:
            result = subprocess.run(
                ["bq", "query", "--use_legacy_sql=false", "--format=json", query],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data:
                    results.append({
                        "dataset": dataset,
                        "table": table,
                        "total_rows": int(data[0]["total_rows"]),
                        "earliest_data": data[0]["earliest_data"],
                        "latest_data": data[0]["latest_data"],
                        "unique_pairs": int(data[0]["unique_pairs"])
                    })
            else:
                print(f"  ERROR: {result.stderr}")
                results.append({
                    "dataset": dataset,
                    "table": table,
                    "error": result.stderr
                })
        except Exception as e:
            print(f"  EXCEPTION: {e}")
            results.append({
                "dataset": dataset,
                "table": table,
                "error": str(e)
            })

with open("/tmp/rowcount_results.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nCompleted {len(results)} queries")
PYEOF
EOF

chmod +x /tmp/execute_rowcount.sh
/tmp/execute_rowcount.sh
```

**Stage 1.3.3: Data Quality Analysis** (30 min)
```python
cat > /tmp/data_quality_analysis.py << 'EOF'
import json
from datetime import datetime

with open("/tmp/rowcount_results.json") as f:
    results = json.load(f)

quality_report = {
    "total_tables_analyzed": len(results),
    "tables_with_data": 0,
    "empty_tables": [],
    "data_coverage": {},
    "pair_coverage": {},
    "errors": []
}

for result in results:
    table_name = f"{result['dataset']}.{result['table']}"

    if "error" in result:
        quality_report["errors"].append({
            "table": table_name,
            "error": result["error"]
        })
        continue

    rows = result["total_rows"]
    if rows == 0:
        quality_report["empty_tables"].append(table_name)
    else:
        quality_report["tables_with_data"] += 1

        # Calculate date range
        try:
            earliest = datetime.fromisoformat(result["earliest_data"].replace("Z", "+00:00"))
            latest = datetime.fromisoformat(result["latest_data"].replace("Z", "+00:00"))
            days_coverage = (latest - earliest).days

            quality_report["data_coverage"][table_name] = {
                "rows": rows,
                "earliest": result["earliest_data"],
                "latest": result["latest_data"],
                "days_coverage": days_coverage,
                "unique_pairs": result["unique_pairs"]
            }
        except:
            pass

# Save report
with open("/tmp/data_quality_report.json", "w") as f:
    json.dump(quality_report, f, indent=2)

print(f"\n=== DATA QUALITY REPORT ===")
print(f"Total tables analyzed: {quality_report['total_tables_analyzed']}")
print(f"Tables with data: {quality_report['tables_with_data']}")
print(f"Empty tables: {len(quality_report['empty_tables'])}")
print(f"Errors encountered: {len(quality_report['errors'])}")
EOF

python3 /tmp/data_quality_analysis.py
```

**Stage 1.3.4: Copy Reports to Workspace** (15 min)
```bash
cp /tmp/rowcount_results.json /home/micha/bqx_ml_v3/data/
cp /tmp/data_quality_report.json /home/micha/bqx_ml_v3/data/
```

**Output**: `/home/micha/bqx_ml_v3/data/data_quality_report.json`

**Status Report**: Report total rows, date coverage, empty tables, errors encountered

---

### PHASE 2: GAP ANALYSIS
**Duration**: 1 day
**Priority**: CRITICAL
**Objective**: Compare expected vs actual feature availability

#### Task 2.1: Feature Matrix Gap Analysis
**Owner**: TBD
**Deliverables**:
- [ ] Compare actual tables vs mandate/BQX_ML_V3_FEATURE_INVENTORY.md
- [ ] Identify missing table types (lag, regime, agg, align, correlation, momentum, volatility)
- [ ] Identify missing centric perspectives (variant, covariant, triangulation, secondary, tertiary)
- [ ] Calculate percentage gap per category

**Expected Tables** (from mandate):
```
Primary (Pair-Centric):    392 tables
Variant (Family):          112 tables
Covariant (Cross-Pair):    800 tables
Triangulation (Arbitrage): 288 tables
Secondary (Currency):      128 tables
Tertiary (Market):          16 tables
TOTAL:                   1,736 tables
```

**Output**: Gap analysis matrix showing expected vs actual

---

#### Task 2.2: Feature Column Gap Analysis
**Owner**: TBD
**Deliverables**:
- [ ] IDX tables: Expected 273 technical indicators, actual columns?
- [ ] BQX tables: Expected 161 derivatives, actual columns?
- [ ] Identify which specific indicators are missing
- [ ] Prioritize indicators by importance

**Expected IDX Indicators**:
```
Momentum: RSI, MACD, Stochastic, Williams %R, ROC, Momentum
Trend: SMA, EMA, DEMA, TEMA, WMA, Bollinger Bands
Volume: OBV, VWAP, MFI, Volume Profile, Chaikin Money Flow
Volatility: ATR, Bollinger Width, Keltner Channels, Standard Deviation
Strength: ADX, Aroon, CCI, DPO
```

**Output**: Detailed list of missing features with priority levels

---

#### Task 2.3: Historical Data Coverage Gap
**Owner**: TBD
**Deliverables**:
- [ ] Verify 5 years of historical data exists
- [ ] Check for data gaps (missing dates/times)
- [ ] Validate all 28 currency pairs have complete data
- [ ] Identify pairs with insufficient history

**Expected Coverage**:
- 5 years × 365 days × 1440 minutes = 2,628,000 data points per pair
- 28 pairs × 2,628,000 = 73,584,000 total data points

**Output**: Data coverage report with gap identification

---

### PHASE 3: REMEDIATION PLANNING
**Duration**: 1 day
**Priority**: HIGH
**Objective**: Create detailed plan to fill all identified gaps

#### Task 3.1: Prioritize Missing Features
**Owner**: TBD
**Deliverables**:
- [ ] Categorize missing features by criticality
  - CRITICAL: Required for 90%+ accuracy (based on feature selection literature)
  - HIGH: Important for model diversity
  - MEDIUM: Supplementary features
  - LOW: Nice-to-have features
- [ ] Create implementation priority matrix
- [ ] Estimate computation cost per feature category

**Priority Framework**:
```
CRITICAL (must have):
- IDX: RSI, MACD, Bollinger Bands, ATR, Volume
- BQX: All 60 lags (paradigm shift requirement)
- Primary tables: lag, regime, agg, align

HIGH (should have):
- IDX: ADX, Stochastic, OBV, EMA/SMA
- BQX: Moving averages, volatility, acceleration
- Variant tables: Currency family features

MEDIUM (nice to have):
- Covariant tables: Cross-pair correlations
- Triangulation tables: Arbitrage features

LOW (future enhancement):
- Secondary/Tertiary tables: Market-wide features
```

**Output**: Prioritized feature implementation roadmap

---

#### Task 3.2: Technical Implementation Design
**Owner**: TBD
**Deliverables**:
- [ ] Design SQL queries to generate missing technical indicators
- [ ] Choose between materialized views vs computed columns vs new tables
- [ ] Design data pipeline for automated feature generation
- [ ] Plan for incremental vs full recalculation

**Design Decisions**:
```
Option A: Materialized Views
+ Pros: Automatic updates, space efficient
- Cons: Query overhead, complex maintenance

Option B: New Tables (Recommended)
+ Pros: Fast queries, explicit control, clear structure
- Cons: More storage, manual updates required

Option C: Computed Columns
+ Pros: Simple, always current
- Cons: Compute overhead per query
```

**Output**: Technical design document for feature generation

---

#### Task 3.3: Resource and Timeline Estimation
**Owner**: TBD
**Deliverables**:
- [ ] Estimate compute resources needed
- [ ] Estimate storage requirements
- [ ] Calculate BigQuery costs
- [ ] Create implementation timeline
- [ ] Identify dependencies and blockers

**Estimates**:
```
Storage (1,736 tables × 5 years × 28 pairs):
- Raw data: ~100 GB
- Feature tables: ~500 GB
- Total: ~600 GB (~$12/month)

Compute (feature generation):
- One-time backfill: ~$50-100
- Ongoing updates: ~$20/month

Timeline:
- Phase 1 (Audit): 1-2 days
- Phase 2 (Gap Analysis): 1 day
- Phase 3 (Planning): 1 day
- Phase 4 (Implementation): 5-7 days
- Phase 5 (Validation): 2-3 days
TOTAL: 10-14 days
```

**Output**: Resource plan and timeline

---

### PHASE 4: FEATURE GENERATION IMPLEMENTATION
**Duration**: 5-7 days
**Priority**: CRITICAL
**Objective**: Generate all missing features and populate tables

#### Task 4.1: IDX Technical Indicators Generation
**Owner**: TBD
**Deliverables**:
- [ ] Implement RSI calculation (14-period default)
- [ ] Implement MACD calculation (12/26/9 default)
- [ ] Implement Bollinger Bands (20-period, 2 std)
- [ ] Implement ATR (14-period)
- [ ] Implement Stochastic Oscillator (14/3/3)
- [ ] Implement all 50+ technical indicators
- [ ] Create idx_features_{pair} tables with all indicators

**Implementation Method**:
```python
# Using TA-Lib or pandas_ta
import talib
import pandas as pd

def generate_idx_features(pair_data):
    df = pair_data.copy()

    # Momentum Indicators
    df['idx_rsi'] = talib.RSI(df['close_idx'], timeperiod=14)
    df['idx_macd'], df['idx_macd_signal'], df['idx_macd_hist'] = \
        talib.MACD(df['close_idx'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['idx_stoch_k'], df['idx_stoch_d'] = \
        talib.STOCH(df['high_idx'], df['low_idx'], df['close_idx'])

    # Trend Indicators
    df['idx_sma_20'] = talib.SMA(df['close_idx'], timeperiod=20)
    df['idx_ema_12'] = talib.EMA(df['close_idx'], timeperiod=12)
    df['idx_bb_upper'], df['idx_bb_middle'], df['idx_bb_lower'] = \
        talib.BBANDS(df['close_idx'], timeperiod=20)

    # Volatility Indicators
    df['idx_atr'] = talib.ATR(df['high_idx'], df['low_idx'], df['close_idx'])

    # Volume Indicators
    df['idx_obv'] = talib.OBV(df['close_idx'], df['volume_idx'])

    # ... (50+ more indicators)

    return df
```

**Output**: Complete idx_features tables for all 28 pairs

---

#### Task 4.2: BQX Feature Derivatives Generation
**Owner**: TBD
**Deliverables**:
- [ ] Generate all 60 BQX lags (paradigm shift requirement)
- [ ] Calculate BQX moving averages (5, 10, 20, 50, 100, 200)
- [ ] Calculate BQX volatility (rolling std dev)
- [ ] Calculate BQX acceleration (rate of change of BQX)
- [ ] Calculate BQX momentum persistence
- [ ] Create bqx_features_{pair} tables with all derivatives

**Implementation**:
```sql
CREATE OR REPLACE TABLE `bqx-ml.bqx_ml_v3_features.bqx_features_eurusd` AS
WITH base AS (
  SELECT
    interval_time,
    pair,
    bqx_45, bqx_90, bqx_180, bqx_360, bqx_720, bqx_1440, bqx_2880
  FROM `bqx-ml.bqx_ml_v3_features.bqx_eurusd`
),
lagged AS (
  SELECT
    *,
    -- 60 lags for each BQX window (paradigm shift)
    LAG(bqx_90, 1) OVER (ORDER BY interval_time) as bqx_90_lag_1,
    LAG(bqx_90, 2) OVER (ORDER BY interval_time) as bqx_90_lag_2,
    -- ... continue to lag 60
    LAG(bqx_90, 60) OVER (ORDER BY interval_time) as bqx_90_lag_60
  FROM base
),
derived AS (
  SELECT
    *,
    -- Moving averages
    AVG(bqx_90) OVER (ORDER BY interval_time ROWS BETWEEN 9 PRECEDING AND CURRENT ROW) as bqx_90_ma_10,
    AVG(bqx_90) OVER (ORDER BY interval_time ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) as bqx_90_ma_20,

    -- Volatility
    STDDEV(bqx_90) OVER (ORDER BY interval_time ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) as bqx_90_volatility,

    -- Acceleration
    bqx_90 - LAG(bqx_90, 1) OVER (ORDER BY interval_time) as bqx_90_acceleration
  FROM lagged
)
SELECT * FROM derived
```

**Output**: Complete bqx_features tables for all 28 pairs

---

#### Task 4.3: Lag Features Tables Generation
**Owner**: TBD
**Deliverables**:
- [ ] Create lag_idx_{pair} tables (60 lags per price feature)
- [ ] Create lag_bqx_{pair} tables (60 lags per BQX window)
- [ ] Verify ROWS BETWEEN logic (interval-centric)
- [ ] Validate no look-ahead bias

**Output**: 56 lag tables (28 pairs × 2 variants)

---

#### Task 4.4: Regime Features Tables Generation
**Owner**: TBD
**Deliverables**:
- [ ] Implement regime classification logic
  - Trending vs Ranging
  - High vs Low Volatility
  - Bullish vs Bearish
- [ ] Create regime_idx_{pair} tables
- [ ] Create regime_bqx_{pair} tables
- [ ] Calculate regime transition metrics

**Output**: 56 regime tables (28 pairs × 2 variants)

---

#### Task 4.5: Aggregation Features Tables Generation
**Owner**: TBD
**Deliverables**:
- [ ] Calculate rolling statistics (mean, std, min, max, percentiles)
- [ ] Implement for multiple windows [45, 90, 180, 360, 720, 1440, 2880]
- [ ] Create agg_idx_{pair} tables
- [ ] Create agg_bqx_{pair} tables

**Output**: 56 aggregation tables (28 pairs × 2 variants)

---

#### Task 4.6: Alignment Features Tables Generation
**Owner**: TBD
**Deliverables**:
- [ ] Calculate cross-window alignment scores
- [ ] Measure trend coherence across timeframes
- [ ] Create align_idx_{pair} tables
- [ ] Create align_bqx_{pair} tables

**Output**: 56 alignment tables (28 pairs × 2 variants)

---

### PHASE 5: VALIDATION AND TESTING
**Duration**: 2-3 days
**Priority**: CRITICAL
**Objective**: Verify all features are correct and usable

#### Task 5.1: Feature Quality Validation
**Owner**: TBD
**Deliverables**:
- [ ] Validate technical indicator calculations against known libraries
- [ ] Check for NULL values in generated features
- [ ] Verify statistical properties (mean, std within expected ranges)
- [ ] Test edge cases (market opens, gaps, holidays)

**Validation Queries**:
```sql
-- Check for NULLs
SELECT
  COUNTIF(idx_rsi IS NULL) as null_rsi,
  COUNTIF(idx_macd IS NULL) as null_macd,
  COUNTIF(bqx_90_lag_1 IS NULL) as null_bqx_lag
FROM `bqx-ml.bqx_ml_v3_features.idx_features_eurusd`

-- Validate RSI range (should be 0-100)
SELECT
  MIN(idx_rsi) as min_rsi,
  MAX(idx_rsi) as max_rsi,
  AVG(idx_rsi) as avg_rsi
FROM `bqx-ml.bqx_ml_v3_features.idx_features_eurusd`
WHERE idx_rsi IS NOT NULL
```

**Output**: Feature quality report with validation results

---

#### Task 5.2: Sample Feature Extraction Test
**Owner**: TBD
**Deliverables**:
- [ ] Extract features for one currency pair (EURUSD)
- [ ] Verify feature count matches expected (8,214+)
- [ ] Test feature selection pipeline on extracted features
- [ ] Measure query performance (<2 seconds requirement)

**Test Query**:
```sql
SELECT
  t1.*,
  t2.* EXCEPT(interval_time, pair),
  t3.* EXCEPT(interval_time, pair),
  t4.* EXCEPT(interval_time, pair),
  t5.* EXCEPT(interval_time, pair)
FROM `bqx-ml.bqx_ml_v3_features.idx_features_eurusd` t1
LEFT JOIN `bqx-ml.bqx_ml_v3_features.bqx_features_eurusd` t2
  USING(interval_time, pair)
LEFT JOIN `bqx-ml.bqx_ml_v3_features.lag_idx_eurusd` t3
  USING(interval_time, pair)
LEFT JOIN `bqx-ml.bqx_ml_v3_features.lag_bqx_eurusd` t4
  USING(interval_time, pair)
LEFT JOIN `bqx-ml.bqx_ml_v3_features.regime_bqx_eurusd` t5
  USING(interval_time, pair)
WHERE interval_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
ORDER BY interval_time DESC
LIMIT 1000
```

**Expected**: 8,214+ columns returned in <2 seconds

**Output**: Performance and completeness test results

---

#### Task 5.3: Cross-Validation with Mandate
**Owner**: TBD
**Deliverables**:
- [ ] Compare implemented tables vs mandate/BQX_ML_V3_FEATURE_INVENTORY.md
- [ ] Verify all CRITICAL features are implemented
- [ ] Document any deviations or postponed features
- [ ] Update feature inventory with actual status

**Checklist**:
```
✅ IDX technical indicators: 273 implemented
✅ BQX derivatives: 161 implemented
✅ Primary tables: All 8 types × 28 pairs
✅ BQX lags: All 60 lags (paradigm shift)
✅ Total features per pair: 8,214+
✅ Ready for 90%+ accuracy testing
```

**Output**: Compliance report showing mandate adherence

---

### PHASE 6: DOCUMENTATION AND HANDOFF
**Duration**: 1 day
**Priority**: HIGH
**Objective**: Document everything for ongoing maintenance

#### Task 6.1: Technical Documentation
**Owner**: TBD
**Deliverables**:
- [ ] Document all feature generation logic
- [ ] Create data dictionary for all tables/columns
- [ ] Document update procedures
- [ ] Create troubleshooting guide

**Output**: Complete technical documentation

---

#### Task 6.2: Operational Runbooks
**Owner**: TBD
**Deliverables**:
- [ ] Create runbook for adding new features
- [ ] Create runbook for updating existing features
- [ ] Create runbook for handling data gaps
- [ ] Create runbook for performance optimization

**Output**: Operational runbooks for maintenance

---

#### Task 6.3: Update Mandate Documents
**Owner**: TBD
**Deliverables**:
- [ ] Update mandate/BQX_ML_V3_FEATURE_INVENTORY.md with actual implementation
- [ ] Mark "Current State" as complete
- [ ] Update expected vs actual gap analysis
- [ ] Remove "missing features" warnings

**Output**: Updated mandate documentation reflecting reality

---

## 📊 SUCCESS METRICS

### Completion Criteria
- [ ] All 1,736 tables created (or prioritized subset)
- [ ] All 273 IDX technical indicators calculated
- [ ] All 161 BQX derivatives calculated
- [ ] All 60 BQX lags implemented (paradigm shift)
- [ ] 8,214+ features available per pair
- [ ] Query performance <2 seconds
- [ ] Data quality >99.9% (no NULLs except edges)
- [ ] Ready for comprehensive feature selection testing

### Quality Gates
1. **Phase 1**: Inventory must be 100% complete before Phase 2
2. **Phase 2**: Gap analysis must identify all critical gaps before Phase 3
3. **Phase 3**: Remediation plan must be approved before Phase 4
4. **Phase 4**: Each table type must pass validation before next type
5. **Phase 5**: All validation tests must pass before Phase 6

---

## 🚨 RISKS AND MITIGATION

### Risk 1: Compute Costs Exceed Budget
**Probability**: Medium
**Impact**: High
**Mitigation**:
- Start with 3 critical pairs (EURUSD, GBPUSD, USDJPY)
- Validate approach before scaling to all 28
- Use batch processing during off-peak hours

### Risk 2: Historical Data Gaps
**Probability**: High
**Impact**: Medium
**Mitigation**:
- Document gaps rather than filling with synthetic data
- Use forward-fill for small gaps (<5 intervals)
- Flag problematic date ranges

### Risk 3: Indicator Calculation Discrepancies
**Probability**: Medium
**Impact**: Medium
**Mitigation**:
- Validate against TA-Lib reference implementation
- Cross-check with trading platforms (TradingView, etc.)
- Document any intentional deviations

### Risk 4: Timeline Slippage
**Probability**: Medium
**Impact**: Low
**Mitigation**:
- Prioritize CRITICAL features first
- Defer LOW priority features to future phase
- Maintain parallel development tracks where possible

---

## 🎯 DELIVERABLES SUMMARY

### Phase 1: Database Inventory
1. Dataset/table inventory (JSON)
2. Complete schema documentation
3. Data quality report

### Phase 2: Gap Analysis
4. Gap analysis matrix
5. Missing features list with priorities
6. Data coverage report

### Phase 3: Remediation Planning
7. Prioritized implementation roadmap
8. Technical design document
9. Resource and timeline plan

### Phase 4: Implementation
10. idx_features_{pair} tables (28 pairs)
11. bqx_features_{pair} tables (28 pairs)
12. lag_idx_{pair} tables (28 pairs)
13. lag_bqx_{pair} tables (28 pairs)
14. regime_idx_{pair} tables (28 pairs)
15. regime_bqx_{pair} tables (28 pairs)
16. agg_idx_{pair} tables (28 pairs)
17. agg_bqx_{pair} tables (28 pairs)
18. align_idx_{pair} tables (28 pairs)
19. align_bqx_{pair} tables (28 pairs)

### Phase 5: Validation
20. Feature quality report
21. Performance test results
22. Compliance report

### Phase 6: Documentation
23. Technical documentation
24. Operational runbooks
25. Updated mandate documents

---

## 📅 TIMELINE SUMMARY

```
Week 1:
├── Days 1-2: Phase 1 (Inventory and Assessment)
├── Day 3: Phase 2 (Gap Analysis)
└── Day 4: Phase 3 (Remediation Planning)

Week 2:
├── Days 5-11: Phase 4 (Feature Generation Implementation)
└── Days 12-14: Phase 5 (Validation and Testing)

Week 3:
└── Day 15: Phase 6 (Documentation and Handoff)

TOTAL: 15 working days (3 weeks)
```

---

## ✅ APPROVAL CHECKLIST

Before proceeding, confirm:
- [ ] Scope is clear and achievable
- [ ] Resources are available (compute, storage, personnel)
- [ ] Budget is approved (~$100-150 one-time + $30/month ongoing)
- [ ] Timeline is acceptable (3 weeks)
- [ ] Priorities are correctly identified
- [ ] Success metrics are measurable
- [ ] Risks are acceptable

---

## 🚀 NEXT STEPS AFTER APPROVAL

1. **Assign ownership** for each phase/task
2. **Create tracking spreadsheet** for daily progress
3. **Set up daily standup** (15 min) during implementation
4. **Begin Phase 1** (Database Inventory) immediately
5. **Weekly stakeholder updates** on progress

---

**STATUS: ✅ APPROVED - BA AUTHORIZED TO PROCEED**

**Authorization Date**: 2025-11-27
**Authorized By**: CE (Chief Engineer)
**Assigned To**: BA (Build Agent)

**INSTRUCTIONS TO BA**:
1. Implement phases in strict sequence (Phase 1 → 2 → 3 → 4 → 5 → 6)
2. Execute all stages within each task sequentially
3. Provide status reports at completion of each task
4. Investigate and resolve issues in realtime
5. If unable to resolve an issue, STOP and notify CE immediately with:
   - Detailed description of the blocker
   - What was attempted
   - Error messages/logs
   - Recommended next steps
6. DO NOT deviate from the plan without CE approval
7. BEGIN IMMEDIATELY with Phase 1, Task 1.1, Stage 1.1.1

---

*Plan created: 2025-11-27*
*Estimated completion: 3 weeks from approval*
*Total cost estimate: $100-150 one-time + $30/month ongoing*
