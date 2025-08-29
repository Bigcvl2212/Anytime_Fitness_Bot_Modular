#!/usr/bin/env python3
"""Test the training clients API response to see what data is being returned"""

import requests
import json

def test_training_clients_api():
    """Test the training clients API endpoint"""
    try:
        url = "http://localhost:5000/api/training-clients/all"
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Length: {len(response.text)} bytes")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Source: {data.get('source')}")
            
            training_clients = data.get('training_clients', [])
            print(f"Number of training clients: {len(training_clients)}")
            
            if training_clients:
                print("\nFirst training client data:")
                print("=" * 50)
                first_client = training_clients[0]
                for key, value in first_client.items():
                    print(f"{key}: {value}")
                
                print("\nAll available keys:")
                print("=" * 50)
                for key in first_client.keys():
                    print(f"- {key}")
            else:
                print("No training clients returned")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_training_clients_api()
