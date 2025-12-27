"""
JARVIS Supabase Memory Backend
==============================
A Supabase-backed memory implementation that's compatible with Agent Zero's 
Memory class API. This enables cloud-based persistent memory with semantic search.

Features:
- Uses OpenAI text-embedding-3-small for embeddings (1536 dimensions)
- Stores memories in Supabase shared_memory table with pgvector
- Semantic similarity search using cosine distance
- Compatible with existing memory_save, memory_load, memory_delete tools

Usage:
    from python.helpers.memory_supabase import SupabaseMemory
    
    memory = await SupabaseMemory.get(agent)
    id = await memory.insert_text("Some important fact", {"area": "main"})
    results = await memory.search_similarity_threshold("important", 10, 0.7)
"""

import os
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
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

from python.helpers import guids
from python.helpers.print_style import PrintStyle
from python.helpers.log import LogItem
from enum import Enum

# Try to import Agent - handle circular import gracefully
try:
    from agent import Agent, AgentContext
except ImportError:
    Agent = None
    AgentContext = None


class SupabaseMemory:
    """
    Supabase-backed memory implementation compatible with Agent Zero's Memory class.
    Uses pgvector for semantic similarity search.
    """
    
    class Area(Enum):
        """Memory areas - matches the local Memory.Area enum."""
        MAIN = "main"
        FRAGMENTS = "fragments"
        SOLUTIONS = "solutions"
        INSTRUMENTS = "instruments"
    
    # Singleton index for caching initialized instances
    index: Dict[str, "SupabaseMemory"] = {}
    
    # Default agent IDs
    JARVIS_ID = "00000000-0000-0000-0000-000000000001"
    
    def __init__(
        self,
        supabase_client: Client,
        openai_client,
        memory_subdir: str = "default"
    ):
        """
        Initialize the Supabase memory backend.
        
        Args:
            supabase_client: Initialized Supabase client
            openai_client: Initialized OpenAI client for embeddings
            memory_subdir: Memory subdirectory (used as namespace/tag)
        """
        self.client = supabase_client
        self.openai_client = openai_client
        self.memory_subdir = memory_subdir
    
    @staticmethod
    async def get(agent) -> "SupabaseMemory":
        """
        Get or create a SupabaseMemory instance for the given agent.
        Compatible with Memory.get(agent) API.
        
        Args:
            agent: Agent instance
            
        Returns:
            SupabaseMemory instance
        """
        from python.helpers.memory import get_agent_memory_subdir
        
        memory_subdir = get_agent_memory_subdir(agent)
        
        if memory_subdir not in SupabaseMemory.index:
            # Initialize clients
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            openai_key = os.getenv("OPENAI_API_KEY")
            
            if not supabase_url or not supabase_key:
                raise ValueError(
                    "Supabase credentials not configured. "
                    "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables."
                )
            
            if not openai_key:
                raise ValueError(
                    "OpenAI API key not configured. "
                    "Set OPENAI_API_KEY environment variable for embeddings."
                )
            
            supabase_client = create_client(supabase_url, supabase_key)
            openai_client = openai.OpenAI(api_key=openai_key) if openai else None
            
            if agent and hasattr(agent, 'context') and agent.context:
                log_item = agent.context.log.log(
                    type="util",
                    heading=f"Initializing Supabase Memory for '/{memory_subdir}'",
                )
                if log_item:
                    log_item.stream(progress="\nConnecting to Supabase...")
            
            instance = SupabaseMemory(
                supabase_client=supabase_client,
                openai_client=openai_client,
                memory_subdir=memory_subdir
            )
            
            SupabaseMemory.index[memory_subdir] = instance
            PrintStyle.standard(f"Supabase Memory initialized for '{memory_subdir}'")
        
        return SupabaseMemory.index[memory_subdir]
    
    @staticmethod
    async def get_by_subdir(
        memory_subdir: str,
        log_item: Optional[LogItem] = None
    ) -> "SupabaseMemory":
        """
        Get or create a SupabaseMemory instance by subdirectory name.
        
        Args:
            memory_subdir: Memory subdirectory name
            log_item: Optional log item for streaming progress
            
        Returns:
            SupabaseMemory instance
        """
        if memory_subdir not in SupabaseMemory.index:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            openai_key = os.getenv("OPENAI_API_KEY")
            
            if not supabase_url or not supabase_key:
                raise ValueError("Supabase credentials not configured.")
            
            supabase_client = create_client(supabase_url, supabase_key)
            openai_client = openai.OpenAI(api_key=openai_key) if openai and openai_key else None
            
            if log_item:
                log_item.stream(progress="\nConnecting to Supabase...")
            
            instance = SupabaseMemory(
                supabase_client=supabase_client,
                openai_client=openai_client,
                memory_subdir=memory_subdir
            )
            
            SupabaseMemory.index[memory_subdir] = instance
        
        return SupabaseMemory.index[memory_subdir]
    
    @staticmethod
    async def reload(agent) -> "SupabaseMemory":
        """
        Reload the memory instance for the agent (clears cache).
        
        Args:
            agent: Agent instance
            
        Returns:
            Fresh SupabaseMemory instance
        """
        from python.helpers.memory import get_agent_memory_subdir
        
        memory_subdir = get_agent_memory_subdir(agent)
        if memory_subdir in SupabaseMemory.index:
            del SupabaseMemory.index[memory_subdir]
        return await SupabaseMemory.get(agent)
    
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
            raise ValueError("OpenAI client not initialized. Cannot generate embeddings.")
        
        response = self.openai_client.embeddings.create(
            input=text,
            model=model
        )
        return response.data[0].embedding
    
    # =========================================
    # CORE MEMORY OPERATIONS
    # =========================================
    
    async def insert_text(self, text: str, metadata: Dict[str, Any] = {}) -> str:
        """
        Insert a text memory into Supabase.
        Compatible with Memory.insert_text API.
        
        Args:
            text: The text content to store
            metadata: Additional metadata (area, timestamp, etc.)
            
        Returns:
            The ID of the created memory
        """
        # Generate unique ID
        doc_id = self._generate_doc_id()
        
        # Add standard fields to metadata
        timestamp = self.get_timestamp()
        area = metadata.get("area", self.Area.MAIN.value)
        
        # Map memory area to Supabase memory_type
        memory_type_map = {
            "main": "fact",
            "fragments": "context",
            "solutions": "solution",
            "instruments": "procedure"
        }
        memory_type = memory_type_map.get(area, "fact")
        
        # Generate embedding
        embedding = self.generate_embedding(text)
        
        # Prepare metadata for storage
        stored_metadata = {
            **metadata,
            "id": doc_id,
            "timestamp": timestamp,
            "area": area,
            "memory_subdir": self.memory_subdir
        }
        
        # Insert into Supabase
        data = {
            "content": text,
            "embedding": embedding,
            "memory_type": memory_type,
            "source_agent_id": self.JARVIS_ID,
            "metadata": stored_metadata
        }
        
        result = self.client.table("shared_memory").insert(data).execute()
        
        if result.data:
            PrintStyle.standard(f"Memory saved to Supabase: {doc_id}")
            return doc_id
        else:
            raise Exception("Failed to save memory to Supabase")
    
    async def insert_documents(self, docs: List[Any]) -> List[str]:
        """
        Insert multiple documents into Supabase.
        Compatible with Memory.insert_documents API.
        
        Args:
            docs: List of Document objects with page_content and metadata
            
        Returns:
            List of document IDs
        """
        ids = []
        for doc in docs:
            # Extract text and metadata from Document object
            text = doc.page_content if hasattr(doc, 'page_content') else str(doc)
            metadata = doc.metadata if hasattr(doc, 'metadata') else {}
            
            doc_id = await self.insert_text(text, metadata)
            ids.append(doc_id)
        
        return ids
    
    async def search_similarity_threshold(
        self,
        query: str,
        limit: int,
        threshold: float,
        filter: str = ""
    ) -> List[Any]:
        """
        Search for similar memories using semantic similarity.
        Compatible with Memory.search_similarity_threshold API.
        
        Args:
            query: Search query text
            limit: Maximum number of results
            threshold: Minimum similarity threshold (0.0 to 1.0)
            filter: Python-style filter expression (optional)
            
        Returns:
            List of Document-like objects with page_content and metadata
        """
        # Generate embedding for query
        query_embedding = self.generate_embedding(query)
        
        # Try RPC function first, fall back to table query
        try:
            result = self.client.rpc(
                "search_memory",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": threshold,
                    "match_count": limit,
                    "filter_type": None
                }
            ).execute()
        except Exception as rpc_error:
            PrintStyle.standard(f"RPC search_memory not available, using direct query: {rpc_error}")
            # Fallback: Direct table query (without vector similarity - just get recent)
            result = self.client.table("shared_memory").select(
                "id, content, memory_type, metadata, created_at"
            ).order("created_at", desc=True).limit(limit).execute()
            
            # Add placeholder similarity for fallback results
            if result.data:
                for row in result.data:
                    row["similarity"] = 0.5  # Placeholder since we can't calculate without RPC
        
        if not result.data:
            return []
        
        # Convert to Document-like objects and apply filter
        documents = []
        for row in result.data:
            metadata = row.get("metadata", {}) or {}
            
            # Add core fields to metadata
            metadata["id"] = metadata.get("id") or row.get("id", "")
            metadata["similarity"] = row.get("similarity", 0.0)
            metadata["memory_type"] = row.get("memory_type", "fact")
            
            # Apply filter if provided (basic implementation)
            if filter:
                if not self._apply_filter(metadata, filter):
                    continue
            
            # Filter by memory_subdir if set
            if self.memory_subdir and self.memory_subdir != "default":
                mem_subdir = metadata.get("memory_subdir", "default")
                if mem_subdir != self.memory_subdir and mem_subdir != "default":
                    continue
            
            # Create Document-like object
            doc = type('Document', (), {
                'page_content': row.get("content", ""),
                'metadata': metadata
            })()
            
            documents.append(doc)
        
        return documents
    
    async def delete_documents_by_ids(self, ids: List[str]) -> List[Any]:
        """
        Delete documents by their IDs.
        Compatible with Memory.delete_documents_by_ids API.
        
        Args:
            ids: List of document IDs to delete
            
        Returns:
            List of deleted documents
        """
        deleted = []
        
        for doc_id in ids:
            # Find and delete the document
            # First find by metadata->id
            result = self.client.table("shared_memory").select("*").filter(
                "metadata->>id", "eq", doc_id
            ).execute()
            
            if result.data:
                for row in result.data:
                    self.client.table("shared_memory").delete().eq("id", row["id"]).execute()
                    deleted.append(row)
                    PrintStyle.standard(f"Memory deleted from Supabase: {doc_id}")
        
        return deleted
    
    async def delete_documents_by_query(
        self,
        query: str,
        threshold: float,
        filter: str = ""
    ) -> List[Any]:
        """
        Delete documents matching a similarity query.
        Compatible with Memory.delete_documents_by_query API.
        
        Args:
            query: Search query text
            threshold: Minimum similarity threshold
            filter: Optional filter expression
            
        Returns:
            List of deleted documents
        """
        # First find matching documents
        docs = await self.search_similarity_threshold(
            query=query,
            limit=100,  # Get up to 100 matches
            threshold=threshold,
            filter=filter
        )
        
        if not docs:
            return []
        
        # Extract IDs and delete
        ids = [doc.metadata.get("id") for doc in docs if doc.metadata.get("id")]
        return await self.delete_documents_by_ids(ids)
    
    def get_document_by_id(self, doc_id: str) -> Optional[Any]:
        """
        Get a single document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document-like object or None
        """
        result = self.client.table("shared_memory").select("*").filter(
            "metadata->>id", "eq", doc_id
        ).execute()
        
        if result.data:
            row = result.data[0]
            metadata = row.get("metadata", {}) or {}
            metadata["id"] = doc_id
            
            return type('Document', (), {
                'page_content': row.get("content", ""),
                'metadata': metadata
            })()
        
        return None
    
    # =========================================
    # HELPER FUNCTIONS
    # =========================================
    
    def _generate_doc_id(self) -> str:
        """Generate a unique document ID."""
        return guids.generate_id(10)
    
    def _apply_filter(self, metadata: Dict[str, Any], filter_expr: str) -> bool:
        """
        Apply a Python-style filter expression to metadata.
        
        Args:
            metadata: Document metadata
            filter_expr: Python expression using metadata keys
            
        Returns:
            True if the document passes the filter
        """
        try:
            # Create a safe evaluation context with metadata values
            from simpleeval import simple_eval
            result = simple_eval(filter_expr, names=metadata)
            return bool(result)
        except Exception as e:
            PrintStyle.error(f"Error evaluating filter: {e}")
            return False
    
    @staticmethod
    def get_timestamp() -> str:
        """Get current timestamp in standard format."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def format_docs_plain(docs: List[Any]) -> List[str]:
        """
        Format documents as plain text.
        Compatible with Memory.format_docs_plain API.
        
        Args:
            docs: List of Document-like objects
            
        Returns:
            List of formatted strings
        """
        result = []
        for doc in docs:
            text = ""
            metadata = doc.metadata if hasattr(doc, 'metadata') else {}
            for k, v in metadata.items():
                if k != "embedding":  # Skip embedding field
                    text += f"{k}: {v}\n"
            content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
            text += f"Content: {content}"
            result.append(text)
        return result


# =========================================
# UTILITY FUNCTIONS
# =========================================

def is_supabase_configured() -> bool:
    """Check if Supabase is properly configured."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    return bool(url and key)


def get_memory_backend() -> str:
    """
    Get the configured memory backend.
    
    Returns:
        'supabase' or 'local'
    """
    backend = os.getenv("MEMORY_BACKEND", "").lower()
    
    if backend == "supabase":
        return "supabase"
    elif backend == "local":
        return "local"
    else:
        # Auto-detect: use supabase if configured, else local
        if is_supabase_configured():
            return "supabase"
        return "local"
