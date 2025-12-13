# Quality Standards Framework - BQX ML V3

**Version**: 1.0.0
**Created**: December 12, 2025 19:40 UTC
**Author**: Quality Assurance (QA)
**Purpose**: Define comprehensive quality standards for BQX ML V3 project
**Scope**: All work products across code, data, documentation, and processes
**Status**: ACTIVE

---

## TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [Code Quality Standards](#code-quality-standards)
3. [Data Quality Standards](#data-quality-standards)
4. [Documentation Standards](#documentation-standards)
5. [Process Standards](#process-standards)
6. [Validation Protocols](#validation-protocols)
7. [Success Metrics](#success-metrics)
8. [Remediation Procedures](#remediation-procedures)

---

## EXECUTIVE SUMMARY

### Framework Purpose

This Quality Standards Framework defines the **minimum acceptable quality levels** for all work products in the BQX ML V3 project, ensuring:

1. **Consistency**: All 28 currency pairs meet identical quality standards
2. **Reliability**: Training files produce reproducible, valid models
3. **Traceability**: All work products are documented and auditable
4. **Efficiency**: Quality checks prevent downstream rework

### User Mandate Alignment

**User Mandate**: "Maximum speed to completion at minimal expense within system limitations"

**Quality Framework Supports Mandate**:
- ✅ **Speed**: Catch issues early (prevents costly rework)
- ✅ **Cost**: Automated validation (minimal manual intervention)
- ✅ **System Limits**: Standards respect BigQuery, Cloud Run, VM constraints

### Target Audience

- **Build Agent (BA)**: Code quality, script validation, data pipeline standards
- **Quality Assurance (QA)**: Validation protocols, documentation standards, audit procedures
- **Enhancement Assistant (EA)**: Architecture standards, optimization guidelines, technical documentation
- **Operations (OPS)**: Infrastructure standards, monitoring protocols, resource management

---

## CODE QUALITY STANDARDS

### 1. Python Code Standards

#### 1.1 Style and Formatting

**Standard**: All Python code must follow PEP 8 style guide

**Requirements**:
- ✅ Maximum line length: 100 characters (not 79, to accommodate modern screens)
- ✅ Indentation: 4 spaces (no tabs)
- ✅ Naming conventions:
  - Functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE`
  - Variables: `snake_case`
- ✅ Imports: Grouped and sorted (stdlib → third-party → local)

**Validation**:
```bash
# Run before commit
python3 -m pylint <script.py> --max-line-length=100
```

**Exceptions**: Line length can exceed 100 for:
- Long string literals (e.g., SQL queries)
- URLs and file paths
- Complex comprehensions (if readability is maintained)

---

#### 1.2 Error Handling

**Standard**: All external operations must have error handling

**Requirements**:
- ✅ BigQuery operations: Try/except with specific error types
- ✅ File I/O: Check file existence before read/write
- ✅ Network requests: Timeout and retry logic
- ✅ Cloud Run executions: Status checking and failure recovery

**Example - GOOD**:
```python
try:
    df = client.query(sql).to_dataframe()
except google.cloud.exceptions.NotFound:
    logger.error(f"Table not found: {table_id}")
    return None
except google.cloud.exceptions.GoogleCloudError as e:
    logger.error(f"BigQuery error: {e}")
    raise
```

**Example - BAD**:
```python
df = client.query(sql).to_dataframe()  # No error handling
```

---

#### 1.3 Logging

**Standard**: All scripts must log key operations and errors

**Requirements**:
- ✅ Use Python logging module (not print statements)
- ✅ Log levels:
  - `DEBUG`: Detailed execution flow
  - `INFO`: Key milestones (e.g., "Extraction started for EURUSD")
  - `WARNING`: Recoverable issues (e.g., "Checkpoint exists, skipping")
  - `ERROR`: Failures that stop execution
- ✅ Log format: `[TIMESTAMP] [LEVEL] [SCRIPT] MESSAGE`
- ✅ Log to file AND console for Cloud Run executions

**Example**:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler(f'logs/extraction_{pair}_{timestamp}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info(f"Starting extraction for {pair}")
```

---

#### 1.4 Resource Management

**Standard**: All resources must be properly managed (opened, used, closed)

**Requirements**:
- ✅ Use context managers for file I/O
- ✅ Close BigQuery clients after use
- ✅ Delete temporary files after processing
- ✅ Clear memory of large DataFrames when no longer needed

**Example - GOOD**:
```python
with open(checkpoint_path, 'wb') as f:
    df.to_parquet(f)
# File automatically closed

del df  # Free memory
gc.collect()
```

**Example - BAD**:
```python
f = open(checkpoint_path, 'wb')
df.to_parquet(f)
# File not closed, memory leak
```

---

### 2. SQL Query Standards

#### 2.1 Query Structure

**Standard**: All SQL queries must be readable, parameterized, and optimized

**Requirements**:
- ✅ Use consistent indentation (2 spaces)
- ✅ UPPERCASE for SQL keywords (SELECT, FROM, WHERE)
- ✅ Lowercase for table/column names
- ✅ Parameterized queries (prevent SQL injection)
- ✅ Explicit column selection (no `SELECT *` unless necessary)

**Example - GOOD**:
```python
sql = f"""
  SELECT
    interval_time,
    {', '.join(feature_columns)}
  FROM
    `{project}.{dataset}.{table}`
  WHERE
    DATE(interval_time) BETWEEN @start_date AND @end_date
  ORDER BY
    interval_time
"""
```

**Example - BAD**:
```python
sql = f"SELECT * FROM {table} WHERE interval_time > '{start_date}'"  # SQL injection risk
```

---

#### 2.2 Query Optimization

**Standard**: All BigQuery queries must be optimized for cost and performance

**Requirements**:
- ✅ Use partitioning filters (reduce scanned data by 90%+)
- ✅ Use clustering keys when available
- ✅ Avoid `SELECT *` (select only needed columns)
- ✅ Use `LIMIT` for testing/validation queries
- ✅ Estimate query cost before running (use dry_run=True)

**Example - Cost Estimation**:
```python
# Dry run to estimate cost
job_config = bigquery.QueryJobConfig(dry_run=True)
query_job = client.query(sql, job_config=job_config)
bytes_processed = query_job.total_bytes_processed
cost_estimate = (bytes_processed / 1e12) * 6.25  # $6.25 per TB
logger.info(f"Query will scan {bytes_processed/1e9:.2f} GB, cost ~${cost_estimate:.4f}")
```

---

### 3. Script Standards

#### 3.1 Command-Line Interface

**Standard**: All scripts must accept clear, documented arguments

**Requirements**:
- ✅ Use `argparse` for argument parsing
- ✅ Provide `--help` documentation
- ✅ Validate arguments before execution
- ✅ Provide sensible defaults where applicable

**Example**:
```python
import argparse

parser = argparse.ArgumentParser(
    description='Extract features for a currency pair from BigQuery'
)
parser.add_argument('--pair', required=True, help='Currency pair (e.g., eurusd)')
parser.add_argument('--output-dir', default='data/features/checkpoints',
                    help='Output directory for checkpoints')
parser.add_argument('--workers', type=int, default=4,
                    help='Number of parallel workers')
args = parser.parse_args()

# Validate
if not args.pair.isalpha() or len(args.pair) != 6:
    parser.error(f"Invalid pair format: {args.pair}")
```

---

#### 3.2 Execution Modes

**Standard**: All scripts must support dry-run and production modes

**Requirements**:
- ✅ `--dry-run` flag: Show what would be done without executing
- ✅ `--verbose` flag: Increase logging detail
- ✅ `--force` flag: Override safety checks (use sparingly)
- ✅ Exit codes: 0 for success, non-zero for failure

**Example**:
```python
if args.dry_run:
    logger.info(f"DRY RUN: Would extract {len(tables)} tables for {args.pair}")
    logger.info(f"DRY RUN: Output directory: {args.output_dir}")
    sys.exit(0)

# Production execution
logger.info(f"Starting extraction for {args.pair}")
```

---

## DATA QUALITY STANDARDS

### 1. Training File Standards

#### 1.1 Schema Validation

**Standard**: All training files must match expected schema

**Requirements**:
- ✅ Column count: 458 (399 features + 49 targets + 10 metadata)
- ✅ Column names: Match feature catalogue naming convention
- ✅ Data types: Numeric for features/targets, datetime for interval_time
- ✅ No duplicate columns
- ✅ Columns in consistent order: metadata → features → targets

**Validation Script**: `scripts/validate_merged_output.py`

**Example Validation**:
```python
expected_columns = 458
actual_columns = len(df.columns)
assert actual_columns == expected_columns, \
    f"Column count mismatch: expected {expected_columns}, got {actual_columns}"

# Verify no duplicates
duplicates = df.columns[df.columns.duplicated()].tolist()
assert len(duplicates) == 0, f"Duplicate columns found: {duplicates}"
```

---

#### 1.2 Data Completeness

**Standard**: Training files must have minimal missing data

**Requirements**:
- ✅ Row count: ~2.17M rows (±5% acceptable variance)
- ✅ Missing values in features: <1% per column
- ✅ Missing values in targets: 0% (no NaN allowed)
- ✅ Missing values in metadata: 0% (no NaN allowed)
- ✅ Time coverage: 2019-01-01 to 2024-12-31 (6 years)

**Validation**:
```python
# Check row count
expected_rows = 2_170_000
actual_rows = len(df)
variance = abs(actual_rows - expected_rows) / expected_rows
assert variance < 0.05, \
    f"Row count variance {variance:.2%} exceeds 5% threshold"

# Check missing values
for col in feature_columns:
    missing_pct = df[col].isna().sum() / len(df)
    assert missing_pct < 0.01, \
        f"Column {col} has {missing_pct:.2%} missing values (>1% threshold)"

# Check targets (no NaN allowed)
for col in target_columns:
    missing_count = df[col].isna().sum()
    assert missing_count == 0, \
        f"Target column {col} has {missing_count} missing values"
```

---

#### 1.3 Data Integrity

**Standard**: Training file data must be valid and consistent

**Requirements**:
- ✅ No infinite values in features/targets
- ✅ No extreme outliers (>10 standard deviations)
- ✅ Monotonic timestamps (no duplicates, no gaps >1 minute)
- ✅ Target values match LEAD(bqx_*, horizon) formula
- ✅ Feature correlations match expected patterns

**Validation**:
```python
# Check for infinite values
for col in feature_columns + target_columns:
    inf_count = np.isinf(df[col]).sum()
    assert inf_count == 0, f"Column {col} has {inf_count} infinite values"

# Check timestamp monotonicity
time_diffs = df['interval_time'].diff().dt.total_seconds()
duplicates = (time_diffs == 0).sum()
gaps = (time_diffs > 60).sum()  # >1 minute gaps
assert duplicates == 0, f"Found {duplicates} duplicate timestamps"
logger.warning(f"Found {gaps} gaps >1 minute in timestamps")
```

---

### 2. BigQuery Table Standards

#### 2.1 Partitioning and Clustering

**Standard**: All feature tables must use partitioning and clustering

**Requirements**:
- ✅ Partition column: `DATE(interval_time)`
- ✅ Clustering column: `pair` (or `pair1` for covariance tables)
- ✅ Partition expiration: None (retain all historical data)
- ✅ Require partition filter: True (enforce cost optimization)

**Validation**:
```python
table = client.get_table(f"{project}.{dataset}.{table_name}")
assert table.time_partitioning is not None, "Table not partitioned"
assert table.time_partitioning.field == "interval_time", "Wrong partition field"
assert table.clustering_fields in [['pair'], ['pair1']], "Wrong clustering"
```

---

#### 2.2 Table Metadata

**Standard**: All tables must have description and labels

**Requirements**:
- ✅ Table description: 1-2 sentence explanation of table purpose
- ✅ Labels:
  - `version: v2` (V2 dataset migration)
  - `feature_type: <type>` (e.g., `lag`, `corr`, `tri`)
  - `data_source: bqx` or `data_source: idx`
- ✅ Schema field descriptions for all non-obvious columns

**Example**:
```python
table.description = "Lag features for EURUSD (historical values 1-60 bars back)"
table.labels = {
    'version': 'v2',
    'feature_type': 'lag',
    'data_source': 'bqx'
}
```

---

## DOCUMENTATION STANDARDS

### 1. Code Documentation

#### 1.1 Function Docstrings

**Standard**: All functions must have docstrings

**Requirements**:
- ✅ One-line summary
- ✅ Detailed description (if complex)
- ✅ Args: Type and description for each parameter
- ✅ Returns: Type and description of return value
- ✅ Raises: Exception types and conditions

**Example - GOOD**:
```python
def extract_features_for_pair(pair: str, output_dir: str, workers: int = 4) -> int:
    """
    Extract all feature tables for a currency pair from BigQuery.

    Extracts 667 feature tables (256 pair-specific + 194 tri + 10 mkt + 63 var + 144 csi)
    from BigQuery and saves as Parquet checkpoints in parallel.

    Args:
        pair: Currency pair code (e.g., 'eurusd')
        output_dir: Directory to save checkpoint files
        workers: Number of parallel extraction workers (default: 4)

    Returns:
        Number of tables successfully extracted

    Raises:
        ValueError: If pair format is invalid
        google.cloud.exceptions.NotFound: If BigQuery tables not found
    """
    ...
```

**Example - BAD**:
```python
def extract_features(pair, dir, n):  # No docstring, unclear parameter names
    ...
```

---

#### 1.2 Inline Comments

**Standard**: Complex logic must have explanatory comments

**Requirements**:
- ✅ Explain **why**, not **what** (code shows what)
- ✅ Document non-obvious behavior
- ✅ Reference user mandates or CE directives when applicable
- ✅ Use TODO/FIXME/NOTE annotations appropriately

**Example - GOOD**:
```python
# User mandated Polars over BigQuery (4.6× faster, see CE-1650)
df_merged = pl.concat(checkpoints, how='vertical')

# Auto-detect CPU count to prevent oversubscription on Cloud Run
workers = min(cpu_count(), 4)  # Max 4 to avoid memory pressure
```

**Example - BAD**:
```python
# Merge dataframes
df = pl.concat(dfs)  # Comment just repeats code
```

---

### 2. Architecture Documentation

#### 2.1 Intelligence Files

**Standard**: All architecture changes must update intelligence files

**Requirements**:
- ✅ Update within 24 hours of deployment
- ✅ Maintain 100% consistency across all 5 files
- ✅ Validate JSON syntax after every edit
- ✅ Version bump for significant changes

**Files**:
1. `intelligence/context.json` - Project context, deployment details
2. `intelligence/roadmap_v2.json` - Roadmap and phase tracking
3. `intelligence/semantics.json` - Model architecture, feature selection
4. `intelligence/ontology.json` - Entity definitions, training pipeline
5. `intelligence/feature_catalogue.json` - Feature inventory, gap status

**Validation**:
```bash
python3 -m json.tool intelligence/context.json > /dev/null
```

---

#### 2.2 Documentation Currency

**Standard**: Documentation must be current (<7 days old)

**Requirements**:
- ✅ Intelligence files: Updated within 24 hours
- ✅ Mandate files: Updated within 48 hours of policy change
- ✅ README files: Updated within 1 week of major changes
- ✅ API documentation: Updated with code changes (same commit)

**Monitoring**:
```bash
# Check file modification times
find intelligence/ mandate/ -name "*.json" -mtime +7
```

---

### 3. Communications Documentation

#### 3.1 Agent Communications

**Standard**: All inter-agent communications must be documented

**Requirements**:
- ✅ Use standard filename format: `YYYYMMDD_HHMM_FROM-to-TO_SUBJECT.md`
- ✅ Include header: Date, From, To, Re, Priority
- ✅ Clear subject line (50 characters max)
- ✅ Actionable recommendations (not just status updates)
- ✅ Copy to recipient's inbox

**Example Filename**:
```
20251212_1930_QA-to-CE_INTELLIGENCE_UPDATES_COMPLETE.md
```

---

#### 3.2 Status Reports

**Standard**: Status reports must include completion criteria

**Requirements**:
- ✅ Executive summary (3-5 bullet points)
- ✅ Completed tasks with evidence
- ✅ Incomplete tasks with timeline
- ✅ Blockers with recommended resolution
- ✅ Next actions with assigned owners

**Template**: See `shared/PHASE1_FILE_UPDATE_TEMPLATE.md`

---

## PROCESS STANDARDS

### 1. Development Workflow

#### 1.1 Code Review

**Standard**: All code changes must be reviewed before production

**Requirements**:
- ✅ Self-review: Author checks code before commit
- ✅ Peer review: Another agent reviews (QA for BA code, EA for architecture)
- ✅ Testing: All scripts tested with dry-run mode
- ✅ Documentation: Changes documented in commit message

**Process**:
1. Author creates code/script
2. Author self-reviews against this framework
3. Author creates communication to QA/EA requesting review
4. Reviewer validates against standards
5. Reviewer approves or requests changes
6. Author commits with detailed message

---

#### 1.2 Git Commit Standards

**Standard**: All commits must have descriptive messages

**Requirements**:
- ✅ Format: `<type>: <summary> (<detailed description>)`
- ✅ Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- ✅ Summary: 50 characters max, imperative mood
- ✅ Description: Explain why (not what), reference directives
- ✅ Include attribution footer

**Example - GOOD**:
```
feat: Add Cloud Run deployment with Polars merge

- Cloud Run job with 4 CPUs, 12 GB memory
- Polars merge protocol (user-mandated, 4.6× faster than BigQuery)
- Auto-detect CPU count to prevent oversubscription
- Cost: $0.71/pair, 99% reduction vs VM

Reference: CE directive 2025-12-12, User mandate for Polars

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Example - BAD**:
```
update code
```

---

### 2. Testing Standards

#### 2.1 Validation Before Production

**Standard**: All production scripts must be tested on sample data

**Requirements**:
- ✅ Unit tests: Test individual functions
- ✅ Integration tests: Test end-to-end pipeline
- ✅ Validation tests: Verify output quality
- ✅ Dry-run tests: Test without side effects

**Example Test Suite**:
```python
# Unit test
def test_extract_single_table():
    df = extract_table('lag_eurusd', limit=1000)
    assert len(df) == 1000
    assert 'interval_time' in df.columns

# Integration test
def test_full_pipeline_eurusd():
    extract_features('eurusd', 'data/test')
    merge_features('eurusd', 'data/test')
    validate_output('eurusd', 'data/test')

# Validation test
def test_schema_validation():
    df = pd.read_parquet('data/training/eurusd_training_h15-h105.parquet')
    assert len(df.columns) == 458
    assert df['interval_time'].dtype == 'datetime64[ns]'
```

---

#### 2.2 Rollback Procedures

**Standard**: All production changes must have rollback plan

**Requirements**:
- ✅ Document rollback steps before deployment
- ✅ Backup critical data before modifications
- ✅ Test rollback procedure in non-production environment
- ✅ Time estimate for rollback (<30 minutes preferred)

**Example Rollback Plan**:
```markdown
## Rollback Plan: Cloud Run Deployment

**Trigger**: If GBPUSD test execution fails validation

**Steps**:
1. Cancel Cloud Run execution: `gcloud run jobs executions cancel <execution-id>`
2. Revert to local VM execution: `./scripts/extract_and_merge_local.sh gbpusd`
3. Validate local output: `python3 scripts/validate_merged_output.py gbpusd`
4. Update intelligence files: Revert deployment status to "TESTING"

**Time Estimate**: 10-15 minutes
**Data Loss**: None (checkpoints preserved in GCS)
```

---

### 3. Change Management

#### 3.1 Configuration Changes

**Standard**: Configuration changes require CE authorization

**Requirements**:
- ✅ Document change rationale
- ✅ Estimate impact (cost, timeline, dependencies)
- ✅ Request CE authorization via communication
- ✅ Update intelligence files after approval

**Example Authorization Request**:
```markdown
## AUTHORIZATION REQUEST: Increase Cloud Run Memory

**Proposed Change**: Increase Cloud Run memory from 12 GB to 16 GB

**Rationale**: GBPUSD execution hit memory warnings at 11.8 GB (98% utilization)

**Impact**:
- Cost: +$0.24/pair (+33% from $0.71 to $0.95)
- Timeline: No change (prevents OOM failures)
- Risk: LOW (prevents execution failures)

**Alternative**: Reduce parallel workers from 4 to 3 (no cost increase, but +10% execution time)

**Recommendation**: Increase to 16 GB for production stability

**Awaiting CE Authorization**
```

---

## VALIDATION PROTOCOLS

### 1. Pre-Production Validation

**Checklist**: Execute before authorizing 25-pair production rollout

#### 1.1 Test Execution Validation

- [ ] **EURUSD**: ✅ COMPLETE (validated QA-0120)
- [ ] **AUDUSD**: ✅ COMPLETE (validated)
- [ ] **GBPUSD**: 🔄 IN PROGRESS (validation pending)

**Validation Steps**:
1. Training file exists
2. File size: 25-35 MB (±20% acceptable)
3. Row count: ~2.17M (±5% acceptable)
4. Column count: 458 (exact)
5. Schema validation passes
6. No missing values in targets
7. <1% missing values in features
8. Timestamp monotonicity validated

---

#### 1.2 Cost Validation

- [ ] **Expected cost/pair**: $0.71 (baseline: EURUSD)
- [ ] **Actual cost/pair**: $0.71 - $0.95 (±33% acceptable)
- [ ] **Total cost 28 pairs**: <$30 (user mandate: minimal expense)

**Monitoring**:
```bash
gcloud run jobs executions list --job=bqx-ml-pipeline --format="table(name,status,costEstimate)"
```

---

#### 1.3 Timeline Validation

- [ ] **Expected time/pair**: 77-101 minutes (baseline: EURUSD)
- [ ] **Actual time/pair**: 77-150 minutes (±50% acceptable for variance)
- [ ] **Total time 28 pairs**: <70 hours (user mandate: maximum speed)

**Monitoring**:
```bash
# Check execution duration
gcloud run jobs executions describe <execution-id> --format="value(status.startTime,status.completionTime)"
```

---

### 2. Production Validation

**Checklist**: Execute during 25-pair production rollout

#### 2.1 Batch Validation

**Frequency**: After every 5 pairs

**Steps**:
1. Verify all 5 training files exist
2. Spot-check 1 random file from batch (full validation)
3. Check cost accumulation vs budget
4. Check timeline projection to completion
5. Report status to CE

---

#### 2.2 Failure Recovery

**Protocol**: If any pair fails validation

**Steps**:
1. **STOP**: Pause rollout immediately
2. **ANALYZE**: Review logs, identify root cause
3. **FIX**: Implement corrective action
4. **RETRY**: Re-run failed pair
5. **VALIDATE**: Full validation on retry
6. **RESUME**: Continue rollout after validation passes

**Do NOT Continue** if:
- 2+ consecutive failures
- Cost exceeds $1.50/pair
- Execution time exceeds 3 hours/pair
- Validation fails after retry

---

## SUCCESS METRICS

### 1. Quality Metrics (QA Charge v2.0.0)

#### 1.1 Audit Coverage
- **Target**: 100% of work products inventoried
- **Measurement**: (Documented items / Total items) × 100%
- **Threshold**: ≥100% (all work must be documented)

#### 1.2 Issue Detection Speed
- **Target**: <1 hour from issue occurrence to detection
- **Measurement**: Time from issue occurrence to QA alert
- **Threshold**: <1 hour for P0/P1 issues

#### 1.3 Remediation Completion
- **Target**: >90% of recommended remediations completed
- **Measurement**: (Completed remediations / Recommended) × 100%
- **Threshold**: ≥90% within agreed timeline

#### 1.4 Cost Variance
- **Target**: ±10% of estimated cost
- **Measurement**: (Actual cost - Estimated cost) / Estimated cost
- **Threshold**: ≤10% variance

#### 1.5 Documentation Currency
- **Target**: <7 days old
- **Measurement**: Days since last documentation update
- **Threshold**: ≤7 days for all critical docs

#### 1.6 Quality Compliance
- **Target**: 100% compliance with standards
- **Measurement**: (Compliant items / Total items) × 100%
- **Threshold**: 100% (no exceptions without CE approval)

---

### 2. Project Success Metrics

#### 2.1 Training File Quality
- **Row count accuracy**: 95% of files within ±5% of expected
- **Schema compliance**: 100% of files match expected schema
- **Data completeness**: <1% missing values per file

#### 2.2 Production Efficiency
- **First-time success rate**: >80% of pairs succeed on first attempt
- **Validation pass rate**: >95% of files pass validation
- **Rollback rate**: <10% of deployments require rollback

#### 2.3 Timeline Performance
- **On-time delivery**: >90% of tasks complete within estimated time
- **Estimation accuracy**: ±25% of actual vs estimated time

---

## REMEDIATION PROCEDURES

### 1. Remediation Process

**Steps**:
1. **Identify**: QA identifies gap/issue during audit
2. **Document**: QA documents in remediation report
3. **Prioritize**: CE assigns priority (P0/P1/P2/P3)
4. **Assign**: CE assigns to responsible agent
5. **Execute**: Agent executes remediation
6. **Validate**: QA validates remediation complete
7. **Close**: QA closes remediation item

---

### 2. Priority Levels

**P0 - CRITICAL**: Blocks production rollout
- **SLA**: Fix within 4 hours
- **Example**: GBPUSD validation fails, 25-pair rollout blocked

**P1 - HIGH**: Impacts quality/documentation
- **SLA**: Fix within 24 hours
- **Example**: Intelligence files not updated after deployment

**P2 - MEDIUM**: Useful but not urgent
- **SLA**: Fix within 1 week
- **Example**: Missing documentation for build iterations

**P3 - LOW**: Nice-to-have, can defer
- **SLA**: Fix when time permits
- **Example**: Code style improvements, refactoring

---

### 3. Escalation Path

**Level 1**: Agent self-remediation (P2/P3 issues)
**Level 2**: Cross-agent collaboration (P1 issues)
**Level 3**: CE directive (P0 issues, or P1 issues blocking progress)
**Level 4**: User consultation (mandate changes, resource constraints)

---

## APPENDIX A: VALIDATION SCRIPTS

### A.1 Training File Validation

**Script**: `scripts/validate_merged_output.py`

**Usage**:
```bash
python3 scripts/validate_merged_output.py eurusd
```

**Checks**:
- File exists
- File size in expected range
- Row count within ±5%
- Column count exact (458)
- Schema matches expected
- No missing values in targets
- <1% missing in features
- No infinite values
- Timestamp monotonicity

---

### A.2 BigQuery Table Validation

**Script**: `scripts/validate_bq_table.py`

**Usage**:
```bash
python3 scripts/validate_bq_table.py bqx_ml_v3_features_v2 lag_eurusd
```

**Checks**:
- Table exists
- Partitioned by DATE(interval_time)
- Clustered by pair
- Has description
- Has labels
- Row count > 0
- No duplicate rows

---

### A.3 Intelligence File Validation

**Script**: `scripts/validate_intelligence_files.py`

**Usage**:
```bash
python3 scripts/validate_intelligence_files.py
```

**Checks**:
- All 5 files exist
- All JSON valid
- Version consistency
- Count consistency (588 models, 667 tables)
- Last updated <24 hours
- Cross-file references valid

---

## APPENDIX B: REFERENCE DOCUMENTS

### B.1 User Mandates
- **Primary Mandate**: "Maximum speed to completion at minimal expense within system limitations"
- **Polars Mandate**: User mandated Polars over BigQuery (2025-12-12)
- **SHAP Samples**: User mandated 100K+ samples (not 10K)

### B.2 CE Directives
- **CE-1750**: Work Product Inventory & Audit (2025-12-12 17:50 UTC)
- **CE-1840**: Intelligence File Updates (2025-12-12 18:35 UTC)
- **CE-1720**: GBPUSD Validation Preparation (2025-12-12 17:20 UTC)

### B.3 Agent Charges
- **QA Charge v2.0.0**: Quality Assurance responsibilities and success metrics
- **BA Charge v2.0.0**: Build Agent responsibilities
- **EA Charge v2.0.0**: Enhancement Assistant responsibilities

### B.4 Related Documentation
- `mandate/AGENT_ONBOARDING_PROTOCOL.md`: Agent onboarding process
- `intelligence/roadmap_v2.json`: Project roadmap and phases
- `docs/CLOUD_RUN_DEPLOYMENT_GUIDE.md`: Cloud Run deployment procedures

---

## VERSION HISTORY

**v1.0.0** (2025-12-12 19:40 UTC):
- Initial framework creation
- Defined code, data, documentation, process standards
- Established validation protocols and success metrics
- Created by QA as P1 remediation from work product inventory

---

**Quality Assurance Agent (QA)**
*Documentation Validation & Project Consistency*

**Framework Status**: ACTIVE
**Last Updated**: 2025-12-12 19:40 UTC
**Next Review**: 2025-12-19 (weekly review)

---

**END OF QUALITY STANDARDS FRAMEWORK**
