#!/usr/bin/env python3
"""
Populate Stage Artifacts and Source File Paths

This script adds:
1. Anticipated artifacts to Stages.artifacts field based on stage type
2. Source file paths to Stages.source field for build agent context

Artifacts are determined by stage type:
- Data stages → BigQuery tables, CSV files
- Model stages → Trained models (.pkl, .h5), checkpoints
- Feature stages → Feature matrices, engineered features
- Infrastructure stages → Config files, Docker images, Terraform state
- Testing stages → Test reports, validation metrics
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

def determine_stage_type(stage_name: str, stage_description: str) -> str:
    """Determine the type of stage based on name and description"""
    name_lower = stage_name.lower()
    desc_lower = stage_description.lower() if stage_description else ""

    # Check for specific keywords
    if any(kw in name_lower for kw in ['data', 'ingest', 'extract', 'load', 'query']):
        return 'data'
    elif any(kw in name_lower for kw in ['model', 'train', 'ensemble', 'algorithm']):
        return 'model'
    elif any(kw in name_lower for kw in ['feature', 'engineer', 'bqx', 'calculation']):
        return 'feature'
    elif any(kw in name_lower for kw in ['deploy', 'infrastructure', 'vertex', 'docker', 'terraform']):
        return 'infrastructure'
    elif any(kw in name_lower for kw in ['test', 'validate', 'verify', 'assessment']):
        return 'testing'
    elif any(kw in name_lower for kw in ['monitor', 'alert', 'observe']):
        return 'monitoring'
    elif any(kw in name_lower for kw in ['security', 'iam', 'auth', 'encryption']):
        return 'security'
    elif any(kw in name_lower for kw in ['api', 'endpoint', 'service', 'serving']):
        return 'api'
    elif any(kw in name_lower for kw in ['baseline', 'metric', 'benchmark']):
        return 'baseline'
    elif any(kw in name_lower for kw in ['document', 'report', 'intelligence']):
        return 'documentation'
    else:
        return 'general'

def generate_artifacts(stage_id: str, stage_name: str, stage_type: str) -> List[str]:
    """Generate anticipated artifacts based on stage type"""

    # Extract phase and stage numbers for naming
    match = re.match(r'MP(\d{2})\.P(\d{2})\.S(\d{2})', stage_id)
    if match:
        plan_num = match.group(1)
        phase_num = match.group(2)
        stage_num = match.group(3)
        prefix = f"mp{plan_num}_p{phase_num}_s{stage_num}"
    else:
        prefix = "output"

    artifacts = []

    if stage_type == 'data':
        artifacts = [
            f"bqx_ml_v3.{prefix}_raw_data",
            f"bqx_ml_v3.{prefix}_processed_data",
            f"gs://bqx-ml-v3-data/{prefix}_validation_report.json",
            f"data/{prefix}_schema.json"
        ]

    elif stage_type == 'model':
        artifacts = [
            f"models/{prefix}_rf_model.pkl",
            f"models/{prefix}_xgb_model.pkl",
            f"models/{prefix}_lgbm_model.pkl",
            f"models/{prefix}_lstm_model.h5",
            f"models/{prefix}_gru_model.h5",
            f"models/{prefix}_ensemble_weights.json",
            f"models/{prefix}_training_metrics.json",
            f"models/{prefix}_model_card.md"
        ]

    elif stage_type == 'feature':
        artifacts = [
            f"bqx_ml_v3.{prefix}_features",
            f"features/{prefix}_feature_definitions.json",
            f"features/{prefix}_feature_importance.csv",
            f"features/{prefix}_correlation_matrix.png"
        ]

    elif stage_type == 'infrastructure':
        artifacts = [
            f"infrastructure/{prefix}_config.yaml",
            f"infrastructure/{prefix}_terraform.tfstate",
            f"gcr.io/bqx-ml-v3/{prefix}:latest",
            f"infrastructure/{prefix}_deployment_manifest.yaml"
        ]

    elif stage_type == 'testing':
        artifacts = [
            f"tests/{prefix}_test_results.json",
            f"tests/{prefix}_coverage_report.html",
            f"tests/{prefix}_validation_metrics.json",
            f"tests/{prefix}_performance_report.pdf"
        ]

    elif stage_type == 'monitoring':
        artifacts = [
            f"monitoring/{prefix}_dashboard.json",
            f"monitoring/{prefix}_alert_rules.yaml",
            f"monitoring/{prefix}_metrics_config.json"
        ]

    elif stage_type == 'security':
        artifacts = [
            f"security/{prefix}_iam_policies.json",
            f"security/{prefix}_audit_log.json",
            f"security/{prefix}_compliance_report.pdf"
        ]

    elif stage_type == 'api':
        artifacts = [
            f"api/{prefix}_openapi_spec.yaml",
            f"api/{prefix}_endpoint_config.json",
            f"api/{prefix}_service_manifest.yaml",
            f"api/{prefix}_api_documentation.md"
        ]

    elif stage_type == 'baseline':
        artifacts = [
            f"baselines/{prefix}_metrics.json",
            f"baselines/{prefix}_benchmark_results.csv",
            f"baselines/{prefix}_comparison_report.pdf"
        ]

    elif stage_type == 'documentation':
        artifacts = [
            f"docs/{prefix}_intelligence_file.md",
            f"docs/{prefix}_technical_spec.pdf",
            f"docs/{prefix}_user_guide.md"
        ]

    else:  # general
        artifacts = [
            f"output/{prefix}_results.json",
            f"output/{prefix}_report.md",
            f"output/{prefix}_summary.txt"
        ]

    return artifacts

def generate_source_paths(stage_id: str, stage_name: str, stage_type: str) -> List[str]:
    """Generate source file paths that build agent may access"""

    sources = []

    # Common sources for all stages
    sources.extend([
        "README.md",
        "requirements.txt",
        ".secrets/github_secrets.json"
    ])

    if stage_type == 'data':
        sources.extend([
            "scripts/data_ingestion/*.py",
            "scripts/data_validation/*.py",
            "config/bigquery_schemas/*.json",
            "sql/data_queries/*.sql"
        ])

    elif stage_type == 'model':
        sources.extend([
            "scripts/model_training/*.py",
            "scripts/model_evaluation/*.py",
            "config/model_configs/*.yaml",
            "src/models/*.py",
            "src/ensemble/*.py"
        ])

    elif stage_type == 'feature':
        sources.extend([
            "scripts/feature_engineering/*.py",
            "src/features/bqx_calculations.py",
            "src/features/technical_indicators.py",
            "config/feature_configs/*.yaml",
            "sql/feature_queries/*.sql"
        ])

    elif stage_type == 'infrastructure':
        sources.extend([
            "infrastructure/*.tf",
            "infrastructure/terraform.tfvars",
            "infrastructure/docker/*.Dockerfile",
            "infrastructure/kubernetes/*.yaml",
            "config/deployment_configs/*.yaml"
        ])

    elif stage_type == 'testing':
        sources.extend([
            "tests/**/*.py",
            "tests/fixtures/*.json",
            "tests/conftest.py",
            "pytest.ini",
            "config/test_configs/*.yaml"
        ])

    elif stage_type == 'monitoring':
        sources.extend([
            "monitoring/dashboards/*.json",
            "monitoring/alerts/*.yaml",
            "config/monitoring_configs/*.yaml",
            "scripts/monitoring/*.py"
        ])

    elif stage_type == 'security':
        sources.extend([
            "security/iam_policies/*.json",
            "security/encryption_configs/*.yaml",
            "config/security_configs/*.yaml",
            "scripts/security/*.py"
        ])

    elif stage_type == 'api':
        sources.extend([
            "api/**/*.py",
            "api/openapi/*.yaml",
            "api/routes/*.py",
            "api/middleware/*.py",
            "config/api_configs/*.yaml"
        ])

    elif stage_type == 'baseline':
        sources.extend([
            "scripts/baseline_evaluation/*.py",
            "scripts/benchmarking/*.py",
            "config/baseline_configs/*.yaml"
        ])

    elif stage_type == 'documentation':
        sources.extend([
            "docs/**/*.md",
            "scripts/create_intelligence_files.py",
            "scripts/generate_docs.py",
            "templates/**/*.md"
        ])

    else:  # general
        sources.extend([
            "scripts/**/*.py",
            "src/**/*.py",
            "config/**/*.yaml"
        ])

    return sources

def populate_stage_fields(dry_run: bool = True):
    """Populate source fields and add artifacts info to notes for all stages"""
    print("\n" + "="*70)
    print("POPULATING STAGE SOURCE PATHS AND ARTIFACTS INFO")
    print("="*70)

    if dry_run:
        print("\n⚠️  DRY RUN MODE - No actual updates will occur")

    all_stages = stages_table.all()

    print(f"\n📋 Processing {len(all_stages)} stages...")

    stats = {
        'total': len(all_stages),
        'updated': 0,
        'skipped': 0,
        'errors': 0,
        'by_type': {}
    }

    for i, stage in enumerate(all_stages, 1):
        fields = stage['fields']
        stage_id = fields.get('stage_id', 'Unknown')
        stage_name = fields.get('name', 'Unnamed')
        stage_description = fields.get('description', '')

        # Determine stage type
        stage_type = determine_stage_type(stage_name, stage_description)
        stats['by_type'][stage_type] = stats['by_type'].get(stage_type, 0) + 1

        # Generate artifacts and sources
        artifacts = generate_artifacts(stage_id, stage_name, stage_type)
        sources = generate_source_paths(stage_id, stage_name, stage_type)

        # Check if update needed
        current_source = fields.get('source', '')
        current_notes = fields.get('notes', '')

        needs_update = not current_source

        if not needs_update:
            stats['skipped'] += 1
            continue

        # Show first 10 updates
        if stats['updated'] < 10:
            print(f"\n  {i}. {stage_id}")
            print(f"     Name: {stage_name[:50]}")
            print(f"     Type: {stage_type}")
            print(f"     Artifacts: {len(artifacts)} files")
            print(f"     Sources: {len(sources)} paths")

        if not dry_run:
            try:
                updates = {}

                # Update source field with file paths
                if not current_source:
                    updates['source'] = "\n".join(sources)

                # Add artifacts info to notes if notes are empty or short
                if not current_notes or len(current_notes) < 100:
                    artifacts_section = "\n\n## Anticipated Artifacts\n" + "\n".join(f"- {a}" for a in artifacts)
                    if current_notes:
                        updates['notes'] = current_notes + artifacts_section
                    else:
                        updates['notes'] = f"## Stage: {stage_name}\n\nType: {stage_type}" + artifacts_section

                if updates:
                    stages_table.update(stage['id'], updates)
                    stats['updated'] += 1
            except Exception as e:
                print(f"  ❌ Error updating {stage_id}: {e}")
                stats['errors'] += 1
        else:
            stats['updated'] += 1

    if stats['updated'] > 10:
        print(f"\n  ... {stats['updated'] - 10} more stages to update")

    return stats

def main():
    print("📦 Populate Stage Artifacts and Source Paths")
    print("="*70)
    print("\nThis script will add:")
    print("1. Anticipated artifacts to artifacts field")
    print("2. Source file paths to source field")
    print("="*70)

    # First run in dry-run mode
    print("\n🔍 Running analysis...")
    stats = populate_stage_fields(dry_run=True)

    # Print summary
    print("\n" + "="*70)
    print("ANALYSIS SUMMARY")
    print("="*70)

    print(f"\n📊 Stage Statistics:")
    print(f"   Total stages: {stats['total']}")
    print(f"   Need updates: {stats['updated']}")
    print(f"   Already complete: {stats['skipped']}")

    print(f"\n📊 Stages by Type:")
    for stage_type, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {stage_type}: {count}")

    if stats['updated'] > 0:
        print("\n" + "="*70)
        response = input(f"\nUpdate {stats['updated']} stages? (yes/no): ")

        if response.lower() == 'yes':
            print("\n🔄 Updating stages...")
            final_stats = populate_stage_fields(dry_run=False)

            print("\n" + "="*70)
            print("UPDATE COMPLETE")
            print("="*70)

            print(f"\n📊 Results:")
            print(f"   Stages updated: {final_stats['updated']}")
            print(f"   Errors: {final_stats['errors']}")

            if final_stats['errors'] == 0:
                print(f"\n✅ SUCCESS: All stages updated with artifacts and source paths")
            else:
                print(f"\n⚠️  WARNING: {final_stats['errors']} stages failed to update")
        else:
            print("\n❌ Update cancelled")
    else:
        print(f"\n✅ All stages already have artifacts and source paths")

    print("\n" + "="*70)

if __name__ == '__main__':
    main()
