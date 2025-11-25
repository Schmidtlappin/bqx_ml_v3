# BQX ML V3 Intelligence Architecture Guide
## The 7-Layer Intelligence System

**Purpose**: Create self-documenting, self-aware system that guides development and maintains consistency
**Location**: `/home/micha/bqx_ml_v3/.bqx_ml_v3/`
**Format**: JSON files with semantic meaning

## 🧠 LAYER 1: CONTEXT (context.json)

### Purpose
Defines the current state, environment, and active configuration of the system.

### Structure
```json
{
  "version": "3.0.0",
  "environment": "production",
  "timestamp": "2024-11-24T20:00:00Z",
  "paradigm": {
    "name": "bqx_features_and_targets",
    "effective_date": "2024-11-24",
    "description": "BQX values serve as both features and targets"
  },
  "active_phase": "P03.2",
  "gcp_project": "bqx-ml",
  "instance": "bqx-ml-master",
  "repository": {
    "url": "https://github.com/Schmidtlappin/bqx_ml_v3",
    "branch": "main",
    "commit": "latest"
  },
  "currency_pairs": [
    "eurusd", "gbpusd", "usdjpy", "usdchf", "usdcad", "audusd", "nzdusd",
    "eurjpy", "eurgbp", "eurchf", "eurcad", "euraud", "eurnzd",
    "gbpjpy", "gbpchf", "gbpcad", "gbpaud", "gbpnzd",
    "audjpy", "nzdjpy", "chfjpy", "cadjpy",
    "audchf", "audcad", "audnzd",
    "nzdchf", "nzdcad", "cadchf"
  ],
  "feature_configuration": {
    "include_bqx_features": true,
    "lag_periods": 60,
    "window_type": "ROWS BETWEEN",
    "aggregation_functions": ["mean", "std", "min", "max", "range"]
  },
  "model_configuration": {
    "ensemble_size": 5,
    "algorithms": ["linear", "xgboost", "neural_network", "lstm", "gaussian_process"],
    "training_platform": "vertex_ai",
    "deployment_platform": "vertex_ai_endpoints"
  }
}
```

### Operationalization
```python
# Load context to understand current state
import json

def load_context():
    with open('.bqx_ml_v3/context.json') as f:
        context = json.load(f)

    # Use context to configure system
    pairs = context['currency_pairs']
    paradigm = context['paradigm']['name']
    phase = context['active_phase']

    return context

# Update context when phase changes
def update_phase(new_phase):
    context = load_context()
    context['active_phase'] = new_phase
    context['timestamp'] = datetime.now().isoformat()

    with open('.bqx_ml_v3/context.json', 'w') as f:
        json.dump(context, f, indent=2)
```

## 📖 LAYER 2: SEMANTICS (semantics.json)

### Purpose
Defines the vocabulary, terminology, and meaning of domain-specific concepts.

### Structure
```json
{
  "terms": {
    "bqx": {
      "definition": "Behavioral Quotient Index - momentum indicator",
      "formula": "idx_mid[T] - AVG(idx_mid[T+1..T+N])",
      "usage": ["feature", "target"],
      "paradigm_shift": "Can now be used as both features and targets"
    },
    "lag": {
      "definition": "Historical value at previous time interval",
      "notation": "variable_lag_N where N is periods back",
      "implementation": "LAG(column, N) OVER (ORDER BY bar_start_time)"
    },
    "regime": {
      "definition": "Market state classification",
      "types": ["trend", "volatility", "momentum"],
      "calculation": "Statistical properties over rolling windows"
    },
    "pair": {
      "definition": "Currency pair trading symbol",
      "format": "base_quote lowercase",
      "examples": ["eurusd", "gbpusd"],
      "count": 28
    },
    "window": {
      "definition": "Data range for calculations",
      "type": "ROWS BETWEEN",
      "prohibited": "RANGE BETWEEN with time intervals"
    }
  },
  "abbreviations": {
    "BQX": "Behavioral Quotient Index",
    "GCP": "Google Cloud Platform",
    "ML": "Machine Learning",
    "V3": "Version 3",
    "MP03": "Project 03 in AirTable"
  },
  "data_types": {
    "price": "FLOAT64",
    "volume": "INTEGER",
    "timestamp": "TIMESTAMP",
    "bqx_value": "FLOAT64",
    "prediction": "FLOAT64"
  }
}
```

