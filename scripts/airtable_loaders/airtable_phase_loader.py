#!/usr/bin/env python3
"""
Load BQX ML V3 Phase Plan into AirTable
Creates/updates Phases, Stages, and Tasks for Project P03
"""

import requests
import json
import time
from typing import Dict, List, Any
from datetime import datetime

# Load credentials
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json') as f:
    secrets = json.load(f)

API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']

# Set up headers
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# Table IDs from schema exploration
PLANS_TABLE = 'tblTtBE4sEa5ibCHE'
PHASES_TABLE = 'tblbNORPGr9fcOnsP'
STAGES_TABLE = 'tblxnuvF8O7yH1dB4'
TASKS_TABLE = 'tblQ9VXdTgZiIR6H2'

def create_phase_records():
    """Create all phase records for P03"""

    phases = [
        {
            "phase_id": "P03.01",
            "name": "Work Environment Setup",
            "status": "Not Started",
            "duration": "2d",
            "description": "Establish development environment and automation foundation. Deploy GitHub secrets, configure GCP authentication, set up AirTable integration, and prepare development tools.",
            "owner": "BQXML CHIEF ENGINEER",
            "milestones": "• GitHub secrets deployed\n• GCP authentication configured\n• AirTable integration operational\n• Development environment ready",
            "deliverables": "• Deployed secrets\n• Configured workflows\n• API integrations\n• Development setup",
            "estimated_budget": 100
        },
        {
            "phase_id": "P03.02",
            "name": "Intelligence Architecture & Discovery",
            "status": "Not Started",
            "duration": "4d",
            "description": "Create the 7-layer intelligence architecture that will guide all development. Build self-documenting JSON files that define context, semantics, ontology, protocols, constraints, workflows, and metadata. Complete documentation review and establish system foundations.",
            "owner": "BQXML CHIEF ENGINEER",
            "milestones": "• 10 Intelligence JSON files created\n• IntelligenceManager class built\n• Paradigm alignment confirmed\n• Resource validation complete",
            "deliverables": "• .bqx_ml_v3/ directory with all JSON files\n• Python intelligence management class\n• Paradigm documentation\n• Resource audit report",
            "estimated_budget": 200
        },
        {
            "phase_id": "P03.03",
            "name": "Planning & Technical Architecture",
            "status": "Not Started",
            "duration": "3d",
            "description": "Design complete system architecture leveraging intelligence framework. Define feature matrix (8×6×2), API specifications, and implementation roadmap.",
            "owner": "BQXML CHIEF ENGINEER",
            "milestones": "• Technical architecture documented\n• Feature matrix defined\n• API contracts specified\n• Timeline finalized",
            "deliverables": "• Architecture document\n• Feature matrix (1,736 tables mapped)\n• API specifications\n• Implementation plan",
            "estimated_budget": 150
        },
        {
            "phase_id": "P03.04",
            "name": "Infrastructure Setup",
            "status": "Not Started",
            "duration": "3d",
            "description": "Create all GCP infrastructure components including BigQuery dataset (bqx_ml), Cloud Storage buckets, Vertex AI environment, and monitoring infrastructure.",
            "owner": "BQXML CHIEF ENGINEER",
            "milestones": "• BigQuery dataset created\n• Storage buckets deployed\n• Vertex AI configured\n• Monitoring enabled",
            "deliverables": "• bqx_ml dataset in us-east1\n• 3 Cloud Storage buckets\n• Vertex AI Workbench\n• Monitoring dashboards",
            "estimated_budget": 300
        },
        {
            "phase_id": "P03.05",
            "name": "Data Pipeline Foundation & Validation",
            "status": "Not Started",
            "duration": "9d",
            "description": "Validate 5 years of historical data (157M+ data points), ensure quality, establish pipeline orchestration, and implement anomaly detection. Critical phase for data integrity.",
            "owner": "BQXML CHIEF ENGINEER",
            "milestones": "• Data quality validated\n• Pipeline orchestration live\n• Anomaly detection active\n• <0.1% missing data",
            "deliverables": "• Data quality reports\n• Pipeline configuration\n• Anomaly alerts\n• Validation documentation",
            "estimated_budget": 400
        },
        {
            "phase_id": "P03.06",
            "name": "Primary Feature Engineering",
            "status": "Not Started",
            "duration": "10d",
            "description": "Create 168 primary feature tables including BQX values as features (paradigm shift). Build lag, regime, aggregation, alignment, momentum, and volatility features for all 28 pairs.",
            "owner": "BQXML CHIEF ENGINEER",
            "milestones": "• 168 tables created\n• BQX features included\n• Query performance <2s\n• All pairs covered",
            "deliverables": "• lag_bqx_* tables (28)\n• regime_bqx_* tables (28)\n• agg_bqx_* tables (28)\n• align_bqx_* tables (28)\n• momentum/volatility tables (56)",
            "estimated_budget": 600
        },
        {
            "phase_id": "P03.07",
            "name": "Advanced Feature Engineering",
            "status": "Not Started",
            "duration": "12d",
            "description": "Create multi-centric features including variant (currency families), covariant (pair relationships), triangulation (arbitrage), secondary (currency strength), and tertiary (market-wide) features.",
            "owner": "BQXML CHIEF ENGINEER",
            "milestones": "• ~244 tables created\n• All centrics implemented\n• Cross-contamination prevented\n• Market regimes identified",
            "deliverables": "• Variant features (7 families)\n• Covariant features (50 relationships)\n• Triangulation features (18)\n• Currency strength indices (8)\n• Market features (1)",
            "estimated_budget": 700
        },
        {
            "phase_id": "P03.08",
            "name": "Model Development & Testing",
            "status": "Not Started",
            "duration": "16d",
            "description": "Train 140 models (28 pairs × 5 algorithms) with comprehensive testing suite. Implement linear regression, XGBoost, neural networks, LSTM, and Gaussian process models.",
            "owner": "BQXML CHIEF ENGINEER",
            "milestones": "• 140 models trained\n• R² > 0.75 achieved\n• Test coverage >90%\n• Load tests passed",
            "deliverables": "• 140 trained models\n• Test suite with >90% coverage\n• Validation reports\n• Performance benchmarks",
            "estimated_budget": 1200
        },
        {
            "phase_id": "P03.09",
            "name": "Deployment & Monitoring",
            "status": "Not Started",
            "duration": "8d",
            "description": "Deploy models to production with comprehensive monitoring. Set up multi-model endpoint, REST API, real-time monitoring, alerting, and model drift detection.",
            "owner": "BQXML CHIEF ENGINEER",
            "milestones": "• Endpoint <100ms latency\n• 99.9% uptime SLO\n• Monitoring active\n• Alerts configured",
            "deliverables": "• Production endpoint\n• REST API\n• Monitoring dashboards\n• Alert policies\n• Drift detection",
            "estimated_budget": 500
        },
        {
            "phase_id": "P03.10",
            "name": "Validation & Disaster Recovery",
            "status": "Not Started",
            "duration": "7d",
            "description": "Final validation, disaster recovery setup, and production readiness. Implement backup procedures, test recovery scenarios, create runbooks, and establish SLAs.",
            "owner": "BQXML CHIEF ENGINEER",
            "milestones": "• Integration tests passed\n• DR tested successfully\n• RTO <4h, RPO <1h\n• Runbooks complete",
            "deliverables": "• Test reports\n• DR procedures\n• Operational runbooks\n• SLA documentation\n• Production checklist",
            "estimated_budget": 400
        },
        {
            "phase_id": "P03.11",
            "name": "Security Hardening",
            "status": "Not Started",
            "duration": "3d",
            "description": "Implement comprehensive security controls including IAM hardening, VPC Service Controls, Cloud KMS encryption, secret rotation, and audit logging.",
            "owner": "BQXML CHIEF ENGINEER",
            "milestones": "• Zero overly permissive IAM\n• All data encrypted\n• Audit logs active\n• Security scan passed",
            "deliverables": "• IAM audit report\n• VPC configuration\n• KMS encryption setup\n• Secret rotation automation\n• Security compliance report",
            "estimated_budget": 300
        }
    ]

    return phases

