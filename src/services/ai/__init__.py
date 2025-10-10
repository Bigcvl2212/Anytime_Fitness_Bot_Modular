"""
AI Services Package
Intelligent agents for admin and sales automation
"""

# Legacy admin/sales agents
try:
    from .ai_service_manager import AIServiceManager
    from .admin_ai_agent import AdminAIAgent
    from .sales_ai_agent import SalesAIAgent
    legacy_available = True
except ImportError:
    legacy_available = False

# New autonomous AI agent (Claude function calling)
from .tools_registry import ToolsRegistry
from .agent_core import GymAgentCore

if legacy_available:
    __all__ = ['AIServiceManager', 'AdminAIAgent', 'SalesAIAgent', 'ToolsRegistry', 'GymAgentCore']
else:
    __all__ = ['ToolsRegistry', 'GymAgentCore']