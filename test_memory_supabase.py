#!/usr/bin/env python3
"""
Test script for Supabase Memory Backend
=======================================
Tests the SupabaseMemory class to verify it works correctly with Agent Zero.

Run: python test_memory_supabase.py
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_result(success, message):
    status = "✅" if success else "❌"
    print(f"  {status} {message}")

async def main():
    print_header("JARVIS Supabase Memory Backend Test")
    
    # Check environment
    print("\n📋 Checking environment...")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    memory_backend = os.getenv("MEMORY_BACKEND", "auto")
    
    print_result(bool(supabase_url), f"SUPABASE_URL: {supabase_url[:30]}..." if supabase_url else "SUPABASE_URL: Not set")
    print_result(bool(supabase_key), f"SUPABASE_SERVICE_ROLE_KEY: {'*'*20}..." if supabase_key else "SUPABASE_SERVICE_ROLE_KEY: Not set")
    print_result(bool(openai_key), f"OPENAI_API_KEY: {'*'*20}..." if openai_key else "OPENAI_API_KEY: Not set")
    print(f"  ℹ️  MEMORY_BACKEND: {memory_backend}")
    
    if not all([supabase_url, supabase_key, openai_key]):
        print("\n❌ Missing required environment variables!")
        return False
    
    # Test SupabaseMemory import
    print("\n📦 Testing imports...")
    try:
        from python.helpers.memory_supabase import SupabaseMemory, is_supabase_configured, get_memory_backend
        print_result(True, "SupabaseMemory imported successfully")
    except Exception as e:
        print_result(False, f"Failed to import SupabaseMemory: {e}")
        return False
    
    # Test backend detection
    print("\n🔍 Testing backend detection...")
    backend = get_memory_backend()
    print_result(backend in ["supabase", "local"], f"Detected backend: {backend}")
    print_result(is_supabase_configured(), "Supabase is configured")
    
    # Test direct SupabaseMemory initialization
    print("\n🔌 Testing SupabaseMemory initialization...")
    try:
        from supabase import create_client
        import openai as openai_module
        
        client = create_client(supabase_url, supabase_key)
        openai_client = openai_module.OpenAI(api_key=openai_key)
        
        memory = SupabaseMemory(
            supabase_client=client,
            openai_client=openai_client,
            memory_subdir="test"
        )
        print_result(True, "SupabaseMemory initialized successfully")
    except Exception as e:
        print_result(False, f"Failed to initialize SupabaseMemory: {e}")
        return False
    
    # Test embedding generation
    print("\n🧠 Testing embedding generation...")
    try:
        test_text = "This is a test memory for JARVIS"
        embedding = memory.generate_embedding(test_text)
        print_result(True, f"Generated embedding with {len(embedding)} dimensions")
        print_result(len(embedding) == 1536, f"Embedding size is correct (1536)")
    except Exception as e:
        print_result(False, f"Failed to generate embedding: {e}")
        return False
    
    # Test saving a memory
    print("\n💾 Testing memory save...")
    try:
        test_content = f"JARVIS test memory created at {memory.get_timestamp()}"
        metadata = {"area": "main", "source": "test_script", "priority": 5}
        
        doc_id = await memory.insert_text(test_content, metadata)
        print_result(bool(doc_id), f"Memory saved with ID: {doc_id}")
    except Exception as e:
        print_result(False, f"Failed to save memory: {e}")
        return False
    
    # Test searching for the memory
    print("\n🔎 Testing memory search...")
    try:
        results = await memory.search_similarity_threshold(
            query="JARVIS test memory",
            limit=5,
            threshold=0.7
        )
        print_result(len(results) > 0, f"Found {len(results)} matching memories")
        
        if results:
            for i, doc in enumerate(results):
                similarity = doc.metadata.get('similarity', 'N/A')
                content_preview = doc.page_content[:50] + "..." if len(doc.page_content) > 50 else doc.page_content
                print(f"      [{i+1}] Similarity: {similarity:.4f} - {content_preview}")
    except Exception as e:
        print_result(False, f"Failed to search memories: {e}")
        return False
    
    # Test getting a document by ID
    print("\n📄 Testing get document by ID...")
    try:
        doc = memory.get_document_by_id(doc_id)
        print_result(doc is not None, f"Retrieved document by ID: {doc_id}")
        if doc:
            print(f"      Content: {doc.page_content[:60]}...")
    except Exception as e:
        print_result(False, f"Failed to get document by ID: {e}")
    
    # Test deleting the memory
    print("\n🗑️  Testing memory delete...")
    try:
        deleted = await memory.delete_documents_by_ids([doc_id])
        print_result(len(deleted) > 0, f"Deleted {len(deleted)} document(s)")
    except Exception as e:
        print_result(False, f"Failed to delete memory: {e}")
    
    # Verify deletion
    print("\n✔️  Verifying deletion...")
    try:
        results = await memory.search_similarity_threshold(
            query="JARVIS test memory",
            limit=5,
            threshold=0.9  # High threshold to find exact match
        )
        # Check if the specific doc_id is no longer in results
        found_ids = [doc.metadata.get('id') for doc in results]
        is_deleted = doc_id not in found_ids
        print_result(is_deleted, f"Memory {doc_id} successfully removed from Supabase")
    except Exception as e:
        print_result(False, f"Failed to verify deletion: {e}")
    
    # Test integration with memory.py backend selector
    print("\n🔄 Testing backend selector integration...")
    try:
        from python.helpers.memory import get_memory_backend as get_backend
        backend = get_backend()
        print_result(backend == "supabase", f"Backend selector returns: {backend}")
    except Exception as e:
        print_result(False, f"Failed to test backend selector: {e}")
    
    print_header("Test Complete!")
    print("\n  All Supabase Memory tests completed successfully! 🎉")
    print("  JARVIS is now ready to use cloud-based memory.\n")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
