"""
Gym AI Agent Core

Main agent orchestration using Groq function calling
"""

import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

try:
    from groq import Groq
except ImportError:
    Groq = None

from .tools_registry import ToolsRegistry
from .agent_tools import campaign_tools, collections_tools, access_tools, member_tools
from .rate_limiter import get_rate_limiter

logger = logging.getLogger(__name__)

class GymAgentCore:
    """Core AI agent using Groq function calling"""

    def __init__(self, api_key: str = None):
        """Initialize the agent

        Args:
            api_key: Groq API key (or set GROQ_API_KEY env var)
        """
        # Get Groq API key
        self.api_key = api_key or os.getenv('GROQ_API_KEY')

        if not self.api_key:
            logger.warning("⚠️ GROQ_API_KEY not found - agent will not be able to make decisions")

        # Initialize Groq client
        if Groq:
            self.client = Groq(api_key=self.api_key) if self.api_key else None
        else:
            self.client = None
            logger.warning("⚠️ Groq package not installed - run: pip install groq")

        # Initialize tools registry
        self.registry = ToolsRegistry()
        self._register_all_tools()

        logger.info(f"✅ Gym AI Agent initialized with {len(self.registry.list_tools())} tools")
    
    def _register_all_tools(self):
        """Register all available tools"""
        
        # Campaign tools
        self.registry.register_tool(
            name="get_campaign_prospects",
            func=campaign_tools.get_campaign_prospects,
            description="Get list of prospects for campaign targeting. Returns prospect details including contact info.",
            input_schema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Optional filters for prospects"
                    }
                }
            },
            category="campaigns",
            risk_level="safe"
        )
        
        self.registry.register_tool(
            name="get_green_members",
            func=campaign_tools.get_green_members,
            description="Get recently signed up members (green members) for welcome campaigns and engagement.",
            input_schema={
                "type": "object",
                "properties": {
                    "days_since_signup": {
                        "type": "integer",
                        "description": "Number of days since signup (default 30)"
                    }
                }
            },
            category="campaigns",
            risk_level="safe"
        )
        
        self.registry.register_tool(
            name="get_ppv_members",
            func=campaign_tools.get_ppv_members,
            description="Get pay-per-visit (PPV) members for conversion campaigns to full membership.",
            input_schema={
                "type": "object",
                "properties": {}
            },
            category="campaigns",
            risk_level="safe"
        )
        
        self.registry.register_tool(
            name="send_bulk_campaign",
            func=campaign_tools.send_bulk_campaign,
            description="Send bulk campaign message to a list of recipients. Use this to send marketing campaigns.",
            input_schema={
                "type": "object",
                "properties": {
                    "recipient_list": {
                        "type": "array",
                        "description": "List of recipients with id, name, phone, email"
                    },
                    "message_text": {
                        "type": "string",
                        "description": "Message content to send"
                    },
                    "campaign_name": {
                        "type": "string",
                        "description": "Campaign name for tracking"
                    },
                    "channel": {
                        "type": "string",
                        "enum": ["sms", "email"],
                        "description": "Communication channel"
                    }
                },
                "required": ["recipient_list", "message_text", "campaign_name"]
            },
            category="campaigns",
            risk_level="moderate"
        )
        
        self.registry.register_tool(
            name="get_campaign_templates",
            func=campaign_tools.get_campaign_templates,
            description="Get available campaign message templates for prospects, green members, PPV members, etc.",
            input_schema={
                "type": "object",
                "properties": {}
            },
            category="campaigns",
            risk_level="safe"
        )
        
        # Collections tools
        self.registry.register_tool(
            name="get_past_due_members",
            func=collections_tools.get_past_due_members,
            description="Get list of members with past due balances. Essential for collections workflow.",
            input_schema={
                "type": "object",
                "properties": {
                    "min_amount": {
                        "type": "number",
                        "description": "Minimum past due amount (default $0.01)"
                    }
                },
                "required": []
            },
            category="collections",
            risk_level="safe"
        )
        
        self.registry.register_tool(
            name="get_past_due_training_clients",
            func=collections_tools.get_past_due_training_clients,
            description="Get training clients with past due balances.",
            input_schema={
                "type": "object",
                "properties": {
                    "min_amount": {
                        "type": "number",
                        "description": "Minimum past due amount (default $0.01)"
                    }
                }
            },
            category="collections",
            risk_level="safe"
        )
        
        self.registry.register_tool(
            name="send_payment_reminder",
            func=collections_tools.send_payment_reminder,
            description="Send payment reminder to a past due member. Choose reminder_type based on escalation level.",
            input_schema={
                "type": "object",
                "properties": {
                    "member_id": {
                        "type": "string",
                        "description": "Member ID"
                    },
                    "amount_past_due": {
                        "type": "number",
                        "description": "Amount owed"
                    },
                    "reminder_type": {
                        "type": "string",
                        "enum": ["friendly", "firm", "final"],
                        "description": "Tone of reminder"
                    },
                    "channel": {
                        "type": "string",
                        "enum": ["sms", "email"],
                        "description": "Communication channel"
                    }
                },
                "required": ["member_id", "amount_past_due"]
            },
            category="collections",
            risk_level="moderate"
        )
        
        self.registry.register_tool(
            name="get_collection_attempts",
            func=collections_tools.get_collection_attempts,
            description="Get collection attempt history for a member to track escalation.",
            input_schema={
                "type": "object",
                "properties": {
                    "member_id": {
                        "type": "string",
                        "description": "Member ID"
                    },
                    "days_back": {
                        "type": "integer",
                        "description": "Days to look back (default 30)"
                    }
                },
                "required": ["member_id"]
            },
            category="collections",
            risk_level="safe"
        )
        
        self.registry.register_tool(
            name="generate_collections_referral_list",
            func=collections_tools.generate_collections_referral_list,
            description="Generate list of members to refer to external collections agency after multiple failed attempts.",
            input_schema={
                "type": "object",
                "properties": {
                    "min_attempts": {
                        "type": "integer",
                        "description": "Minimum attempts before referral (default 3)"
                    },
                    "min_days_past_due": {
                        "type": "integer",
                        "description": "Minimum days past due (default 14)"
                    },
                    "min_amount": {
                        "type": "number",
                        "description": "Minimum amount to refer (default $50)"
                    }
                }
            },
            category="collections",
            risk_level="high"
        )
        
        # Access control tools
        self.registry.register_tool(
            name="lock_door_for_member",
            func=access_tools.lock_door_for_member,
            description="Lock gym door access for a member (ban via ClubHub API). Use when member is past due.",
            input_schema={
                "type": "object",
                "properties": {
                    "member_id": {
                        "type": "string",
                        "description": "Member ID"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for locking"
                    }
                },
                "required": ["member_id"]
            },
            category="access",
            risk_level="high"
        )
        
        self.registry.register_tool(
            name="unlock_door_for_member",
            func=access_tools.unlock_door_for_member,
            description="Unlock gym door access for a member (unban via ClubHub API). Use when payment is resolved.",
            input_schema={
                "type": "object",
                "properties": {
                    "member_id": {
                        "type": "string",
                        "description": "Member ID"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for unlocking"
                    }
                },
                "required": ["member_id"]
            },
            category="access",
            risk_level="high"
        )
        
        self.registry.register_tool(
            name="check_member_access_status",
            func=access_tools.check_member_access_status,
            description="Check current door access status for a member.",
            input_schema={
                "type": "object",
                "properties": {
                    "member_id": {
                        "type": "string",
                        "description": "Member ID"
                    }
                },
                "required": ["member_id"]
            },
            category="access",
            risk_level="safe"
        )
        
        self.registry.register_tool(
            name="auto_manage_access_by_payment_status",
            func=access_tools.auto_manage_access_by_payment_status,
            description="Automatically manage door access for all members based on payment status. Locks past due, unlocks paid.",
            input_schema={
                "type": "object",
                "properties": {
                    "min_past_due_amount": {
                        "type": "number",
                        "description": "Minimum amount to trigger lock (default $0.01)"
                    },
                    "grace_period_days": {
                        "type": "integer",
                        "description": "Grace period before locking (default 3 days)"
                    }
                }
            },
            category="access",
            risk_level="high"
        )
        
        # Member management tools
        self.registry.register_tool(
            name="get_member_profile",
            func=member_tools.get_member_profile,
            description="Get complete member profile including billing, membership status, and access status.",
            input_schema={
                "type": "object",
                "properties": {
                    "member_id": {
                        "type": "string",
                        "description": "Member ID"
                    }
                },
                "required": ["member_id"]
            },
            category="members",
            risk_level="safe"
        )
        
        self.registry.register_tool(
            name="add_member_note",
            func=member_tools.add_member_note,
            description="Add a note to member's account for tracking issues, complaints, or important info.",
            input_schema={
                "type": "object",
                "properties": {
                    "member_id": {
                        "type": "string",
                        "description": "Member ID"
                    },
                    "note_text": {
                        "type": "string",
                        "description": "Note content"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["billing", "service", "complaint", "general"],
                        "description": "Note category"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "normal", "high", "urgent"],
                        "description": "Note priority"
                    }
                },
                "required": ["member_id", "note_text"]
            },
            category="members",
            risk_level="safe"
        )
        
        self.registry.register_tool(
            name="send_message_to_member",
            func=member_tools.send_message_to_member,
            description="Send a message to a specific member via SMS or email.",
            input_schema={
                "type": "object",
                "properties": {
                    "member_id": {
                        "type": "string",
                        "description": "Member ID"
                    },
                    "message_text": {
                        "type": "string",
                        "description": "Message content"
                    },
                    "channel": {
                        "type": "string",
                        "enum": ["sms", "email"],
                        "description": "Communication channel"
                    }
                },
                "required": ["member_id", "message_text"]
            },
            category="members",
            risk_level="moderate"
        )
    
    def execute_task(self, task_description: str, max_iterations: int = 10) -> Dict[str, Any]:
        """Execute an autonomous task using Claude
        
        Args:
            task_description: Natural language task description
            max_iterations: Maximum tool-calling iterations
        
        Returns:
            {
                "success": True,
                "result": "...",
                "tool_calls": [...],
                "iterations": 3
            }
        """
        if not self.client:
            return {
                "success": False,
                "error": "Anthropic client not initialized - set CLAUDE_API_KEY or ANTHROPIC_API_KEY in .env"
            }
        
        logger.info(f"🤖 Starting autonomous task: {task_description[:100]}...")
        
        rate_limiter = get_rate_limiter()
        
        messages = [
            {
                "role": "user",
                "content": task_description
            }
        ]
        
        tool_calls_made = []
        
        for iteration in range(max_iterations):
            try:
                logger.info(f"   Iteration {iteration + 1}/{max_iterations}")
                
                # Check rate limit before calling Claude (estimate 5K tokens per call)
                rate_limiter.wait_if_needed(estimated_tokens=5000)
                
                # Call Claude with tools
                response = self.client.messages.create(
                    model="claude-3-7-sonnet-20250219",
                    max_tokens=4096,
                    tools=self.registry.get_tool_schemas(),
                    messages=messages
                )
                
                # Record actual token usage
                rate_limiter.add_request(
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens
                )
                
                logger.info(f"   📊 Tokens: {response.usage.input_tokens} in, {response.usage.output_tokens} out")
                
                # Check if Claude wants to use tools
                if response.stop_reason == "tool_use":
                    # Extract tool calls
                    tool_use_blocks = [
                        block for block in response.content 
                        if hasattr(block, 'type') and block.type == "tool_use"
                    ]
                    
                    # Execute each tool
                    tool_results = []
                    for tool_use in tool_use_blocks:
                        tool_name = tool_use.name
                        tool_input = tool_use.input
                        
                        logger.info(f"   🔧 Calling: {tool_name}")
                        
                        # Execute tool
                        try:
                            result = self.registry.execute_tool(tool_name, tool_input)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": json.dumps(result, default=str)
                            })
                            
                            tool_calls_made.append({
                                "tool": tool_name,
                                "input": tool_input,
                                "result": result,
                                "success": True
                            })
                            
                        except Exception as e:
                            logger.error(f"   ❌ Tool error: {e}")
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": f"Error: {str(e)}",
                                "is_error": True
                            })
                            
                            tool_calls_made.append({
                                "tool": tool_name,
                                "input": tool_input,
                                "error": str(e),
                                "success": False
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
                        (block.text for block in response.content 
                         if hasattr(block, "text")),
                        "Task completed"
                    )
                    
                    logger.info(f"✅ Task completed in {iteration + 1} iterations")
                    
                    return {
                        "success": True,
                        "result": final_text,
                        "tool_calls": tool_calls_made,
                        "iterations": iteration + 1
                    }
            
            except Exception as e:
                logger.error(f"❌ Error in iteration {iteration + 1}: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "tool_calls": tool_calls_made,
                    "iterations": iteration + 1
                }
        
        return {
            "success": False,
            "error": "Max iterations reached without completion",
            "tool_calls": tool_calls_made,
            "iterations": max_iterations
        }
    
    def list_available_tools(self) -> List[Dict[str, Any]]:
        """List all available tools with descriptions"""
        tools = []
        for tool_name in self.registry.list_tools():
            tools.append(self.registry.get_tool_info(tool_name))
        return tools
