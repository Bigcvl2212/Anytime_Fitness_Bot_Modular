"""Secrets Management - Local Development and Production"""
import os

def get_secret(key):
    """Get secret from environment variables first, then fall back to local secrets"""
    
    # Environment variable mappings
    env_mappings = {
        "square-production-access-token": "SQUARE_ACCESS_TOKEN",
        "square-production-location-id": "SQUARE_LOCATION_ID", 
        "square-production-application-secret": "SQUARE_APPLICATION_SECRET",
        "clubos-username": "CLUBOS_USERNAME",
        "clubos-password": "CLUBOS_PASSWORD",
        "clubhub-email": "CLUBHUB_EMAIL",
        "clubhub-password": "CLUBHUB_PASSWORD",
        "square-sandbox-access-token": "SQUARE_SANDBOX_ACCESS_TOKEN",
        "square-sandbox-location-id": "SQUARE_SANDBOX_LOCATION_ID"
    }
    
    # Try environment variable first (for cloud deployment)
    env_key = env_mappings.get(key)
    if env_key and os.getenv(env_key):
        return os.getenv(env_key)
    
    # Fall back to local secrets (for development)
    local_secrets = {
        # ClubOS Credentials
        "clubos-username": "j.mayo",
        "clubos-password": "Ls$gpZ98L!hht.G",

        # ClubHub Credentials
        "clubhub-email": "mayo.jeremy2212@gmail.com",
        "clubhub-password": "fygxy9-sybses-suvtYc",
        
        # Square Sandbox Credentials  
        "square-sandbox-access-token": "EAAAl2BQfXhiYAaiKWZ_eFEvTf_XMauKjH3vITw1wBn0w9TTiZ20EwatO65I6zVp",
        "square-sandbox-location-id": "sq0csp-vQmH9jeq-VIN-GDIaVNVpZYJ2dcnpAbKOrP0LnkEcgQ",
        
        # Square Production Credentials
        "square-production-access-token": "EAAAl3E3RnKndmM_XvqfVlLoVj_VbVtBpimwy4xeljcwkkAF2tOStaxYq7KhPXCA",
        "square-production-location-id": "Q0TK7D7CFHWE3",  # Updated to match API response
        "square-production-application-secret": "sq0csp-uAnchFNGLSyfrvBP2906jzajvmnJSUlYmeMh465sn-4",
        
        # Add other secrets as needed
    }
    return local_secrets.get(key)
