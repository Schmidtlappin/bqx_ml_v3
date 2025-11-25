#!/usr/bin/env python3
"""
Add Intelligence Stages S03.02.07 and S03.02.08 to AirTable
Addresses gaps identified in intelligence plan verification
"""
import json
import os
import sys
from pyairtable import Api

# Load secrets
with open('.secrets/github_secrets.json') as f:
    secrets = json.load(f)['secrets']

AIRTABLE_API_KEY = secrets['AIRTABLE_API_KEY']['value']
AIRTABLE_BASE_ID = secrets['AIRTABLE_BASE_ID']['value']

# Initialize API
api = Api(AIRTABLE_API_KEY)
stages_table = api.table(AIRTABLE_BASE_ID, 'Stages')
phases_table = api.table(AIRTABLE_BASE_ID, 'Phases')

# Get Phase P03.02 record ID
print("🔍 Finding Phase P03.02...")
phases = phases_table.all(formula="{phase_id} = 'P03.02'")

if not phases:
    print("❌ Error: Phase P03.02 not found in AirTable")
    sys.exit(1)

phase_p03_02_record_id = phases[0]['id']
print(f"✓ Found Phase P03.02 (Record ID: {phase_p03_02_record_id})")

# Define new intelligence stages
NEW_STAGES = [
    {
        "stage_id": "S03.02.07",
        "name": "Implement Intelligence File Update Hooks",
        "description": """Implement automated hooks and mechanisms to keep intelligence files synchronized with codebase changes.

## Scope
- Git hooks (pre-commit, post-merge, pre-push) for intelligence validation
- CI/CD pipeline hooks (GitHub Actions) for automated synchronization
- Automated update triggers for architecture changes, currency pair additions
- Validation workflows to prevent inconsistent intelligence states
- Comprehensive documentation for hook usage and maintenance

## Key Components
1. **Git Hooks**:
   - Pre-commit hook: Validates intelligence file consistency before commits
   - Post-merge hook: Auto-updates intelligence files after merges
   - Pre-push hook: Comprehensive validation before pushing to remote

2. **CI/CD Workflows**:
   - GitHub Actions workflow for intelligence validation on every PR
   - Automated intelligence file synchronization on push to main
   - Intelligence report generation for code review

3. **Update Triggers**:
   - Architecture change trigger: Updates ontology.json when code structure changes
   - Currency pair addition trigger: Updates context.json and metadata.json
   - Constraint change trigger: Updates constraints.json
   - Workflow change trigger: Updates workflows.json

4. **Validation Scripts**:
   - validate_intelligence_consistency.py: Cross-file consistency checks
   - check_intelligence_updates.py: Detects when updates needed
   - validate_constraints.py: Ensures constraint compliance
   - generate_intelligence_report.py: Creates validation reports

## Technical Implementation
```bash
# Git hooks installation
.git/hooks/
├── pre-commit           # Validate intelligence
├── post-merge          # Auto-update intelligence
└── pre-push            # Final validation

# CI/CD workflows
.github/workflows/
└── intelligence-validation.yml

# Update trigger scripts
scripts/hooks/
├── validate_intelligence_consistency.py
├── update_intelligence_context.py
├── update_intelligence_metadata.py
├── on_architecture_change.py
├── on_pair_addition.py
└── check_intelligence_updates.py
```

## Acceptance Criteria
- Pre-commit hook validates intelligence files in < 5 seconds
- Post-merge hook auto-updates intelligence files successfully
- CI/CD pipeline validates intelligence on every PR in < 2 minutes
- Architecture changes trigger automatic intelligence updates
- New currency pairs automatically update all relevant files
- Zero false positives in validation
- Comprehensive error messages for failures

## Benefits
- Intelligence files always synchronized with code
- Prevents inconsistent intelligence states
- Reduces manual update errors
- Enforces intelligence validation in development workflow
- Provides continuous intelligence quality assurance

---
📚 **Detailed Specification**: See [S03.02.07_INTELLIGENCE_HOOKS_SPECIFICATION.md](../docs/S03.02.07_INTELLIGENCE_HOOKS_SPECIFICATION.md)
""",
        "status": "Todo",
        "phase_link": [phase_p03_02_record_id],
        "notes": "Dependencies: S03.02.05, S03.02.06, T03.01.04.04\nResources: Backend: 4h, CI/CD: 2h, Testing: 1h, Docs: 1h\nEstimated Hours: 8\nPriority: High",
        "record_score": 95.0
    },
    {
        "stage_id": "S03.02.08",
        "name": "Implement Intelligence Violation Policing Service",
        "description": """Implement a continuous operational policing service that monitors the BQX ML V3 system for violations of critical intelligence constraints, paradigm mandates, and architectural rules.

## Scope
- Continuous monitoring daemon/service for constraint violations
- Real-time detection of paradigm, constraint, architecture, and data quality violations
- Multi-channel alerting system (Email, Slack, AirTable, PagerDuty)
- Violation tracking and logging to BigQuery
- Automated enforcement mechanisms (blocking, rollback)
- Grafana dashboard for violation metrics and trends

## System Architecture
```
Intelligence Policing Service
├── Violation Detector
│   ├── Paradigm Monitor (BQX paradigm compliance)
│   ├── Constraint Monitor (ROWS BETWEEN, model isolation)
│   ├── Architecture Monitor (GCP-only, 28 models)
│   └── Data Quality Monitor (missing data, row counts)
├── Alert Manager
│   ├── Email Alerts (critical violations)
│   ├── Slack Notifications (all severities)
│   ├── AirTable Updates (violation tracking)
│   └── PagerDuty (critical only)
├── Violation Logger
│   ├── BigQuery Logging (long-term storage)
│   └── Local File Logging (backup)
├── Enforcement Engine
│   ├── Model Training Blocking
│   ├── SQL File Blocking
│   ├── Model Rollback
│   └── Access Revocation
└── Metrics Exporter
    ├── Prometheus Metrics
    └── Grafana Dashboard
```

## Key Components
1. **Policing Service Daemon** (`intelligence_policing_service.py`):
   - Runs continuously as system service
   - 4 monitoring loops: paradigm, constraint, architecture, data quality
   - Handles violations based on severity (critical/high/warning)
   - Exports metrics every 30 seconds

2. **Violation Detector** (`violation_detector.py`):
   - Checks for BQX paradigm violations (missing BQX features/targets)
   - Checks for constraint violations (ROWS BETWEEN, model independence)
   - Checks for architecture violations (model count, non-GCP services)
   - Checks for data quality violations (missing data, insufficient rows)

3. **Alert Manager** (`alert_manager.py`):
   - Multi-channel alerting: Email + Slack + AirTable + PagerDuty
   - Severity-based routing (critical→all channels, high→email+Slack, warning→Slack only)
   - Async alert delivery for performance

4. **Violation Logger** (`violation_logger.py`):
   - BigQuery table: `bqx_ml.intelligence_violations`
   - Structured logging with violation ID, timestamp, details
   - Local JSONL backup logs

5. **Enforcement Engine** (`enforcement_engine.py`):
   - Automated enforcement for critical violations
   - Blocks model training for paradigm violations
   - Blocks SQL execution for constraint violations
   - Triggers model rollback for contamination violations

6. **Metrics Exporter** (`metrics_exporter.py`):
   - Prometheus metrics: violation counts, active violations, resolution time
   - Grafana dashboard with real-time charts and trends

## Violation Types Detected
1. **Paradigm Violations**: Missing BQX features/targets
2. **Constraint Violations**: RANGE BETWEEN usage, INTERVAL usage, Cross-pair contamination
3. **Architecture Violations**: Incorrect model count, Non-GCP service usage
4. **Data Quality Violations**: Excessive missing data, Insufficient data

## Acceptance Criteria
- Service runs continuously 24/7 with > 99.9% uptime
- Detects all defined violation types with 100% accuracy
- Sends alerts within 1 minute of detection
- Logs all violations to BigQuery with zero data loss
- Enforces critical violations automatically
- Provides real-time metrics via Prometheus
- Grafana dashboard displays violation trends
- False positive rate < 0.1%

## Benefits
- Continuous enforcement of critical intelligence constraints
- Early detection of paradigm and constraint violations
- Automated alerting reduces manual monitoring burden
- Historical violation tracking enables trend analysis
- Automated enforcement prevents contamination and errors
- Real-time dashboards provide visibility

---
📚 **Detailed Specification**: See [S03.02.08_VIOLATION_POLICING_SPECIFICATION.md](../docs/S03.02.08_VIOLATION_POLICING_SPECIFICATION.md)
""",
        "status": "Todo",
        "phase_link": [phase_p03_02_record_id],
        "notes": "Dependencies: S03.02.05, S03.02.06, S03.02.07\nResources: Service Dev: 8h, Enforcement: 4h, Dashboard: 2h, Testing/Docs: 2h\nEstimated Hours: 16\nPriority: High",
        "record_score": 95.0
    }
]

