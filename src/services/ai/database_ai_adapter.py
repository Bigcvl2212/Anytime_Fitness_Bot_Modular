#!/usr/bin/env python3
"""
Database AI Adapter
Converts natural language queries to safe SQL and interprets results
"""

import logging
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseAIAdapter:
    """
    Handles natural language to SQL conversion and safe query execution
    """

    def __init__(self, db_manager, ai_service_manager):
        """
        Initialize Database AI Adapter

        Args:
            db_manager: Database manager instance
            ai_service_manager: AI service for natural language processing
        """
        self.db_manager = db_manager
        self.ai_service = ai_service_manager

        # Approved table schema for safe queries
        self.approved_tables = {
            'admin_users': {
                'columns': ['id', 'manager_id', 'username', 'email', 'is_admin', 'is_super_admin',
                           'is_active', 'created_at', 'updated_at', 'last_login', 'login_attempts'],
                'safe_operations': ['SELECT', 'COUNT']
            },
            'audit_log': {
                'columns': ['id', 'admin_user_id', 'action', 'target_type', 'target_id',
                           'description', 'success', 'created_at'],
                'safe_operations': ['SELECT', 'COUNT']
            },
            'members': {
                'columns': ['id', 'prospect_id', 'member_id', 'first_name', 'last_name', 'email',
                           'mobile_phone', 'status', 'amount_past_due', 'last_payment_date',
                           'created_at', 'updated_at'],
                'safe_operations': ['SELECT', 'COUNT']
            },
            'training_clients': {
                'columns': ['id', 'member_name', 'total_past_due', 'payment_status',
                           'sessions_remaining', 'trainer_name', 'active_packages'],
                'safe_operations': ['SELECT', 'COUNT']
            },
            'campaigns': {
                'columns': ['id', 'name', 'category', 'status', 'total_recipients',
                           'created_at', 'started_at', 'completed_at'],
                'safe_operations': ['SELECT', 'COUNT']
            }
        }

        # Common query patterns for quick recognition
        self.query_patterns = {
            'user_count': r'how many (users?|admins?)',
            'past_due': r'(past due|overdue|behind)',
            'recent_activity': r'(recent|today|yesterday|last week)',
            'campaign_status': r'(campaign|messaging)',
            'system_health': r'(health|status|errors?)'
        }

    async def process_natural_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process natural language query and return results

        Args:
            query: Natural language query from user
            context: Additional context (user permissions, etc.)

        Returns:
            Dictionary with query results and metadata
        """
        try:
            logger.info(f"🔍 Processing natural language query: {query}")

            # Step 1: Analyze query intent and generate SQL
            sql_result = await self._generate_sql_from_query(query, context)

            if not sql_result['success']:
                return sql_result

            sql_query = sql_result['sql']
            explanation = sql_result['explanation']

            # Step 2: Validate and execute SQL
            execution_result = await self._execute_safe_query(sql_query)

            if not execution_result['success']:
                return execution_result

            # Step 3: Interpret results with AI
            interpretation = await self._interpret_results(query, execution_result['data'], explanation)

            return {
                'success': True,
                'query': query,
                'sql': sql_query,
                'data': execution_result['data'],
                'interpretation': interpretation,
                'row_count': len(execution_result['data']) if execution_result['data'] else 0,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error processing natural query: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query,
                'timestamp': datetime.now().isoformat()
            }

    async def _generate_sql_from_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate SQL from natural language query using AI"""
        try:
            # Build system prompt with database schema
            schema_info = self._build_schema_prompt()

            system_prompt = f"""You are a SQL generator for a gym management system. Convert natural language queries to safe SQL.

Database Schema:
{schema_info}

Important Rules:
1. ONLY use SELECT and COUNT operations
2. ONLY query the approved tables listed above
3. Always use proper SQL syntax
4. Include appropriate WHERE clauses for filtering
5. Use LIMIT for large result sets (max 100 rows)
6. Return JSON with: {{"sql": "query", "explanation": "what this query does"}}
7. If query is unsafe or not possible, return {{"error": "reason"}}

Examples:
- "How many admin users" → SELECT COUNT(*) FROM admin_users
- "Show recent logins" → SELECT username, last_login FROM admin_users WHERE last_login IS NOT NULL ORDER BY last_login DESC LIMIT 10
- "Past due members" → SELECT first_name, last_name, amount_past_due FROM members WHERE amount_past_due > 0 ORDER BY amount_past_due DESC LIMIT 20"""

            messages = [
                {
                    "role": "user",
                    "content": f"Convert this query to SQL: {query}"
                }
            ]

            ai_response = await self.ai_service.send_message(messages, system_prompt)

            if not ai_response['success']:
                return {
                    'success': False,
                    'error': f"AI query generation failed: {ai_response['error']}"
                }

            # Parse AI response
            try:
                response_text = ai_response['response'].strip()

                # Extract JSON from response (handle both direct JSON and text with JSON)
                if response_text.startswith('{'):
                    parsed = json.loads(response_text)
                else:
                    # Look for JSON in the response
                    json_match = re.search(r'\{[^}]+\}', response_text)
                    if json_match:
                        parsed = json.loads(json_match.group())
                    else:
                        return {
                            'success': False,
                            'error': "Could not parse AI response as JSON"
                        }

                if 'error' in parsed:
                    return {
                        'success': False,
                        'error': parsed['error']
                    }

                return {
                    'success': True,
                    'sql': parsed.get('sql', ''),
                    'explanation': parsed.get('explanation', 'SQL query generated from natural language')
                }

            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse AI SQL response: {e}")
                return {
                    'success': False,
                    'error': "Invalid response format from AI"
                }

        except Exception as e:
            logger.error(f"❌ Error generating SQL from query: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _build_schema_prompt(self) -> str:
        """Build database schema information for AI prompt"""
        schema_lines = []

        for table, info in self.approved_tables.items():
            columns = ', '.join(info['columns'])
            operations = ', '.join(info['safe_operations'])
            schema_lines.append(f"Table: {table}")
            schema_lines.append(f"  Columns: {columns}")
            schema_lines.append(f"  Allowed: {operations}")
            schema_lines.append("")

        return '\n'.join(schema_lines)

    async def _execute_safe_query(self, sql: str) -> Dict[str, Any]:
        """Execute SQL query with safety checks"""
        try:
            # Safety validation
            if not self._is_query_safe(sql):
                return {
                    'success': False,
                    'error': 'Query failed safety validation'
                }

            # Execute query
            logger.info(f"🔍 Executing safe SQL: {sql}")
            results = self.db_manager.execute_query(sql, fetch_all=True)

            # Convert to list of dictionaries
            if results:
                data = [dict(row) for row in results]
            else:
                data = []

            return {
                'success': True,
                'data': data,
                'row_count': len(data)
            }

        except Exception as e:
            logger.error(f"❌ Error executing safe query: {e}")
            return {
                'success': False,
                'error': f"Query execution failed: {str(e)}"
            }

    def _is_query_safe(self, sql: str) -> bool:
        """Validate SQL query for safety"""
        try:
            sql_upper = sql.upper().strip()

            # Check for allowed operations only
            if not (sql_upper.startswith('SELECT') or 'COUNT(' in sql_upper):
                logger.warning(f"⚠️ Unsafe SQL operation: {sql}")
                return False

            # Check for dangerous keywords
            dangerous_keywords = [
                'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
                'TRUNCATE', 'EXEC', 'EXECUTE', 'UNION', 'SCRIPT', '--',
                'INFORMATION_SCHEMA', 'SYS', 'MASTER'
            ]

            for keyword in dangerous_keywords:
                if keyword in sql_upper:
                    logger.warning(f"⚠️ Dangerous keyword in SQL: {keyword}")
                    return False

            # Check for approved tables only
            referenced_tables = self._extract_table_names(sql)
            for table in referenced_tables:
                if table not in self.approved_tables:
                    logger.warning(f"⚠️ Unauthorized table access: {table}")
                    return False

            return True

        except Exception as e:
            logger.error(f"❌ Error validating SQL safety: {e}")
            return False

    def _extract_table_names(self, sql: str) -> List[str]:
        """Extract table names from SQL query"""
        try:
            # Simple regex to find table names after FROM and JOIN
            pattern = r'(?:FROM|JOIN)\s+(\w+)'
            matches = re.findall(pattern, sql, re.IGNORECASE)
            return [match.lower() for match in matches]

        except Exception as e:
            logger.error(f"❌ Error extracting table names: {e}")
            return []

    async def _interpret_results(self, original_query: str, data: List[Dict], explanation: str) -> str:
        """Use AI to interpret query results in natural language"""
        try:
            if not data:
                return "No results found for your query."

            # Prepare data summary for AI
            data_summary = {
                'row_count': len(data),
                'columns': list(data[0].keys()) if data else [],
                'sample_data': data[:5] if len(data) > 5 else data  # First 5 rows
            }

            system_prompt = """You are a data interpreter for a gym management system.

Explain query results in clear, natural language that's helpful for gym administrators.
Focus on key insights, patterns, and actionable information.
Keep explanations concise but informative."""

            user_message = f"""
Original query: "{original_query}"
SQL explanation: {explanation}
Results summary: {json.dumps(data_summary, default=str, indent=2)}

Please provide a clear, helpful explanation of these results."""

            messages = [{"role": "user", "content": user_message}]

            ai_response = await self.ai_service.send_message(messages, system_prompt)

            if ai_response['success']:
                return ai_response['response']
            else:
                return f"Found {len(data)} results. {explanation}"

        except Exception as e:
            logger.error(f"❌ Error interpreting results: {e}")
            return f"Found {len(data)} results from your query."

    def get_quick_stats(self) -> Dict[str, Any]:
        """Get quick database statistics for dashboard"""
        try:
            stats = {}

            # Safe queries for common stats
            safe_queries = {
                'total_admins': 'SELECT COUNT(*) as count FROM admin_users WHERE is_active = 1',
                'total_members': 'SELECT COUNT(*) as count FROM members',
                'past_due_members': 'SELECT COUNT(*) as count FROM members WHERE amount_past_due > 0',
                'recent_logins': 'SELECT COUNT(*) as count FROM admin_users WHERE last_login >= date("now", "-7 days")',
                'active_campaigns': 'SELECT COUNT(*) as count FROM campaigns WHERE status = "running"'
            }

            for stat_name, query in safe_queries.items():
                try:
                    result = self.db_manager.execute_query(query, fetch_one=True)
                    stats[stat_name] = result['count'] if result else 0
                except Exception as e:
                    logger.warning(f"⚠️ Failed to get {stat_name}: {e}")
                    stats[stat_name] = 0

            return {
                'success': True,
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Error getting quick stats: {e}")
            return {
                'success': False,
                'error': str(e)
            }