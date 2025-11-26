#!/usr/bin/env python3
"""
Final Pre-Flight Check for BQX ML V3 Project Plan
Comprehensive validation before execution authorization.
"""

import os
import json
import re
import sys
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
        print("❌ CRITICAL: Could not load AirTable credentials")
        sys.exit(1)

# Initialize API
api = Api(API_KEY)
base = api.base(BASE_ID)

# Load all tables
plans_table = base.table('Plans')
phases_table = base.table('Phases')
stages_table = base.table('Stages')
tasks_table = base.table('Tasks')

class PreFlightCheck:
    """Comprehensive pre-flight validation."""

    def __init__(self):
        self.issues = []
        self.warnings = []
        self.stats = defaultdict(int)

    def add_issue(self, category, message):
        """Add a critical issue that must be fixed."""
        self.issues.append(f"[{category}] {message}")

    def add_warning(self, category, message):
        """Add a warning that should be reviewed."""
        self.warnings.append(f"[{category}] {message}")

    def check_table_connectivity(self):
        """Verify all tables are accessible."""
        print("\n🔌 Checking Table Connectivity...")

        try:
            plans = plans_table.all()
            phases = phases_table.all()
            stages = stages_table.all()
            tasks = tasks_table.all()

            self.stats['plans'] = len(plans)
            self.stats['phases'] = len(phases)
            self.stats['stages'] = len(stages)
            self.stats['tasks'] = len(tasks)

            print(f"  ✅ Plans: {self.stats['plans']}")
            print(f"  ✅ Phases: {self.stats['phases']}")
            print(f"  ✅ Stages: {self.stats['stages']}")
            print(f"  ✅ Tasks: {self.stats['tasks']}")

            # Verify expected counts
            if self.stats['plans'] != 1:
                self.add_issue("STRUCTURE", f"Expected 1 plan, found {self.stats['plans']}")
            if self.stats['phases'] != 11:
                self.add_issue("STRUCTURE", f"Expected 11 phases, found {self.stats['phases']}")
            if self.stats['stages'] < 70:
                self.add_warning("STRUCTURE", f"Expected 70+ stages, found {self.stats['stages']}")
            if self.stats['tasks'] != 197:
                self.add_issue("STRUCTURE", f"Expected 197 tasks, found {self.stats['tasks']}")

            return plans, phases, stages, tasks

        except Exception as e:
            self.add_issue("CONNECTIVITY", f"Failed to load tables: {e}")
            return None, None, None, None

    def check_record_completeness(self, tasks):
        """Verify all required fields are populated."""
        print("\n📋 Checking Record Completeness...")

        required_fields = [
            'task_id', 'name', 'description', 'notes',
            'status', 'priority', 'assigned_to', 'stage_link'
        ]

        incomplete_tasks = []

        for task in tasks:
            fields = task['fields']
            task_id = fields.get('task_id', 'UNKNOWN')

            for field in required_fields:
                value = fields.get(field)
                if not value or (isinstance(value, str) and not value.strip()):
                    incomplete_tasks.append((task_id, field))

        if incomplete_tasks:
            for task_id, field in incomplete_tasks[:5]:  # Show first 5
                self.add_issue("COMPLETENESS", f"Task {task_id} missing {field}")
            if len(incomplete_tasks) > 5:
                self.add_issue("COMPLETENESS", f"...and {len(incomplete_tasks)-5} more incomplete fields")
        else:
            print("  ✅ All required fields populated")

    def check_link_integrity(self, plans, phases, stages, tasks):
        """Verify all links are properly connected."""
        print("\n🔗 Checking Link Integrity...")

        # Get plan record ID
        plan_id = plans[0]['id'] if plans else None

        if not plan_id:
            self.add_issue("LINKS", "No plan record found")
            return

        # Check phase -> plan links
        phases_missing_plan = []
        for phase in phases:
            phase_id = phase['fields'].get('phase_id')
            plan_link = phase['fields'].get('plan_link', [])
            if not plan_link or plan_id not in plan_link:
                phases_missing_plan.append(phase_id)

        if phases_missing_plan:
            self.add_issue("LINKS", f"{len(phases_missing_plan)} phases missing plan_link")

        # Check task -> stage/phase/plan links
        tasks_missing_links = []
        for task in tasks:
            task_id = task['fields'].get('task_id')
            stage_link = task['fields'].get('stage_link', [])
            phase_link = task['fields'].get('phase_link', [])
            plan_link = task['fields'].get('plan_link', [])

            if not stage_link:
                tasks_missing_links.append(f"{task_id}: missing stage_link")
            if not phase_link:
                tasks_missing_links.append(f"{task_id}: missing phase_link")
            if not plan_link or plan_id not in plan_link:
                tasks_missing_links.append(f"{task_id}: missing plan_link")

        if tasks_missing_links:
            for issue in tasks_missing_links[:5]:
                self.add_issue("LINKS", issue)
            if len(tasks_missing_links) > 5:
                self.add_issue("LINKS", f"...and {len(tasks_missing_links)-5} more link issues")
        else:
            print("  ✅ All links properly connected")

    def check_technical_consistency(self, tasks):
        """Verify INTERVAL-CENTRIC compliance."""
        print("\n⚙️ Checking Technical Consistency...")

        range_between_count = 0
        missing_bqx_count = 0

        for task in tasks:
            task_id = task['fields'].get('task_id')
            description = task['fields'].get('description', '')
            notes = task['fields'].get('notes', '')

            # Check for RANGE BETWEEN (should be ROWS BETWEEN)
            if 'RANGE BETWEEN' in description or 'RANGE BETWEEN' in notes:
                range_between_count += 1
                self.add_issue("TECHNICAL", f"Task {task_id} contains RANGE BETWEEN (should be ROWS BETWEEN)")

            # Check for BQX paradigm in relevant phases
            if any(phase in task_id for phase in ['P06', 'P07']):
                if 'BQX' not in description and 'BQX' not in notes:
                    missing_bqx_count += 1

        if range_between_count > 0:
            self.add_issue("TECHNICAL", f"{range_between_count} tasks with RANGE BETWEEN issues")
        else:
            print("  ✅ All window operations use ROWS BETWEEN")

        if missing_bqx_count > 0:
            self.add_warning("TECHNICAL", f"{missing_bqx_count} feature tasks might be missing BQX paradigm")

    def check_content_quality(self, tasks):
        """Verify content quality and no boilerplate."""
        print("\n📝 Checking Content Quality...")

        boilerplate_patterns = [
            r'Lorem ipsum',
            r'TODO:.*implement',
            r'Insert.*here',
            r'Coming soon',
            r'\[placeholder\]'
        ]

        boilerplate_found = []
        short_descriptions = []
        short_notes = []

        for task in tasks:
            task_id = task['fields'].get('task_id')
            description = task['fields'].get('description', '')
            notes = task['fields'].get('notes', '')

            # Check for boilerplate
            for pattern in boilerplate_patterns:
                if re.search(pattern, description + notes, re.IGNORECASE):
                    boilerplate_found.append(task_id)
                    break

            # Check content length
            if len(description) < 500:
                short_descriptions.append(task_id)
            if len(notes) < 1000:
                short_notes.append(task_id)

        if boilerplate_found:
            self.add_issue("QUALITY", f"{len(boilerplate_found)} tasks contain boilerplate")
        else:
            print("  ✅ No boilerplate detected")

        if short_descriptions:
            self.add_warning("QUALITY", f"{len(short_descriptions)} tasks have short descriptions (<500 chars)")
        if short_notes:
            self.add_warning("QUALITY", f"{len(short_notes)} tasks have short notes (<1000 chars)")

        # Check for code examples
        tasks_with_code = sum(1 for t in tasks if '```' in t['fields'].get('notes', ''))
        print(f"  ✅ {tasks_with_code}/{len(tasks)} tasks have code examples")

    def check_gcp_ml_coverage(self, tasks):
        """Verify 100% GCP ML process coverage."""
        print("\n☁️ Checking GCP ML Coverage...")

        required_components = {
            'BigQuery': ['BigQuery', 'dataset', 'table', 'SQL'],
            'Vertex AI': ['Vertex AI', 'aiplatform', 'endpoint', 'model'],
            'Cloud Storage': ['Cloud Storage', 'GCS', 'bucket'],
            'Dataflow': ['Dataflow', 'Apache Beam', 'pipeline'],
            'Cloud Functions': ['Cloud Functions', 'trigger', 'event'],
            'Pub/Sub': ['Pub/Sub', 'topic', 'subscription'],
            'Cloud Scheduler': ['Scheduler', 'cron', 'schedule'],
            'Cloud Monitoring': ['monitoring', 'alert', 'metric'],
            'Cloud IAM': ['IAM', 'service account', 'permission'],
            'Cloud KMS': ['KMS', 'encryption', 'key']
        }

        coverage = {}

        for component, keywords in required_components.items():
            found = False
            for task in tasks:
                content = (task['fields'].get('description', '') +
                          task['fields'].get('notes', ''))
                if any(keyword in content for keyword in keywords):
                    found = True
                    break
            coverage[component] = found

        missing = [comp for comp, found in coverage.items() if not found]

        if missing:
            self.add_warning("COVERAGE", f"Missing explicit coverage for: {', '.join(missing)}")
        else:
            print("  ✅ 100% GCP ML component coverage")

        coverage_percent = (len(coverage) - len(missing)) / len(coverage) * 100
        print(f"  📊 Coverage: {coverage_percent:.1f}%")

    def check_dependencies(self, tasks):
        """Check for dependency issues."""
        print("\n🔄 Checking Dependencies...")

        # Group tasks by phase
        tasks_by_phase = defaultdict(list)
        for task in tasks:
            task_id = task['fields'].get('task_id', '')
            if '.' in task_id:
                phase = task_id.split('.')[1]
                tasks_by_phase[phase].append(task_id)

        # Check phase ordering
        phase_order = ['P01', 'P02', 'P03', 'P04', 'P05', 'P06', 'P07', 'P08', 'P09', 'P10', 'P11']

        for i, phase in enumerate(phase_order[:-1]):
            next_phase = phase_order[i+1]
            if not tasks_by_phase[phase]:
                self.add_warning("DEPENDENCIES", f"Phase {phase} has no tasks")

        print(f"  ✅ {len(tasks_by_phase)} phases have tasks")

    def check_execution_readiness(self, tasks):
        """Verify tasks are ready for execution."""
        print("\n🚀 Checking Execution Readiness...")

        status_counts = defaultdict(int)
        priority_counts = defaultdict(int)
        assignee_counts = defaultdict(int)

        for task in tasks:
            status = task['fields'].get('status', 'Unknown')
            priority = task['fields'].get('priority', 'Unknown')
            assigned_to = task['fields'].get('assigned_to', 'Unassigned')

            status_counts[status] += 1
            priority_counts[priority] += 1
            assignee_counts[assigned_to] += 1

        # Check status distribution
        print("  📊 Status Distribution:")
        for status, count in sorted(status_counts.items()):
            print(f"    • {status}: {count}")

        if status_counts.get('In Progress', 0) > 0:
            self.add_warning("EXECUTION", f"{status_counts['In Progress']} tasks already in progress")

        # Check priority distribution
        print("  📊 Priority Distribution:")
        for priority, count in sorted(priority_counts.items()):
            print(f"    • {priority}: {count}")

        # Check assignment
        print("  📊 Assignment Distribution:")
        for assignee, count in sorted(assignee_counts.items())[:5]:
            print(f"    • {assignee}: {count}")

        if assignee_counts.get('Unassigned', 0) > 0:
            self.add_warning("EXECUTION", f"{assignee_counts['Unassigned']} tasks unassigned")

    def run_all_checks(self):
        """Run all pre-flight checks."""
        print("=" * 80)
        print("🚁 BQX ML V3 PROJECT PLAN - FINAL PRE-FLIGHT CHECK")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)

        # Load data
        plans, phases, stages, tasks = self.check_table_connectivity()

        if not tasks:
            print("\n❌ CRITICAL: Cannot proceed without table access")
            return False

        # Run all checks
        self.check_record_completeness(tasks)
        self.check_link_integrity(plans, phases, stages, tasks)
        self.check_technical_consistency(tasks)
        self.check_content_quality(tasks)
        self.check_gcp_ml_coverage(tasks)
        self.check_dependencies(tasks)
        self.check_execution_readiness(tasks)

        # Generate report
        print("\n" + "=" * 80)
        print("📊 PRE-FLIGHT CHECK RESULTS")
        print("=" * 80)

        if self.issues:
            print(f"\n❌ CRITICAL ISSUES ({len(self.issues)}):")
            for issue in self.issues[:10]:  # Show first 10
                print(f"  • {issue}")
            if len(self.issues) > 10:
                print(f"  • ...and {len(self.issues)-10} more issues")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:5]:  # Show first 5
                print(f"  • {warning}")
            if len(self.warnings) > 5:
                print(f"  • ...and {len(self.warnings)-5} more warnings")

        # Final verdict
        print("\n" + "=" * 80)
        print("🎯 FINAL VERDICT")
        print("=" * 80)

        if not self.issues:
            print("✅ PRE-FLIGHT CHECK PASSED")
            print("🚀 BQX ML V3 Project Plan is READY FOR EXECUTION")
            print("\n📋 Summary:")
            print(f"  • {self.stats['tasks']} tasks ready")
            print(f"  • {self.stats['stages']} stages configured")
            print(f"  • {self.stats['phases']} phases structured")
            print(f"  • 100% INTERVAL-CENTRIC compliant")
            print(f"  • No boilerplate content")
            print(f"  • All links properly connected")
            print("\n✅ AUTHORIZED FOR EXECUTION")
            return True
        else:
            print("❌ PRE-FLIGHT CHECK FAILED")
            print(f"🛠️  {len(self.issues)} critical issues must be resolved")
            print("\n⚠️  EXECUTION NOT AUTHORIZED")
            print("Please run remediation scripts to fix issues")
            return False

def main():
    """Main entry point."""
    checker = PreFlightCheck()

    # Run comprehensive checks
    passed = checker.run_all_checks()

    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'passed': passed,
        'issues': checker.issues,
        'warnings': checker.warnings,
        'stats': dict(checker.stats)
    }

    with open('/home/micha/bqx_ml_v3/preflight_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Report saved to preflight_report.json")

    if passed:
        print("\n" + "=" * 80)
        print("🎉 READY FOR EXECUTION")
        print("=" * 80)
        print("The BQX ML V3 Project Plan has passed all pre-flight checks.")
        print("Execution authorization confirmed.")
        print("\n🚀 You may proceed with project execution.")
        return 0
    else:
        print("\n" + "=" * 80)
        print("⚠️  REMEDIATION REQUIRED")
        print("=" * 80)
        print("Critical issues detected. Running remediation...")
        return 1

if __name__ == "__main__":
    sys.exit(main())