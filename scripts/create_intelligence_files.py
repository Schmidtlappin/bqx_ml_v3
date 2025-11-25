#!/usr/bin/env python3
"""
BQX ML V3 Intelligence Architecture Generator
Creates all 7 intelligence layer JSON files
"""

import json
import os
from datetime import datetime

def create_context():
    """Layer 1: System context and current state"""
    return {
        "version": "3.0.0",
        "environment": "production",
        "timestamp": datetime.now().isoformat(),
        "paradigm": {
            "name": "bqx_features_and_targets",
            "effective_date": "2024-11-24",
            "description": "BQX values serve as both features and targets - paradigm shift"
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
            "include_bqx_features": True,
            "lag_periods": 60,
            "window_type": "ROWS BETWEEN",
            "aggregation_functions": ["mean", "std", "min", "max", "range"]
        },
        "model_configuration": {
            "ensemble_size": 5,
            "algorithms": ["linear", "xgboost", "neural_network", "lstm", "gaussian_process"],
            "training_platform": "vertex_ai",
            "deployment_platform": "vertex_ai_endpoints"
        },
        "airtable": {
            "base_id": "appR3PPnrNkVo48mO",
            "project": "P03",
            "api_key_ref": ".secrets/github_secrets.json"
        }
    }

def create_semantics():
    """Layer 2: Domain vocabulary and terminology"""
    return {
        "terms": {
            "bqx": {
                "definition": "Behavioral Quotient Index - momentum indicator",
                "formula": "idx_mid[T] - AVG(idx_mid[T+1..T+N])",
                "usage": ["feature", "target"],
                "paradigm_shift": "Now used as both features and targets (changed 2024-11-24)"
            },
            "lag": {
                "definition": "Historical value at previous time interval",
                "notation": "variable_lag_N where N is periods back",
                "implementation": "LAG(column, N) OVER (ORDER BY bar_start_time)",
                "range": [1, 60]
            },
            "regime": {
                "definition": "Market state classification",
                "types": ["trend", "volatility", "momentum"],
                "calculation": "Statistical properties over rolling windows"
            },
            "pair": {
                "definition": "Currency pair trading symbol",
                "format": "base_quote lowercase no underscore",
                "examples": ["eurusd", "gbpusd"],
                "count": 28,
                "categories": ["major", "cross", "exotic"]
            },
            "window": {
                "definition": "Data range for calculations",
                "required_type": "ROWS BETWEEN",
                "prohibited": ["RANGE BETWEEN", "INTERVAL"],
                "reason": "Interval-centric not time-centric"
            }
        },
        "abbreviations": {
            "BQX": "Behavioral Quotient Index",
            "GCP": "Google Cloud Platform",
            "ML": "Machine Learning",
            "V3": "Version 3",
            "P03": "Project 03 in AirTable",
            "POC": "Proof of Concept",
            "MVP": "Minimum Viable Product"
        },
        "data_types": {
            "price": "FLOAT64",
            "volume": "INTEGER",
            "timestamp": "TIMESTAMP",
            "bqx_value": "FLOAT64",
            "prediction": "FLOAT64",
            "pair_id": "STRING"
        },
        "sql_patterns": {
            "correct_lag": "LAG({column}, {n}) OVER (ORDER BY bar_start_time)",
            "correct_window": "ROWS BETWEEN {start} PRECEDING AND CURRENT ROW",
            "incorrect_window": "RANGE BETWEEN INTERVAL"
        }
    }

