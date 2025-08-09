#!/bin/bash

# Gym Bot MCP Server Launcher
# Provides safe startup, monitoring, and recovery for the custom MCP server

set -euo pipefail

# Configuration
SERVER_DIR="/workspaces/Anytime_Fitness_Bot_Modular/mcp-server"
# Use the simpler, production-ready MCP server script by default
SERVER_SCRIPT="simple-gym-mcp.py"
PID_FILE="$SERVER_DIR/server.pid"
LOG_FILE="$SERVER_DIR/logs/server.log"
MAX_RETRIES=3
RETRY_DELAY=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Create necessary directories
mkdir -p "$SERVER_DIR/logs"
mkdir -p "$SERVER_DIR/data"
mkdir -p "$SERVER_DIR/backups"

# Check if server is already running
is_running() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Start the server
start_server() {
    if is_running; then
        warning "MCP Server is already running (PID: $(cat $PID_FILE))"
        return 0
    fi

    log "Starting Gym Bot MCP Server..."
    
    # Change to server directory
    cd "$SERVER_DIR"
    
    # Start server in background with an open stdin (MCP stdio servers exit when stdin closes)
    bash -c "tail -f /dev/null | python3 '$SERVER_SCRIPT'" > "$LOG_FILE" 2>&1 &
    local pid=$!
    
    # Save PID
    echo $pid > "$PID_FILE"
    
    # Wait a moment and check if it started successfully
    sleep 2
    if ps -p $pid > /dev/null 2>&1; then
        success "MCP Server started successfully (PID: $pid)"
        return 0
    else
        error "Failed to start MCP Server"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Stop the server
stop_server() {
    if ! is_running; then
        warning "MCP Server is not running"
        return 0
    fi

    local pid=$(cat "$PID_FILE")
    log "Stopping MCP Server (PID: $pid)..."
    
    kill $pid
    sleep 2
    
    if ps -p $pid > /dev/null 2>&1; then
        warning "Server did not stop gracefully, forcing..."
        kill -9 $pid
        sleep 1
    fi
    
    rm -f "$PID_FILE"
    success "MCP Server stopped"
}

# Restart the server
restart_server() {
    log "Restarting MCP Server..."
    stop_server
    sleep 1
    start_server
}

# Check server health
health_check() {
    if ! is_running; then
        error "MCP Server is not running"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    log "MCP Server health check (PID: $pid)..."
    
    # Basic process check
    if ps -p $pid > /dev/null 2>&1; then
        success "Server process is running"
    else
        error "Server process not found"
        return 1
    fi
    
    # Check log for recent activity
    if [[ -f "$LOG_FILE" ]]; then
        local recent_logs=$(tail -n 10 "$LOG_FILE" | grep -c "$(date '+%Y-%m-%d')" || true)
        if [[ $recent_logs -gt 0 ]]; then
            success "Server is logging activity"
        else
            warning "No recent log activity"
        fi
    fi
    
    return 0
}

# Monitor and auto-restart if needed
monitor() {
    log "Starting MCP Server monitoring..."
    local retry_count=0
    
    while true; do
        if health_check; then
            retry_count=0
            sleep 30  # Check every 30 seconds
        else
            ((retry_count++))
            error "Health check failed (attempt $retry_count/$MAX_RETRIES)"
            
            if [[ $retry_count -ge $MAX_RETRIES ]]; then
                error "Max retries reached. Attempting restart..."
                restart_server
                retry_count=0
            fi
            
            sleep $RETRY_DELAY
        fi
    done
}

# Show server status
status() {
    echo "=== Gym Bot MCP Server Status ==="
    
    if is_running; then
        local pid=$(cat "$PID_FILE")
        success "Server is running (PID: $pid)"
        
        # Show process info
        echo "Process info:"
        ps -p $pid -o pid,ppid,cmd,etime,pcpu,pmem
        
        # Show recent logs
        if [[ -f "$LOG_FILE" ]]; then
            echo -e "\nRecent logs:"
            tail -n 5 "$LOG_FILE"
        fi
    else
        warning "Server is not running"
    fi
    
    echo -e "\nLog file: $LOG_FILE"
    echo "PID file: $PID_FILE"
}

# Show usage
usage() {
    echo "Usage: $0 {start|stop|restart|status|health|monitor}"
    echo ""
    echo "Commands:"
    echo "  start   - Start the MCP server"
    echo "  stop    - Stop the MCP server"
    echo "  restart - Restart the MCP server"
    echo "  status  - Show server status"
    echo "  health  - Perform health check"
    echo "  monitor - Start continuous monitoring"
}

# Main command handler
case "${1:-}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        status
        ;;
    health)
        health_check
        ;;
    monitor)
        monitor
        ;;
    *)
        usage
        exit 1
        ;;
esac
