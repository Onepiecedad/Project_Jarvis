"""
Task Create Tool
================
Creates tasks in Supabase for Agent Zero agents.
"""

from python.helpers.tool import Tool, Response
from python.tools.supabase_client import get_client
import uuid
from datetime import datetime


class TaskCreate(Tool):
    """Tool for creating new tasks in the task management system."""

    async def execute(self, **kwargs):
        title = kwargs.get("title", "")
        description = kwargs.get("description", "")
        agent_name = kwargs.get("agent", "jarvis").lower()
        priority = kwargs.get("priority", 5)

        if not title:
            return Response(
                message="Error: 'title' is required to create a task.",
                break_loop=False
            )

        try:
            client = get_client()
            
            # Get agent_id from name (use wildcards for partial matching)
            agent_result = client.client.table("agents").select("id").ilike("name", f"%{agent_name}%").execute()
            
            if not agent_result.data:
                return Response(
                    message=f"Agent '{agent_name}' not found in database.",
                    break_loop=False
                )
            
            agent_id = agent_result.data[0]["id"]
            
            # Create task
            task = {
                "id": str(uuid.uuid4()),
                "agent_id": agent_id,
                "title": title,
                "description": description,
                "status": "pending",
                "priority": priority,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = client.client.table("tasks").insert(task).execute()
            
            if result.data:
                return Response(
                    message=f"✅ Task created successfully!\n- Title: {title}\n- ID: {task['id']}\n- Assigned to: {agent_name}\n- Priority: {priority}",
                    break_loop=False
                )
            else:
                return Response(
                    message="Failed to create task - no data returned from database.",
                    break_loop=False
                )
                
        except Exception as e:
            return Response(
                message=f"Error creating task: {str(e)}",
                break_loop=False
            )
