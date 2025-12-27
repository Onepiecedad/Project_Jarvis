"""
Delegate Tool
=============
Delegates tasks to specialist sub-agents with full Supabase task tracking.
Uses Agent Zero's native subordinate system combined with task management.
"""

from agent import Agent, UserMessage
from python.helpers.tool import Tool, Response
from python.tools.supabase_client import get_client
from initialize import initialize_agent
import uuid
from datetime import datetime


class Delegate(Tool):
    """
    Delegates tasks to specialist agents (research, writer, ops).
    Creates a tracked task in Supabase, runs a subordinate agent,
    and saves the result back to the task.
    """
    
    # Valid specialist agents
    VALID_AGENTS = {
        "research": "Research Agent - For research, analysis, and information gathering",
        "writer": "Writer Agent - For content creation, copywriting, and documentation",
        "ops": "Ops Agent - For operations, automation, and system tasks"
    }
    
    # Map agent names to profile directories in agents/
    PROFILE_MAP = {
        "research": "researcher",  # agents/researcher exists
        "writer": "writer",        # agents/writer
        "ops": "ops"               # agents/ops
    }

    async def execute(self, agent="", task="", description="", context="", **kwargs):
        agent_name = agent.lower().strip()
        
        # Validate agent
        if agent_name not in self.VALID_AGENTS:
            agents_list = "\n".join([f"  - {k}: {v}" for k, v in self.VALID_AGENTS.items()])
            return Response(
                message=f"❌ Invalid agent: '{agent_name}'\n\nAvailable agents:\n{agents_list}",
                break_loop=False
            )
        
        if not task:
            return Response(
                message="❌ Error: 'task' parameter is required. Provide a task title.",
                break_loop=False
            )
        
        try:
            supabase = get_client()
            
            # Map shorthand names to full database names
            agent_name_map = {
                "research": "Research Agent",
                "researcher": "Research Agent",
                "writer": "Writer Agent",
                "ops": "Ops Agent"
            }
            
            # Get the full database name
            db_agent_name = agent_name_map.get(agent_name, agent_name)
            
            # Try exact match first
            agent_result = supabase.client.table("agents").select("id, name").eq("name", db_agent_name).execute()
            
            # If no exact match, try ilike as fallback
            if not agent_result.data:
                agent_result = supabase.client.table("agents").select("id, name").ilike("name", f"%{agent_name}%").execute()
            
            if not agent_result.data:
                return Response(
                    message=f"❌ Agent '{agent_name}' not found in database. Run seed.sql to create agents.",
                    break_loop=False
                )
            
            agent_id = agent_result.data[0]["id"]
            agent_db_name = agent_result.data[0]["name"]
            
            # Create task in Supabase with status 'active'
            task_id = str(uuid.uuid4())
            task_record = {
                "id": task_id,
                "agent_id": agent_id,
                "title": task,
                "description": description or task,
                "status": "running",
                "priority": 5,
                "started_at": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
            supabase.client.table("tasks").insert(task_record).execute()
            
            # Build the message for the subordinate agent
            delegation_message = self._build_delegation_message(
                task_id=task_id,
                task_title=task,
                description=description,
                context=context,
                agent_name=agent_db_name
            )
            
            # Create or reuse subordinate agent
            # Use agent_name as key to maintain separate subordinates per specialist
            subordinate_key = f"delegate_{agent_name}"
            
            if self.agent.get_data(subordinate_key) is None:
                # Initialize with agent-specific profile
                config = initialize_agent()
                # Map to actual profile directory name
                config.profile = self.PROFILE_MAP.get(agent_name, agent_name)
                
                # Create subordinate agent
                sub = Agent(self.agent.number + 1, config, self.agent.context)
                sub.set_data(Agent.DATA_NAME_SUPERIOR, self.agent)
                self.agent.set_data(subordinate_key, sub)
            
            # Get the subordinate
            subordinate: Agent = self.agent.get_data(subordinate_key)
            
            # Add the task message to subordinate
            subordinate.hist_add_user_message(UserMessage(message=delegation_message, attachments=[]))
            
            # Run the subordinate agent
            result_text = await subordinate.monologue()
            
            # Update task with success
            supabase.client.table("tasks").update({
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat(),
                "result": {"output": result_text[:5000]}  # Truncate if too long
            }).eq("id", task_id).execute()
            
            return Response(
                message=f"✅ **{agent_db_name}** completed the task.\n\n**Task:** {task}\n**Task ID:** {task_id[:8]}...\n\n---\n\n**Result:**\n{result_text}",
                break_loop=False
            )
            
        except Exception as e:
            # Try to mark task as failed if we have a task_id
            try:
                if 'task_id' in locals():
                    supabase.client.table("tasks").update({
                        "status": "failed",
                        "completed_at": datetime.utcnow().isoformat(),
                        "result": {"error": str(e)}
                    }).eq("id", task_id).execute()
            except:
                pass
            
            return Response(
                message=f"❌ Delegation failed: {str(e)}",
                break_loop=False
            )
    
    def _build_delegation_message(self, task_id: str, task_title: str, description: str, context: str, agent_name: str) -> str:
        """Build the message to send to the subordinate agent."""
        return f"""
# DELEGATED TASK

You are **{agent_name}**, a specialist agent. You have been delegated a task by JARVIS.

## Task Details
- **Task ID:** {task_id}
- **Title:** {task_title}
- **Description:** {description or 'See title'}

## Context
{context or 'No additional context provided.'}

## Instructions
1. Complete the task according to your specialization
2. Be thorough and concrete - deliver actionable results
3. Use available tools (code execution, web search, etc.) as needed
4. Save important findings to memory if relevant
5. Provide a clear summary of what you accomplished

Please proceed with the task now.
"""

    def get_log_object(self):
        return self.agent.context.log.log(
            type="tool",
            heading=f"icon://people {self.agent.agent_name}: Delegating to specialist agent",
            content="",
            kvps=self.args,
        )
