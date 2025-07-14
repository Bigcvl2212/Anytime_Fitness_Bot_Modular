# Gym Bot Dashboard

A web-based dashboard for monitoring and controlling the Anytime Fitness Bot system.

## Features

- **System Status Monitoring**: Real-time health checks for all services
- **Workflow Management**: Execute workflows with configurable migration modes
- **Live Logs**: View system logs with filtering and auto-refresh
- **Service Configuration**: Monitor and manage system settings
- **Demo Mode**: Runs independently with mock data when gym_bot modules are unavailable

## Quick Start

1. **Install Flask** (if not already installed):
   ```bash
   pip install flask
   ```

2. **Start the dashboard**:
   ```bash
   python gym_bot_dashboard.py
   ```

3. **Access the dashboard**:
   Open your browser to http://localhost:5000

## Configuration

Environment variables:
- `DASHBOARD_HOST`: Host to bind to (default: 127.0.0.1)
- `DASHBOARD_PORT`: Port to bind to (default: 5000)
- `DASHBOARD_DEBUG`: Enable debug mode (default: False)
- `FLASK_SECRET_KEY`: Secret key for Flask sessions

## Pages

### Dashboard (/)
- System information and quick stats
- Service status indicators
- Recent log entries
- Auto-refreshing status updates

![Dashboard Main Page](https://github.com/user-attachments/assets/97d9179d-4b2a-4690-941e-aecb3e63f256)

### Workflows (/workflows)
- Execute different workflows (Message Processing, Payment Processing, etc.)
- Configure migration modes (API Only, Hybrid, Selenium Only, Testing)
- Real-time workflow output
- Background execution with live updates

![Workflows Page](https://github.com/user-attachments/assets/3f7cd961-4197-4221-977f-2fbcacc509c0)

### Logs (/logs)
- Complete system log history
- Filter by log level (INFO, WARNING, ERROR)
- Search functionality
- Auto-refresh capability
- Export logs to CSV

### Settings (/settings)
- System configuration overview
- Service status details
- Development tools and diagnostics
- Security information

## API Endpoints

- `GET /api/status` - Get current system status
- `GET /api/refresh-status` - Force refresh system status
- `POST /api/run-workflow` - Execute a workflow
- `GET /api/logs` - Get system logs

## Testing

Run the test suite:
```bash
python -m tests.test_dashboard
```

## Architecture

- **Flask Web Framework**: Lightweight web server and routing
- **Bootstrap UI**: Responsive, modern interface
- **Background Tasks**: Status monitoring and workflow execution
- **Mock Services**: Demo mode for development and testing
- **Template System**: Modular HTML templates with Jinja2

## Integration

The dashboard integrates with the existing gym bot system by importing:
- Core services (driver, authentication)
- API services (Square, Gemini AI, ClubOS)
- Migration services and configuration
- Workflow execution functions

When gym_bot modules are unavailable, it runs in demo mode with mock data.

## Development

### Adding New Workflows
1. Add workflow definition to `workflows_page()` function
2. Implement workflow execution in `api_run_workflow()` 
3. Update workflow runner to handle the new workflow

### Adding New Pages
1. Create HTML template in `templates/` directory
2. Add route handler function
3. Update navigation in `base.html`

### Extending API
1. Add new endpoint function with `@app.route` decorator
2. Implement business logic
3. Return appropriate JSON response

## Security Notes

- Dashboard runs without authentication in development mode
- For production use, implement proper authentication
- API keys are secured via Google Secret Manager
- All user inputs are validated and sanitized