# Add stages to AirTable
print("\n📤 Adding new intelligence stages to AirTable...")

for stage in NEW_STAGES:
    stage_id = stage['stage_id']
    stage_name = stage['name']

    # Check if stage already exists
    existing = stages_table.all(formula=f"{{stage_id}} = '{stage_id}'")

    if existing:
        print(f"⚠️  Stage {stage_id} already exists, skipping...")
        continue

    print(f"\n📝 Adding {stage_id}: {stage_name}")

    try:
        # Create stage
        record = stages_table.create(stage)
        print(f"✅ Successfully added {stage_id} (Record ID: {record['id']})")

    except Exception as e:
        print(f"❌ Error adding {stage_id}: {e}")
        continue

print("\n" + "="*70)
print("✅ Intelligence stages added to AirTable!")
print("="*70)
print("\n📊 Summary:")
print(f"   New Stages Added: 2")
print(f"   - S03.02.07: Implement Intelligence File Update Hooks (8 hours)")
print(f"   - S03.02.08: Implement Intelligence Violation Policing Service (16 hours)")
print(f"\n📈 Phase P03.02 now has 4 stages (previously 2)")
print(f"   Total Hours: 36 hours (previously 12 hours)")
print(f"\n🔗 View in AirTable:")
print(f"   https://airtable.com/{AIRTABLE_BASE_ID}")
print(f"\n📚 Documentation:")
print(f"   - INTELLIGENCE_PLAN_VERIFICATION.md")
print(f"   - S03.02.07_INTELLIGENCE_HOOKS_SPECIFICATION.md")
print(f"   - S03.02.08_VIOLATION_POLICING_SPECIFICATION.md")
print(f"   - INTELLIGENCE_GAP_REMEDIATION_SUMMARY.md")
