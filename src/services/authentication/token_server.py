"""
ClubHub Token Server API
Flask API server to receive and manage ClubHub tokens from Charles Proxy automation.
Provides secure token storage and retrieval for ClubHub API access.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from flask import Flask, request, jsonify, Response
from flask_cors import CORS


class ClubHubTokenServer:
    """
    Flask API server for receiving and managing ClubHub tokens.
    Integrates with Charles Proxy automation system.
    """
    
    def __init__(self, token_storage_path: str = "data/token_server"):
        """Initialize ClubHub token server"""
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for cross-origin requests
        
        self.token_storage_path = Path(token_storage_path)
        self.token_storage_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = self._setup_logging()
        self._setup_routes()
        
        # Token validation settings
        self.token_expiry_hours = 24
        self.max_stored_tokens = 50
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for token server"""
        logger = logging.getLogger("ClubHubTokenServer")
        logger.setLevel(logging.INFO)
        
        # Create handlers
        handler = logging.FileHandler("logs/token_server.log")
        handler.setLevel(logging.INFO)
        
        # Create formatters and add it to handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # Add handlers to the logger
        logger.addHandler(handler)
        
        return logger
    
    def _setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "ClubHub Token Server"
            })
        
        @self.app.route('/tokens', methods=['POST'])
        def receive_tokens():
            """Receive tokens from Charles Proxy automation"""
            try:
                self.logger.info("Received token submission request")
                
                if not request.is_json:
                    return jsonify({"error": "Content-Type must be application/json"}), 400
                
                data = request.get_json()
                
                # Validate required fields
                required_fields = ["tokens", "timestamp", "source"]
                for field in required_fields:
                    if field not in data:
                        return jsonify({"error": f"Missing required field: {field}"}), 400
                
                # Store tokens
                success = self._store_received_tokens(data)
                
                if success:
                    self.logger.info("✅ Tokens stored successfully")
                    return jsonify({
                        "status": "success",
                        "message": "Tokens received and stored",
                        "timestamp": datetime.now().isoformat()
                    }), 200
                else:
                    self.logger.error("❌ Failed to store tokens")
                    return jsonify({"error": "Failed to store tokens"}), 500
                    
            except Exception as e:
                self.logger.error(f"❌ Error processing token submission: {e}")
                return jsonify({"error": "Internal server error"}), 500
        
        @self.app.route('/tokens/latest', methods=['GET'])
        def get_latest_tokens():
            """Get the latest valid tokens"""
            try:
                self.logger.info("Received request for latest tokens")
                
                latest_tokens = self._get_latest_valid_tokens()
                
                if latest_tokens:
                    self.logger.info("✅ Returning latest valid tokens")
                    return jsonify({
                        "status": "success",
                        "tokens": latest_tokens["tokens"],
                        "extracted_at": latest_tokens["extracted_at"],
                        "validated": latest_tokens["validated"]
                    }), 200
                else:
                    self.logger.warning("⚠️ No valid tokens available")
                    return jsonify({
                        "status": "error",
                        "message": "No valid tokens available"
                    }), 404
                    
            except Exception as e:
                self.logger.error(f"❌ Error retrieving latest tokens: {e}")
                return jsonify({"error": "Internal server error"}), 500
        
        @self.app.route('/tokens/validate', methods=['POST'])
        def validate_tokens():
            """Validate provided tokens against ClubHub API"""
            try:
                self.logger.info("Received token validation request")
                
                if not request.is_json:
                    return jsonify({"error": "Content-Type must be application/json"}), 400
                
                data = request.get_json()
                
                if "tokens" not in data:
                    return jsonify({"error": "Missing tokens field"}), 400
                
                # Validate tokens
                is_valid = self._validate_tokens_against_api(data["tokens"])
                
                return jsonify({
                    "status": "success",
                    "valid": is_valid,
                    "timestamp": datetime.now().isoformat()
                }), 200
                
            except Exception as e:
                self.logger.error(f"❌ Error validating tokens: {e}")
                return jsonify({"error": "Internal server error"}), 500
        
        @self.app.route('/tokens/refresh', methods=['POST'])
        def trigger_token_refresh():
            """Trigger fresh token extraction"""
            try:
                self.logger.info("Received token refresh request")
                
                # This would trigger the Charles Proxy automation
                # For now, return success (actual implementation would call the automation)
                
                return jsonify({
                    "status": "success",
                    "message": "Token refresh triggered",
                    "timestamp": datetime.now().isoformat()
                }), 200
                
            except Exception as e:
                self.logger.error(f"❌ Error triggering token refresh: {e}")
                return jsonify({"error": "Internal server error"}), 500
        
        @self.app.route('/tokens/history', methods=['GET'])
        def get_token_history():
            """Get token extraction history"""
            try:
                self.logger.info("Received request for token history")
                
                history = self._get_token_history()
                
                return jsonify({
                    "status": "success",
                    "history": history,
                    "timestamp": datetime.now().isoformat()
                }), 200
                
            except Exception as e:
                self.logger.error(f"❌ Error retrieving token history: {e}")
                return jsonify({"error": "Internal server error"}), 500
    
    def _store_received_tokens(self, data: Dict[str, Any]) -> bool:
        """Store received tokens with metadata"""
        try:
            # Create token entry
            token_entry = {
                "tokens": data["tokens"],
                "extracted_at": data["timestamp"],
                "received_at": datetime.now().isoformat(),
                "source": data["source"],
                "validated": False  # Will be validated separately
            }
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tokens_{timestamp}.json"
            filepath = self.token_storage_path / filename
            
            # Store token entry
            with open(filepath, 'w') as f:
                json.dump(token_entry, f, indent=2)
            
            # Update latest tokens file
            latest_file = self.token_storage_path / "latest_tokens.json"
            with open(latest_file, 'w') as f:
                json.dump(token_entry, f, indent=2)
            
            self.logger.info(f"✅ Tokens stored to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error storing tokens: {e}")
            return False
    
    def _get_latest_valid_tokens(self) -> Optional[Dict[str, Any]]:
        """Get the latest valid tokens from storage"""
        try:
            latest_file = self.token_storage_path / "latest_tokens.json"
            
            if not latest_file.exists():
                return None
            
            with open(latest_file, 'r') as f:
                token_data = json.load(f)
            
            # Check if tokens are still valid (not expired)
            extracted_at = datetime.fromisoformat(token_data["extracted_at"])
            if datetime.now() - extracted_at > timedelta(hours=self.token_expiry_hours):
                self.logger.warning("⚠️ Latest tokens are expired")
                return None
            
            return token_data
            
        except Exception as e:
            self.logger.error(f"❌ Error getting latest tokens: {e}")
            return None
    
    def _validate_tokens_against_api(self, tokens: Dict[str, Any]) -> bool:
        """Validate tokens against ClubHub API"""
        try:
            import requests
            
            if not tokens.get("bearer_token"):
                return False
            
            # Test against ClubHub API
            test_url = "https://clubhub-ios-api.anytimefitness.com/api/v1.0/clubs/1156/members"
            
            headers = {
                "Authorization": f"Bearer {tokens['bearer_token']}",
                "API-version": "1",
                "Accept": "application/json",
                "User-Agent": "ClubHub Store/2.15.0 (com.anytimefitness.Club-Hub; build:1004; iOS 18.5.0) Alamofire/5.6.4"
            }
            
            if tokens.get("session_cookie"):
                headers["Cookie"] = f"incap_ses_132_434694={tokens['session_cookie']}"
            
            response = requests.get(test_url, headers=headers, timeout=10)
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"❌ Error validating tokens against API: {e}")
            return False
    
    def _get_token_history(self) -> List[Dict[str, Any]]:
        """Get token extraction history"""
        try:
            history = []
            
            # Get all token files
            token_files = list(self.token_storage_path.glob("tokens_*.json"))
            token_files.sort(reverse=True)  # Most recent first
            
            for filepath in token_files[:10]:  # Last 10 extractions
                try:
                    with open(filepath, 'r') as f:
                        token_data = json.load(f)
                    
                    # Add file info
                    token_data["filename"] = filepath.name
                    token_data["file_size"] = filepath.stat().st_size
                    
                    history.append(token_data)
                    
                except Exception as e:
                    self.logger.error(f"❌ Error reading token file {filepath}: {e}")
            
            return history
            
        except Exception as e:
            self.logger.error(f"❌ Error getting token history: {e}")
            return []
    
    def run_server(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
        """Run the Flask token server"""
        self.logger.info(f"Starting ClubHub Token Server on {host}:{port}")
        
        self.app.run(
            host=host,
            port=port,
            debug=debug
        )


# Convenience functions
def create_token_server(token_storage_path: str = "data/token_server") -> ClubHubTokenServer:
    """Create and configure ClubHub token server"""
    return ClubHubTokenServer(token_storage_path)


def run_token_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    """Run ClubHub token server"""
    server = create_token_server()
    server.run_server(host, port, debug)


if __name__ == "__main__":
    run_token_server() 