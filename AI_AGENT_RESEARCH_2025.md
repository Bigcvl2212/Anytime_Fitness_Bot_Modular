# AI Agent Research: Building Autonomous Gym Management Agent (2025)

## Executive Summary

**Goal**: Build an autonomous AI agent that can manage ALL gym operations by using existing infrastructure as tools - inbox management, past due collections, door access control, appointment scheduling, etc.

**Key Insight**: Modern AI agents (2024-2025) use **function calling** (tool use) to interact with external systems. The agent doesn't just respond to messages - it can execute actions by calling predefined functions/tools.

## How Modern AI Agents Work

### Core Architecture Pattern

```
User Request
    ↓
AI Agent (Claude/GPT)
    ↓
Decides which tool(s) to call
    ↓
Execute tool(s) (ClubOS API, Database, etc.)
    ↓
Agent receives results
    ↓
Agent decides: Call more tools OR respond to user
    ↓
Final Response
```

### Key Components

1. **LLM with Tool Binding** - Claude/GPT model configured with available tools
2. **Tool Definitions** - JSON schemas describing what each function does
3. **Tool Execution** - Python functions that actually perform actions
4. **Orchestration Loop** - Logic that manages the conversation and tool execution
5. **State Management** - Tracking conversation history, tool results, agent decisions

---

## Implementation Strategy for Gym Bot

### Phase 1: Convert Existing Functions to AI Tools

Your existing infrastructure becomes **tools** the agent can call:

#### Tool Catalog

```python
# Tool 1: Inbox Management
@tool
def send_message_to_member(member_id: str, message: str) -> str:
    """Send a message to a member via ClubOS inbox"""
    # Uses existing ClubOSIntegration.send_message()
    return result

@tool
def get_member_messages(member_id: str, limit: int = 10) -> List[Dict]:
    """Retrieve recent messages from a member"""
    # Queries messages table
    return messages

# Tool 2: Collections Management
@tool
def get_past_due_members(threshold_days: int = 30) -> List[Dict]:
    """Get list of members with past due balances"""
    # Uses existing past_due query logic
    return past_due_list

@tool
def send_payment_reminder(member_id: str, amount: float) -> str:
    """Send automated payment reminder to past due member"""
    # Uses ClubOS messaging + templates
    return status

@tool
def create_payment_plan(member_id: str, installments: int) -> Dict:
    """Set up payment plan for past due member"""
    # Creates structured payment arrangement
    return plan_details

# Tool 3: Door Access Control
@tool
def grant_door_access(member_id: str, door_id: str, duration_hours: int) -> str:
    """Grant temporary door access to a member"""
    # Interfaces with door access system
    return access_code

@tool
def revoke_door_access(member_id: str, door_id: str) -> str:
    """Revoke door access from a member"""
    return status

@tool
def check_member_access_status(member_id: str) -> Dict:
    """Check current access permissions for a member"""
    return access_info

# Tool 4: Appointment Management
@tool
def schedule_training_session(member_id: str, trainer_id: str, datetime: str) -> Dict:
    """Schedule PT session for member"""
    # Uses ClubOS calendar API
    return appointment

@tool
def cancel_appointment(appointment_id: str, reason: str) -> str:
    """Cancel an appointment"""
    return status

@tool
def get_available_trainers(datetime: str) -> List[Dict]:
    """Get list of available trainers for given time"""
    return trainers

# Tool 5: Member Management
@tool
def get_member_profile(member_id: str) -> Dict:
    """Get complete member profile including billing, membership, appointments"""
    return profile

@tool
def update_member_status(member_id: str, status: str, reason: str) -> str:
    """Update member status (active, frozen, canceled)"""
    return result

@tool
def add_member_note(member_id: str, note: str, category: str) -> str:
    """Add a note to member's account"""
    return note_id

# Tool 6: Reporting & Analytics
@tool
def get_daily_checkins(date: str = "today") -> Dict:
    """Get check-in statistics for specified date"""
    return stats

@tool
def get_revenue_summary(period: str = "month") -> Dict:
    """Get revenue summary for specified period"""
    return revenue_data

@tool
def get_membership_trends() -> Dict:
    """Get membership growth/churn trends"""
    return trends
```

