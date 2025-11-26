#!/usr/bin/env python3
"""
GCP ML COVERAGE AUDIT
Verifies that BQX ML V3 project plan achieves 100% coverage of the GCP ML process.
Checks against Google Cloud ML best practices and required components.
"""

import os
import json
from datetime import datetime
from collections import defaultdict
from pyairtable import Api

# AirTable configuration
BASE_ID = os.getenv('AIRTABLE_BASE_ID')
API_KEY = os.getenv('AIRTABLE_API_KEY')

# Load from secrets if not in environment
if not API_KEY or not BASE_ID:
    try:
        with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
            secrets = json.load(f)
            API_KEY = API_KEY or secrets['secrets']['AIRTABLE_API_KEY']['value']
            BASE_ID = BASE_ID or secrets['secrets']['AIRTABLE_BASE_ID']['value']
    except:
        print("Warning: Could not load AirTable credentials")

# Initialize API
api = Api(API_KEY)
base = api.base(BASE_ID)
phases_table = base.table('Phases')
stages_table = base.table('Stages')
tasks_table = base.table('Tasks')

class GCPMLCoverageAudit:
    """Comprehensive GCP ML process coverage audit."""

    def __init__(self):
        self.tasks = []
        self.stages = []
        self.phases = []
        self.coverage_gaps = []
        self.coverage_scores = {}

    def load_data(self):
        """Load all data from AirTable."""
        print("📥 Loading AirTable data...")
        self.phases = phases_table.all()
        self.stages = stages_table.all()
        self.tasks = tasks_table.all()
        print(f"  Loaded: {len(self.phases)} phases, {len(self.stages)} stages, {len(self.tasks)} tasks")

    def get_all_content(self):
        """Get all text content for analysis."""
        content = []
        for task in self.tasks:
            fields = task['fields']
            content.append(f"{fields.get('description', '')} {fields.get('notes', '')} {fields.get('artifacts', '')}")
        for stage in self.stages:
            fields = stage['fields']
            content.append(f"{fields.get('name', '')} {fields.get('description', '')}")
        return ' '.join(content).lower()

    def audit_data_pipeline(self):
        """Audit data ingestion and pipeline coverage."""
        print("\n📊 Auditing Data Pipeline Coverage...")

        required_components = {
            'Data Ingestion': {
                'keywords': ['pub/sub', 'pubsub', 'streaming', 'batch', 'dataflow', 'data ingestion'],
                'critical': True
            },
            'Data Validation': {
                'keywords': ['tensorflow data validation', 'tfdv', 'data validation', 'schema', 'anomaly detection'],
                'critical': True
            },
            'Data Storage': {
                'keywords': ['bigquery', 'cloud storage', 'gcs', 'data warehouse'],
                'critical': True
            },
            'Data Versioning': {
                'keywords': ['data version', 'dataset version', 'lineage', 'data catalog'],
                'critical': False
            },
            'Data Quality Monitoring': {
                'keywords': ['data quality', 'data drift', 'distribution shift', 'statistical monitoring'],
                'critical': True
            }
        }

        content = self.get_all_content()
        coverage = {}
        gaps = []

        for component, details in required_components.items():
            found = any(keyword in content for keyword in details['keywords'])
            coverage[component] = found

            if not found and details['critical']:
                gaps.append(f"CRITICAL: Missing {component}")
            elif not found:
                gaps.append(f"Missing {component}")

        return coverage, gaps

    def audit_feature_engineering(self):
        """Audit feature engineering coverage."""
        print("📊 Auditing Feature Engineering Coverage...")

        required_components = {
            'Feature Store': {
                'keywords': ['feature store', 'vertex ai feature store', 'feast', 'feature management'],
                'critical': False
            },
            'Feature Transformation': {
                'keywords': ['preprocessing', 'transformation', 'scaling', 'normalization', 'encoding'],
                'critical': True
            },
            'Feature Selection': {
                'keywords': ['feature selection', 'feature importance', 'correlation', 'mutual information'],
                'critical': False
            },
            'Feature Validation': {
                'keywords': ['feature validation', 'feature schema', 'feature drift'],
                'critical': False
            },
            'LAG Features': {
                'keywords': ['lag', 'lag features', 'historical features', 'lagged values'],
                'critical': True
            },
            'Aggregation Features': {
                'keywords': ['aggregation', 'rolling', 'window functions', 'moving average'],
                'critical': True
            }
        }

        content = self.get_all_content()
        coverage = {}
        gaps = []

        for component, details in required_components.items():
            found = any(keyword in content for keyword in details['keywords'])
            coverage[component] = found

            if not found and details['critical']:
                gaps.append(f"CRITICAL: Missing {component}")
            elif not found:
                gaps.append(f"Missing {component}")

        return coverage, gaps

    def audit_ml_training(self):
        """Audit ML training and experimentation coverage."""
        print("📊 Auditing ML Training Coverage...")

        required_components = {
            'Model Training': {
                'keywords': ['training', 'model training', 'fit', 'train'],
                'critical': True
            },
            'Hyperparameter Tuning': {
                'keywords': ['hyperparameter', 'tuning', 'vizier', 'optimization', 'grid search', 'bayesian'],
                'critical': True
            },
            'Cross Validation': {
                'keywords': ['cross validation', 'cv', 'k-fold', 'time series split'],
                'critical': True
            },
            'Experiment Tracking': {
                'keywords': ['mlflow', 'experiment tracking', 'vertex ai experiments', 'tensorboard'],
                'critical': False
            },
            'Model Registry': {
                'keywords': ['model registry', 'model versioning', 'model management'],
                'critical': True
            },
            'Distributed Training': {
                'keywords': ['distributed', 'parallel training', 'multi-gpu', 'cluster'],
                'critical': False
            }
        }

        content = self.get_all_content()
        coverage = {}
        gaps = []

        for component, details in required_components.items():
            found = any(keyword in content for keyword in details['keywords'])
            coverage[component] = found

            if not found and details['critical']:
                gaps.append(f"CRITICAL: Missing {component}")
            elif not found:
                gaps.append(f"Missing {component}")

        return coverage, gaps

    def audit_model_evaluation(self):
        """Audit model evaluation and testing coverage."""
        print("📊 Auditing Model Evaluation Coverage...")

        required_components = {
            'Performance Metrics': {
                'keywords': ['r2', 'rmse', 'mae', 'accuracy', 'precision', 'recall', 'metrics'],
                'critical': True
            },
            'A/B Testing': {
                'keywords': ['a/b test', 'split test', 'experimentation', 'control group'],
                'critical': False
            },
            'Model Comparison': {
                'keywords': ['model comparison', 'baseline', 'benchmark', 'champion challenger'],
                'critical': False
            },
            'Bias Detection': {
                'keywords': ['bias', 'fairness', 'what-if tool', 'model cards'],
                'critical': False
            },
            'Explainability': {
                'keywords': ['explainability', 'interpretability', 'shap', 'lime', 'xai'],
                'critical': False
            }
        }

        content = self.get_all_content()
        coverage = {}
        gaps = []

        for component, details in required_components.items():
            found = any(keyword in content for keyword in details['keywords'])
            coverage[component] = found

            if not found and details['critical']:
                gaps.append(f"CRITICAL: Missing {component}")
            elif not found:
                gaps.append(f"Missing {component}")

        return coverage, gaps

    def audit_deployment(self):
        """Audit deployment and serving coverage."""
        print("📊 Auditing Deployment Coverage...")

        required_components = {
            'Online Prediction': {
                'keywords': ['endpoint', 'online prediction', 'real-time', 'serving', 'rest api'],
                'critical': True
            },
            'Batch Prediction': {
                'keywords': ['batch prediction', 'batch inference', 'batch scoring'],
                'critical': True
            },
            'Model Serving': {
                'keywords': ['vertex ai', 'model serving', 'deployment', 'production'],
                'critical': True
            },
            'Auto-scaling': {
                'keywords': ['autoscaling', 'auto-scaling', 'scaling', 'replicas'],
                'critical': False
            },
            'Edge Deployment': {
                'keywords': ['edge', 'iot', 'tensorflow lite', 'mobile'],
                'critical': False
            },
            'Multi-Model Serving': {
                'keywords': ['multi-model', 'model ensemble', 'model routing'],
                'critical': False
            }
        }

        content = self.get_all_content()
        coverage = {}
        gaps = []

        for component, details in required_components.items():
            found = any(keyword in content for keyword in details['keywords'])
            coverage[component] = found

            if not found and details['critical']:
                gaps.append(f"CRITICAL: Missing {component}")
            elif not found:
                gaps.append(f"Missing {component}")

        return coverage, gaps

    def audit_monitoring(self):
        """Audit monitoring and operations coverage."""
        print("📊 Auditing Monitoring & Operations Coverage...")

        required_components = {
            'Model Monitoring': {
                'keywords': ['monitoring', 'model monitoring', 'performance tracking'],
                'critical': True
            },
            'Alerting': {
                'keywords': ['alert', 'alerting', 'notification', 'threshold'],
                'critical': True
            },
            'Logging': {
                'keywords': ['logging', 'cloud logging', 'log', 'audit'],
                'critical': True
            },
            'Data Drift Detection': {
                'keywords': ['data drift', 'distribution shift', 'concept drift', 'covariate shift'],
                'critical': True
            },
            'Model Performance Degradation': {
                'keywords': ['performance degradation', 'model decay', 'retraining trigger'],
                'critical': True
            },
            'SLA Monitoring': {
                'keywords': ['sla', 'service level', 'latency', 'availability', 'uptime'],
                'critical': False
            }
        }

        content = self.get_all_content()
        coverage = {}
        gaps = []

        for component, details in required_components.items():
            found = any(keyword in content for keyword in details['keywords'])
            coverage[component] = found

            if not found and details['critical']:
                gaps.append(f"CRITICAL: Missing {component}")
            elif not found:
                gaps.append(f"Missing {component}")

        return coverage, gaps

    def audit_mlops(self):
        """Audit MLOps and automation coverage."""
        print("📊 Auditing MLOps Coverage...")

        required_components = {
            'CI/CD Pipeline': {
                'keywords': ['ci/cd', 'continuous integration', 'continuous deployment', 'cloud build'],
                'critical': True
            },
            'Automated Retraining': {
                'keywords': ['retraining', 'automated retraining', 'scheduled training', 'pipeline trigger'],
                'critical': True
            },
            'Model Versioning': {
                'keywords': ['model version', 'versioning', 'git', 'model registry'],
                'critical': True
            },
            'Infrastructure as Code': {
                'keywords': ['terraform', 'iac', 'infrastructure as code', 'deployment manager'],
                'critical': False
            },
            'Kubeflow Pipelines': {
                'keywords': ['kubeflow', 'vertex ai pipelines', 'pipeline', 'orchestration'],
                'critical': False
            },
            'Workflow Orchestration': {
                'keywords': ['airflow', 'composer', 'orchestration', 'workflow', 'dag'],
                'critical': False
            }
        }

        content = self.get_all_content()
        coverage = {}
        gaps = []

        for component, details in required_components.items():
            found = any(keyword in content for keyword in details['keywords'])
            coverage[component] = found

            if not found and details['critical']:
                gaps.append(f"CRITICAL: Missing {component}")
            elif not found:
                gaps.append(f"Missing {component}")

        return coverage, gaps

    def audit_security_compliance(self):
        """Audit security and compliance coverage."""
        print("📊 Auditing Security & Compliance Coverage...")

        required_components = {
            'Data Encryption': {
                'keywords': ['encryption', 'encrypt', 'cmek', 'kms'],
                'critical': False
            },
            'Access Control': {
                'keywords': ['iam', 'access control', 'permissions', 'rbac'],
                'critical': False
            },
            'Audit Logging': {
                'keywords': ['audit log', 'audit trail', 'compliance log'],
                'critical': False
            },
            'Data Privacy': {
                'keywords': ['privacy', 'pii', 'gdpr', 'data protection'],
                'critical': False
            },
            'Model Governance': {
                'keywords': ['governance', 'approval', 'review process', 'model risk'],
                'critical': False
            },
            'Backup and Recovery': {
                'keywords': ['backup', 'disaster recovery', 'restore', 'retention'],
                'critical': False
            }
        }

        content = self.get_all_content()
        coverage = {}
        gaps = []

        for component, details in required_components.items():
            found = any(keyword in content for keyword in details['keywords'])
            coverage[component] = found

            if not found and details['critical']:
                gaps.append(f"CRITICAL: Missing {component}")
            elif not found:
                gaps.append(f"Missing {component}")

        return coverage, gaps

    def audit_cost_optimization(self):
        """Audit cost optimization coverage."""
        print("📊 Auditing Cost Optimization Coverage...")

        required_components = {
            'Resource Optimization': {
                'keywords': ['cost optimization', 'resource optimization', 'preemptible', 'spot instances'],
                'critical': False
            },
            'Cost Monitoring': {
                'keywords': ['cost monitoring', 'budget', 'billing', 'cost tracking'],
                'critical': False
            },
            'Efficient Storage': {
                'keywords': ['storage optimization', 'data lifecycle', 'archival', 'compression'],
                'critical': False
            },
            'Compute Optimization': {
                'keywords': ['gpu optimization', 'tpu', 'batch size', 'resource allocation'],
                'critical': False
            }
        }

        content = self.get_all_content()
        coverage = {}
        gaps = []

        for component, details in required_components.items():
            found = any(keyword in content for keyword in details['keywords'])
            coverage[component] = found

            if not found and details['critical']:
                gaps.append(f"CRITICAL: Missing {component}")
            elif not found:
                gaps.append(f"Missing {component}")

        return coverage, gaps

    def generate_comprehensive_report(self):
        """Generate comprehensive GCP ML coverage report."""
        print("\n" + "="*80)
        print("GCP ML COVERAGE AUDIT REPORT")
        print("="*80)

        # Run all audits
        audits = {
            'Data Pipeline': self.audit_data_pipeline(),
            'Feature Engineering': self.audit_feature_engineering(),
            'ML Training': self.audit_ml_training(),
            'Model Evaluation': self.audit_model_evaluation(),
            'Deployment': self.audit_deployment(),
            'Monitoring & Operations': self.audit_monitoring(),
            'MLOps': self.audit_mlops(),
            'Security & Compliance': self.audit_security_compliance(),
            'Cost Optimization': self.audit_cost_optimization()
        }

        # Calculate overall coverage
        total_components = 0
        covered_components = 0
        critical_gaps = []
        all_gaps = []

        for category, (coverage, gaps) in audits.items():
            total_components += len(coverage)
            covered_components += sum(1 for v in coverage.values() if v)

            for gap in gaps:
                if gap.startswith("CRITICAL"):
                    critical_gaps.append(f"{category}: {gap}")
                all_gaps.append(f"{category}: {gap}")

        coverage_percentage = (covered_components / total_components * 100) if total_components > 0 else 0

        # Generate report
        report = []
        report.append(f"\nDate: {datetime.now().isoformat()}")
        report.append(f"Overall GCP ML Coverage: {coverage_percentage:.1f}%")
        report.append(f"Components Covered: {covered_components}/{total_components}")
        report.append(f"Critical Gaps: {len(critical_gaps)}")
        report.append(f"Total Gaps: {len(all_gaps)}")

        # Detailed breakdown
        report.append("\n" + "="*80)
        report.append("DETAILED COVERAGE BY CATEGORY")
        report.append("="*80)

        for category, (coverage, gaps) in audits.items():
            category_covered = sum(1 for v in coverage.values() if v)
            category_total = len(coverage)
            category_percentage = (category_covered / category_total * 100) if category_total > 0 else 0

            report.append(f"\n📊 {category}: {category_percentage:.1f}% ({category_covered}/{category_total})")
            report.append("-"*40)

            # Show covered components
            covered = [k for k, v in coverage.items() if v]
            if covered:
                report.append("✅ Covered:")
                for comp in covered:
                    report.append(f"  • {comp}")

            # Show missing components
            missing = [k for k, v in coverage.items() if not v]
            if missing:
                report.append("❌ Missing:")
                for comp in missing:
                    report.append(f"  • {comp}")

        # Critical gaps summary
        if critical_gaps:
            report.append("\n" + "="*80)
            report.append("🚨 CRITICAL GAPS REQUIRING IMMEDIATE ATTENTION")
            report.append("="*80)
            for gap in critical_gaps:
                report.append(f"  • {gap}")

        # Recommendations
        report.append("\n" + "="*80)
        report.append("📝 RECOMMENDATIONS")
        report.append("="*80)

        if coverage_percentage == 100:
            report.append("✅ EXCELLENT! 100% GCP ML process coverage achieved")
        elif coverage_percentage >= 90:
            report.append("✅ Good coverage. Address remaining gaps for completeness")
        elif coverage_percentage >= 80:
            report.append("⚠️  Adequate coverage. Several important components missing")
        else:
            report.append("❌ Significant gaps in GCP ML coverage. Immediate action required")

        # Save results
        self.coverage_scores = {
            'overall': coverage_percentage,
            'covered': covered_components,
            'total': total_components,
            'critical_gaps': len(critical_gaps),
            'all_gaps': len(all_gaps)
        }

        self.coverage_gaps = all_gaps

        return "\n".join(report)

    def run_audit(self):
        """Run complete GCP ML coverage audit."""
        self.load_data()
        report = self.generate_comprehensive_report()

        print(report)

        # Save report
        report_file = f"/home/micha/bqx_ml_v3/docs/GCP_ML_COVERAGE_AUDIT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write("# GCP ML Coverage Audit Report\n\n")
            f.write("```\n")
            f.write(report)
            f.write("\n```\n\n")
            f.write("## Gap Summary\n\n")
            if self.coverage_gaps:
                f.write("### Components Requiring Implementation:\n\n")
                for gap in self.coverage_gaps:
                    f.write(f"- {gap}\n")
            else:
                f.write("✅ No gaps identified - 100% coverage achieved\n")

        print(f"\n📄 Report saved to: {report_file}")

        return self.coverage_scores, self.coverage_gaps

def main():
    """Main entry point."""
    auditor = GCPMLCoverageAudit()
    scores, gaps = auditor.run_audit()

    if scores['overall'] == 100:
        print("\n✅ SUCCESS! 100% GCP ML coverage confirmed")
        return 0
    else:
        print(f"\n⚠️  Coverage at {scores['overall']:.1f}% - {len(gaps)} gaps identified")
        return 1

if __name__ == "__main__":
    exit(main())