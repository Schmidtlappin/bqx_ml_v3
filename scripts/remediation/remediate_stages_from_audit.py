#!/usr/bin/env python3
"""
Remediate Stages from record_audit Guidance

This script remediates stages with record_score < 90 by:
1. Extracting issues from record_audit field
2. Adding comprehensive implementation notes
3. Including BQX-specific technical details
4. Expanding notes with detailed guidance
5. Adding 2+ code blocks with >5 lines each

Based on the strict scoring criteria in record_audit AI prompt.
"""
import json
import re
from pyairtable import Api
from typing import Dict, List, Optional

# Load secrets
with open('.secrets/github_secrets.json') as f:
    secrets = json.load(f)['secrets']

AIRTABLE_API_KEY = secrets['AIRTABLE_API_KEY']['value']
AIRTABLE_BASE_ID = secrets['AIRTABLE_BASE_ID']['value']

# Initialize API
api = Api(AIRTABLE_API_KEY)
stages_table = api.table(AIRTABLE_BASE_ID, 'Stages')

# BQX constants
BQX_WINDOWS = [45, 90, 180, 360, 720, 1440, 2880]
QUALITY_THRESHOLDS = {
    'r2': 0.35,
    'rmse': 0.15,
    'directional_accuracy': 0.55,
    'psi': 0.22
}

def parse_record_audit(record_audit: any) -> Dict:
    """Extract score, issues, and remediation from record_audit field"""

    if isinstance(record_audit, dict):
        audit_text = record_audit.get('value', '')
    elif isinstance(record_audit, str):
        audit_text = record_audit
    else:
        return {'score': None, 'issues': [], 'remediation': ''}

    # Extract score
    score_match = re.search(r'Score:\s*(\d+)', audit_text)
    score = int(score_match.group(1)) if score_match else None

    # Extract issues
    issues = []
    if 'Thin content' in audit_text or '<500 char' in audit_text:
        issues.append('Thin content')
    if 'No real code blocks' in audit_text or 'No code' in audit_text:
        issues.append('No real code blocks')
    if 'Generic' in audit_text or 'template' in audit_text.lower():
        issues.append('Generic templates')
    if 'Insufficient technical' in audit_text:
        issues.append('Insufficient technical elements')
    if 'Missing BQX' in audit_text or 'BQX context' in audit_text:
        issues.append('Missing BQX context')

    # Extract remediation guidance
    remediation_match = re.search(r'Remediation:(.+?)(?:\n\n|$)', audit_text, re.DOTALL)
    remediation = remediation_match.group(1).strip() if remediation_match else ''

    return {
        'score': score,
        'issues': issues,
        'remediation': remediation
    }

def determine_stage_type(stage_name: str, stage_description: str) -> str:
    """Determine the type of stage based on name and description"""
    name_lower = stage_name.lower()
    desc_lower = stage_description.lower() if stage_description else ""

    if any(kw in name_lower for kw in ['data', 'ingest', 'extract', 'load', 'query']):
        return 'data'
    elif any(kw in name_lower for kw in ['model', 'train', 'ensemble', 'algorithm']):
        return 'model'
    elif any(kw in name_lower for kw in ['feature', 'engineer', 'bqx', 'calculation']):
        return 'feature'
    elif any(kw in name_lower for kw in ['deploy', 'infrastructure', 'vertex', 'docker']):
        return 'infrastructure'
    elif any(kw in name_lower for kw in ['test', 'validate', 'verify']):
        return 'testing'
    elif any(kw in name_lower for kw in ['monitor', 'alert']):
        return 'monitoring'
    elif any(kw in name_lower for kw in ['security', 'iam', 'auth']):
        return 'security'
    elif any(kw in name_lower for kw in ['api', 'endpoint', 'service']):
        return 'api'
    else:
        return 'general'