def create_ontology():
    """Layer 3: Entity relationships and hierarchies"""
    return {
        "entities": {
            "currency_pair": {
                "parent": "market_data",
                "children": ["price_data", "volume_data", "bqx_values"],
                "properties": {
                    "symbol": "string",
                    "base_currency": "string",
                    "quote_currency": "string"
                },
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
                    "derived_features": {
                        "lags": "historical values",
                        "aggregations": "statistical summaries",
                        "regimes": "market states"
                    }
                },
                "relationships": {
                    "used_by": "model",
                    "derived_from": "raw_data",
                    "stored_in": "bigquery_table",
                    "validated_by": "constraints"
                }
            },
            "model": {
                "parent": "system",
                "types": {
                    "linear": "baseline",
                    "xgboost": "tree_based",
                    "neural_network": "deep_learning",
                    "lstm": "sequence_model",
                    "gaussian_process": "probabilistic"
                },
                "relationships": {
                    "trained_on": "features",
                    "predicts": "targets",
                    "deployed_to": "vertex_ai_endpoint",
                    "specific_to": "currency_pair",
                    "part_of": "ensemble"
                }
            },
            "pipeline": {
                "parent": "system",
                "stages": ["ingestion", "feature_engineering", "training", "validation", "deployment"],
                "relationships": {
                    "processes": "currency_pair",
                    "outputs": "model",
                    "monitored_by": "airtable",
                    "orchestrated_by": "cloud_composer"
                }
            }
        },
        "hierarchies": {
            "data_flow": [
                "raw_data",
                "backup_bqx_tables",
                "simple_bqx_tables",
                "regression_bqx_tables",
                "lag_bqx_tables",
                "regime_bqx_tables",
                "agg_bqx_tables",
                "align_bqx_tables",
                "model_input",
                "predictions",
                "trading_signals"
            ],
            "model_hierarchy": [
                "base_models",
                "ensemble_model",
                "production_endpoint"
            ],
            "organizational": [
                "system",
                "project",
                "phase",
                "task",
                "subtask"
            ]
        }
    }

def create_protocols():
    """Layer 4: Communication standards and formats"""
    return {
        "data_protocols": {
            "bigquery": {
                "project": "bqx-ml",
                "dataset": "bqx_ml",
                "table_naming": "{type}_bqx_{pair}",
                "types": ["backup", "simple", "regression", "lag", "regime", "agg", "align"],
                "partitioning": {
                    "field": "bar_start_time",
                    "type": "TIMESTAMP"
                },
                "clustering": ["pair"],
                "location": "us-east1"
            },
            "storage": {
                "buckets": {
                    "features": "gs://bqx-ml-features/",
                    "models": "gs://bqx-ml-models/",
                    "experiments": "gs://bqx-ml-experiments/",
                    "checkpoints": "gs://bqx-ml-checkpoints/"
                },
                "format": "parquet",
                "compression": "snappy",
                "naming": "{type}/{pair}/{timestamp}_{version}.parquet"
            },
            "api": {
                "base_url": "https://us-east1-aiplatform.googleapis.com",
                "authentication": "service_account",
                "timeout_seconds": 60,
                "retry_count": 3,
                "retry_backoff": "exponential"
            }
        },
        "naming_conventions": {
            "features": "{variable}_lag_{period}",
            "models": "model_{pair}_{algorithm}_{version}",
            "endpoints": "endpoint_{pair}_{environment}",
            "experiments": "exp_{date}_{pair}_{algorithm}",
            "checkpoints": "ckpt_{epoch}_{pair}_{algorithm}"
        },
        "data_formats": {
            "timestamps": "ISO8601",
            "dates": "YYYY-MM-DD",
            "prices": "DECIMAL(10,5)",
            "volumes": "BIGINT",
            "predictions": "FLOAT64",
            "ids": "UUID4"
        },
        "validation_rules": {
            "price_range": {"min": 0, "max": 1000000},
            "volume_range": {"min": 0, "max": 1000000000},
            "bqx_range": {"min": -100, "max": 100},
            "lag_range": {"min": 1, "max": 60},
            "probability_range": {"min": 0, "max": 1}
        }
    }

