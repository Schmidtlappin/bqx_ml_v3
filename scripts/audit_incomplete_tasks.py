#!/usr/bin/env python3
"""
Audit all incomplete tasks and create a work sequence for completion.
"""

import json
from collections import defaultdict
from pyairtable import Api

# Load credentials
with open('/home/micha/bqx_ml_v3/.secrets/github_secrets.json', 'r') as f:
    secrets = json.load(f)
    API_KEY = secrets['secrets']['AIRTABLE_API_KEY']['value']
    BASE_ID = secrets['secrets']['AIRTABLE_BASE_ID']['value']

api = Api(API_KEY)
base = api.base(BASE_ID)
tasks_table = base.table('Tasks')

def main():
    print("="*80)
    print("🔍 BQX ML V3 - COMPREHENSIVE TASK AUDIT")
    print("="*80)

    # Get all tasks
    tasks = tasks_table.all()

    # Categorize tasks
    phase_tasks = defaultdict(lambda: {'done': [], 'todo': []})
    total_done = 0
    total_todo = 0

    for task in tasks:
        task_id = task['fields'].get('task_id', '')
        task_name = task['fields'].get('name', '')
        status = task['fields'].get('status', '')
        priority = task['fields'].get('priority', 'Medium')

        if '.' in task_id:
            phase = task_id.split('.')[1]

            task_info = {
                'id': task_id,
                'name': task_name[:60],
                'priority': priority,
                'status': status
            }

            if status == 'Done':
                phase_tasks[phase]['done'].append(task_info)
                total_done += 1
            else:
                phase_tasks[phase]['todo'].append(task_info)
                total_todo += 1

    # Print overall summary
    print(f"\n📊 OVERALL STATUS:")
    print(f"  Total Tasks: {total_done + total_todo}")
    print(f"  Completed: {total_done} ({total_done/(total_done+total_todo)*100:.1f}%)")
    print(f"  Remaining: {total_todo} ({total_todo/(total_done+total_todo)*100:.1f}%)")

    # Phase-by-phase analysis
    print("\n" + "="*80)
    print("📋 PHASE-BY-PHASE ANALYSIS")
    print("="*80)

    for phase in sorted(phase_tasks.keys()):
        done_count = len(phase_tasks[phase]['done'])
        todo_count = len(phase_tasks[phase]['todo'])
        total_phase = done_count + todo_count
        completion_pct = (done_count / total_phase * 100) if total_phase > 0 else 0

        status_icon = "✅" if completion_pct == 100 else "🔄" if completion_pct > 0 else "⏳"

        print(f"\n{status_icon} Phase {phase}: {done_count}/{total_phase} ({completion_pct:.0f}%)")

        if todo_count > 0:
            print(f"  Remaining tasks ({todo_count}):")

            # Sort by priority
            priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
            sorted_todos = sorted(phase_tasks[phase]['todo'],
                                key=lambda x: priority_order.get(x['priority'], 2))

            for i, task in enumerate(sorted_todos[:5], 1):  # Show first 5
                priority_icon = "🔴" if task['priority'] == 'Critical' else "🟠" if task['priority'] == 'High' else "🟢"
                print(f"    {i}. {priority_icon} {task['id']}: {task['name']}")

            if todo_count > 5:
                print(f"    ... and {todo_count - 5} more")

    # Create work sequence
    print("\n" + "="*80)
    print("🎯 RECOMMENDED WORK SEQUENCE")
    print("="*80)

    work_sequence = []

    # Priority order for phases (logical dependencies)
    phase_priority = [
        ('P02', 'Data Indexing - Foundation for all data operations'),
        ('P03', 'Cross-Validation - Essential for model training'),
        ('P04', 'Model Optimization - Core ML functionality'),
        ('P05', 'Currency Pairs - Configure all 28 pairs'),
        ('P06', 'BQX Paradigm - Core feature implementation'),
        ('P07', 'Advanced Features - Enhanced capabilities'),
        ('P08', 'Performance - Optimization for production'),
        ('P09', 'Deployment - Vertex AI serving'),
        ('P10', 'Production Validation - Testing & QA'),
        ('P11', 'Security & Compliance - Final hardening')
    ]

    print("\n📝 EXECUTION PLAN:")
    print("-" * 40)

    batch_size = 10  # Tasks per batch
    current_batch = 1

    for phase, description in phase_priority:
        if phase in phase_tasks and len(phase_tasks[phase]['todo']) > 0:
            todo_tasks = phase_tasks[phase]['todo']

            # Sort by priority
            priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
            sorted_tasks = sorted(todo_tasks,
                                key=lambda x: priority_order.get(x['priority'], 2))

            work_sequence.extend(sorted_tasks)

            print(f"\n📌 {phase}: {description}")
            print(f"   {len(todo_tasks)} tasks to complete")

    # Create execution batches
    print("\n" + "="*80)
    print("⚙️ EXECUTION BATCHES")
    print("="*80)

    total_batches = (len(work_sequence) + batch_size - 1) // batch_size

    print(f"\nTotal tasks to execute: {len(work_sequence)}")
    print(f"Batch size: {batch_size} tasks")
    print(f"Number of batches: {total_batches}")

    # Show first 3 batches in detail
    for batch_num in range(min(3, total_batches)):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(work_sequence))
        batch_tasks = work_sequence[start_idx:end_idx]

        print(f"\n📦 Batch {batch_num + 1} ({len(batch_tasks)} tasks):")
        for task in batch_tasks[:5]:  # Show first 5 of each batch
            print(f"  • {task['id']}: {task['name']}")
        if len(batch_tasks) > 5:
            print(f"  ... and {len(batch_tasks) - 5} more")

    if total_batches > 3:
        print(f"\n... and {total_batches - 3} more batches")

    # Implementation strategy
    print("\n" + "="*80)
    print("🚀 IMPLEMENTATION STRATEGY")
    print("="*80)

    print("\n1. IMMEDIATE ACTIONS (Next 10 tasks):")
    print("   Complete remaining P02 Data Indexing tasks")
    print("   Finish P03 Cross-Validation setup")

    print("\n2. SHORT-TERM (Tasks 11-50):")
    print("   Complete P04 Model Optimization")
    print("   Set up all P05 Currency Pairs")
    print("   Begin P06 BQX Paradigm implementation")

    print("\n3. MID-TERM (Tasks 51-100):")
    print("   Complete P06 BQX features")
    print("   Implement P07 Advanced Features")
    print("   Start P08 Performance Optimization")

    print("\n4. FINAL PHASE (Tasks 101-125):")
    print("   Complete P09 Deployment")
    print("   Execute P10 Production Validation")
    print("   Finalize P11 Security & Compliance")

    # Time estimate
    print("\n" + "="*80)
    print("⏱️ EXECUTION METRICS")
    print("="*80)

    print(f"\n• Tasks remaining: {total_todo}")
    print(f"• Current completion rate: ~10 tasks/batch")
    print(f"• Estimated batches: {total_batches}")
    print(f"• Rate limiting: 0.5 sec/task (AirTable API)")
    print(f"• Estimated time: {total_todo * 0.5 / 60:.1f} minutes for AirTable updates")
    print(f"• Plus actual GCP resource creation time")

    # Save work sequence to file
    print("\n" + "="*80)
    print("💾 SAVING WORK SEQUENCE")
    print("="*80)

    with open('/home/micha/bqx_ml_v3/work_sequence.json', 'w') as f:
        json.dump({
            'total_tasks': len(work_sequence),
            'batch_size': batch_size,
            'total_batches': total_batches,
            'tasks': work_sequence
        }, f, indent=2)

    print("✅ Work sequence saved to work_sequence.json")
    print(f"   Total tasks: {len(work_sequence)}")
    print(f"   Ready for systematic execution")

    return work_sequence

if __name__ == "__main__":
    work_sequence = main()