"""
Task Update Tool
================
Updates existing tasks in Supabase for Agent Zero agents.
"""

from python.helpers.tool import Tool, Response
from python.tools.supabase_client import get_client
from datetime import datetime


class TaskUpdate(Tool):
    """Tool for updating existing tasks in the task management system."""

    async def execute(self, **kwargs):
        task_id = kwargs.get("task_id", "")
        status = kwargs.get("status", None)
        result_data = kwargs.get("result", None)
        priority = kwargs.get("priority", None)
        description = kwargs.get("description", None)

        if not task_id:
            return Response(
                message="Error: 'task_id' is required to update a task.",
                break_loop=False
            )

        try:
            client = get_client()
            
            # Build update data
            update_data = {}
            
            if status:
                update_data["status"] = status
                if status == "running":
                    update_data["started_at"] = datetime.utcnow().isoformat()
                elif status in ["completed", "failed", "cancelled"]:
                    update_data["completed_at"] = datetime.utcnow().isoformat()
            
            if result_data:
                if isinstance(result_data, dict):
                    update_data["result"] = result_data
                else:
                    update_data["result"] = {"output": str(result_data)}
            
            if priority is not None:
                update_data["priority"] = priority
                
            if description is not None:
                update_data["description"] = description
            
            if not update_data:
                return Response(
                    message="No fields provided to update. Provide at least one of: status, result, priority, description.",
                    break_loop=False
                )
            
            # Execute update
            result = client.client.table("tasks").update(update_data).eq("id", task_id).execute()
            
            if result.data:
                updates = ", ".join([f"{k}={v}" for k, v in update_data.items() if k not in ["result"]])
                return Response(
                    message=f"✅ Task updated successfully!\n- Task ID: {task_id[:8]}...\n- Updates: {updates}",
                    break_loop=False
                )
            else:
                return Response(
                    message=f"Task with ID '{task_id}' not found or update failed.",
                    break_loop=False
                )
                
        except Exception as e:
            return Response(
                message=f"Error updating task: {str(e)}",
                break_loop=False
            )