def create_record(table_id: str, fields: Dict[str, Any]):
    """Create a single record in AirTable"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{table_id}'

    data = {
        "fields": fields
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error creating record: {response.status_code}")
        print(response.text)
        return None

def update_record(table_id: str, record_id: str, fields: Dict[str, Any]):
    """Update an existing record in AirTable"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{table_id}/{record_id}'

    data = {
        "fields": fields
    }

    response = requests.patch(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error updating record: {response.status_code}")
        print(response.text)
        return None

def find_record(table_id: str, field_name: str, field_value: str):
    """Find a record by field value"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{table_id}'

    params = {
        'filterByFormula': f'{{{field_name}}}="{field_value}"',
        'maxRecords': 1
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        records = response.json().get('records', [])
        return records[0] if records else None
    else:
        return None

def load_phases_to_airtable(dry_run: bool = True):
    """Load all phases to AirTable"""

    phases = create_phase_records()

    # First, ensure P03 plan exists
    plan_record = find_record(PLANS_TABLE, 'plan_id', 'P03')
    if not plan_record:
        print("Warning: Plan P03 not found. Please create it first.")
        if not dry_run:
            return

    plan_record_id = plan_record['id'] if plan_record else None

    created = 0
    updated = 0

    for phase in phases:
        phase_id = phase['phase_id']

        # Add plan link if we have the plan record
        if plan_record_id:
            phase['plan_link'] = [plan_record_id]

        if dry_run:
            print(f"[DRY RUN] Would create/update phase: {phase_id} - {phase['name']}")
            print(f"  Duration: {phase['duration']}")
            print(f"  Budget: ${phase.get('estimated_budget', 0)}")
            print()
        else:
            # Check if phase exists
            existing = find_record(PHASES_TABLE, 'phase_id', phase_id)

            if existing:
                # Update existing
                result = update_record(PHASES_TABLE, existing['id'], phase)
                if result:
                    updated += 1
                    print(f"Updated phase: {phase_id}")
            else:
                # Create new
                result = create_record(PHASES_TABLE, phase)
                if result:
                    created += 1
                    print(f"Created phase: {phase_id}")

            # Rate limiting
            time.sleep(0.2)

    print("\n" + "="*60)
    print(f"SUMMARY:")
    print(f"  Total Phases: {len(phases)}")
    if not dry_run:
        print(f"  Created: {created}")
        print(f"  Updated: {updated}")
    print(f"  Total Duration: 75 days")
    print(f"  Total Budget: $5,000")
    print("="*60)

def main():
    """Main execution"""
    print("BQX ML V3 PHASE LOADER")
    print("="*60)
    print(f"Base ID: {BASE_ID}")
    print(f"Phases to load: 11")
    print()

    # First do a dry run
    print("Performing DRY RUN...")
    print("-"*60)
    load_phases_to_airtable(dry_run=True)

    print("\n" + "="*60)
    response = input("Proceed with actual loading? (y/n): ")

    if response.lower() == 'y':
        print("\nLoading phases to AirTable...")
        print("-"*60)
        load_phases_to_airtable(dry_run=False)
        print("\nPhases loaded successfully!")
    else:
        print("Loading cancelled.")

if __name__ == "__main__":
    main()