### Phase 2: Build Agent Orchestration Layer

#### Option A: Anthropic Claude Function Calling (Recommended)

```python
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Define tools in Claude format
tools = [
    {
        "name": "send_message_to_member",
        "description": "Send a message to a gym member via ClubOS inbox. Use this when you need to contact a member.",
        "input_schema": {
            "type": "object",
            "properties": {
                "member_id": {
                    "type": "string",
                    "description": "The ClubOS member ID"
                },
                "message": {
                    "type": "string",
                    "description": "The message content to send"
                }
            },
            "required": ["member_id", "message"]
        }
    },
    {
        "name": "get_past_due_members",
        "description": "Retrieve list of members with past due balances. Use this to identify members who need payment follow-up.",
        "input_schema": {
            "type": "object",
            "properties": {
                "threshold_days": {
                    "type": "integer",
                    "description": "Number of days past due to filter by (default 30)"
                }
            }
        }
    },
    # ... all other tools
]

# Tool execution mapping
def execute_tool(tool_name: str, tool_input: Dict) -> Any:
    """Execute the requested tool and return results"""
    tool_map = {
        "send_message_to_member": send_message_to_member,
        "get_past_due_members": get_past_due_members,
        "grant_door_access": grant_door_access,
        # ... map all tools
    }
    
    tool_func = tool_map.get(tool_name)
    if not tool_func:
        raise ValueError(f"Unknown tool: {tool_name}")
    
    return tool_func(**tool_input)

# Main agent loop
def autonomous_agent(user_request: str, max_iterations: int = 10) -> str:
    """Main agent orchestration loop with tool execution"""
    
    messages = [
        {
            "role": "user",
            "content": user_request
        }
    ]
    
    for iteration in range(max_iterations):
        # Call Claude with tools
        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )
        
        # Check if Claude wants to use tools
        if response.stop_reason == "tool_use":
            # Extract tool calls
            tool_use_blocks = [
                block for block in response.content 
                if block.type == "tool_use"
            ]
            
            # Execute each tool
            tool_results = []
            for tool_use in tool_use_blocks:
                tool_name = tool_use.name
                tool_input = tool_use.input
                
                print(f"[Agent] Calling tool: {tool_name}")
                print(f"[Agent] Input: {tool_input}")
                
                # Execute tool
                try:
                    result = execute_tool(tool_name, tool_input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": str(result)
                    })
                    print(f"[Agent] Result: {result}")
                except Exception as e:
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": f"Error: {str(e)}",
                        "is_error": True
                    })
            
            # Add assistant response and tool results to conversation
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            messages.append({
                "role": "user",
                "content": tool_results
            })
            
        else:
            # No more tools to call, return final response
            final_text = next(
                block.text for block in response.content 
                if hasattr(block, "text")
            )
            return final_text
    
    return "Max iterations reached without completion"
```

#### Option B: LangGraph State Machine (More Complex, More Control)

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    task: str  # Current task being performed
    context: Dict  # Accumulated context from tool calls

def agent_node(state: AgentState):
    """Main LLM decision node"""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    """Decide whether to call tools or end"""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

# Build graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

agent = workflow.compile()
```

### Phase 3: Autonomous Workflows

#### Example 1: Collections Management

```python
# Agent request
agent_request = """
You are the gym collections manager. Your task:
1. Get all members with past due balances over 30 days
2. For each member:
   - Check their message history to see if we've contacted them
   - If not contacted in last 7 days, send payment reminder
   - If contacted 3+ times, escalate to manager (add note)
3. Provide summary report

Execute this task autonomously.
"""

