"""
Task List Tool
==============
Lists and queries tasks from Supabase for Agent Zero agents.
"""

from python.helpers.tool import Tool, Response
from python.tools.supabase_client import get_client


class TaskList(Tool):
    """Tool for listing and querying tasks in the task management system."""

    async def execute(self, **kwargs):
        status = kwargs.get("status", None)
        agent_name = kwargs.get("agent", None)
        limit = kwargs.get("limit", 10)

        try:
            client = get_client()
            
            # Build query with agent relationship
            query = client.client.table("tasks").select("*, agents(name)").order("created_at", desc=True).limit(limit)
            
            # Apply filters
            if status:
                query = query.eq("status", status)
            
            if agent_name:
                # First get agent_id from name
                agent_result = client.client.table("agents").select("id").ilike("name", f"%{agent_name}%").execute()
                if agent_result.data:
                    agent_id = agent_result.data[0]["id"]
                    query = query.eq("agent_id", agent_id)
            
            result = query.execute()
            
            if not result.data:
                filter_msg = ""
                if status:
                    filter_msg += f" with status '{status}'"
                if agent_name:
                    filter_msg += f" for agent '{agent_name}'"
                return Response(
                    message=f"No tasks found{filter_msg}.",
                    break_loop=False
                )
            
            # Format tasks for display
            tasks_lines = []
            for t in result.data:
                agent_display = t['agents']['name'] if t.get('agents') else 'N/A'
                status_emoji = {
                    "pending": "⏳",
                    "active": "🔄",
                    "running": "🔄", 
                    "completed": "✅",
                    "failed": "❌",
                    "cancelled": "🚫"
                }.get(t['status'], "❓")
                
                priority_str = f"P{t.get('priority', '?')}"
                tasks_lines.append(
                    f"{status_emoji} [{t['status']}] {t['title']}\n"
                    f"   Agent: {agent_display} | Priority: {priority_str} | ID: {t['id'][:8]}..."
                )
            
            tasks_str = "\n".join(tasks_lines)
            
            return Response(
                message=f"📋 Tasks ({len(result.data)} found):\n\n{tasks_str}",
                break_loop=False
            )
                
        except Exception as e:
            return Response(
                message=f"Error listing tasks: {str(e)}",
                break_loop=False
            )
