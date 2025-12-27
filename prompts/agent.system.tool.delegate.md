### delegate

Delegate tasks to specialist sub-agents for focused execution.
Available agents:

- **research**: Information gathering, analysis, competitor research, market analysis
- **writer**: Content creation, copywriting, emails, documentation, blog posts
- **ops**: Operations, automation, system tasks, DevOps

When to delegate:

- Task requires specialized expertise
- Task can run independently without user interaction
- Task is well-defined with clear deliverables

Example usages:

~~~json
{
    "thoughts": [
        "User needs competitor analysis",
        "This is a research task - perfect for the research agent",
        "I'll delegate with clear context"
    ],
    "tool_name": "delegate",
    "tool_args": {
        "agent": "research",
        "task": "Analyze top 5 competitors in Swedish SaaS market",
        "description": "Find companies similar to Acme AB, analyze their pricing, features, and market positioning",
        "context": "Acme AB is a B2B SaaS company selling project management tools to SMEs"
    }
}
~~~

~~~json
{
    "thoughts": [
        "I need to create outreach content",
        "The writer agent specializes in this",
        "I'll provide the research context"
    ],
    "tool_name": "delegate",
    "tool_args": {
        "agent": "writer",
        "task": "Write cold outreach email to CEO",
        "description": "Create a personalized cold email for CEO of TechCorp AB",
        "context": "Target: Johan Svensson, CEO of TechCorp. They recently raised Series A. Pain points: scaling their team."
    }
}
~~~

~~~json
{
    "thoughts": [
        "Need to set up a monitoring script",
        "This is an ops task"
    ],
    "tool_name": "delegate",
    "tool_args": {
        "agent": "ops",
        "task": "Create uptime monitoring script",
        "description": "Python script that checks if api.example.com is responding every 5 minutes",
        "context": "Should log results to a file and alert if down for more than 15 minutes"
    }
}
~~~

**Response handling:**

- Subordinate results are saved to Supabase tasks table with status 'completed'
- Long responses may be truncated - use task_list to see full results
- Failed tasks are marked with status 'failed' and include error details
