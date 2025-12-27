#!/usr/bin/env python3
"""
Test script for JARVIS Supabase integration
"""
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

print("=" * 50)
print("🧪 JARVIS Supabase Integration Test")
print("=" * 50)

try:
    from python.tools.supabase_client import SupabaseClient
    print("\n✅ Import successful!")
except ImportError as e:
    print(f"\n❌ Import failed: {e}")
    sys.exit(1)

try:
    # Initialize client
    print("\n📡 Connecting to Supabase...")
    client = SupabaseClient()
    print("✅ Connected successfully!")
    
    # Test 1: Get agents
    print("\n" + "-" * 40)
    print("📋 Test 1: Get Agents")
    print("-" * 40)
    agents = client.get_agents()
    print(f"Found {len(agents)} agents:")
    for agent in agents:
        print(f"   • {agent['name']} ({agent['type']})")
    
    # Test 2: Get entities
    print("\n" + "-" * 40)
    print("🏷️  Test 2: Get Entities")
    print("-" * 40)
    entities = client.get_entities()
    print(f"Found {len(entities)} entities:")
    for entity in entities:
        print(f"   • {entity['name']} ({entity['type']})")
    
    # Test 3: Create a task
    print("\n" + "-" * 40)
    print("📝 Test 3: Create Task")
    print("-" * 40)
    task = client.create_task(
        title="Test task from JARVIS setup",
        description="This is a test task to verify Supabase integration",
        priority=7
    )
    if task:
        print(f"✅ Task created!")
        print(f"   ID: {task['id']}")
        print(f"   Title: {task['title']}")
        print(f"   Status: {task['status']}")
    
    # Test 4: Update task
    print("\n" + "-" * 40)
    print("🔄 Test 4: Update Task")
    print("-" * 40)
    updated = client.update_task(task['id'], status="completed", result={"test": "success"})
    if updated:
        print(f"✅ Task updated!")
        print(f"   New status: {updated['status']}")
    
    # Test 5: Get all tasks
    print("\n" + "-" * 40)
    print("📋 Test 5: Get All Tasks")
    print("-" * 40)
    tasks = client.get_tasks(limit=5)
    print(f"Found {len(tasks)} tasks:")
    for t in tasks:
        print(f"   • {t['title']} (status: {t['status']})")
    
    # Test 6: Create entity
    print("\n" + "-" * 40)
    print("🏷️  Test 6: Create Entity")
    print("-" * 40)
    entity = client.create_entity(
        entity_type="test",
        name="Test Entity from Setup",
        properties={"created_by": "setup_script", "timestamp": "2025-12-25"}
    )
    if entity:
        print(f"✅ Entity created!")
        print(f"   ID: {entity['id']}")
        print(f"   Name: {entity['name']}")
    
    # Test 7: Create conversation and message
    print("\n" + "-" * 40)
    print("💬 Test 7: Create Conversation")
    print("-" * 40)
    conversation = client.create_conversation(title="Test Conversation")
    if conversation:
        print(f"✅ Conversation created: {conversation['id']}")
        
        # Add a message
        message = client.add_message(
            conversation_id=conversation['id'],
            role="user",
            content="Hello JARVIS, this is a test message!"
        )
        if message:
            print(f"✅ Message added: {message['id']}")
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed!")
    print("=" * 50)
    
    # Summary
    print("\n📊 Summary:")
    print(f"   • Agents in DB: {len(agents)}")
    print(f"   • Entities in DB: {len(entities) + 1}")  # +1 for the new one
    print(f"   • Tasks in DB: {len(tasks)}")
    print(f"   • New conversation created: Yes")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