### Operationalization
```python
# Use semantics for validation
def validate_column_name(col_name):
    semantics = load_json('.bqx_ml_v3/semantics.json')

    # Check if follows naming convention
    if 'lag' in col_name:
        # Should follow pattern: variable_lag_N
        parts = col_name.split('_')
        if len(parts) != 3 or parts[1] != 'lag':
            raise ValueError(f"Invalid lag column name: {col_name}")

    return True

# Generate correct names using semantics
def generate_feature_name(variable, lag_period):
    return f"{variable}_lag_{lag_period}"
```

## 🔗 LAYER 3: ONTOLOGY (ontology.json)

### Purpose
Defines relationships between entities and their hierarchies.

### Structure
```json
{
  "entities": {
    "currency_pair": {
      "parent": "market_data",
      "children": ["price_data", "volume_data", "bqx_values"],
      "relationships": {
        "has_features": ["lag_features", "regime_features", "aggregate_features"],
        "produces_targets": ["bqx_ask", "bqx_bid", "bqx_mid"],
        "belongs_to_model": "pair_specific_model"
      }
    },
    "feature": {
      "parent": "data",
      "types": {
        "price_features": ["open", "high", "low", "close"],
        "volume_features": ["volume"],
        "bqx_features": ["bqx_ask", "bqx_bid", "bqx_mid"],
        "derived_features": ["lags", "aggregations", "regimes"]
      },
      "relationships": {
        "used_by": "model",
        "derived_from": "raw_data",
        "stored_in": "bigquery_table"
      }
    },
    "model": {
      "parent": "system",
      "types": ["linear", "xgboost", "neural_network", "lstm", "gaussian_process"],
      "relationships": {
        "trained_on": "features",
        "predicts": "targets",
        "deployed_to": "vertex_ai_endpoint",
        "specific_to": "currency_pair"
      }
    },
    "pipeline": {
      "parent": "system",
      "stages": ["ingestion", "feature_engineering", "training", "validation", "deployment"],
      "relationships": {
        "processes": "currency_pair",
        "outputs": "model",
        "monitored_by": "airtable"
      }
    }
  },
  "hierarchies": {
    "data_flow": [
      "raw_data",
      "regression_bqx_tables",
      "lag_bqx_tables",
      "regime_bqx_tables",
      "agg_bqx_tables",
      "align_bqx_tables",
      "model_input"
    ],
    "model_hierarchy": [
      "base_models",
      "ensemble_model",
      "production_endpoint"
    ]
  }
}
```

### Operationalization
```python
# Navigate relationships
def get_feature_types_for_pair(pair):
    ontology = load_json('.bqx_ml_v3/ontology.json')

    feature_types = ontology['entities']['feature']['types']
    features = []

    for category, items in feature_types.items():
        if category == 'bqx_features':  # Paradigm shift - include BQX
            features.extend(items)
        features.extend(items)

    return features

# Validate pipeline stage
def validate_pipeline_stage(current, next):
    ontology = load_json('.bqx_ml_v3/ontology.json')
    flow = ontology['hierarchies']['data_flow']

    current_idx = flow.index(current)
    next_idx = flow.index(next)

    if next_idx != current_idx + 1:
        raise ValueError(f"Invalid transition: {current} -> {next}")
```

## 📜 LAYER 4: PROTOCOLS (protocols.json)

### Purpose
Defines communication standards, data formats, and interaction patterns.

