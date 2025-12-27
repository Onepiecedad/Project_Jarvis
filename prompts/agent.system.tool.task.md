## Task management tools

manage tasks assigned to agents

### task_create

create a new task for an agent

- title: task title (required)
- description: detailed task description
- agent: agent name (default: jarvis)
- priority: 1-10 (default: 5, higher = more important)
usage:

~~~json
{
    "thoughts": [
        "I need to create a new task for...",
    ],
    "headline": "Creating a new task",
    "tool_name": "task_create",
    "tool_args": {
        "title": "Analyze project requirements",
        "description": "Review and document the technical requirements",
        "agent": "research",
        "priority": 7
    }
}
~~~

### task_update

update an existing task status or result

- task_id: UUID of the task (required)
- status: pending, active, running, completed, failed, cancelled
- result: task result data (string or dict)
- priority: new priority level
- description: updated description
usage:

~~~json
{
    "thoughts": [
        "I need to mark this task as completed...",
    ],
    "headline": "Updating task status",
    "tool_name": "task_update",
    "tool_args": {
        "task_id": "12345678-1234-1234-1234-123456789abc",
        "status": "completed",
        "result": "Task completed successfully with results..."
    }
}
~~~

### task_list

list tasks with optional filters

- status: filter by status (pending, active, completed, failed)
- agent: filter by agent name
- limit: max results (default: 10)
usage:

~~~json
{
    "thoughts": [
        "Let me check what tasks are pending...",
    ],
    "headline": "Listing pending tasks",
    "tool_name": "task_list",
    "tool_args": {
        "status": "pending",
        "agent": "jarvis",
        "limit": 20
    }
}
~~~
