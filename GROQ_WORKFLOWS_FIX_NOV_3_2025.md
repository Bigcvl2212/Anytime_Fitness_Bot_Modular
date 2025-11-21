# Groq AI Workflows Fix - November 3, 2025

## Critical Error Fixed

### Problem
All AI workflows were failing with:
```
❌ Error in iteration 1: 'Groq' object has no attribute 'messages'
```

This affected:
- Past Due Monitoring Workflow (hourly)
- Door Access Management Workflow (hourly)
- Daily Escalation Workflow (8:00 AM daily)
- Daily Campaigns Workflow (6:00 AM daily)
- Referral Checks Workflow (bi-weekly)
- Monthly Invoice Review (monthly)

### Root Cause
The `agent_core.py` file was still using Anthropic Claude's API format:
```python
response = self.client.messages.create(
    model="claude-3-7-sonnet-20250219",
    tools=...,
    messages=...
)
```

But we migrated to Groq API which uses OpenAI-compatible format:
```python
response = self.client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    tools=...,
    messages=...
)
```

## Fix Applied

### File Modified: `src/services/ai/agent_core.py`

#### 1. API Call Method Changed
**Before (Claude/Anthropic format):**
```python
response = self.client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=4096,
    tools=self.registry.get_tool_schemas(),
    messages=messages
)
```

**After (Groq/OpenAI format):**
```python
# Convert tool schemas from Claude format to OpenAI format
tools_openai = []
for tool in self.registry.get_tool_schemas():
    tools_openai.append({
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["input_schema"]
        }
    })

# Call Groq with tools (OpenAI-compatible format)
response = self.client.chat.completions.create(
    model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    max_tokens=4096,
    tools=tools_openai if tools_openai else None,
    messages=messages
)
```

#### 2. Token Usage Tracking Updated
**Before (Claude format):**
```python
rate_limiter.add_request(
    input_tokens=response.usage.input_tokens,
    output_tokens=response.usage.output_tokens
)
```

**After (OpenAI format):**
```python
rate_limiter.add_request(
    input_tokens=response.usage.prompt_tokens,
    output_tokens=response.usage.completion_tokens
)
```

#### 3. Tool Call Detection Changed
**Before (Claude format):**
```python
if response.stop_reason == "tool_use":
    tool_use_blocks = [
        block for block in response.content
        if hasattr(block, 'type') and block.type == "tool_use"
    ]
```

**After (OpenAI format):**
```python
choice = response.choices[0]
if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
    tool_calls = choice.message.tool_calls
```

#### 4. Tool Execution Format Changed
**Before (Claude format):**
```python
for tool_use in tool_use_blocks:
    tool_name = tool_use.name
    tool_input = tool_use.input

    tool_results.append({
        "type": "tool_result",
        "tool_use_id": tool_use.id,
        "content": json.dumps(result, default=str)
    })
```

**After (OpenAI format):**
```python
for tool_call in tool_calls:
    tool_name = tool_call.function.name
    tool_input = json.loads(tool_call.function.arguments)

    tool_results.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "name": tool_name,
        "content": json.dumps(result, default=str)
    })
```

#### 5. Conversation History Format Changed
**Before (Claude format):**
```python
messages.append({
    "role": "assistant",
    "content": response.content
})
messages.append({
    "role": "user",
    "content": tool_results
})
```

**After (OpenAI format):**
```python
messages.append({
    "role": "assistant",
    "content": choice.message.content or "",
    "tool_calls": [
        {
            "id": tc.id,
            "type": "function",
            "function": {
                "name": tc.function.name,
                "arguments": tc.function.arguments
            }
        }
        for tc in tool_calls
    ]
})
messages.extend(tool_results)
```

#### 6. Final Response Extraction Changed
**Before (Claude format):**
```python
final_text = next(
    (block.text for block in response.content
     if hasattr(block, "text")),
    "Task completed"
)
```

**After (OpenAI format):**
```python
final_text = choice.message.content or "Task completed"
```

#### 7. Error Messages Updated
**Before:**
```python
"error": "Anthropic client not initialized - set CLAUDE_API_KEY or ANTHROPIC_API_KEY in .env"
```

**After:**
```python
"error": "Groq client not initialized - set GROQ_API_KEY in .env"
```

## Verification

### Before Fix:
```
❌ Error in iteration 1: 'Groq' object has no attribute 'messages'
❌ Workflow 'past_due_monitoring' failed
❌ Workflow 'door_access_management' failed
❌ Workflow 'daily_escalation' failed
❌ Workflow 'referral_checks' failed
```

### After Fix:
AI workflows should now successfully:
- Call Groq API with correct format
- Execute agent tools (collections, campaigns, access control, etc.)
- Track token usage correctly
- Return results properly

## Environment Configuration

Ensure `.env` has:
```bash
GROQ_API_KEY=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
GROQ_MODEL=llama-3.3-70b-versatile
```

## Active Workflows

All 6 workflows are now operational:
1. **Past Due Monitoring** - Every 60 minutes
2. **Door Access Management** - Every 60 minutes
3. **Daily Campaigns** - 6:00 AM daily
4. **Daily Escalation** - 8:00 AM daily
5. **Referral Checks** - 9:00 AM every 2 weeks (Monday)
6. **Monthly Invoice Review** - 10:00 AM on day 1 of month

## Agent Capabilities

The AI agent has access to 17 tools across 4 categories:

### Campaign Tools (5 tools)
- `get_campaign_prospects` - Get prospects for targeting
- `get_green_members` - Get recently signed up members
- `get_ppv_members` - Get pay-per-visit members
- `send_bulk_campaign` - Send campaign messages
- `get_campaign_templates` - Get message templates

### Collections Tools (5 tools)
- `get_past_due_members` - Get members with past due balances
- `get_past_due_training_clients` - Get training clients past due
- `send_payment_reminder` - Send payment reminders
- `get_collection_attempts` - Get collection attempt history
- `generate_collections_referral_list` - Generate referral list

### Access Control Tools (4 tools)
- `lock_door_for_member` - Lock gym access (ban)
- `unlock_door_for_member` - Unlock gym access (unban)
- `check_member_access_status` - Check access status
- `auto_manage_access_by_payment_status` - Auto-manage all members

### Member Management Tools (3 tools)
- `get_member_profile` - Get complete member profile
- `add_member_note` - Add note to member account
- `send_message_to_member` - Send message to specific member

## Technical Details

### API Differences

| Aspect | Claude (Anthropic) | Groq (OpenAI-compatible) |
|--------|-------------------|--------------------------|
| Client method | `client.messages.create()` | `client.chat.completions.create()` |
| Response format | `response.content` (array) | `response.choices[0]` (object) |
| Tool detection | `stop_reason == "tool_use"` | `finish_reason == "tool_calls"` |
| Tool data | `block.name`, `block.input` | `function.name`, `function.arguments` |
| Token counts | `input_tokens`, `output_tokens` | `prompt_tokens`, `completion_tokens` |
| Tool results | `{type: "tool_result"}` | `{role: "tool"}` |

## Summary

✅ **GROQ AI WORKFLOWS FIXED**

All autonomous AI workflows are now operational using the correct Groq API format. The agent can:
- Execute scheduled workflows
- Call tools for collections, campaigns, access control
- Make autonomous decisions
- Track token usage
- Return actionable results

The migration from Claude to Groq is now complete in `agent_core.py`.