### Structure
```json
{
  "data_protocols": {
    "bigquery": {
      "dataset": "bqx_ml",
      "table_naming": "{type}_bqx_{pair}",
      "types": ["backup", "simple", "regression", "lag", "regime", "agg", "align"],
      "partitioning": "bar_start_time",
      "clustering": ["pair"]
    },
    "storage": {
      "buckets": {
        "features": "gs://bqx-ml-features/",
        "models": "gs://bqx-ml-models/",
        "experiments": "gs://bqx-ml-experiments/"
      },
      "format": "parquet",
      "compression": "snappy"
    },
    "api": {
      "endpoint": "https://us-east1-aiplatform.googleapis.com",
      "authentication": "service_account",
      "timeout": 60,
      "retry": 3
    }
  },
  "naming_conventions": {
    "features": "{variable}_lag_{period}",
    "models": "model_{pair}_{algorithm}_{version}",
    "endpoints": "endpoint_{pair}_{environment}",
    "experiments": "exp_{date}_{pair}_{algorithm}"
  },
  "data_formats": {
    "timestamps": "ISO8601",
    "prices": "DECIMAL(10,5)",
    "predictions": "FLOAT64",
    "ids": "UUID"
  },
  "validation_rules": {
    "price_range": [0, 1000000],
    "volume_range": [0, 1000000000],
    "bqx_range": [-100, 100],
    "lag_range": [1, 60]
  }
}
```

### Operationalization
```python
# Generate compliant table names
def get_table_name(table_type, pair):
    protocols = load_json('.bqx_ml_v3/protocols.json')

    template = protocols['data_protocols']['bigquery']['table_naming']
    valid_types = protocols['data_protocols']['bigquery']['types']

    if table_type not in valid_types:
        raise ValueError(f"Invalid table type: {table_type}")

    return template.format(type=table_type, pair=pair)

# Validate data ranges
def validate_data(df):
    protocols = load_json('.bqx_ml_v3/protocols.json')
    rules = protocols['validation_rules']

    for col, (min_val, max_val) in rules.items():
        if col in df.columns:
            assert df[col].between(min_val, max_val).all()
```

## 🚫 LAYER 5: CONSTRAINTS (constraints.json)

### Purpose
Defines system boundaries, limitations, and invariants that must be maintained.

### Structure
```json
{
  "paradigm_constraints": {
    "bqx_usage": {
      "rule": "BQX can be both features and targets",
      "enforcement": "required",
      "validation": "check_bqx_in_features() == True"
    },
    "window_functions": {
      "rule": "Must use ROWS BETWEEN",
      "prohibited": ["RANGE BETWEEN", "time intervals"],
      "validation": "no TIME or INTERVAL keywords in SQL"
    },
    "model_independence": {
      "rule": "No cross-pair contamination",
      "enforcement": "strict",
      "validation": "each model uses single pair data only"
    }
  },
  "resource_constraints": {
    "budget": {
      "total": 2500,
      "training": 1500,
      "inference": 500,
      "storage": 500,
      "currency": "USD",
      "period": "monthly"
    },
    "compute": {
      "training_gpus": "V100",
      "max_instances": 4,
      "preemptible": true
    },
    "storage": {
      "max_size_gb": 1000,
      "retention_days": 90
    }
  },
  "performance_constraints": {
    "latency": {
      "inference_ms": 100,
      "query_seconds": 2,
      "training_hours": 4
    },
    "accuracy": {
      "min_r2": 0.75,
      "min_sharpe": 1.5,
      "max_drawdown": 0.10,
      "min_win_rate": 0.55
    }
  },
  "data_constraints": {
    "minimum_rows": 100000,
    "date_range": {
      "start": "2020-01-01",
      "end": "2025-10-31"
    },
    "missing_data_threshold": 0.01
  }
}
```