result = autonomous_agent(agent_request)
```

**Agent's autonomous actions:**
1. Calls `get_past_due_members(threshold_days=30)`
2. For each member:
   - Calls `get_member_messages(member_id)`
   - Analyzes message history
   - Calls `send_message_to_member()` OR `add_member_note()`
3. Compiles and returns summary

#### Example 2: Inbox Management

```python
# Agent request
agent_request = """
You are the gym inbox manager. Process all unread messages:
1. Get unread messages from database
2. For each message:
   - Classify intent (billing, appointment, complaint, info)
   - If billing question: Look up member account, respond with details
   - If appointment request: Check trainer availability, suggest times
   - If complaint: Add urgent note, notify manager
   - If general info: Respond directly
3. Mark messages as processed

Execute this task autonomously.
"""

result = autonomous_agent(agent_request)
```

#### Example 3: Daily Operations Dashboard

```python
# Agent request
agent_request = """
You are the gym operations assistant. Generate morning briefing:
1. Get yesterday's check-in count
2. Get current past due count and total amount
3. Get today's PT appointments
4. Identify any members who need follow-up
5. Check for any access issues
6. Compile into executive summary

Execute this task and format as markdown report.
"""

result = autonomous_agent(agent_request)
```

---

## Advanced Features

### 1. Multi-Step Reasoning

Agents can plan and execute multi-step workflows:

```python
# Example: Agent handles complex member issue
"""
Member John Smith (ID: C12345) messaged saying:
'I was charged twice this month and my door access stopped working'

Handle this issue completely.
"""

# Agent's autonomous plan:
# 1. get_member_profile(C12345) - Get billing/access info
# 2. check_member_access_status(C12345) - Verify access issue
# 3. grant_door_access(C12345, "main_door", 72) - Restore access
# 4. add_member_note(C12345, "Billing issue - double charge", "billing")
# 5. send_message_to_member(C12345, "We've restored your access...")
# 6. Return summary for manager review
```

### 2. Context Accumulation

Agent remembers tool results and uses them for decisions:

```python
# Agent maintains context across tool calls
context = {
    "member_profile": {...},  # From get_member_profile()
    "past_due_amount": 89.99,  # From profile
    "last_payment_date": "2025-01-15",
    "message_history": [...]  # From get_member_messages()
}

# Uses context to make intelligent decisions
# E.g., if last_payment was recent, be more lenient in reminder tone
```

### 3. Human-in-the-Loop

For sensitive operations, require human approval:

```python
from langgraph.types import interrupt

@tool
def cancel_membership(member_id: str, reason: str) -> str:
    """Cancel member's membership - requires approval"""
    
    # Interrupt and wait for human approval
    approval = interrupt({
        "action": "cancel_membership",
        "member_id": member_id,
        "reason": reason,
        "message": "Approve membership cancellation?"
    })
    
    if approval["approved"]:
        # Execute cancellation
        return cancel_membership_internal(member_id, reason)
    else:
        return "Cancellation rejected by operator"
```

### 4. Scheduled Autonomous Tasks

```python
# Daily morning routine
@scheduled("0 6 * * *")  # 6 AM daily
def morning_operations():
    autonomous_agent("""
    Execute morning operations checklist:
    1. Collections follow-up for past due > 30 days
    2. Process overnight messages
    3. Generate daily briefing
    4. Check equipment maintenance schedule
    5. Verify trainer schedules
    """)

# Hourly inbox check
@scheduled("0 * * * *")  # Every hour
def process_inbox():
    autonomous_agent("""
    Process new inbox messages:
    1. Get unread messages
    2. Respond to urgent items
    3. Queue non-urgent for batch processing
    """)
```

---

## Safety & Control

### 1. Tool Permission Levels

```python
# Define tool categories
SAFE_TOOLS = [
    "get_member_profile",
    "get_past_due_members",
    "check_member_access_status",
]

MODERATE_RISK = [
    "send_message_to_member",
    "add_member_note",
    "schedule_training_session",
]

HIGH_RISK = [
    "cancel_membership",
    "refund_payment",
    "revoke_door_access",
]