def create_constraints():
    """Layer 5: System boundaries and limitations"""
    return {
        "paradigm_constraints": {
            "bqx_usage": {
                "rule": "BQX must be used as both features and targets",
                "enforcement": "required",
                "validation": "assert 'bqx' in feature_columns",
                "since": "2024-11-24"
            },
            "window_functions": {
                "rule": "Must use ROWS BETWEEN exclusively",
                "prohibited": ["RANGE BETWEEN", "TIME", "INTERVAL"],
                "validation": "sql_query.count('ROWS BETWEEN') > 0",
                "reason": "Interval-centric architecture"
            },
            "model_independence": {
                "rule": "No cross-pair contamination allowed",
                "enforcement": "strict",
                "validation": "data.pair.nunique() == 1",
                "implementation": "Separate models per pair"
            },
            "platform": {
                "rule": "GCP services only",
                "prohibited": ["AWS", "Azure", "on-premise"],
                "allowed": ["BigQuery", "Vertex AI", "Cloud Storage", "Cloud Composer"],
                "validation": "no AWS references in code"
            }
        },
        "resource_constraints": {
            "budget": {
                "total": 2500,
                "breakdown": {
                    "training": 1500,
                    "inference": 500,
                    "storage": 300,
                    "networking": 200
                },
                "currency": "USD",
                "period": "monthly"
            },
            "compute": {
                "training": {
                    "gpu_type": "V100",
                    "max_instances": 4,
                    "preemptible": True,
                    "max_hours": 100
                },
                "inference": {
                    "cpu_type": "n1-standard-4",
                    "min_replicas": 1,
                    "max_replicas": 5,
                    "autoscaling": True
                }
            },
            "storage": {
                "bigquery_gb": 500,
                "cloud_storage_gb": 1000,
                "retention_days": 90,
                "backup_copies": 2
            }
        },
        "performance_constraints": {
            "latency": {
                "inference_p50_ms": 50,
                "inference_p99_ms": 100,
                "query_seconds": 2,
                "training_hours": 4
            },
            "accuracy": {
                "min_r2": 0.75,
                "min_sharpe": 1.5,
                "max_drawdown": 0.10,
                "min_win_rate": 0.55
            },
            "availability": {
                "uptime_percent": 99.9,
                "max_downtime_minutes": 43
            }
        },
        "data_constraints": {
            "minimum_rows_per_pair": 100000,
            "date_range": {
                "train_start": "2020-01-01",
                "train_end": "2024-06-30",
                "valid_start": "2024-07-01",
                "valid_end": "2024-12-31",
                "test_start": "2025-01-01",
                "test_end": "2025-10-31"
            },
            "missing_data_threshold": 0.01,
            "outlier_threshold": 5.0
        }
    }