### Operationalization
```python
# Enforce constraints
class ConstraintValidator:
    def __init__(self):
        self.constraints = load_json('.bqx_ml_v3/constraints.json')

    def validate_paradigm(self, features):
        # Check BQX features are included
        bqx_features = [f for f in features if 'bqx' in f]
        if not bqx_features:
            raise ConstraintViolation("BQX must be in features!")

    def validate_performance(self, metrics):
        min_metrics = self.constraints['performance_constraints']['accuracy']

        for metric, threshold in min_metrics.items():
            if metric in metrics:
                if 'min' in metric and metrics[metric] < threshold:
                    raise ConstraintViolation(f"{metric} below threshold")
                if 'max' in metric and metrics[metric] > threshold:
                    raise ConstraintViolation(f"{metric} above threshold")

    def check_budget(self, cost):
        budget = self.constraints['resource_constraints']['budget']['total']
        if cost > budget:
            raise ConstraintViolation(f"Cost ${cost} exceeds budget ${budget}")
```

## 🔄 LAYER 6: WORKFLOWS (workflows.json)

### Purpose
Defines process flows, dependencies, and execution sequences.

### Structure
```json
{
  "workflows": {
    "feature_engineering": {
      "steps": [
        {
          "id": "create_lag_tables",
          "description": "Create lag features including BQX",
          "dependencies": ["regression_tables_exist"],
          "script": "scripts/create_lag_tables.py",
          "parallel": true,
          "validation": "check_lag_tables_exist()"
        },
        {
          "id": "create_regime_tables",
          "description": "Create market regime indicators",
          "dependencies": ["create_lag_tables"],
          "script": "scripts/create_regime_tables.py",
          "parallel": true,
          "validation": "check_regime_tables_exist()"
        },
        {
          "id": "create_agg_tables",
          "description": "Create aggregated features",
          "dependencies": ["create_regime_tables"],
          "script": "scripts/create_agg_tables.py",
          "parallel": true,
          "validation": "check_agg_tables_exist()"
        },
        {
          "id": "create_align_tables",
          "description": "Create final aligned dataset",
          "dependencies": ["create_agg_tables"],
          "script": "scripts/create_align_tables.py",
          "parallel": true,
          "validation": "check_align_tables_exist()"
        }
      ]
    },
    "model_training": {
      "steps": [
        {
          "id": "prepare_data",
          "dependencies": ["feature_engineering"],
          "parallel": false
        },
        {
          "id": "train_base_models",
          "dependencies": ["prepare_data"],
          "parallel": true,
          "models": ["linear", "xgboost", "neural_network", "lstm", "gaussian_process"]
        },
        {
          "id": "create_ensemble",
          "dependencies": ["train_base_models"],
          "parallel": false
        },
        {
          "id": "validate_model",
          "dependencies": ["create_ensemble"],
          "parallel": false,
          "threshold": 0.75
        }
      ]
    },
    "deployment": {
      "steps": [
        {
          "id": "export_model",
          "dependencies": ["model_training"],
          "format": "saved_model"
        },
        {
          "id": "create_endpoint",
          "dependencies": ["export_model"],
          "platform": "vertex_ai"
        },
        {
          "id": "deploy_model",
          "dependencies": ["create_endpoint"],
          "traffic_split": 100
        },
        {
          "id": "test_endpoint",
          "dependencies": ["deploy_model"],
          "validation": "latency < 100ms"
        }
      ]
    }
  },
  "schedules": {
    "feature_update": "0 2 * * *",
    "model_retrain": "0 3 * * 0",
    "performance_check": "*/10 * * * *"
  }
}
```

