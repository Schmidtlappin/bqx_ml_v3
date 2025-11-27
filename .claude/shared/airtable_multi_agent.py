#!/usr/bin/env python3
"""
Multi-Agent AirTable Integration
Enables CE, BA, MA, TA, and any other agents to access and update AirTable
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path

# Import the main sync service
import sys
sys.path.append('/home/micha/bqx_ml_v3/scripts')

class MultiAgentAirTable:
    """Multi-agent wrapper for AirTable integration"""

    AGENT_ROLES = {
        'CE': 'Chief Engineer',
        'BA': 'Builder Agent',
        'MA': 'Monitoring Agent',
        'TA': 'Testing Agent',
        'USER': 'Human User'
    }

    def __init__(self, agent_id: str = None):
        """Initialize for specific agent"""
        self.agent_id = agent_id or self._detect_agent()
        self.agent_name = self.AGENT_ROLES.get(self.agent_id, 'Unknown Agent')

        # Import sync service
        try:
            from airtable_sync_service import AirTableSync
            self.sync = AirTableSync()
            self.connected = True
        except Exception as e:
            print(f"⚠️ AirTable not connected: {e}")
            self.connected = False

    def _detect_agent(self) -> str:
        """Auto-detect which agent is running"""
        # Check environment variable
        if os.environ.get('AGENT_ID'):
            return os.environ.get('AGENT_ID')

        # Check message files
        if Path('/home/micha/bqx_ml_v3/.claude/sandbox/communications').exists():
            # Check recent messages to identify agent
            comm_dir = Path('/home/micha/bqx_ml_v3/.claude/sandbox/communications/active')
            for msg_file in sorted(comm_dir.glob('*.md'), reverse=True)[:5]:
                content = msg_file.read_text()
                if 'Builder Agent' in content or 'BA' in content[:100]:
                    return 'BA'
                elif 'Chief Engineer' in content or 'CE' in content[:100]:
                    return 'CE'

        # Default to CE
        return 'CE'

    def get_my_tasks(self) -> List[Dict]:
        """Get tasks assigned to current agent"""
        if not self.connected:
            return []

        try:
            tasks = self.sync.tasks_table.all(
                formula=f"AND({{status}}!='Completed', {{assigned_to}}='{self.agent_id}')",
                sort=['-priority', 'created_time']
            )
            return tasks
        except Exception as e:
            print(f"❌ Error fetching tasks for {self.agent_name}: {e}")
            return []

    def claim_task(self, task_id: str):
        """Claim a task for current agent"""
        if not self.connected:
            return False

        try:
            self.sync.tasks_table.update(task_id, {
                'assigned_to': self.agent_id,
                'claimed_by': self.agent_name,
                'claimed_time': datetime.now().isoformat()
            })
            print(f"✅ {self.agent_name} claimed task {task_id}")
            return True
        except Exception as e:
            print(f"❌ Error claiming task: {e}")
            return False

    def update_my_task(self, task_id: str, updates: Dict):
        """Update a task with agent signature"""
        if not self.connected:
            return False

        try:
            # Add agent metadata
            updates['last_updated_by'] = self.agent_name
            updates['last_updated'] = datetime.now().isoformat()

            self.sync.tasks_table.update(task_id, updates)
            print(f"✅ {self.agent_name} updated task {task_id}")
            return True
        except Exception as e:
            print(f"❌ Error updating task: {e}")
            return False

    def handoff_task(self, task_id: str, to_agent: str, notes: str = ""):
        """Hand off a task to another agent"""
        if not self.connected:
            return False

        try:
            handoff_notes = f"[{datetime.now().strftime('%H:%M')}] Handed off from {self.agent_name} to {to_agent}"
            if notes:
                handoff_notes += f": {notes}"

            self.sync.tasks_table.update(task_id, {
                'assigned_to': to_agent,
                'status': 'Pending',
                'handoff_notes': handoff_notes,
                'last_handoff_from': self.agent_id,
                'last_handoff_time': datetime.now().isoformat()
            })

            print(f"✅ Task {task_id} handed off from {self.agent_name} to {to_agent}")
            return True
        except Exception as e:
            print(f"❌ Error handing off task: {e}")
            return False

    def collaborate_on_task(self, task_id: str, message: str):
        """Add collaboration message to task"""
        if not self.connected:
            return False

        try:
            task = self.sync.tasks_table.get(task_id)
            existing_collab = task['fields'].get('collaboration_log', '')

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            new_entry = f"[{timestamp}] {self.agent_name}: {message}"

            if existing_collab:
                updated_collab = f"{existing_collab}\n{new_entry}"
            else:
                updated_collab = new_entry

            self.sync.tasks_table.update(task_id, {
                'collaboration_log': updated_collab[:1000]  # Limit length
            })

            print(f"✅ {self.agent_name} added collaboration note")
            return True
        except Exception as e:
            print(f"❌ Error adding collaboration: {e}")
            return False

    def get_team_status(self) -> Dict:
        """Get status of all agents' tasks"""
        if not self.connected:
            return {}

        try:
            status = {}
            for agent_id, agent_name in self.AGENT_ROLES.items():
                tasks = self.sync.tasks_table.all(
                    formula=f"{{assigned_to}}='{agent_id}'"
                )

                status[agent_id] = {
                    'name': agent_name,
                    'total_tasks': len(tasks),
                    'in_progress': len([t for t in tasks if t['fields'].get('status') == 'In Progress']),
                    'pending': len([t for t in tasks if t['fields'].get('status') == 'Pending']),
                    'completed': len([t for t in tasks if t['fields'].get('status') == 'Completed']),
                    'blocked': len([t for t in tasks if t['fields'].get('status') == 'Blocked'])
                }

            return status
        except Exception as e:
            print(f"❌ Error getting team status: {e}")
            return {}


