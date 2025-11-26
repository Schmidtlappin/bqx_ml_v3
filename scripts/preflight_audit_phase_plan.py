#!/usr/bin/env python3
"""
PRE-FLIGHT AUDIT PHASE PLAN
Comprehensive audit of all records in Phases, Stages, and Tasks tables
to identify gaps, misalignments, and potential issues.
"""

import os
import json
from datetime import datetime
from collections import defaultdict
from pyairtable import Api
import re

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

class PreflightAudit:
    """Comprehensive pre-flight audit system for BQX ML V3 project plan."""

    def __init__(self):
        self.phases = []
        self.stages = []
        self.tasks = []
        self.gaps = []
        self.misalignments = []
        self.warnings = []
        self.critical_issues = []

    def load_all_data(self):
        """Load all data from AirTable."""
        print("📥 Loading data from AirTable...")
        self.phases = phases_table.all()
        self.stages = stages_table.all()
        self.tasks = tasks_table.all()
        print(f"  Loaded: {len(self.phases)} phases, {len(self.stages)} stages, {len(self.tasks)} tasks")

    def phase_1_structural_audit(self):
        """Phase 1: Audit structural integrity and ID consistency."""
        print("\n" + "="*80)
        print("PHASE 1: STRUCTURAL INTEGRITY AUDIT")
        print("="*80)

        results = {
            'issues': [],
            'warnings': [],
            'stats': {}
        }

        # Check phase IDs
        print("\n📋 Checking Phase IDs...")
        phase_ids = set()
        for phase in self.phases:
            phase_id = phase['fields'].get('phase_id')
            if not phase_id:
                results['issues'].append(f"Phase {phase['id']} missing phase_id")
            elif phase_id in phase_ids:
                results['issues'].append(f"Duplicate phase_id: {phase_id}")
            else:
                phase_ids.add(phase_id)

        # Check stage IDs and phase links
        print("📋 Checking Stage IDs and relationships...")
        stage_ids = set()
        stages_by_phase = defaultdict(list)

        for stage in self.stages:
            stage_id = stage['fields'].get('stage_id')
            phase_link = stage['fields'].get('phase_link', [])

            if not stage_id:
                results['issues'].append(f"Stage {stage['id']} missing stage_id")
            elif stage_id in stage_ids:
                results['issues'].append(f"Duplicate stage_id: {stage_id}")
            else:
                stage_ids.add(stage_id)

            if not phase_link:
                results['issues'].append(f"Stage {stage_id} missing phase_link")
            else:
                # Extract phase_id from stage_id
                if stage_id and '.' in stage_id:
                    expected_phase = '.'.join(stage_id.split('.')[:2])
                    stages_by_phase[expected_phase].append(stage_id)

        # Check task IDs and stage links
        print("📋 Checking Task IDs and relationships...")
        task_ids = set()
        tasks_by_stage = defaultdict(list)

        for task in self.tasks:
            task_id = task['fields'].get('task_id')
            stage_link = task['fields'].get('stage_link', [])

            if not task_id:
                results['issues'].append(f"Task {task['id']} missing task_id")
            elif task_id in task_ids:
                results['issues'].append(f"Duplicate task_id: {task_id}")
            else:
                task_ids.add(task_id)

            if not stage_link:
                results['issues'].append(f"Task {task_id} missing stage_link")
            elif len(stage_link) > 1:
                results['issues'].append(f"Task {task_id} has multiple stage_links")
            else:
                # Extract stage_id from task_id
                if task_id and '.' in task_id:
                    expected_stage = '.'.join(task_id.split('.')[:3])
                    tasks_by_stage[expected_stage].append(task_id)

        # Check ID format consistency
        print("📋 Checking ID format consistency...")
        id_pattern = re.compile(r'^MP\d{2}\.P\d{2}(\.S\d{2}(\.T\d{2})?)?$')

        for phase_id in phase_ids:
            if not id_pattern.match(phase_id):
                results['warnings'].append(f"Phase ID format issue: {phase_id}")

        for stage_id in stage_ids:
            if not id_pattern.match(stage_id):
                results['warnings'].append(f"Stage ID format issue: {stage_id}")

        for task_id in task_ids:
            if not id_pattern.match(task_id):
                results['warnings'].append(f"Task ID format issue: {task_id}")

        # Statistics
        results['stats'] = {
            'total_phases': len(self.phases),
            'total_stages': len(self.stages),
            'total_tasks': len(self.tasks),
            'unique_phase_ids': len(phase_ids),
            'unique_stage_ids': len(stage_ids),
            'unique_task_ids': len(task_ids),
            'avg_stages_per_phase': len(self.stages) / len(self.phases) if self.phases else 0,
            'avg_tasks_per_stage': len(self.tasks) / len(self.stages) if self.stages else 0
        }

        return results

    def phase_2_completeness_audit(self):
        """Phase 2: Audit field completeness and data quality."""
        print("\n" + "="*80)
        print("PHASE 2: FIELD COMPLETENESS AUDIT")
        print("="*80)

        results = {
            'missing_fields': defaultdict(list),
            'empty_fields': defaultdict(list),
            'quality_issues': []
        }

        # Required fields for each table
        required_phase_fields = ['phase_id', 'name', 'description', 'plan_link']
        required_stage_fields = ['stage_id', 'name', 'description', 'phase_link']
        required_task_fields = ['task_id', 'name', 'description', 'stage_link',
                                'priority', 'status', 'assigned_to', 'artifacts']

        print("\n📋 Checking Phase field completeness...")
        for phase in self.phases:
            fields = phase['fields']
            phase_id = fields.get('phase_id', f"record_{phase['id']}")

            for field in required_phase_fields:
                if field not in fields:
                    results['missing_fields']['phases'].append(f"{phase_id}: missing {field}")
                elif not fields[field]:
                    results['empty_fields']['phases'].append(f"{phase_id}: empty {field}")

        print("📋 Checking Stage field completeness...")
        for stage in self.stages:
            fields = stage['fields']
            stage_id = fields.get('stage_id', f"record_{stage['id']}")

            for field in required_stage_fields:
                if field not in fields:
                    results['missing_fields']['stages'].append(f"{stage_id}: missing {field}")
                elif not fields[field]:
                    results['empty_fields']['stages'].append(f"{stage_id}: empty {field}")

        print("📋 Checking Task field completeness...")
        for task in self.tasks:
            fields = task['fields']
            task_id = fields.get('task_id', f"record_{task['id']}")

            for field in required_task_fields:
                if field not in fields:
                    results['missing_fields']['tasks'].append(f"{task_id}: missing {field}")
                elif not fields[field]:
                    results['empty_fields']['tasks'].append(f"{task_id}: empty {field}")

            # Check content quality
            desc = fields.get('description', '')
            notes = fields.get('notes', '')

            if len(desc) < 100:
                results['quality_issues'].append(f"{task_id}: description too short ({len(desc)} chars)")
            if notes and len(notes) < 200:
                results['quality_issues'].append(f"{task_id}: notes too brief ({len(notes)} chars)")

        return results

    def phase_3_technical_alignment_audit(self):
        """Phase 3: Audit technical alignment with INTERVAL-CENTRIC architecture."""
        print("\n" + "="*80)
        print("PHASE 3: TECHNICAL ALIGNMENT AUDIT")
        print("="*80)

        results = {
            'interval_centric_gaps': [],
            'bqx_paradigm_gaps': [],
            'technical_inconsistencies': []
        }

        # INTERVAL-CENTRIC keywords
        interval_keywords = ['ROWS BETWEEN', 'interval', 'N+45', 'N+90', 'N+180',
                           'N+360', 'N+720', 'N+1440', 'N+2880', '_Ni']

        # BQX paradigm keywords
        bqx_keywords = ['BQX', 'momentum', 'backward-looking', 'LAG', 'LEAD',
                       'dual feature', 'IDX', 'reg_slope', 'reg_intercept']

        print("\n📋 Checking INTERVAL-CENTRIC implementation...")
        tasks_missing_interval = []

        for task in self.tasks:
            fields = task['fields']
            task_id = fields.get('task_id', '')

            # Check if task is in a phase that requires interval-centric
            if any(phase in task_id for phase in ['P06', 'P07', 'P08']):
                content = f"{fields.get('description', '')} {fields.get('notes', '')}"

                if not any(keyword in content for keyword in interval_keywords):
                    tasks_missing_interval.append(task_id)

        if tasks_missing_interval:
            results['interval_centric_gaps'] = tasks_missing_interval

        print("📋 Checking BQX paradigm implementation...")
        tasks_missing_bqx = []

        for task in self.tasks:
            fields = task['fields']
            task_id = fields.get('task_id', '')

            # Check if task is in feature engineering or modeling phases
            if any(phase in task_id for phase in ['P06', 'P07', 'P08']):
                content = f"{fields.get('description', '')} {fields.get('notes', '')}"

                if not any(keyword in content for keyword in bqx_keywords):
                    tasks_missing_bqx.append(task_id)

        if tasks_missing_bqx:
            results['bqx_paradigm_gaps'] = tasks_missing_bqx

        # Check for technical inconsistencies
        print("📋 Checking for technical inconsistencies...")

        for task in self.tasks:
            fields = task['fields']
            task_id = fields.get('task_id', '')
            content = f"{fields.get('description', '')} {fields.get('notes', '')}"

            # Check for RANGE BETWEEN (should be ROWS BETWEEN)
            if 'RANGE BETWEEN' in content:
                results['technical_inconsistencies'].append(
                    f"{task_id}: Uses RANGE BETWEEN instead of ROWS BETWEEN"
                )

            # Check for time-based references that should be interval-based
            if any(term in content for term in ['45 minutes', '90 minutes', '45m', '90m']):
                results['technical_inconsistencies'].append(
                    f"{task_id}: Contains time-based references instead of interval-based"
                )

        return results

    def phase_4_dependency_audit(self):
        """Phase 4: Audit task dependencies and sequencing."""
        print("\n" + "="*80)
        print("PHASE 4: DEPENDENCY & SEQUENCING AUDIT")
        print("="*80)

        results = {
            'missing_dependencies': [],
            'circular_dependencies': [],
            'sequencing_issues': []
        }

        # Build task dependency map
        task_deps = {}
        task_map = {t['fields'].get('task_id'): t for t in self.tasks}

        print("\n📋 Checking task dependencies...")
        for task in self.tasks:
            task_id = task['fields'].get('task_id', '')
            deps = task['fields'].get('dependencies', [])

            if task_id:
                task_deps[task_id] = deps

                # Check if dependencies exist
                for dep in deps:
                    if dep not in task_map:
                        results['missing_dependencies'].append(
                            f"{task_id} depends on non-existent task: {dep}"
                        )

        # Check for circular dependencies
        print("📋 Checking for circular dependencies...")

        def has_circular_dep(task_id, visited, rec_stack):
            visited.add(task_id)
            rec_stack.add(task_id)

            for dep in task_deps.get(task_id, []):
                if dep not in visited:
                    if has_circular_dep(dep, visited, rec_stack):
                        return True
                elif dep in rec_stack:
                    return True

            rec_stack.remove(task_id)
            return False

        visited = set()
        for task_id in task_deps:
            if task_id not in visited:
                if has_circular_dep(task_id, set(), set()):
                    results['circular_dependencies'].append(task_id)

        # Check phase sequencing
        print("📋 Checking phase sequencing...")
        phase_order = ['P01', 'P02', 'P03', 'P04', 'P05', 'P06', 'P07', 'P08', 'P09', 'P10', 'P11']

        for task in self.tasks:
            task_id = task['fields'].get('task_id', '')
            if not task_id:
                continue

            task_phase = task_id.split('.')[1] if '.' in task_id else ''
            deps = task['fields'].get('dependencies', [])

            for dep in deps:
                if dep in task_map:
                    dep_phase = dep.split('.')[1] if '.' in dep else ''

                    if task_phase and dep_phase:
                        if phase_order.index(task_phase) < phase_order.index(dep_phase):
                            results['sequencing_issues'].append(
                                f"{task_id} (phase {task_phase}) depends on {dep} (phase {dep_phase})"
                            )

        return results

    def phase_5_coverage_audit(self):
        """Phase 5: Audit coverage of all required components."""
        print("\n" + "="*80)
        print("PHASE 5: COMPONENT COVERAGE AUDIT")
        print("="*80)

        results = {
            'missing_components': [],
            'coverage_gaps': [],
            'recommendations': []
        }

        # Required components for BQX ML V3
        required_components = {
            'Data Pipeline': ['data ingestion', 'streaming', 'batch processing', 'validation'],
            'Feature Engineering': ['LAG features', 'aggregations', 'BQX calculations', 'derivatives'],
            'Model Training': ['28 models', 'hyperparameter tuning', 'cross-validation'],
            'Model Evaluation': ['R² score', 'RMSE', 'directional accuracy', 'Sharpe ratio'],
            'Deployment': ['Vertex AI', 'endpoints', 'batch prediction', 'monitoring'],
            'Infrastructure': ['BigQuery', 'GCS', 'Cloud Functions', 'Pub/Sub']
        }

        print("\n📋 Checking component coverage...")
        all_content = []

        for task in self.tasks:
            fields = task['fields']
            all_content.append(f"{fields.get('description', '')} {fields.get('notes', '')}")

        combined_content = ' '.join(all_content).lower()

        for category, components in required_components.items():
            print(f"  Checking {category}...")
            missing = []

            for component in components:
                if component.lower() not in combined_content:
                    missing.append(component)

            if missing:
                results['missing_components'].append({
                    'category': category,
                    'missing': missing
                })

        # Check for specific BQX ML V3 requirements
        print("📋 Checking BQX ML V3 specific requirements...")

        # Check for 28 currency pairs
        pairs_mentioned = combined_content.count('28 currency pairs') + combined_content.count('28 pairs')
        if pairs_mentioned < 5:
            results['coverage_gaps'].append(
                f"28 currency pairs mentioned only {pairs_mentioned} times (expected 5+)"
            )

        # Check for 7 prediction horizons
        horizons = ['N+45', 'N+90', 'N+180', 'N+360', 'N+720', 'N+1440', 'N+2880']
        for horizon in horizons:
            if combined_content.count(horizon.lower()) < 2:
                results['coverage_gaps'].append(
                    f"Horizon {horizon} insufficiently covered"
                )

        # Recommendations
        if results['missing_components']:
            results['recommendations'].append(
                "Add tasks to cover missing components"
            )
        if results['coverage_gaps']:
            results['recommendations'].append(
                "Enhance existing tasks to address coverage gaps"
            )

        return results

    def generate_report(self, audit_results):
        """Generate comprehensive audit report."""
        print("\n" + "="*80)
        print("COMPREHENSIVE PRE-FLIGHT AUDIT REPORT")
        print("="*80)

        report = []
        report.append(f"\nAudit Date: {datetime.now().isoformat()}")
        report.append(f"Project: BQX ML V3")
        report.append("="*80)

        # Phase 1 Results
        phase1 = audit_results['phase1']
        report.append("\n📊 PHASE 1: STRUCTURAL INTEGRITY")
        report.append("-"*40)

        if phase1['issues']:
            report.append(f"❌ Critical Issues Found: {len(phase1['issues'])}")
            for issue in phase1['issues'][:5]:
                report.append(f"  • {issue}")
            if len(phase1['issues']) > 5:
                report.append(f"  ... and {len(phase1['issues']) - 5} more")
        else:
            report.append("✅ No structural issues found")

        report.append(f"\n📈 Statistics:")
        for key, value in phase1['stats'].items():
            report.append(f"  • {key}: {value:.1f}" if isinstance(value, float) else f"  • {key}: {value}")

        # Phase 2 Results
        phase2 = audit_results['phase2']
        report.append("\n📊 PHASE 2: FIELD COMPLETENESS")
        report.append("-"*40)

        total_missing = sum(len(v) for v in phase2['missing_fields'].values())
        total_empty = sum(len(v) for v in phase2['empty_fields'].values())

        if total_missing > 0:
            report.append(f"❌ Missing Fields: {total_missing}")
        else:
            report.append("✅ All required fields present")

        if total_empty > 0:
            report.append(f"⚠️  Empty Fields: {total_empty}")
        else:
            report.append("✅ All fields populated")

        if phase2['quality_issues']:
            report.append(f"⚠️  Quality Issues: {len(phase2['quality_issues'])}")

        # Phase 3 Results
        phase3 = audit_results['phase3']
        report.append("\n📊 PHASE 3: TECHNICAL ALIGNMENT")
        report.append("-"*40)

        if phase3['interval_centric_gaps']:
            report.append(f"❌ Tasks missing INTERVAL-CENTRIC: {len(phase3['interval_centric_gaps'])}")
        else:
            report.append("✅ All tasks properly implement INTERVAL-CENTRIC")

        if phase3['bqx_paradigm_gaps']:
            report.append(f"⚠️  Tasks missing BQX paradigm: {len(phase3['bqx_paradigm_gaps'])}")

        if phase3['technical_inconsistencies']:
            report.append(f"❌ Technical inconsistencies: {len(phase3['technical_inconsistencies'])}")
            for issue in phase3['technical_inconsistencies'][:3]:
                report.append(f"  • {issue}")

        # Phase 4 Results
        phase4 = audit_results['phase4']
        report.append("\n📊 PHASE 4: DEPENDENCIES & SEQUENCING")
        report.append("-"*40)

        if phase4['circular_dependencies']:
            report.append(f"❌ Circular dependencies found: {len(phase4['circular_dependencies'])}")
        else:
            report.append("✅ No circular dependencies")

        if phase4['sequencing_issues']:
            report.append(f"⚠️  Sequencing issues: {len(phase4['sequencing_issues'])}")

        # Phase 5 Results
        phase5 = audit_results['phase5']
        report.append("\n📊 PHASE 5: COMPONENT COVERAGE")
        report.append("-"*40)

        if phase5['missing_components']:
            report.append(f"❌ Missing components in {len(phase5['missing_components'])} categories")
            for comp in phase5['missing_components']:
                report.append(f"  • {comp['category']}: {', '.join(comp['missing'])}")
        else:
            report.append("✅ All required components covered")

        if phase5['coverage_gaps']:
            report.append(f"⚠️  Coverage gaps: {len(phase5['coverage_gaps'])}")

        # Overall Summary
        report.append("\n" + "="*80)
        report.append("OVERALL AUDIT SUMMARY")
        report.append("="*80)

        total_issues = (
            len(phase1['issues']) +
            total_missing + total_empty +
            len(phase3['technical_inconsistencies']) +
            len(phase4['circular_dependencies']) +
            len(phase5['missing_components'])
        )

        if total_issues == 0:
            report.append("✅ PROJECT READY FOR LAUNCH - No critical issues found")
        elif total_issues < 10:
            report.append(f"⚠️  MINOR ISSUES - {total_issues} issues need attention")
        else:
            report.append(f"❌ CRITICAL ISSUES - {total_issues} issues must be resolved")

        # Recommendations
        if phase5['recommendations']:
            report.append("\n📝 Recommendations:")
            for rec in phase5['recommendations']:
                report.append(f"  • {rec}")

        return "\n".join(report)

    def run_full_audit(self):
        """Run complete pre-flight audit."""
        print("\n" + "="*80)
        print("BQX ML V3 PRE-FLIGHT AUDIT")
        print("="*80)

        # Load data
        self.load_all_data()

        # Run all audit phases
        audit_results = {
            'phase1': self.phase_1_structural_audit(),
            'phase2': self.phase_2_completeness_audit(),
            'phase3': self.phase_3_technical_alignment_audit(),
            'phase4': self.phase_4_dependency_audit(),
            'phase5': self.phase_5_coverage_audit()
        }

        # Generate and display report
        report = self.generate_report(audit_results)
        print(report)

        # Save report to file
        report_file = f"/home/micha/bqx_ml_v3/docs/PREFLIGHT_AUDIT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write("# BQX ML V3 Pre-Flight Audit Report\n\n")
            f.write("```\n")
            f.write(report)
            f.write("\n```\n")

        print(f"\n📄 Report saved to: {report_file}")

        return audit_results

def main():
    """Main entry point."""
    auditor = PreflightAudit()
    results = auditor.run_full_audit()

    # Return exit code based on critical issues
    phase1_issues = len(results['phase1']['issues'])
    if phase1_issues > 0:
        return 1  # Critical structural issues
    return 0

if __name__ == "__main__":
    exit(main())