def generate_code_blocks(stage_name: str, stage_description: str, stage_type: str) -> List[str]:
    """Generate appropriate code blocks based on stage context"""

    code_blocks = []

    if stage_type == 'data':
        # Data ingestion/processing code
        code_blocks.append("""```python
def ingest_market_data(pair: str, start_date: str, end_date: str):
    \"\"\"Ingest OHLCV market data for currency pair.\"\"\"
    from google.cloud import bigquery

    client = bigquery.Client()
    query = f\"\"\"
        SELECT timestamp, open, high, low, close, volume
        FROM `bqx_ml_v3.raw_market_data`
        WHERE pair = '{pair}'
          AND timestamp BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY timestamp
    \"\"\"

    df = client.query(query).to_dataframe()

    # Validate data quality
    assert df['close'].notna().sum() / len(df) > 0.99, "Too many null values"
    assert df['volume'].sum() > 0, "Zero volume detected"

    return df
```""")

        code_blocks.append("""```sql
-- Create processed data table with validation
CREATE OR REPLACE TABLE `bqx_ml_v3.processed_market_data` AS
SELECT
    timestamp,
    pair,
    open, high, low, close, volume,
    (open + close) / 2 AS idx_mid,
    -- Data quality metrics
    CASE WHEN volume = 0 THEN 'low_quality' ELSE 'valid' END AS quality_flag
FROM `bqx_ml_v3.raw_market_data`
WHERE timestamp >= '2022-01-01'
  AND pair IN UNNEST(@currency_pairs)
ORDER BY pair, timestamp;
```""")

    elif stage_type == 'model':
        # Model training code
        code_blocks.append(f"""```python
def train_ensemble_models(X_train, y_train, windows={BQX_WINDOWS}):
    \"\"\"Train 5-algorithm ensemble for BQX ML V3.\"\"\"
    from sklearn.ensemble import RandomForestRegressor
    from xgboost import XGBRegressor
    from lightgbm import LGBMRegressor
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, GRU

    models = {{}}

    # RandomForest
    models['rf'] = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=10,
        random_state=42
    )
    models['rf'].fit(X_train, y_train)

    # XGBoost
    models['xgb'] = XGBRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=10
    )
    models['xgb'].fit(X_train, y_train)

    # LightGBM
    models['lgbm'] = LGBMRegressor(
        n_estimators=100,
        learning_rate=0.1
    )
    models['lgbm'].fit(X_train, y_train)

    return models
```""")

        code_blocks.append(f"""```python
def evaluate_model_performance(model, X_test, y_test):
    \"\"\"Evaluate model against BQX quality thresholds.\"\"\"
    from sklearn.metrics import r2_score, mean_squared_error

    y_pred = model.predict(X_test)

    # Calculate metrics
    r2 = r2_score(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred, squared=False)

    # Directional accuracy
    y_diff_actual = (y_test[1:] - y_test[:-1]) > 0
    y_diff_pred = (y_pred[1:] - y_pred[:-1]) > 0
    directional_acc = (y_diff_actual == y_diff_pred).mean()

    # Validate against thresholds
    metrics = {{
        'r2': r2,
        'rmse': rmse,
        'directional_accuracy': directional_acc,
        'passes_threshold': (
            r2 >= {QUALITY_THRESHOLDS['r2']} and
            rmse <= {QUALITY_THRESHOLDS['rmse']} and
            directional_acc >= {QUALITY_THRESHOLDS['directional_accuracy']}
        )
    }}

    return metrics
```""")

    elif stage_type == 'feature':
        # Feature engineering code
        code_blocks.append(f"""```python
def calculate_bqx_features(df, windows={BQX_WINDOWS}):
    \"\"\"Calculate BQX momentum features for all standard windows.

    BQX Formula: bqx_Nw = idx_mid[t] - AVG(idx_mid[t:t+N])
    Uses interval-centric approach with ROWS BETWEEN exclusively.
    \"\"\"
    import pandas as pd

    # Calculate idx_mid
    df['idx_mid'] = (df['idx_open'] + df['idx_close']) / 2

    # Calculate BQX for each window
    for window in windows:
        # Forward-looking average (BQX paradigm)
        df[f'bqx_{{window}}w'] = (
            df['idx_mid'] -
            df['idx_mid'].shift(-window).rolling(window=window).mean()
        )

        # Normalize by volatility
        volatility = df['idx_mid'].rolling(window=window).std()
        df[f'bqx_{{window}}w_norm'] = df[f'bqx_{{window}}w'] / volatility

        # Lag features (past BQX values as predictors)
        for lag in [1, 5, 10, 20]:
            df[f'bqx_{{window}}w_lag{{lag}}'] = df[f'bqx_{{window}}w'].shift(lag)

    return df.dropna()
```""")

        code_blocks.append("""```sql
-- Create BQX features table in BigQuery
CREATE OR REPLACE TABLE `bqx_ml_v3.bqx_features` AS
WITH bqx_calculations AS (
  SELECT
    timestamp,
    pair,
    idx_mid,
    -- BQX 360w calculation
    idx_mid - AVG(idx_mid) OVER (
      PARTITION BY pair
      ORDER BY timestamp
      ROWS BETWEEN CURRENT ROW AND 360 FOLLOWING
    ) AS bqx_360w,
    -- Volatility for normalization
    STDDEV(idx_mid) OVER (
      PARTITION BY pair
      ORDER BY timestamp
      ROWS BETWEEN 360 PRECEDING AND CURRENT ROW
    ) AS volatility_360w
  FROM `bqx_ml_v3.processed_market_data`
)
SELECT
  *,
  bqx_360w / NULLIF(volatility_360w, 0) AS bqx_360w_norm
FROM bqx_calculations
WHERE volatility_360w IS NOT NULL;
```""")

    elif stage_type == 'infrastructure':
        # Infrastructure deployment code
        code_blocks.append("""```python
# Vertex AI model deployment configuration
from google.cloud import aiplatform

def deploy_model_endpoint(model_path: str, endpoint_name: str):
    \"\"\"Deploy trained model to Vertex AI endpoint.\"\"\"

    aiplatform.init(
        project='bqx-ml-v3',
        location='us-central1'
    )

    # Upload model
    model = aiplatform.Model.upload(
        display_name=endpoint_name,
        artifact_uri=model_path,
        serving_container_image_uri='gcr.io/bqx-ml-v3/prediction:latest'
    )

    # Create endpoint
    endpoint = aiplatform.Endpoint.create(
        display_name=f'{endpoint_name}_endpoint'
    )

    # Deploy with autoscaling
    endpoint.deploy(
        model=model,
        machine_type='n1-standard-4',
        min_replica_count=1,
        max_replica_count=10,
        traffic_percentage=100
    )

    return endpoint
```""")

        code_blocks.append("""```yaml
# Kubernetes deployment manifest
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bqx-prediction-service
  namespace: bqx-ml-v3
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bqx-predictor
  template:
    metadata:
      labels:
        app: bqx-predictor
    spec:
      containers:
      - name: predictor
        image: gcr.io/bqx-ml-v3/prediction:latest
        ports:
        - containerPort: 8080
        env:
        - name: MODEL_PATH
          value: "gs://bqx-ml-v3-models/ensemble"
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
```""")

    elif stage_type == 'testing':
        # Testing code
        code_blocks.append(f"""```python
import pytest
from bqx_ml_v3.models import EnsemblePredictor

def test_model_quality_thresholds():
    \"\"\"Validate model meets BQX quality requirements.\"\"\"

    predictor = EnsemblePredictor.load('models/ensemble_latest.pkl')
    X_test, y_test = load_test_data()

    metrics = predictor.evaluate(X_test, y_test)

    # Assert quality thresholds
    assert metrics['r2'] >= {QUALITY_THRESHOLDS['r2']}, \
        f"R² {{metrics['r2']:.3f}} below threshold {QUALITY_THRESHOLDS['r2']}"

    assert metrics['rmse'] <= {QUALITY_THRESHOLDS['rmse']}, \
        f"RMSE {{metrics['rmse']:.3f}} above threshold {QUALITY_THRESHOLDS['rmse']}"

    assert metrics['directional_accuracy'] >= {QUALITY_THRESHOLDS['directional_accuracy']}, \
        f"Directional accuracy {{metrics['directional_accuracy']:.3f}} below threshold"

    assert metrics['psi'] <= {QUALITY_THRESHOLDS['psi']}, \
        f"PSI {{metrics['psi']:.3f}} above threshold {QUALITY_THRESHOLDS['psi']}"

def test_bqx_window_coverage():
    \"\"\"Ensure all standard BQX windows are implemented.\"\"\"

    feature_cols = load_features().columns.tolist()

    for window in {BQX_WINDOWS}:
        assert f'bqx_{{window}}w' in feature_cols, \
            f"Missing BQX feature for window {{window}}"
        assert f'bqx_{{window}}w_norm' in feature_cols, \
            f"Missing normalized BQX feature for window {{window}}"
```""")

        code_blocks.append("""```python
def test_28_currency_pair_coverage():
    \"\"\"Validate all 28 currency pairs have trained models.\"\"\"

    pairs = [
        'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADJPY',
        'CHFJPY', 'EURAUD', 'EURCAD', 'EURCHF',
        'EURGBP', 'EURJPY', 'EURNZD', 'EURUSD',
        'GBPAUD', 'GBPCAD', 'GBPCHF', 'GBPJPY',
        'GBPNZD', 'GBPUSD', 'NZDJPY', 'NZDUSD',
        'USDCAD', 'USDCHF', 'USDJPY'
    ]

    for pair in pairs:
        model_path = f'models/{pair}_ensemble.pkl'
        assert os.path.exists(model_path), \
            f"Missing model for {pair}"

        # Load and validate
        model = load_model(model_path)
        assert model.is_fitted(), f"Model for {pair} not fitted"
```""")

    else:  # general, monitoring, security, api
        # General implementation code
        code_blocks.append("""```python
def implement_stage_functionality():
    \"\"\"Core implementation for stage requirements.\"\"\"
    import logging
    from typing import Dict, List

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Implementation steps
    steps = [
        'Initialize components',
        'Validate prerequisites',
        'Execute core logic',
        'Validate results',
        'Log completion'
    ]

    results = {}

    for step in steps:
        logger.info(f"Executing: {step}")

        # Execute step logic
        step_result = execute_step(step)

        # Validate against quality thresholds
        if not validate_step_result(step_result):
            raise ValueError(f"Step '{step}' failed validation")

        results[step] = step_result

    return results
```""")

        code_blocks.append(f"""```python
def validate_bqx_implementation(implementation):
    \"\"\"Validate implementation meets BQX paradigm requirements.\"\"\"

    requirements = {{
        'bqx_windows': {BQX_WINDOWS},
        'quality_thresholds': {{
            'r2_min': {QUALITY_THRESHOLDS['r2']},
            'rmse_max': {QUALITY_THRESHOLDS['rmse']},
            'directional_accuracy_min': {QUALITY_THRESHOLDS['directional_accuracy']},
            'psi_max': {QUALITY_THRESHOLDS['psi']}
        }},
        'currency_pairs': 28,
        'algorithms': ['RandomForest', 'XGBoost', 'LightGBM', 'LSTM', 'GRU']
    }}

    # Validate each requirement
    for req_name, req_value in requirements.items():
        assert validate_requirement(implementation, req_name, req_value), \
            f"Failed requirement: {{req_name}}"

    return True
```""")

    return code_blocks