### Operationalization
```python
# Execute workflows
class WorkflowExecutor:
    def __init__(self):
        self.workflows = load_json('.bqx_ml_v3/workflows.json')

    def execute_workflow(self, workflow_name):
        workflow = self.workflows['workflows'][workflow_name]

        for step in workflow['steps']:
            # Check dependencies
            if not self.check_dependencies(step['dependencies']):
                raise WorkflowError(f"Dependencies not met for {step['id']}")

            # Execute step
            if step.get('parallel'):
                self.execute_parallel(step)
            else:
                self.execute_sequential(step)

            # Validate
            if 'validation' in step:
                assert eval(step['validation'])

    def execute_parallel(self, step):
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor() as executor:
            if 'models' in step:
                futures = [executor.submit(train_model, m)
                          for m in step['models']]
```

## 📊 LAYER 7: METADATA (metadata.json)

### Purpose
Tracks system metadata, versioning, and operational history.

### Structure
```json
{
  "system": {
    "name": "BQX ML V3",
    "version": "3.0.0",
    "created": "2024-11-24",
    "author": "BQX ML Team",
    "repository": "https://github.com/Schmidtlappin/bqx_ml_v3"
  },
  "versioning": {
    "schema_version": "3.0",
    "data_version": "2024.11.24",
    "model_version": "3.0.0-paradigm-shift",
    "api_version": "v3"
  },
  "statistics": {
    "total_pairs": 28,
    "total_features": 360,
    "total_models": 140,
    "total_tables": 112,
    "data_points": 157680000,
    "training_samples": 126144000
  },
  "history": {
    "paradigm_shifts": [
      {
        "date": "2024-11-24",
        "change": "BQX from targets-only to features-and-targets",
        "impact": "major",
        "version": "3.0.0"
      }
    ],
    "deployments": [],
    "incidents": []
  },
  "dependencies": {
    "python": "3.10",
    "tensorflow": "2.13",
    "xgboost": "1.7",
    "pandas": "2.0",
    "google-cloud-bigquery": "3.11",
    "google-cloud-aiplatform": "1.35"
  },
  "monitoring": {
    "dashboards": [
      "https://console.cloud.google.com/monitoring/dashboards/bqx-ml-v3"
    ],
    "alerts": [
      "model_accuracy_degradation",
      "inference_latency_spike",
      "data_pipeline_failure"
    ],
    "logs": [
      "gs://bqx-ml-logs/",
      "bigquery://bqx-ml.logs"
    ]
  }
}
```

### Operationalization
```python
# Track metadata
class MetadataManager:
    def __init__(self):
        self.metadata = load_json('.bqx_ml_v3/metadata.json')

    def update_statistics(self):
        # Update counts
        self.metadata['statistics']['total_tables'] = count_bigquery_tables()
        self.metadata['statistics']['data_points'] = count_data_points()
        self.save()

    def record_deployment(self, model_id, endpoint_id):
        deployment = {
            'timestamp': datetime.now().isoformat(),
            'model_id': model_id,
            'endpoint_id': endpoint_id,
            'version': self.metadata['versioning']['model_version']
        }
        self.metadata['history']['deployments'].append(deployment)
        self.save()

    def check_version_compatibility(self):
        required = self.metadata['dependencies']
        for package, version in required.items():
            installed = get_installed_version(package)
            if not compatible(installed, version):
                raise VersionError(f"{package} version mismatch")
```

## 🚀 CREATING INTELLIGENCE FILES

### Step-by-Step Implementation

```python
# Script to create all intelligence files
import json
import os
from datetime import datetime

def create_intelligence_architecture():
    base_dir = '.bqx_ml_v3'
    os.makedirs(base_dir, exist_ok=True)

    # Create each layer
    layers = {
        'context': create_context(),
        'semantics': create_semantics(),
        'ontology': create_ontology(),
        'protocols': create_protocols(),
        'constraints': create_constraints(),
        'workflows': create_workflows(),
        'metadata': create_metadata()
    }

    for name, content in layers.items():
        path = os.path.join(base_dir, f'{name}.json')
        with open(path, 'w') as f:
            json.dump(content, f, indent=2)
        print(f"Created: {path}")

    # Create index file
    create_index_file(base_dir)

def create_index_file(base_dir):
    index = {
        "intelligence_architecture": {
            "version": "1.0",
            "layers": [
                "context.json - Current system state",
                "semantics.json - Domain vocabulary",
                "ontology.json - Entity relationships",
                "protocols.json - Communication standards",
                "constraints.json - System boundaries",
                "workflows.json - Process definitions",
                "metadata.json - System metadata"
            ],
            "usage": "Load these files to understand and operate the system"
        }
    }

    with open(os.path.join(base_dir, 'index.json'), 'w') as f:
        json.dump(index, f, indent=2)
```

