# Gym Bot MCP Server

A comprehensive Model Context Protocol (MCP) server specifically designed for Anytime Fitness Bot development, production deployment, and ongoing maintenance.

## Features

### Development Tools
- **ClubOS API Analysis**: Analyze HAR files to understand API patterns
- **API Sequence Testing**: Test authentication flows and member operations
- **Member Data Validation**: Validate data structures and detect anomalies
- **Test Data Generation**: Generate realistic test scenarios

### Production Deployment
- **Safe Deployment**: Deploy with automated backups and testing
- **Database Management**: Initialize, migrate, and maintain databases
- **Environment Configuration**: Secure credential and config management
- **Monitoring Setup**: Configure logging, alerts, and health checks

### Maintenance & Operations
- **Health Monitoring**: Comprehensive system health checks
- **Performance Analysis**: Identify bottlenecks and optimization opportunities
- **Automated Backups**: Full system backup and restore capabilities
- **Log Analysis**: Parse and analyze system logs for insights
- **Dependency Management**: Safe dependency updates with testing

### Specialized Gym Bot Tools
- **Member Payment Analysis**: Track past-due accounts and payment patterns
- **ClubOS Session Management**: Handle authentication tokens and sessions
- **Report Generation**: Generate operational reports in multiple formats
- **Database Operations**: Gym-specific database queries and maintenance

## Installation

1. Install dependencies:
```bash
cd /workspaces/Anytime_Fitness_Bot_Modular/mcp-server
pip install -r requirements.txt
```

2. Test the server:
```bash
python gym-bot-mcp.py --help
```

## Usage

### Start the Server
```bash
# Start manually
python gym-bot-mcp.py

# Start with control script
./server-control.sh start
```

### Server Management
```bash
# Check status
./server-control.sh status

# Health check
./server-control.sh health

# Restart server
./server-control.sh restart

# Stop server
./server-control.sh stop

# Monitor continuously
./server-control.sh monitor
```

### Integration with VS Code

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "gym-bot": {
      "command": "python",
      "args": ["/workspaces/Anytime_Fitness_Bot_Modular/mcp-server/gym-bot-mcp.py"],
      "env": {
        "WORKSPACE_PATH": "/workspaces/Anytime_Fitness_Bot_Modular"
      }
    }
  }
}
```

## Available Tools

### Development
- `analyze_clubos_api` - Analyze ClubOS API endpoints from HAR files
- `test_api_sequence` - Test authentication and API call sequences
- `validate_member_data` - Validate member data structures
- `generate_test_data` - Generate realistic test scenarios

### Production
- `deploy_to_production` - Safe production deployment with checks
- `setup_database` - Database initialization and migration
- `configure_environment` - Environment and credential setup
- `setup_monitoring` - Configure monitoring and alerting

### Maintenance
- `health_check` - Comprehensive system health analysis
- `performance_analysis` - Performance monitoring and optimization
- `backup_system` - Full system backup and restore
- `log_analysis` - Log parsing and analysis
- `update_dependencies` - Safe dependency management

### Specialized
- `member_payment_analysis` - Member payment and collections analysis
- `clubos_session_manager` - ClubOS authentication management
- `generate_reports` - Operational report generation
- `database_operations` - Gym-specific database operations

## Configuration

The server uses these default configurations:

- **Workspace**: `/workspaces/Anytime_Fitness_Bot_Modular`
- **ClubOS API**: `https://anytimefitness.clubos.com`
- **Database**: `data/gym_bot.db`
- **Logs**: `logs/`
- **Backups**: `backups/`

## Security

- Never exposes actual credentials in logs or outputs
- Uses placeholder credentials in demonstrations
- Enforces HTTPS-only connections
- Implements proper session management
- Validates all inputs and outputs

## Monitoring

The server includes comprehensive monitoring:

- Process health checks
- API endpoint monitoring
- Database connectivity tests
- Log analysis and alerting
- Performance metrics tracking

## Troubleshooting

### Common Issues

1. **Server won't start**:
   ```bash
   # Check dependencies
   pip install -r requirements.txt
   
   # Check logs
   tail -f logs/server.log
   ```

2. **MCP connection issues**:
   ```bash
   # Verify server is running
   ./server-control.sh status
   
   # Test health
   ./server-control.sh health
   ```

3. **Permission errors**:
   ```bash
   # Fix permissions
   chmod +x server-control.sh
   chmod 644 *.py
   ```

## Development

### Adding New Tools

1. Add tool definition to `handle_list_tools()`
2. Implement tool logic in `handle_call_tool()`
3. Add implementation function
4. Update documentation

### Testing

```bash
# Run tests
python -m pytest tests/ -v

# Test specific tool
python -c "from gym_bot_mcp import *; test_tool('health_check')"
```

## Support

For issues and feature requests, check the main repository documentation or logs in `logs/server.log`.
