"""
Tools Registry

Central registry for all AI agent tools. Manages tool registration,
schemas, and execution routing.
"""

import logging
from typing import Dict, List, Callable, Any
import json

logger = logging.getLogger(__name__)

class ToolsRegistry:
    """Central registry for AI agent tools"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.schemas: List[Dict] = []
        self._tool_metadata: Dict[str, Dict] = {}
    
    def register_tool(
        self, 
        name: str, 
        func: Callable, 
        description: str,
        input_schema: Dict,
        category: str = "general",
        risk_level: str = "safe"
    ):
        """Register a tool with the agent
        
        Args:
            name: Tool name (must match function name)
            func: Tool function to execute
            description: Human-readable description for the AI
            input_schema: JSON schema for tool parameters
            category: Tool category (campaigns, collections, access, etc.)
            risk_level: 'safe', 'moderate', or 'high'
        """
        # Build Claude-compatible schema
        claude_schema = {
            "name": name,
            "description": description,
            "input_schema": input_schema
        }
        
        self.tools[name] = func
        self.schemas.append(claude_schema)
        self._tool_metadata[name] = {
            "category": category,
            "risk_level": risk_level,
            "description": description
        }
        
        logger.info(f"✅ Registered tool: {name} (category: {category}, risk: {risk_level})")
    
    def execute_tool(self, name: str, input_params: Dict) -> Any:
        """Execute a registered tool
        
        Args:
            name: Tool name
            input_params: Tool input parameters
        
        Returns:
            Tool execution result
        
        Raises:
            ValueError: If tool not found
        """
        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")
        
        tool_func = self.tools[name]
        metadata = self._tool_metadata.get(name, {})
        
        logger.info(f"🔧 Executing tool: {name} (category: {metadata.get('category', 'unknown')})")
        logger.debug(f"   Input: {json.dumps(input_params, indent=2)}")
        
        try:
            result = tool_func(**input_params)
            logger.info(f"✅ Tool {name} completed successfully")
            logger.debug(f"   Result: {json.dumps(result, default=str, indent=2)[:500]}...")
            return result
        except Exception as e:
            logger.error(f"❌ Tool {name} failed: {str(e)}")
            raise
    
    def get_tool_schemas(self) -> List[Dict]:
        """Get all tool schemas in Claude format"""
        return self.schemas
    
    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self.tools.keys())
    
    def get_tools_by_category(self, category: str) -> List[str]:
        """Get tools filtered by category"""
        return [
            name for name, metadata in self._tool_metadata.items()
            if metadata.get('category') == category
        ]
    
    def get_tool_info(self, name: str) -> Dict:
        """Get detailed info about a tool"""
        if name not in self.tools:
            return {}
        
        schema = next((s for s in self.schemas if s['name'] == name), {})
        metadata = self._tool_metadata.get(name, {})
        
        return {
            "name": name,
            "description": schema.get('description', ''),
            "category": metadata.get('category', 'unknown'),
            "risk_level": metadata.get('risk_level', 'unknown'),
            "parameters": schema.get('input_schema', {})
        }
    
    def get_high_risk_tools(self) -> List[str]:
        """Get list of high-risk tools"""
        return [
            name for name, metadata in self._tool_metadata.items()
            if metadata.get('risk_level') == 'high'
        ]