class AgentCoordinator:
    """Coordinates tasks between multiple agents"""

    def __init__(self):
        self.airtable = MultiAgentAirTable()

    def smart_task_assignment(self, task: Dict) -> str:
        """Intelligently assign task to best agent"""
        task_name = task['fields'].get('name', '').lower()
        task_desc = task['fields'].get('description', '').lower()

        # Assignment logic based on keywords
        if any(word in task_name + task_desc for word in ['deploy', 'build', 'implement', 'install']):
            return 'BA'
        elif any(word in task_name + task_desc for word in ['monitor', 'alert', 'metric', 'dashboard']):
            return 'MA'
        elif any(word in task_name + task_desc for word in ['test', 'validate', 'verify', 'qa']):
            return 'TA'
        elif any(word in task_name + task_desc for word in ['design', 'architect', 'plan', 'strategy']):
            return 'CE'
        else:
            return 'CE'  # Default to Chief Engineer

    def distribute_tasks(self):
        """Distribute pending tasks to appropriate agents"""
        if not self.airtable.connected:
            return

        try:
            # Get unassigned tasks
            unassigned = self.airtable.sync.tasks_table.all(
                formula="OR({assigned_to}='', {assigned_to}='Unassigned')"
            )

            for task in unassigned:
                best_agent = self.smart_task_assignment(task)
                self.airtable.sync.tasks_table.update(task['id'], {
                    'assigned_to': best_agent,
                    'auto_assigned': True,
                    'assignment_time': datetime.now().isoformat()
                })
                print(f"✅ Auto-assigned '{task['fields']['name']}' to {best_agent}")

        except Exception as e:
            print(f"❌ Error distributing tasks: {e}")


# Agent-specific command handlers
def ba_handler():
    """Builder Agent specific commands"""
    agent = MultiAgentAirTable('BA')

    print(f"\n🔨 BUILDER AGENT - AIRTABLE INTEGRATION")
    print("=" * 50)

    # Get BA's tasks
    tasks = agent.get_my_tasks()
    print(f"\n📋 Your Tasks ({len(tasks)}):")

    for i, task in enumerate(tasks[:5], 1):
        fields = task['fields']
        print(f"{i}. [{fields.get('status', 'Unknown')}] {fields.get('name', 'Unnamed')}")
        print(f"   Priority: {fields.get('priority', 'Medium')}")

    # Check for Smart Vertex AI tasks
    vertex_tasks = [t for t in tasks if 'vertex' in t['fields'].get('name', '').lower()]
    if vertex_tasks:
        print(f"\n🚀 VERTEX AI DEPLOYMENT TASKS:")
        for task in vertex_tasks:
            print(f"- {task['fields']['name']}: {task['fields'].get('status', 'Unknown')}")

    return agent

def ce_handler():
    """Chief Engineer specific commands"""
    agent = MultiAgentAirTable('CE')

    print(f"\n👷 CHIEF ENGINEER - AIRTABLE INTEGRATION")
    print("=" * 50)

    # Get team status
    team_status = agent.get_team_status()
    print(f"\n📊 TEAM STATUS:")

    for agent_id, status in team_status.items():
        if status['total_tasks'] > 0:
            print(f"\n{status['name']} ({agent_id}):")
            print(f"  In Progress: {status['in_progress']}")
            print(f"  Pending: {status['pending']}")
            print(f"  Completed: {status['completed']}")
            print(f"  Blocked: {status['blocked']}")

    return agent


# Make it accessible to all agents
if __name__ == "__main__":
    import sys

    # Detect which agent is calling
    if 'BA' in str(sys.argv):
        ba_handler()
    elif 'CE' in str(sys.argv):
        ce_handler()
    else:
        # Generic handler
        agent = MultiAgentAirTable()
        print(f"\n🤖 {agent.agent_name} - AirTable Connected")
        tasks = agent.get_my_tasks()
        print(f"You have {len(tasks)} tasks assigned")