def create_workflows():
    """Layer 6: Process definitions and dependencies"""
    return {
        "workflows": {
            "feature_engineering": {
                "description": "Create all feature tables with BQX included",
                "steps": [
                    {
                        "id": "create_lag_tables",
                        "description": "Create lag features including BQX lags",
                        "dependencies": ["regression_tables_exist"],
                        "script": "scripts/gcp/create_lag_tables.py",
                        "parallel": True,
                        "timeout_minutes": 30,
                        "validation": "SELECT COUNT(*) FROM `bqx-ml.bqx_ml.lag_bqx_{pair}`"
                    },
                    {
                        "id": "create_regime_tables",
                        "description": "Create market regime indicators",
                        "dependencies": ["create_lag_tables"],
                        "script": "scripts/gcp/create_regime_tables.py",
                        "parallel": True,
                        "timeout_minutes": 20,
                        "validation": "SELECT COUNT(*) FROM `bqx-ml.bqx_ml.regime_bqx_{pair}`"
                    },
                    {
                        "id": "create_agg_tables",
                        "description": "Create aggregated features",
                        "dependencies": ["create_regime_tables"],
                        "script": "scripts/gcp/create_agg_tables.py",
                        "parallel": True,
                        "timeout_minutes": 25,
                        "validation": "SELECT COUNT(*) FROM `bqx-ml.bqx_ml.agg_bqx_{pair}`"
                    },
                    {
                        "id": "create_align_tables",
                        "description": "Create final aligned dataset",
                        "dependencies": ["create_agg_tables"],
                        "script": "scripts/gcp/create_align_tables.py",
                        "parallel": True,
                        "timeout_minutes": 30,
                        "validation": "SELECT COUNT(*) FROM `bqx-ml.bqx_ml.align_bqx_{pair}`"
                    }
                ],
                "on_failure": "rollback",
                "notification": "airtable_update"
            },
            "model_training": {
                "description": "Train ensemble models with BQX features",
                "steps": [
                    {
                        "id": "prepare_data",
                        "dependencies": ["feature_engineering_complete"],
                        "parallel": False,
                        "script": "scripts/gcp/prepare_training_data.py"
                    },
                    {
                        "id": "train_base_models",
                        "dependencies": ["prepare_data"],
                        "parallel": True,
                        "models": {
                            "linear": "sklearn.linear_model.LinearRegression",
                            "xgboost": "xgboost.XGBRegressor",
                            "neural_network": "tensorflow.keras.Sequential",
                            "lstm": "tensorflow.keras.layers.LSTM",
                            "gaussian_process": "sklearn.gaussian_process.GaussianProcessRegressor"
                        },
                        "script": "scripts/gcp/train_models.py"
                    },
                    {
                        "id": "create_ensemble",
                        "dependencies": ["train_base_models"],
                        "parallel": False,
                        "method": "weighted_average",
                        "script": "scripts/gcp/create_ensemble.py"
                    },
                    {
                        "id": "validate_model",
                        "dependencies": ["create_ensemble"],
                        "parallel": False,
                        "metrics": ["r2", "sharpe", "drawdown", "win_rate"],
                        "threshold": 0.75,
                        "script": "scripts/gcp/validate_model.py"
                    }
                ]
            },
            "deployment": {
                "description": "Deploy models to Vertex AI endpoints",
                "steps": [
                    {
                        "id": "export_model",
                        "dependencies": ["model_training_complete"],
                        "format": "saved_model",
                        "location": "gs://bqx-ml-models/"
                    },
                    {
                        "id": "create_endpoint",
                        "dependencies": ["export_model"],
                        "platform": "vertex_ai",
                        "region": "us-east1"
                    },
                    {
                        "id": "deploy_model",
                        "dependencies": ["create_endpoint"],
                        "traffic_split": 100,
                        "min_replicas": 1,
                        "max_replicas": 5
                    },
                    {
                        "id": "test_endpoint",
                        "dependencies": ["deploy_model"],
                        "tests": ["latency", "accuracy", "throughput"],
                        "validation": "latency_ms < 100"
                    }
                ]
            }
        },
        "schedules": {
            "feature_update": {
                "cron": "0 2 * * *",
                "description": "Daily feature table update"
            },
            "model_retrain": {
                "cron": "0 3 * * 0",
                "description": "Weekly model retraining"
            },
            "performance_check": {
                "cron": "*/10 * * * *",
                "description": "Performance monitoring every 10 minutes"
            }
        },
        "error_handling": {
            "retry_policy": {
                "max_attempts": 3,
                "backoff": "exponential",
                "initial_delay_seconds": 60
            },
            "failure_actions": ["log", "alert", "rollback"],
            "notification_channels": ["email", "airtable", "slack"]
        }
    }