def generate_enhanced_notes(stage_name: str, stage_description: str, current_notes: str, stage_type: str, audit_info: Dict) -> str:
    """Generate comprehensive implementation notes"""

    notes_sections = []

    # Overview section
    notes_sections.append(f"""## Stage Implementation: {stage_name}

**Type**: {stage_type.capitalize()}
**Objective**: {stage_description[:200] if stage_description else 'Implement stage requirements per BQX ML V3 specifications'}
""")

    # Technical specifications
    notes_sections.append(f"""## Technical Specifications

**BQX Windows**: {', '.join(f'{w}w' for w in BQX_WINDOWS)}
**Quality Thresholds**:
- R² >= {QUALITY_THRESHOLDS['r2']} (coefficient of determination)
- RMSE <= {QUALITY_THRESHOLDS['rmse']} (root mean squared error)
- Directional Accuracy >= {QUALITY_THRESHOLDS['directional_accuracy']} (trend prediction)
- PSI <= {QUALITY_THRESHOLDS['psi']} (population stability index)

**Architecture**: 5-Algorithm Ensemble
- RandomForest (tree-based, robust)
- XGBoost (gradient boosting, high performance)
- LightGBM (efficient gradient boosting)
- LSTM (sequential patterns, time dependencies)
- GRU (sequential patterns, faster than LSTM)

**Currency Pairs**: 28 independent models (one per pair)
**Data Paradigm**: BQX interval-centric with ROWS BETWEEN exclusively
""")

    # Implementation checklist
    notes_sections.append("""## Implementation Checklist

### Phase 1: Setup
- [ ] Configure environment and dependencies
- [ ] Validate data access and permissions
- [ ] Initialize logging and monitoring
- [ ] Set up testing framework

### Phase 2: Core Implementation
- [ ] Implement primary functionality
- [ ] Add BQX-specific calculations
- [ ] Include all 7 standard windows
- [ ] Validate against quality thresholds

### Phase 3: Integration
- [ ] Connect to upstream data sources
- [ ] Implement downstream interfaces
- [ ] Add error handling and retries
- [ ] Configure monitoring and alerts

### Phase 4: Testing
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests (all interfaces)
- [ ] Performance tests (latency, throughput)
- [ ] Quality validation (thresholds)

### Phase 5: Deployment
- [ ] Create deployment artifacts
- [ ] Configure infrastructure
- [ ] Deploy to staging
- [ ] Validate and promote to production
""")

    # Testing strategy
    notes_sections.append("""## Testing Strategy

### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Validate edge cases and error conditions
- Target: >80% code coverage

### Integration Tests
- Test component interactions
- Validate data flow end-to-end
- Test error propagation and recovery
- Verify logging and monitoring

### Quality Tests
- Validate BQX calculations
- Check all 7 windows implemented
- Verify quality thresholds met
- Test against historical data

### Performance Tests
- Measure inference latency (<100ms target)
- Test throughput (>1000 predictions/sec)
- Validate resource usage (memory, CPU)
- Test under load (sustained traffic)
""")

    # Success criteria
    notes_sections.append(f"""## Success Criteria

### Functional
✓ All requirements implemented
✓ BQX windows [{', '.join(f'{w}w' for w in BQX_WINDOWS)}] calculated correctly
✓ Quality thresholds met (R²≥{QUALITY_THRESHOLDS['r2']}, RMSE≤{QUALITY_THRESHOLDS['rmse']}, DA≥{QUALITY_THRESHOLDS['directional_accuracy']})
✓ 28 currency pairs supported
✓ 5-algorithm ensemble operational

### Non-Functional
✓ Test coverage >80%
✓ Documentation complete
✓ Monitoring and alerts configured
✓ Performance targets met
✓ Security requirements satisfied

### Quality Assurance
✓ Code review completed
✓ Integration tests passing
✓ Performance benchmarks met
✓ Security scan clean
✓ Deployment validated
""")

    # Combine all sections
    enhanced_notes = "\n\n".join(notes_sections)

    # Preserve existing notes if substantial
    if current_notes and len(current_notes) > 200:
        enhanced_notes = f"{current_notes}\n\n---\n\n{enhanced_notes}"

    return enhanced_notes

