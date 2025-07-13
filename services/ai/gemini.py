"""
Gemini AI Service - PROVEN WORKING CODE FROM ORIGINAL SCRIPT
Contains the EXACT working AI initialization and client functions from Anytime_Bot.py
"""

import google.generativeai as genai
from google.cloud import firestore

from ...config.secrets import get_secret


# Global variables to match original script
gemini_model = None
db = None


def initialize_services():
    """
    Initialize Google services and AI model.
    
    PROVEN FUNCTION FROM ORIGINAL ANYTIME_BOT.PY
    """
    global gemini_model, db
    try:
        # Initialize Gemini AI
        gemini_api_key = get_secret("gemini-api-key")
        if not gemini_api_key:
            print("ERROR: Missing Gemini API key")
            return False
            
        genai.configure(api_key=gemini_api_key)
        gemini_model = genai.GenerativeModel('gemini-pro')
        print("✅ Gemini AI initialized")
        
        # Initialize Firestore
        db = firestore.Client()
        print("✅ Firestore initialized")
        
        print("SUCCESS: Services initialized")
        return True
    except Exception as e:
        print(f"ERROR: Failed to initialize services: {e}")
        gemini_model = None
        db = None
        return False


def get_gemini_client():
    """
    Get Gemini AI client.
    
    PROVEN FUNCTION FROM ORIGINAL ANYTIME_BOT.PY
    """
    global gemini_model
    if gemini_model is None:
        if not initialize_services():
            return None
    return gemini_model


def get_firestore_client():
    """
    Get Firestore client.
    
    PROVEN FUNCTION FROM ORIGINAL ANYTIME_BOT.PY
    """
    global db
    if db is None:
        if not initialize_services():
            return None
    return db