# Require confirmation for high-risk tools
def execute_tool_with_safety(tool_name: str, tool_input: Dict):
    if tool_name in HIGH_RISK:
        # Require human approval
        return request_approval(tool_name, tool_input)
    else:
        return execute_tool(tool_name, tool_input)
```

### 2. Audit Logging

```python
# Log every agent action
class AgentAction(Base):
    __tablename__ = "agent_actions"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    agent_id = Column(String)
    task_description = Column(Text)
    tool_called = Column(String)
    tool_input = Column(JSON)
    tool_result = Column(JSON)
    success = Column(Boolean)
    error = Column(Text, nullable=True)
    
# Every tool execution is logged
log_agent_action(
    tool_called="send_message_to_member",
    tool_input={"member_id": "C123", "message": "..."},
    tool_result="Message sent successfully",
    success=True
)
```

### 3. Rate Limiting

```python
from functools import wraps
import time

def rate_limit(max_calls: int, period_seconds: int):
    """Rate limit tool calls"""
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls
            calls[:] = [c for c in calls if now - c < period_seconds]
            
            if len(calls) >= max_calls:
                raise Exception(f"Rate limit exceeded: {max_calls} calls per {period_seconds}s")
            
            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_calls=10, period_seconds=60)
@tool
def send_message_to_member(member_id: str, message: str):
    """Send message with rate limiting"""
    # Max 10 messages per minute
    pass
```

---

## Implementation Roadmap

### Week 1-2: Tool Infrastructure
- ✅ Convert existing functions to @tool decorators
- ✅ Define tool schemas for Claude
- ✅ Build tool execution router
- ✅ Test individual tools

### Week 3-4: Agent Core
- ✅ Implement Claude function calling loop
- ✅ Add conversation state management
- ✅ Build tool result processing
- ✅ Test basic autonomous workflows

### Week 5-6: Safety & Control
- ✅ Add permission levels
- ✅ Implement audit logging
- ✅ Build approval workflow for high-risk actions
- ✅ Add rate limiting

### Week 7-8: Workflows
- ✅ Implement collections management workflow
- ✅ Implement inbox management workflow
- ✅ Implement daily operations workflow
- ✅ Build monitoring dashboard

### Week 9-10: Production Deployment
- ✅ Load testing
- ✅ Security audit
- ✅ Performance optimization
- ✅ Staff training
- ✅ Gradual rollout

---

## Cost Analysis

### Claude API Costs (2025 Pricing)

**Claude 3.7 Sonnet:**
- Input: $3 per million tokens
- Output: $15 per million tokens

**Estimated Monthly Usage:**
- Daily operations: ~10,000 requests/day
- Avg 1,000 input tokens, 500 output tokens per request
- Monthly: 300K requests
- Cost: (300K * 1K * $3/1M) + (300K * 500 * $15/1M) = $900 + $2,250 = **$3,150/month**

**Cost Savings:**
- Reduction in staff time: 20-30 hours/week = $2,400-$3,600/month
- Faster response times = better retention
- **ROI: Positive within 1-2 months**

---

## Key Takeaways

1. **Modern Pattern**: Function calling (tool use) is THE standard for 2024-2025 AI agents
2. **Your Advantage**: You already have the infrastructure - just expose it as tools
3. **Anthropic Claude** has best function calling reliability and reasoning
4. **LangGraph** provides more control but adds complexity - start with Claude directly
5. **Safety First**: Audit logs, rate limits, approval workflows for high-risk actions
6. **Start Small**: Collections workflow first, then expand to inbox, then full operations

---

## Next Steps

1. **Choose Implementation**: Anthropic Claude function calling (recommended for MVP)
2. **Build Tool Registry**: Convert 10-15 core functions first
3. **Test Agent Loop**: Validate tool calling works correctly
4. **Deploy First Workflow**: Collections management (lowest risk, high value)
5. **Iterate**: Add more tools and workflows based on results

**Ready to build this?** Start with the tool conversion - that's your foundation for everything else.