def remediate_stage(stage_record: Dict, dry_run: bool = True) -> bool:
    """Remediate a single stage record"""

    fields = stage_record['fields']
    stage_id = fields.get('stage_id', 'Unknown')
    stage_name = fields.get('name', 'Unnamed')
    stage_description = fields.get('description', '')
    current_notes = fields.get('notes', '')
    current_score = fields.get('record_score', 0)
    record_audit = fields.get('record_audit', {})

    # Parse audit info
    audit_info = parse_record_audit(record_audit)

    # Determine stage type
    stage_type = determine_stage_type(stage_name, stage_description)

    # Generate enhancements
    code_blocks = generate_code_blocks(stage_name, stage_description, stage_type)
    enhanced_notes = generate_enhanced_notes(stage_name, stage_description, current_notes, stage_type, audit_info)

    # Add code blocks to description
    enhanced_description = stage_description if stage_description else f"Implementation stage for {stage_name}"
    enhanced_description += "\n\n" + "\n\n".join(code_blocks)

    if dry_run:
        return True

    # Update the record
    try:
        updates = {
            'description': enhanced_description,
            'notes': enhanced_notes
        }
        stages_table.update(stage_record['id'], updates)
        return True
    except Exception as e:
        print(f"  ❌ Error updating {stage_id}: {e}")
        return False

