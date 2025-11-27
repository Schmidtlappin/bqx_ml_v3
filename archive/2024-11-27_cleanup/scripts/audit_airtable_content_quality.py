#!/usr/bin/env python3
"""
Audit AirTable content quality and sequencing for BQX ML V3 project.
Identifies boilerplate descriptions, sequencing issues, and Build Agent requirements.
"""

import json
import os
import subprocess
from pyairtable import Api
from datetime import datetime
from collections import defaultdict, Counter
import re
from difflib import SequenceMatcher

# Get credentials from GCP Secrets Manager
def get_secret(secret_name):
    try:
        result = subprocess.run(
            ["gcloud", "secrets", "versions", "access", "latest", f"--secret={secret_name}"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except:
        return None

# Try GitHub secrets as fallback
def get_github_secret():
    try:
        with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
            secrets = json.load(f)
            api_key = secrets['secrets']['AIRTABLE_API_KEY']['value']
            base_id = secrets['secrets']['AIRTABLE_BASE_ID']['value']
            return api_key, base_id
    except:
        return None, None

# Get credentials
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY") or get_secret("bqx-ml-airtable-token")
BASE_ID = os.environ.get("AIRTABLE_BASE_ID") or get_secret("bqx-ml-airtable-base-id")

# Fallback to GitHub secrets
if not AIRTABLE_API_KEY or not BASE_ID:
    AIRTABLE_API_KEY, BASE_ID = get_github_secret()

if not AIRTABLE_API_KEY or not BASE_ID:
    raise ValueError("Could not load AirTable credentials from any source")

api = Api(AIRTABLE_API_KEY)
base = api.base(BASE_ID)

# Get all tables
tasks_table = base.table('Tasks')
stages_table = base.table('Stages')
phases_table = base.table('Phases')
plans_table = base.table('Plans')

def similarity_score(a, b):
    """Calculate similarity between two strings."""
    return SequenceMatcher(None, a, b).ratio()

def contains_boilerplate_phrases(text):
    """Check if text contains generic boilerplate phrases."""
    boilerplate_patterns = [
        r'establish.*infrastructure',
        r'implement.*system',
        r'develop.*framework',
        r'create.*process',
        r'set up.*environment',
        r'configure.*settings',
        r'optimize.*performance',
        r'ensure.*quality',
        r'maintain.*standards',
        r'complete.*implementation',
        r'finalize.*configuration',
        r'verify.*functionality',
        r'test.*implementation',
        r'document.*process',
        r'review.*implementation'
    ]

    text_lower = text.lower()
    for pattern in boilerplate_patterns:
        if re.search(pattern, text_lower):
            return True
    return False

def analyze_description_quality(description):
    """Analyze quality metrics for a description."""
    quality = {
        'length': len(description),
        'is_boilerplate': False,
        'has_specific_metrics': False,
        'has_technical_details': False,
        'has_build_agent_context': False,
        'issues': []
    }

    # Check length
    if quality['length'] < 100:
        quality['issues'].append('Too short (<100 chars)')
    elif quality['length'] > 500:
        quality['issues'].append('Too long (>500 chars)')

    # Check for boilerplate
    if contains_boilerplate_phrases(description):
        quality['is_boilerplate'] = True
        quality['issues'].append('Contains boilerplate phrases')

    # Check for specific metrics (numbers, thresholds, etc.)
    metrics_patterns = [r'\d+', r'R²', r'RMSE', r'\d+%', r'\d+x', r'≥', r'≤', r'threshold']
    if any(re.search(pattern, description) for pattern in metrics_patterns):
        quality['has_specific_metrics'] = True
    else:
        quality['issues'].append('No specific metrics or thresholds')

    # Check for technical details
    technical_patterns = [
        r'API', r'endpoint', r'pipeline', r'model', r'algorithm', r'container',
        r'deployment', r'monitoring', r'BQX', r'Vertex AI', r'GCP', r'Docker',
        r'Python', r'SQL', r'BigQuery', r'TensorFlow', r'sklearn'
    ]
    if any(re.search(pattern, description, re.IGNORECASE) for pattern in technical_patterns):
        quality['has_technical_details'] = True
    else:
        quality['issues'].append('Lacks technical details')

    # Check for Build Agent context
    agent_patterns = [
        r'script', r'command', r'execute', r'run', r'invoke', r'call',
        r'input', r'output', r'parameter', r'configuration', r'file',
        r'directory', r'path', r'environment', r'variable'
    ]
    if any(re.search(pattern, description, re.IGNORECASE) for pattern in agent_patterns):
        quality['has_build_agent_context'] = True
    else:
        quality['issues'].append('Missing Build Agent execution context')

    return quality

def analyze_task_dependencies(all_tasks):
    """Analyze task dependencies and sequencing issues."""
    dependencies = defaultdict(list)
    sequence_issues = []

    # Group tasks by phase and stage
    phase_tasks = defaultdict(list)
    stage_tasks = defaultdict(list)

    for task in all_tasks:
        task_id = task['fields'].get('task_id', '')
        parts = task_id.split('.')

        if len(parts) >= 2:
            phase = '.'.join(parts[:2])
            phase_tasks[phase].append(task)

        if len(parts) >= 3:
            stage = '.'.join(parts[:3])
            stage_tasks[stage].append(task)

    # Check for dependency patterns in descriptions and notes
    for task in all_tasks:
        task_id = task['fields'].get('task_id', '')
        description = task['fields'].get('description', '')
        notes = task['fields'].get('notes', '')
        combined_text = f"{description} {notes}".lower()

        # Look for dependency keywords
        if 'requires' in combined_text or 'depends on' in combined_text:
            dependencies[task_id].append('Has explicit dependencies')

        if 'before' in combined_text or 'prerequisite' in combined_text:
            dependencies[task_id].append('Is prerequisite for other tasks')

        if 'after' in combined_text or 'following' in combined_text:
            dependencies[task_id].append('Follows other tasks')

    # Check for sequencing issues
    for stage, tasks in stage_tasks.items():
        task_numbers = []
        for task in tasks:
            task_id = task['fields'].get('task_id', '')
            match = re.search(r'T(\d+)$', task_id)
            if match:
                task_numbers.append(int(match.group(1)))

        # Check for gaps in task numbering
        if task_numbers:
            task_numbers.sort()
            expected = list(range(1, len(task_numbers) + 1))
            if task_numbers != expected:
                sequence_issues.append({
                    'stage': stage,
                    'issue': 'Task numbering gaps',
                    'actual': task_numbers,
                    'expected': expected
                })

    return dependencies, sequence_issues

def generate_build_agent_requirements(task):
    """Generate Build Agent context requirements for a task."""
    task_id = task['fields'].get('task_id', '')
    task_name = task['fields'].get('name', '')

    requirements = {
        'execution_context': [],
        'required_inputs': [],
        'expected_outputs': [],
        'success_criteria': [],
        'error_handling': []
    }

    # Extract phase and stage for context
    parts = task_id.split('.')
    if len(parts) >= 2:
        phase = parts[1]

        # Phase-specific requirements
        if phase == 'P00':  # Setup
            requirements['execution_context'].append('Requires GCP project access')
            requirements['required_inputs'].append('Project configuration file')
            requirements['expected_outputs'].append('Initialized environment')

        elif phase in ['P01', 'P02']:  # Data preparation
            requirements['execution_context'].append('Requires BigQuery access')
            requirements['required_inputs'].append('Data source specifications')
            requirements['expected_outputs'].append('Preprocessed datasets')

        elif phase in ['P03', 'P04', 'P05']:  # Vertex AI phases
            requirements['execution_context'].append('Requires Vertex AI API access')
            requirements['required_inputs'].append('Model configuration')
            requirements['expected_outputs'].append('Deployed models/pipelines')

        elif phase in ['P08', 'P09']:  # Deployment and monitoring
            requirements['execution_context'].append('Requires production environment access')
            requirements['required_inputs'].append('Deployment specifications')
            requirements['expected_outputs'].append('Running services')

    # Task-specific requirements based on keywords
    task_lower = task_name.lower()

    if 'train' in task_lower:
        requirements['required_inputs'].append('Training data path')
        requirements['expected_outputs'].append('Trained model artifacts')
        requirements['success_criteria'].append('Model metrics meet thresholds')

    if 'test' in task_lower:
        requirements['required_inputs'].append('Test data path')
        requirements['expected_outputs'].append('Test results report')
        requirements['success_criteria'].append('All tests pass')

    if 'deploy' in task_lower:
        requirements['required_inputs'].append('Model artifacts')
        requirements['expected_outputs'].append('Deployment endpoint')
        requirements['success_criteria'].append('Endpoint responds to requests')

    if 'monitor' in task_lower:
        requirements['required_inputs'].append('Service endpoints')
        requirements['expected_outputs'].append('Monitoring dashboard')
        requirements['success_criteria'].append('Metrics within bounds')

    # Error handling
    requirements['error_handling'] = [
        'Log all errors to centralized logging',
        'Retry transient failures up to 3 times',
        'Alert on persistent failures'
    ]

    return requirements

def audit_content_quality():
    """Main audit function for content quality and sequencing."""

    print("🔍 AUDITING AIRTABLE CONTENT QUALITY AND SEQUENCING")
    print("=" * 80)

    # Get all records
    all_tasks = tasks_table.all()
    all_stages = stages_table.all()
    all_phases = phases_table.all()

    print(f"\nAnalyzing {len(all_tasks)} tasks across {len(all_phases)} phases")

    # Track audit results
    audit_results = {
        'total_tasks': len(all_tasks),
        'boilerplate_descriptions': [],
        'duplicate_descriptions': [],
        'missing_build_context': [],
        'sequencing_issues': [],
        'quality_scores': {}
    }

    # Analyze descriptions
    print("\n📋 ANALYZING DESCRIPTION QUALITY")
    print("-" * 60)

    description_texts = {}
    description_quality = {}

    for task in all_tasks:
        task_id = task['fields'].get('task_id', '')
        description = task['fields'].get('description', '')

        if description:
            # Store for duplicate detection
            description_texts[task_id] = description

            # Analyze quality
            quality = analyze_description_quality(description)
            description_quality[task_id] = quality

            # Track issues
            if quality['is_boilerplate']:
                audit_results['boilerplate_descriptions'].append({
                    'task_id': task_id,
                    'description': description[:100] + '...',
                    'issues': quality['issues']
                })

            if not quality['has_build_agent_context']:
                audit_results['missing_build_context'].append({
                    'task_id': task_id,
                    'name': task['fields'].get('name', '')[:50]
                })

    # Find duplicate descriptions
    print("\n🔄 DETECTING DUPLICATE DESCRIPTIONS")
    print("-" * 60)

    for task1_id, desc1 in description_texts.items():
        for task2_id, desc2 in description_texts.items():
            if task1_id < task2_id:  # Avoid duplicate comparisons
                similarity = similarity_score(desc1, desc2)
                if similarity > 0.8:  # 80% similar
                    audit_results['duplicate_descriptions'].append({
                        'task1': task1_id,
                        'task2': task2_id,
                        'similarity': f"{similarity:.1%}"
                    })

    # Analyze dependencies and sequencing
    print("\n🔗 ANALYZING TASK DEPENDENCIES AND SEQUENCING")
    print("-" * 60)

    dependencies, sequence_issues = analyze_task_dependencies(all_tasks)
    audit_results['sequencing_issues'] = sequence_issues

    # Generate quality scores
    print("\n📊 CALCULATING QUALITY SCORES")
    print("-" * 60)

    for task_id, quality in description_quality.items():
        score = 0
        max_score = 100

        # Length score (20 points)
        if 100 <= quality['length'] <= 300:
            score += 20
        elif 50 <= quality['length'] < 100 or 300 < quality['length'] <= 500:
            score += 10

        # Not boilerplate (30 points)
        if not quality['is_boilerplate']:
            score += 30

        # Has specific metrics (20 points)
        if quality['has_specific_metrics']:
            score += 20

        # Has technical details (15 points)
        if quality['has_technical_details']:
            score += 15

        # Has Build Agent context (15 points)
        if quality['has_build_agent_context']:
            score += 15

        audit_results['quality_scores'][task_id] = {
            'score': score,
            'max_score': max_score,
            'percentage': f"{score/max_score:.1%}"
        }

    # Generate summary report
    print("\n" + "=" * 80)
    print("📊 AUDIT SUMMARY REPORT")
    print("=" * 80)

    # Overall statistics
    total_tasks = audit_results['total_tasks']
    boilerplate_count = len(audit_results['boilerplate_descriptions'])
    duplicate_count = len(audit_results['duplicate_descriptions'])
    missing_context_count = len(audit_results['missing_build_context'])
    sequence_issue_count = len(audit_results['sequencing_issues'])

    print(f"\n📈 CONTENT QUALITY METRICS:")
    print(f"  • Total tasks analyzed: {total_tasks}")
    print(f"  • Boilerplate descriptions: {boilerplate_count} ({boilerplate_count/total_tasks*100:.1f}%)")
    print(f"  • Duplicate descriptions: {duplicate_count}")
    print(f"  • Missing Build Agent context: {missing_context_count} ({missing_context_count/total_tasks*100:.1f}%)")
    print(f"  • Sequencing issues: {sequence_issue_count}")

    # Quality score distribution
    scores = [q['score'] for q in audit_results['quality_scores'].values()]
    if scores:
        avg_score = sum(scores) / len(scores)
        print(f"\n📊 QUALITY SCORE DISTRIBUTION:")
        print(f"  • Average score: {avg_score:.1f}/100 ({avg_score:.1f}%)")
        print(f"  • Excellent (80-100): {len([s for s in scores if s >= 80])}")
        print(f"  • Good (60-79): {len([s for s in scores if 60 <= s < 80])}")
        print(f"  • Fair (40-59): {len([s for s in scores if 40 <= s < 60])}")
        print(f"  • Poor (0-39): {len([s for s in scores if s < 40])}")

    # Top boilerplate offenders
    if audit_results['boilerplate_descriptions']:
        print(f"\n⚠️  TOP BOILERPLATE DESCRIPTIONS:")
        for item in audit_results['boilerplate_descriptions'][:5]:
            print(f"  • {item['task_id']}: {item['description']}")
            print(f"    Issues: {', '.join(item['issues'])}")

    # Duplicate descriptions
    if audit_results['duplicate_descriptions']:
        print(f"\n🔄 DUPLICATE DESCRIPTIONS FOUND:")
        for item in audit_results['duplicate_descriptions'][:5]:
            print(f"  • {item['task1']} ↔ {item['task2']} ({item['similarity']} similar)")

    # Sequencing issues
    if audit_results['sequencing_issues']:
        print(f"\n🔀 SEQUENCING ISSUES:")
        for issue in audit_results['sequencing_issues'][:5]:
            print(f"  • Stage {issue['stage']}: {issue['issue']}")
            print(f"    Expected: {issue['expected']}")
            print(f"    Actual: {issue['actual']}")

    # Generate Build Agent requirements for sample tasks
    print("\n🤖 SAMPLE BUILD AGENT REQUIREMENTS:")
    print("-" * 60)

    sample_tasks = all_tasks[:3]  # First 3 tasks as examples
    for task in sample_tasks:
        task_id = task['fields'].get('task_id', '')
        task_name = task['fields'].get('name', '')
        requirements = generate_build_agent_requirements(task)

        print(f"\n📌 {task_id}: {task_name[:50]}")
        print(f"  Execution Context: {', '.join(requirements['execution_context'][:2])}")
        print(f"  Required Inputs: {', '.join(requirements['required_inputs'][:2])}")
        print(f"  Expected Outputs: {', '.join(requirements['expected_outputs'][:2])}")

    # Recommendations
    print("\n" + "=" * 80)
    print("💡 RECOMMENDATIONS")
    print("=" * 80)

    print("\n1. IMMEDIATE ACTIONS:")
    print(f"   • Replace {boilerplate_count} boilerplate descriptions with specific content")
    print(f"   • Add Build Agent context to {missing_context_count} tasks")
    print(f"   • Resolve {duplicate_count} duplicate descriptions")
    print(f"   • Fix {sequence_issue_count} sequencing issues")

    print("\n2. CONTENT IMPROVEMENTS NEEDED:")
    print("   • Add specific metrics and thresholds to descriptions")
    print("   • Include execution commands and parameters")
    print("   • Specify input/output file paths and formats")
    print("   • Define clear success criteria for each task")

    print("\n3. BUILD AGENT CONTEXT TEMPLATE:")
    print("   Each description should include:")
    print("   • What script/command to execute")
    print("   • Required environment variables")
    print("   • Input data sources and formats")
    print("   • Expected output artifacts")
    print("   • Success/failure criteria")

    # Save detailed report
    report_path = '/home/micha/bqx_ml_v3/docs/AIRTABLE_CONTENT_AUDIT_REPORT.json'
    with open(report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"\n📄 Detailed audit report saved to: {report_path}")

    print(f"\nAudit completed: {datetime.now().isoformat()}")
    print("=" * 80)

    return audit_results

if __name__ == "__main__":
    results = audit_content_quality()

    # Return exit code based on quality
    if len(results['boilerplate_descriptions']) > 50:
        print("\n❌ CRITICAL: More than 50 boilerplate descriptions found!")
        exit(1)
    elif len(results['boilerplate_descriptions']) > 20:
        print("\n⚠️  WARNING: Significant boilerplate content detected")
        exit(0)
    else:
        print("\n✅ Content quality is acceptable")
        exit(0)