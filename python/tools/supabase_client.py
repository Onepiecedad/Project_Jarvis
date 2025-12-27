"""
JARVIS Supabase Client
======================
Integration layer for JARVIS to interact with Supabase database.
Provides functions for memory management, task handling, and entity operations.

Usage:
    from python.tools.supabase_client import SupabaseClient
    
    client = SupabaseClient()
    
    # Save a memory
    client.save_memory("Important fact about the project", "fact", {"source": "user"})
    
    # Search memories
    results = client.search_memory(query_embedding, threshold=0.7, limit=10)
"""

import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from supabase import create_client, Client
except ImportError:
    raise ImportError("Please install supabase-py: pip install supabase")

try:
    import openai
except ImportError:
    openai = None


class SupabaseClient:
    """
    Client for interacting with the JARVIS Supabase database.
    Uses service_role key for full database access.
    """
    
    # Default agent IDs from seed data
    JARVIS_ID = "00000000-0000-0000-0000-000000000001"
    RESEARCH_AGENT_ID = "00000000-0000-0000-0000-000000000002"
    WRITER_AGENT_ID = "00000000-0000-0000-0000-000000000003"
    OPS_AGENT_ID = "00000000-0000-0000-0000-000000000004"
    
    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize the Supabase client.
        
        Args:
            url: Supabase project URL (defaults to SUPABASE_URL env var)
            key: Supabase service role key (defaults to SUPABASE_SERVICE_ROLE_KEY env var)
            openai_api_key: OpenAI API key for embeddings (defaults to OPENAI_API_KEY env var)
        """
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.url or not self.key:
            raise ValueError(
                "Supabase URL and service role key are required. "
                "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables."
            )
        
        self.client: Client = create_client(self.url, self.key)
        
        # Initialize OpenAI client if available
        if openai and self.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        else:
            self.openai_client = None
    
    # =========================================
    # EMBEDDING FUNCTIONS
    # =========================================
    
    def generate_embedding(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        """
        Generate an embedding vector for the given text.
        
        Args:
            text: Text to embed
            model: OpenAI embedding model to use
            
        Returns:
            List of floats representing the embedding vector (1536 dimensions)
        """
        if not self.openai_client:
            raise ValueError(
                "OpenAI client not initialized. Set OPENAI_API_KEY environment variable."
            )
        
        response = self.openai_client.embeddings.create(
            input=text,
            model=model
        )
        return response.data[0].embedding
    
    # =========================================
    # MEMORY FUNCTIONS
    # =========================================
    
    def save_memory(
        self,
        content: str,
        memory_type: str = "fact",
        metadata: Optional[Dict[str, Any]] = None,
        source_agent_id: Optional[str] = None,
        embedding: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Save a memory to the shared_memory table.
        
        Args:
            content: The memory content to save
            memory_type: Type of memory (fact, procedure, preference, context, solution)
            metadata: Optional metadata dictionary
            source_agent_id: ID of the agent that created this memory
            embedding: Pre-computed embedding vector (generates one if not provided)
            
        Returns:
            The created memory record
        """
        # Generate embedding if not provided
        if embedding is None:
            embedding = self.generate_embedding(content)
        
        data = {
            "content": content,
            "embedding": embedding,
            "memory_type": memory_type,
            "source_agent_id": source_agent_id or self.JARVIS_ID,
            "metadata": metadata or {}
        }
        
        result = self.client.table("shared_memory").insert(data).execute()
        return result.data[0] if result.data else None
    
    def search_memory(
        self,
        query: str,
        threshold: float = 0.7,
        limit: int = 10,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memories using semantic similarity.
        
        Args:
            query: Search query text
            threshold: Minimum similarity threshold (0.0 to 1.0)
            limit: Maximum number of results
            memory_type: Optional filter by memory type
            
        Returns:
            List of matching memories with similarity scores
        """
        # Generate embedding for search query
        query_embedding = self.generate_embedding(query)
        
        # Call the search_memory RPC function
        result = self.client.rpc(
            "search_memory",
            {
                "query_embedding": query_embedding,
                "match_threshold": threshold,
                "match_count": limit,
                "filter_type": memory_type
            }
        ).execute()
        
        return result.data if result.data else []
    
    def get_all_memories(
        self,
        memory_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all memories, optionally filtered by type.
        
        Args:
            memory_type: Optional filter by memory type
            limit: Maximum number of results
            
        Returns:
            List of memory records
        """
        query = self.client.table("shared_memory").select("*")
        
        if memory_type:
            query = query.eq("memory_type", memory_type)
        
        result = query.order("created_at", desc=True).limit(limit).execute()
        return result.data if result.data else []
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory by ID.
        
        Args:
            memory_id: UUID of the memory to delete
            
        Returns:
            True if deleted successfully
        """
        result = self.client.table("shared_memory").delete().eq("id", memory_id).execute()
        return len(result.data) > 0 if result.data else False
    
    # =========================================
    # TASK FUNCTIONS
    # =========================================
    
    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        agent_id: Optional[str] = None,
        parent_task_id: Optional[str] = None,
        priority: int = 5,
        related_entities: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new task.
        
        Args:
            title: Task title
            description: Task description
            agent_id: ID of the agent assigned to this task
            parent_task_id: Parent task ID for subtasks
            priority: Priority level (1-10, higher is more important)
            related_entities: List of related entity IDs
            
        Returns:
            The created task record
        """
        data = {
            "title": title,
            "description": description,
            "agent_id": agent_id or self.JARVIS_ID,
            "parent_task_id": parent_task_id,
            "priority": priority,
            "status": "pending",
            "related_entities": related_entities or []
        }
        
        result = self.client.table("tasks").insert(data).execute()
        return result.data[0] if result.data else None
    
    def update_task(
        self,
        task_id: str,
        status: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update a task.
        
        Args:
            task_id: UUID of the task to update
            status: New status (pending, running, completed, failed, cancelled)
            result: Task result data (for completed tasks)
            **kwargs: Additional fields to update
            
        Returns:
            The updated task record
        """
        data = {}
        
        if status:
            data["status"] = status
            if status == "running":
                data["started_at"] = datetime.utcnow().isoformat()
            elif status in ("completed", "failed", "cancelled"):
                data["completed_at"] = datetime.utcnow().isoformat()
        
        if result:
            data["result"] = result
        
        data.update(kwargs)
        
        result = self.client.table("tasks").update(data).eq("id", task_id).execute()
        return result.data[0] if result.data else None
    
    def get_tasks(
        self,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get tasks, optionally filtered by agent and/or status.
        
        Args:
            agent_id: Filter by agent ID
            status: Filter by status
            limit: Maximum number of results
            
        Returns:
            List of task records
        """
        query = self.client.table("tasks").select("*")
        
        if agent_id:
            query = query.eq("agent_id", agent_id)
        if status:
            query = query.eq("status", status)
        
        result = query.order("priority", desc=True).order("created_at", desc=True).limit(limit).execute()
        return result.data if result.data else []
    
    def get_pending_tasks(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all pending tasks for an agent."""
        return self.get_tasks(agent_id=agent_id, status="pending")
    
    # =========================================
    # ENTITY FUNCTIONS
    # =========================================
    
    def create_entity(
        self,
        entity_type: str,
        name: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new entity in the knowledge graph.
        
        Args:
            entity_type: Type of entity (e.g., person, organization, project)
            name: Entity name
            properties: Additional properties as JSON
            
        Returns:
            The created entity record
        """
        data = {
            "type": entity_type,
            "name": name,
            "properties": properties or {}
        }
        
        result = self.client.table("entities").insert(data).execute()
        return result.data[0] if result.data else None
    
    def get_entities(
        self,
        entity_type: Optional[str] = None,
        search_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get entities, optionally filtered by type or name.
        
        Args:
            entity_type: Filter by entity type
            search_name: Search for entities by name (case-insensitive)
            limit: Maximum number of results
            
        Returns:
            List of entity records
        """
        query = self.client.table("entities").select("*")
        
        if entity_type:
            query = query.eq("type", entity_type)
        if search_name:
            query = query.ilike("name", f"%{search_name}%")
        
        result = query.order("name").limit(limit).execute()
        return result.data if result.data else []
    
    def get_entity_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get a single entity by ID."""
        result = self.client.table("entities").select("*").eq("id", entity_id).execute()
        return result.data[0] if result.data else None
    
    def update_entity(
        self,
        entity_id: str,
        properties: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update an entity.
        
        Args:
            entity_id: UUID of the entity to update
            properties: New properties (merged with existing)
            **kwargs: Additional fields to update
            
        Returns:
            The updated entity record
        """
        data = {}
        
        if properties:
            # Get existing properties and merge
            existing = self.get_entity_by_id(entity_id)
            if existing:
                merged_props = {**existing.get("properties", {}), **properties}
                data["properties"] = merged_props
        
        data.update(kwargs)
        
        result = self.client.table("entities").update(data).eq("id", entity_id).execute()
        return result.data[0] if result.data else None
    
    def create_relationship(
        self,
        from_entity_id: str,
        to_entity_id: str,
        relationship: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a relationship between two entities.
        
        Args:
            from_entity_id: Source entity ID
            to_entity_id: Target entity ID
            relationship: Relationship type (e.g., "owns", "works_for", "develops")
            properties: Additional relationship properties
            
        Returns:
            The created relationship record
        """
        data = {
            "from_entity": from_entity_id,
            "to_entity": to_entity_id,
            "relationship": relationship,
            "properties": properties or {}
        }
        
        result = self.client.table("entity_relationships").insert(data).execute()
        return result.data[0] if result.data else None
    
    def get_entity_relationships(
        self,
        entity_id: str,
        direction: str = "both"
    ) -> List[Dict[str, Any]]:
        """
        Get relationships for an entity.
        
        Args:
            entity_id: Entity ID to find relationships for
            direction: "from" (outgoing), "to" (incoming), or "both"
            
        Returns:
            List of relationship records
        """
        results = []
        
        if direction in ("from", "both"):
            from_result = self.client.table("entity_relationships").select(
                "*, from_entity:entities!from_entity(*), to_entity:entities!to_entity(*)"
            ).eq("from_entity", entity_id).execute()
            results.extend(from_result.data or [])
        
        if direction in ("to", "both"):
            to_result = self.client.table("entity_relationships").select(
                "*, from_entity:entities!from_entity(*), to_entity:entities!to_entity(*)"
            ).eq("to_entity", entity_id).execute()
            results.extend(to_result.data or [])
        
        return results
    
    # =========================================
    # AGENT FUNCTIONS
    # =========================================
    
    def get_agents(self, agent_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all agents, optionally filtered by type.
        
        Args:
            agent_type: Filter by type (master, specialist, subordinate)
            
        Returns:
            List of agent records
        """
        query = self.client.table("agents").select("*")
        
        if agent_type:
            query = query.eq("type", agent_type)
        
        result = query.order("name").execute()
        return result.data if result.data else []
    
    def get_agent_stats(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for an agent.
        
        Args:
            agent_id: UUID of the agent
            
        Returns:
            Agent statistics including task counts and memory counts
        """
        result = self.client.rpc("get_agent_stats", {"target_agent_id": agent_id}).execute()
        return result.data[0] if result.data else None
    
    # =========================================
    # CONVERSATION FUNCTIONS
    # =========================================
    
    def create_conversation(
        self,
        agent_id: Optional[str] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new conversation.
        
        Args:
            agent_id: ID of the agent for this conversation
            title: Optional conversation title
            
        Returns:
            The created conversation record
        """
        data = {
            "agent_id": agent_id or self.JARVIS_ID,
            "title": title
        }
        
        result = self.client.table("conversations").insert(data).execute()
        return result.data[0] if result.data else None
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: UUID of the conversation
            role: Message role (user, assistant, system, tool)
            content: Message content
            metadata: Optional metadata
            
        Returns:
            The created message record
        """
        data = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        
        result = self.client.table("messages").insert(data).execute()
        return result.data[0] if result.data else None
    
    def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get messages for a conversation.
        
        Args:
            conversation_id: UUID of the conversation
            limit: Maximum number of messages
            
        Returns:
            List of message records in chronological order
        """
        result = self.client.table("messages").select("*").eq(
            "conversation_id", conversation_id
        ).order("created_at").limit(limit).execute()
        
        return result.data if result.data else []
    
    # =========================================
    # COST TRACKING FUNCTIONS
    # =========================================
    
    def log_agent_cost(
        self,
        agent_id: str,
        tokens_in: int = 0,
        tokens_out: int = 0,
        api_cost: float = 0.0,
        tasks_completed: int = 0
    ) -> Dict[str, Any]:
        """
        Log usage costs for an agent.
        
        Args:
            agent_id: UUID of the agent
            tokens_in: Number of input tokens
            tokens_out: Number of output tokens
            api_cost: Cost in USD
            tasks_completed: Number of tasks completed
            
        Returns:
            The updated cost record
        """
        today = datetime.utcnow().date().isoformat()
        
        # Try to get existing record for today
        existing = self.client.table("agent_costs").select("*").eq(
            "agent_id", agent_id
        ).eq("date", today).execute()
        
        if existing.data:
            # Update existing record
            current = existing.data[0]
            data = {
                "tokens_in": current["tokens_in"] + tokens_in,
                "tokens_out": current["tokens_out"] + tokens_out,
                "api_cost": float(current["api_cost"]) + api_cost,
                "tasks_completed": current["tasks_completed"] + tasks_completed
            }
            result = self.client.table("agent_costs").update(data).eq(
                "id", current["id"]
            ).execute()
        else:
            # Create new record
            data = {
                "agent_id": agent_id,
                "date": today,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "api_cost": api_cost,
                "tasks_completed": tasks_completed
            }
            result = self.client.table("agent_costs").insert(data).execute()
        
        return result.data[0] if result.data else None


# =========================================
# SINGLETON INSTANCE
# =========================================

_client_instance: Optional[SupabaseClient] = None


def get_client() -> SupabaseClient:
    """
    Get the singleton SupabaseClient instance.
    
    Returns:
        Initialized SupabaseClient
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = SupabaseClient()
    return _client_instance


# =========================================
# CONVENIENCE FUNCTIONS
# =========================================

def save_memory(content: str, memory_type: str = "fact", metadata: Optional[Dict] = None) -> Dict:
    """Save a memory using the singleton client."""
    return get_client().save_memory(content, memory_type, metadata)


def search_memory(query: str, threshold: float = 0.7, limit: int = 10) -> List[Dict]:
    """Search memories using the singleton client."""
    return get_client().search_memory(query, threshold, limit)


def create_task(title: str, description: str = None, priority: int = 5) -> Dict:
    """Create a task using the singleton client."""
    return get_client().create_task(title, description, priority=priority)


def update_task(task_id: str, status: str = None, result: Dict = None) -> Dict:
    """Update a task using the singleton client."""
    return get_client().update_task(task_id, status, result)


def get_entities(entity_type: str = None) -> List[Dict]:
    """Get entities using the singleton client."""
    return get_client().get_entities(entity_type)


def create_entity(entity_type: str, name: str, properties: Dict = None) -> Dict:
    """Create an entity using the singleton client."""
    return get_client().create_entity(entity_type, name, properties)


# =========================================
# CLI TESTING
# =========================================

if __name__ == "__main__":
    print("Testing Supabase Client...")
    
    try:
        client = SupabaseClient()
        print("✅ Client initialized successfully!")
        
        # Test getting agents
        agents = client.get_agents()
        print(f"\n📋 Agents in database: {len(agents)}")
        for agent in agents:
            print(f"   - {agent['name']} ({agent['type']})")
        
        # Test getting entities
        entities = client.get_entities()
        print(f"\n🏷️  Entities in database: {len(entities)}")
        for entity in entities:
            print(f"   - {entity['name']} ({entity['type']})")
        
        # Test creating a task
        print("\n📝 Creating test task...")
        task = client.create_task(
            title="Test task from CLI",
            description="This is a test task created by the CLI",
            priority=7
        )
        if task:
            print(f"   ✅ Task created: {task['id']}")
            
            # Update the task
            updated = client.update_task(task['id'], status="completed")
            print(f"   ✅ Task completed!")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
