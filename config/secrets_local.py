"""Local Secrets Management for Testing"""

def get_secret(key):
    secrets = {
        # ClubOS Credentials
        "clubos-username": "j.mayo",
        "clubos-password": "L*KYqnec5z7nEL$",
        
        # Square Sandbox Credentials  
        "square-sandbox-access-token": "EAAAl2BQfXhiYAaiKWZ_eFEvTf_XMauKjH3vITw1wBn0w9TTiZ20EwatO65I6zVp",
        "square-sandbox-location-id": "sq0csp-vQmH9jeq-VIN-GDIaVNVpZYJ2dcnpAbKOrP0LnkEcgQ",
        
        # Square Production Credentials
        "square-production-access-token": "EAAAl3bTM7XhOaWCr6axYMHHM4La1l4cH7q01aXDcox3iSCe8xcfOBeB58622TDQ",
        "square-production-location-id": "LCR9E5HA00KPA",
        
        # Add other secrets as needed
    }
    return secrets.get(key)
