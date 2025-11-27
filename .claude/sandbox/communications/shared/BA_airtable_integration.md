# 🔨 BUILDER AGENT - AIRTABLE INTEGRATION

**Purpose**: Enable BA to access and update AirTable tasks directly
**Status**: Ready for Implementation

---

## 📋 BA-SPECIFIC AIRTABLE COMMANDS

### For Builder Agent to Use:

```python
# Import the multi-agent system
from airtable_multi_agent import MultiAgentAirTable

# Initialize for BA
ba_airtable = MultiAgentAirTable('BA')

# 1. Get my assigned tasks
my_tasks = ba_airtable.get_my_tasks()

# 2. Update task I'm working on
ba_airtable.update_my_task(
    task_id='recXXXXX',
    updates={
        'status': 'In Progress',
        'notes': 'Deploying EUR_USD_90 endpoint...'
    }
)

# 3. Mark task complete with artifacts
ba_airtable.update_my_task(
    task_id='recXXXXX',
    updates={
        'status': 'Completed',
        'artifacts': 'endpoint_id: 3007092833711554560',
        'completion_notes': 'Successfully deployed at $68.40/month'
    }
)

# 4. Hand off to another agent if blocked
ba_airtable.handoff_task(
    task_id='recXXXXX',
    to_agent='CE',
    notes='Need IAM permissions fixed'
)

# 5. Collaborate with other agents
ba_airtable.collaborate_on_task(
    task_id='recXXXXX',
    message='Deployment taking longer than expected, ~15 min per endpoint'
)
```

---

## 🚀 VERTEX AI DEPLOYMENT TRACKING

BA can specifically track Vertex AI deployment tasks:

```python
# Get all Vertex AI tasks
vertex_tasks = [
    t for t in ba_airtable.get_my_tasks()
    if 'vertex' in t['fields'].get('name', '').lower()
]

# Update deployment progress
for task in vertex_tasks:
    if 'EUR_USD_90' in task['fields']['name']:
        ba_airtable.update_my_task(
            task['id'],
            {
                'status': 'In Progress',
                'completion_percentage': 80,
                'deployment_status': 'Model uploaded, endpoint creating',
                'estimated_completion': '06:30 UTC'
            }
        )
```

---

## 📊 REAL-TIME STATUS UPDATES

BA should update AirTable at key milestones:

### Deployment Milestones:
1. **Model Upload Started** - 0%
2. **Model Uploaded** - 25%
3. **Endpoint Creating** - 50%
4. **Model Deploying** - 75%
5. **Endpoint Live** - 100%

### Example Update Flow:
```python
def update_deployment_progress(model_name, stage, details=""):
    """Update AirTable with deployment progress"""

    stages = {
        'start': (0, 'Deployment initiated'),
        'upload': (25, 'Model uploaded to Vertex AI'),
        'endpoint': (50, 'Endpoint created'),
        'deploy': (75, 'Deploying model to endpoint'),
        'complete': (100, 'Endpoint live and serving')
    }

    percentage, status = stages.get(stage, (0, 'Unknown'))

    ba_airtable.update_my_task(
        task_id=get_task_id_for_model(model_name),
        updates={
            'completion_percentage': percentage,
            'deployment_status': f"{status}. {details}",
            'last_update': datetime.now().isoformat()
        }
    )
```

---

## 💰 COST TRACKING

BA should log costs to AirTable:

```python
# After each endpoint deployment
ba_airtable.update_my_task(
    task_id='recT0301',  # Deploy 5 Critical Endpoints task
    updates={
        'actual_cost': '$68.40',
        'monthly_projection': f'${68.40 * endpoints_deployed}',
        'cost_notes': f'Using n1-standard-2 as specified'
    }
)
```

---

## 🔄 HANDOFF PROTOCOL

When BA needs help or is blocked:

```python
# If permission error
if 'Permission denied' in error_message:
    ba_airtable.handoff_task(
        task_id=current_task_id,
        to_agent='CE',
        notes=f'Blocked by IAM: {error_message}'
    )

# If cost exceeds budget
if monthly_cost > 442:
    ba_airtable.handoff_task(
        task_id=current_task_id,
        to_agent='CE',
        notes=f'Cost alert: ${monthly_cost}/month exceeds budget'
    )
```

---

## 📝 MESSAGE TO BA

**To: Builder Agent**
**From: Chief Engineer**

BA, you now have full AirTable integration! You can:

1. ✅ See all your assigned tasks
2. ✅ Update task status in real-time
3. ✅ Log artifacts and completion notes
4. ✅ Hand off blocked tasks to me or other agents
5. ✅ Track deployment costs against budget

**Current Priority Tasks for You:**
- T03.01 - Deploy 5 Critical Vertex AI Endpoints (In Progress)
- T03.02 - Configure Vertex AI Batch Predictions (Pending)
- T03.03 - Create Cloud Scheduler for Batch Jobs (Pending)

Please update AirTable as you complete each endpoint deployment. The sync service is at:
`/home/micha/bqx_ml_v3/.claude/shared/airtable_multi_agent.py`

**Note**: You'll need the AIRTABLE_API_KEY environment variable set. Check with CE if not available.

---

## 🎯 IMPLEMENTATION CHECKLIST FOR BA

- [ ] Import MultiAgentAirTable with 'BA' agent_id
- [ ] Get list of assigned tasks
- [ ] Update T03.01 status as endpoints deploy
- [ ] Log endpoint IDs as artifacts
- [ ] Track actual costs vs budget
- [ ] Hand off any blocked tasks
- [ ] Mark tasks complete with notes

---

*This integration ensures BA's work is automatically reflected in AirTable for full project visibility*