def create_metadata():
    """Layer 7: System metadata and versioning"""
    return {
        "system": {
            "name": "BQX ML V3",
            "version": "3.0.0",
            "created": "2024-11-24",
            "last_updated": datetime.now().isoformat(),
            "author": "BQX ML Team",
            "repository": "https://github.com/Schmidtlappin/bqx_ml_v3",
            "documentation": "/home/micha/bqx_ml_v3/docs/"
        },
        "versioning": {
            "schema_version": "3.0",
            "data_version": "2024.11.24",
            "model_version": "3.0.0-paradigm-shift",
            "api_version": "v3",
            "intelligence_version": "1.0"
        },
        "statistics": {
            "total_pairs": 28,
            "features_per_pair": 360,
            "models_per_pair": 5,
            "total_models": 140,
            "total_tables": 112,
            "table_types": 4,
            "estimated_data_points": 157680000,
            "estimated_training_samples": 126144000
        },
        "history": {
            "paradigm_shifts": [
                {
                    "date": "2024-11-24",
                    "change": "BQX from targets-only to features-and-targets",
                    "impact": "major",
                    "version": "3.0.0",
                    "reason": "Autoregressive capability improvement"
                }
            ],
            "deployments": [],
            "incidents": [],
            "milestones": [
                {
                    "date": "2024-11-24",
                    "event": "V3 architecture finalized",
                    "phase": "P03.2"
                }
            ]
        },
        "dependencies": {
            "python": "3.10",
            "tensorflow": "2.13",
            "xgboost": "1.7",
            "pandas": "2.0",
            "numpy": "1.24",
            "scikit-learn": "1.3",
            "google-cloud-bigquery": "3.11",
            "google-cloud-aiplatform": "1.35",
            "google-cloud-storage": "2.10"
        },
        "monitoring": {
            "dashboards": {
                "main": "https://console.cloud.google.com/monitoring/dashboards/bqx-ml-v3",
                "models": "https://console.cloud.google.com/vertex-ai/models",
                "data": "https://console.cloud.google.com/bigquery"
            },
            "alerts": [
                {
                    "name": "model_accuracy_degradation",
                    "threshold": 0.7,
                    "metric": "r2_score"
                },
                {
                    "name": "inference_latency_spike",
                    "threshold": 100,
                    "metric": "latency_ms"
                },
                {
                    "name": "data_pipeline_failure",
                    "threshold": 1,
                    "metric": "failed_runs"
                }
            ],
            "logs": {
                "application": "gs://bqx-ml-logs/app/",
                "training": "gs://bqx-ml-logs/training/",
                "inference": "gs://bqx-ml-logs/inference/",
                "bigquery": "bigquery://bqx-ml.logs"
            }
        },
        "contacts": {
            "technical_lead": "BQXML CHIEF ENGINEER",
            "project_manager": "Michael",
            "repository_owner": "Schmidtlappin"
        }
    }

def create_index():
    """Create index file for intelligence architecture"""
    return {
        "intelligence_architecture": {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "purpose": "Self-documenting system intelligence for BQX ML V3",
            "layers": {
                "context": "Current system state and configuration",
                "semantics": "Domain vocabulary and terminology",
                "ontology": "Entity relationships and hierarchies",
                "protocols": "Communication standards and formats",
                "constraints": "System boundaries and limitations",
                "workflows": "Process definitions and dependencies",
                "metadata": "System metadata and versioning"
            },
            "usage": {
                "initialization": "Load all layers on system start",
                "validation": "Check constraints before operations",
                "navigation": "Use ontology for relationships",
                "execution": "Follow workflow definitions",
                "communication": "Apply protocol standards"
            },
            "files": [
                "context.json",
                "semantics.json",
                "ontology.json",
                "protocols.json",
                "constraints.json",
                "workflows.json",
                "metadata.json",
                "index.json"
            ]
        }
    }

def main():
    """Create all intelligence files"""
    base_dir = '.bqx_ml_v3'

    # Create directory if not exists
    os.makedirs(base_dir, exist_ok=True)
    print(f"Creating intelligence architecture in {base_dir}/")

    # Create each layer
    layers = {
        'context': create_context(),
        'semantics': create_semantics(),
        'ontology': create_ontology(),
        'protocols': create_protocols(),
        'constraints': create_constraints(),
        'workflows': create_workflows(),
        'metadata': create_metadata(),
        'index': create_index()
    }

    # Write each file
    for name, content in layers.items():
        path = os.path.join(base_dir, f'{name}.json')
        with open(path, 'w') as f:
            json.dump(content, f, indent=2)
        print(f"✓ Created: {path}")

    print("\n✅ Intelligence architecture created successfully!")
    print(f"📁 Location: {os.path.abspath(base_dir)}")
    print("📝 Next step: Review and customize each layer for your specific needs")

if __name__ == "__main__":
    main()