## 🔧 OPERATIONALIZING INTELLIGENCE

### Central Intelligence Manager

```python
class IntelligenceManager:
    def __init__(self, base_dir='.bqx_ml_v3'):
        self.base_dir = base_dir
        self.layers = {}
        self.load_all_layers()

    def load_all_layers(self):
        """Load all 7 intelligence layers"""
        layer_names = ['context', 'semantics', 'ontology', 'protocols',
                      'constraints', 'workflows', 'metadata']

        for name in layer_names:
            path = os.path.join(self.base_dir, f'{name}.json')
            with open(path) as f:
                self.layers[name] = json.load(f)

    def get_current_phase(self):
        """Get active phase from context"""
        return self.layers['context']['active_phase']

    def get_valid_pairs(self):
        """Get currency pairs from context"""
        return self.layers['context']['currency_pairs']

    def validate_table_name(self, table_name):
        """Validate against protocols"""
        pattern = self.layers['protocols']['data_protocols']['bigquery']['table_naming']
        # Validation logic

    def check_constraint(self, constraint_type, value):
        """Check against constraints"""
        constraint = self.layers['constraints'][constraint_type]
        # Validation logic

    def get_workflow(self, workflow_name):
        """Get workflow definition"""
        return self.layers['workflows']['workflows'][workflow_name]

    def update_metadata(self, key, value):
        """Update metadata and persist"""
        self.layers['metadata'][key] = value
        self.save_layer('metadata')

    def save_layer(self, layer_name):
        """Save updated layer back to file"""
        path = os.path.join(self.base_dir, f'{layer_name}.json')
        with open(path, 'w') as f:
            json.dump(self.layers[layer_name], f, indent=2)
```

### Usage in Development

```python
# Initialize intelligence
intel = IntelligenceManager()

# Use for decision making
def create_feature_table(pair):
    # Check constraints
    if pair not in intel.get_valid_pairs():
        raise ValueError(f"Invalid pair: {pair}")

    # Get naming convention
    table_name = intel.validate_table_name(f"lag_bqx_{pair}")

    # Get workflow
    workflow = intel.get_workflow('feature_engineering')

    # Execute with intelligence guidance
    for step in workflow['steps']:
        execute_step(step)
```

## 📝 KEY COACHING POINTS

### For the BQXML CHIEF ENGINEER:

1. **Create First**: Start by creating all 7 JSON files in `.bqx_ml_v3/`
2. **Load Always**: Every script should load relevant intelligence layers
3. **Validate Continuously**: Use constraints and protocols for validation
4. **Update Regularly**: Keep context and metadata current
5. **Follow Workflows**: Use workflow definitions for complex processes
6. **Respect Ontology**: Understand entity relationships
7. **Enforce Constraints**: Never violate defined constraints

### Benefits of Intelligence Architecture:
- **Self-Documenting**: System explains itself
- **Consistency**: Enforces standards automatically
- **Evolution Tracking**: Metadata captures history
- **Error Prevention**: Constraints catch issues early
- **Process Clarity**: Workflows define exact steps
- **Semantic Understanding**: Clear vocabulary prevents confusion

---
**This intelligence architecture makes BQX ML V3 self-aware and self-guiding.**
**Implement all 7 layers before proceeding with development.**