"""
Automated ClubHub Token Workflow
Complete automation system for ClubHub token extraction, validation, and management.
Integrates Charles Proxy capture with Flask server and scheduled execution.
"""

import time
import schedule
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from .clubhub_token_capture import ClubHubTokenCapture
from .token_server import ClubHubTokenServer


class AutomatedTokenWorkflow:
    """
    Complete automation workflow for ClubHub token management.
    Integrates Charles Proxy capture, Flask server, and scheduled execution.
    """
    
    def __init__(self, charles_config: Dict[str, Any] = None, server_config: Dict[str, Any] = None):
        """Initialize automated token workflow"""
        self.charles_config = charles_config
        self.server_config = server_config or self._get_default_server_config()
        
        # Initialize components
        self.token_capture = ClubHubTokenCapture(charles_config)
        self.token_server = ClubHubTokenServer(self.server_config.get("token_storage_path"))
        
        self.logger = self._setup_logging()
        
        # Workflow settings
        self.extraction_interval_hours = 23  # Extract tokens every 23 hours
        self.server_port = self.server_config.get("port", 5000)
        self.server_host = self.server_config.get("host", "0.0.0.0")
        
        # Threading for server
        self.server_thread = None
        self.server_running = False
    
    def _get_default_server_config(self) -> Dict[str, Any]:
        """Get default server configuration"""
        return {
            "token_storage_path": "data/token_server",
            "host": "0.0.0.0",
            "port": 5000,
            "debug": False
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for automated workflow"""
        logger = logging.getLogger("AutomatedTokenWorkflow")
        logger.setLevel(logging.INFO)
        
        # Create handlers
        handler = logging.FileHandler("logs/automated_token_workflow.log")
        handler.setLevel(logging.INFO)
        
        # Create formatters and add it to handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # Add handlers to the logger
        logger.addHandler(handler)
        
        return logger
    
    def start_token_server(self) -> bool:
        """Start the Flask token server in a separate thread"""
        try:
            self.logger.info("Starting token server...")
            
            # Start server in separate thread
            self.server_thread = threading.Thread(
                target=self.token_server.run_server,
                kwargs={
                    "host": self.server_host,
                    "port": self.server_port,
                    "debug": False
                },
                daemon=True
            )
            
            self.server_thread.start()
            self.server_running = True
            
            # Wait for server to start
            time.sleep(3)
            
            self.logger.info(f"✅ Token server started on {self.server_host}:{self.server_port}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error starting token server: {e}")
            return False
    
    def stop_token_server(self) -> bool:
        """Stop the Flask token server"""
        try:
            self.logger.info("Stopping token server...")
            
            # Flask doesn't have a built-in stop method, so we'll just mark it as stopped
            self.server_running = False
            
            self.logger.info("✅ Token server stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping token server: {e}")
            return False
    
    def run_token_extraction_workflow(self) -> Dict[str, Any]:
        """
        Run complete token extraction workflow:
        1. Extract tokens via Charles Proxy
        2. Validate tokens against ClubHub API
        3. Store tokens securely
        4. Send tokens to Flask server
        
        Returns:
            Dict containing workflow results
        """
        try:
            self.logger.info("🚀 Starting token extraction workflow...")
            
            workflow_results = {
                "timestamp": datetime.now().isoformat(),
                "steps": {},
                "success": False,
                "error": None
            }
            
            # Step 1: Extract tokens via Charles Proxy
            self.logger.info("📊 Step 1: Extracting tokens via Charles Proxy...")
            extracted_tokens = self.token_capture.extract_fresh_tokens()
            
            if not extracted_tokens:
                workflow_results["error"] = "Failed to extract tokens"
                self.logger.error("❌ Token extraction failed")
                return workflow_results
            
            workflow_results["steps"]["extraction"] = {
                "success": True,
                "tokens_found": len(extracted_tokens),
                "timestamp": datetime.now().isoformat()
            }
            
            # Step 2: Validate tokens against ClubHub API
            self.logger.info("🔍 Step 2: Validating tokens against ClubHub API...")
            tokens_valid = self.token_capture.validate_tokens(extracted_tokens)
            
            workflow_results["steps"]["validation"] = {
                "success": tokens_valid,
                "timestamp": datetime.now().isoformat()
            }
            
            if not tokens_valid:
                workflow_results["error"] = "Extracted tokens are invalid"
                self.logger.error("❌ Token validation failed")
                return workflow_results
            
            # Step 3: Store tokens securely
            self.logger.info("💾 Step 3: Storing tokens securely...")
            storage_success = self.token_capture.store_tokens_securely(extracted_tokens)
            
            workflow_results["steps"]["storage"] = {
                "success": storage_success,
                "timestamp": datetime.now().isoformat()
            }
            
            if not storage_success:
                workflow_results["error"] = "Failed to store tokens"
                self.logger.error("❌ Token storage failed")
                return workflow_results
            
            # Step 4: Send tokens to Flask server
            self.logger.info("📡 Step 4: Sending tokens to Flask server...")
            server_url = f"http://{self.server_host}:{self.server_port}/tokens"
            
            server_success = self.token_capture.send_tokens_to_server(
                extracted_tokens, server_url
            )
            
            workflow_results["steps"]["server_submission"] = {
                "success": server_success,
                "server_url": server_url,
                "timestamp": datetime.now().isoformat()
            }
            
            if not server_success:
                self.logger.warning("⚠️ Failed to send tokens to server, but extraction was successful")
            
            # Workflow completed successfully
            workflow_results["success"] = True
            self.logger.info("✅ Token extraction workflow completed successfully")
            
            return workflow_results
            
        except Exception as e:
            self.logger.error(f"❌ Error in token extraction workflow: {e}")
            workflow_results["error"] = str(e)
            return workflow_results
    
    def run_scheduled_workflow(self) -> bool:
        """
        Run the complete scheduled workflow including server startup.
        
        Returns:
            bool: True if workflow completed successfully
        """
        try:
            self.logger.info("🔄 Running scheduled token workflow...")
            
            # Start token server if not running
            if not self.server_running:
                if not self.start_token_server():
                    self.logger.error("❌ Failed to start token server")
                    return False
            
            # Run token extraction workflow
            workflow_results = self.run_token_extraction_workflow()
            
            if workflow_results["success"]:
                self.logger.info("✅ Scheduled workflow completed successfully")
                return True
            else:
                self.logger.error(f"❌ Scheduled workflow failed: {workflow_results.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error in scheduled workflow: {e}")
            return False
    
    def setup_scheduled_extraction(self) -> bool:
        """
        Setup scheduled token extraction.
        
        Returns:
            bool: True if scheduling setup successfully
        """
        try:
            self.logger.info("⏰ Setting up scheduled token extraction...")
            
            # Schedule token extraction every 23 hours
            schedule.every(self.extraction_interval_hours).hours.do(self.run_scheduled_workflow)
            
            # Also schedule extraction at specific times (e.g., 6 AM daily)
            schedule.every().day.at("06:00").do(self.run_scheduled_workflow)
            
            self.logger.info(f"✅ Scheduled token extraction every {self.extraction_interval_hours} hours")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up scheduled extraction: {e}")
            return False
    
    def run_scheduler(self) -> None:
        """Run the scheduler loop"""
        try:
            self.logger.info("🔄 Starting scheduler loop...")
            
            # Start token server
            if not self.start_token_server():
                self.logger.error("❌ Failed to start token server")
                return
            
            # Setup scheduled extraction
            if not self.setup_scheduled_extraction():
                self.logger.error("❌ Failed to setup scheduled extraction")
                return
            
            # Run initial extraction
            self.logger.info("🚀 Running initial token extraction...")
            self.run_scheduled_workflow()
            
            # Start scheduler loop
            self.logger.info("⏰ Starting scheduler loop...")
            while self.server_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Scheduler interrupted by user")
        except Exception as e:
            self.logger.error(f"❌ Error in scheduler loop: {e}")
        finally:
            self.stop_token_server()
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        try:
            # Check if server is running
            server_status = "running" if self.server_running else "stopped"
            
            # Get latest tokens
            latest_tokens = self.token_capture.get_latest_valid_tokens()
            
            # Get next scheduled run
            next_run = schedule.next_run()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "server_status": server_status,
                "server_url": f"http://{self.server_host}:{self.server_port}",
                "latest_tokens_available": latest_tokens is not None,
                "next_scheduled_run": next_run.isoformat() if next_run else None,
                "extraction_interval_hours": self.extraction_interval_hours
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting workflow status: {e}")
            return {"error": str(e)}


# Convenience functions
def create_automated_workflow(charles_config: Dict[str, Any] = None, 
                             server_config: Dict[str, Any] = None) -> AutomatedTokenWorkflow:
    """Create automated token workflow"""
    return AutomatedTokenWorkflow(charles_config, server_config)


def run_automated_workflow(charles_config: Dict[str, Any] = None, 
                          server_config: Dict[str, Any] = None) -> None:
    """Run automated token workflow with scheduler"""
    workflow = create_automated_workflow(charles_config, server_config)
    workflow.run_scheduler()


def run_single_extraction(charles_config: Dict[str, Any] = None, 
                         server_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Run single token extraction workflow"""
    workflow = create_automated_workflow(charles_config, server_config)
    return workflow.run_token_extraction_workflow()


if __name__ == "__main__":
    # Example usage
    print("🚀 Starting ClubHub Token Automation System...")
    
    # Custom configuration (optional)
    charles_config = {
        "charles_path": "/Applications/Charles.app/Contents/MacOS/Charles",
        "ipad_ip": "192.168.1.100",  # Update with your iPad IP
        "clubhub_domain": "clubhub-ios-api.anytimefitness.com"
    }
    
    server_config = {
        "host": "0.0.0.0",
        "port": 5000,
        "token_storage_path": "data/token_server"
    }
    
    # Run automated workflow
    run_automated_workflow(charles_config, server_config) 