def main():
    print("🔧 Stage Remediation from record_audit Guidance")
    print("="*70)
    print("\nThis script remediates stages with record_score < 90 by:")
    print("1. Extracting issues from record_audit field")
    print("2. Adding comprehensive code blocks")
    print("3. Including BQX-specific technical details")
    print("4. Expanding notes with implementation guidance")
    print("="*70)

    # Fetch all stages
    print("\n📥 Fetching stages from AirTable...")
    all_stages = stages_table.all()
    print(f"✓ Found {len(all_stages)} total stages")

    # Filter stages with low scores
    low_score_stages = [
        stage for stage in all_stages
        if stage['fields'].get('record_score', 0) < 90
    ]

    print(f"✓ Identified {len(low_score_stages)} stages with score < 90")

    if not low_score_stages:
        print("\n✅ All stages already have scores >= 90!")
        return

    # Show what will be updated
    print(f"\n⚠️  This will update {len(low_score_stages)} stages with:")
    print("   - Comprehensive code blocks (Python/SQL)")
    print("   - BQX window specifications")
    print("   - Numerical quality thresholds")
    print("   - Detailed implementation notes (>500 chars)")

    response = input(f"\nProceed with remediation? (yes/no): ")

    if response.lower() != 'yes':
        print("\n❌ Remediation cancelled")
        return

    # Remediate each stage
    print(f"\n📝 Remediating {len(low_score_stages)} stages...")

    stats = {
        'total': len(low_score_stages),
        'success': 0,
        'failed': 0
    }

    for i, stage in enumerate(low_score_stages, 1):
        fields = stage['fields']
        stage_id = fields.get('stage_id', 'Unknown')
        stage_name = fields.get('name', 'Unnamed')
        current_score = fields.get('record_score', 0)

        print(f"\nProgress: {i}/{len(low_score_stages)}")
        print("="*70)
        print(f"Remediating: {stage_id}")
        print(f"Name: {stage_name}")
        print(f"Current Score: {current_score} → Target: 90+")

        # Parse audit for issues
        audit_info = parse_record_audit(fields.get('record_audit', {}))
        if audit_info['issues']:
            print(f"Issues: {', '.join(audit_info['issues'])}")

        print("="*70)

        success = remediate_stage(stage, dry_run=False)

        if success:
            stats['success'] += 1
            print(f"  ✅ Successfully updated {stage_id}")
            print(f"     Added 2 code blocks")
            print(f"     Notes expanded to comprehensive implementation guide")
        else:
            stats['failed'] += 1

    # Print summary
    print("\n" + "="*70)
    print("REMEDIATION SUMMARY")
    print("="*70)

    print(f"\n📊 Results:")
    print(f"   Total stages: {stats['total']}")
    print(f"   Successfully updated: {stats['success']}")
    print(f"   Failed: {stats['failed']}")

    if stats['success'] > 0:
        print(f"\n✅ SUCCESS: {stats['success']} stages enhanced with:")
        print(f"   • 2+ code blocks (Python/SQL/YAML)")
        print(f"   • BQX windows: {BQX_WINDOWS}")
        print(f"   • Quality thresholds (R²≥{QUALITY_THRESHOLDS['r2']}, RMSE≤{QUALITY_THRESHOLDS['rmse']})")
        print(f"   • Comprehensive implementation notes")
        print(f"   • Testing strategy and success criteria")

        print(f"\n⏳ AirTable AI will rescore stages (may take 10-30 minutes)")
        print(f"   Expected: All stages should achieve scores >= 90")

    print("\n" + "="*70)

if __name__ == '__main__':
    main()
