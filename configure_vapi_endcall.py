#!/usr/bin/env python3
"""
Script to configure VAPI assistant with endCall tool and endCallPhrases.
This enables automatic call termination when SOMERA says goodbye.

Run with: python configure_vapi_endcall.py
"""

import os
import requests

VAPI_API_KEY = os.environ.get("VAPI_API_KEY")
ASSISTANT_ID = os.environ.get("NEXT_PUBLIC_VAPI_ASSISTANT_ID", "c09f6a3b-35d5-4e23-bd67-36299a4f44dd")

def configure_assistant():
    if not VAPI_API_KEY:
        print("ERROR: VAPI_API_KEY environment variable not set")
        print("Please set it with: export VAPI_API_KEY='your-api-key'")
        return False
    
    url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
    
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "endCallPhrases": [
            "talk to you soon",
            "take care of yourself", 
            "bye for now",
            "until next time",
            "wishing you well",
            "here whenever you're ready",
            "come back anytime"
        ]
    }
    
    print(f"Configuring VAPI assistant: {ASSISTANT_ID}")
    print(f"Adding endCallPhrases: {payload['endCallPhrases']}")
    
    try:
        response = requests.patch(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print("\nSUCCESS! Assistant updated with endCallPhrases.")
            result = response.json()
            print(f"\nAssistant name: {result.get('name', 'N/A')}")
            print(f"endCallPhrases: {result.get('endCallPhrases', [])}")
            return True
        else:
            print(f"\nERROR: Failed to update assistant")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\nERROR: Request failed: {e}")
        return False

def get_current_config():
    if not VAPI_API_KEY:
        return None
        
    url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
    headers = {"Authorization": f"Bearer {VAPI_API_KEY}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

if __name__ == "__main__":
    print("=" * 60)
    print("VAPI Assistant Configuration Tool")
    print("=" * 60)
    
    print("\nChecking current configuration...")
    current = get_current_config()
    if current:
        print(f"Current endCallPhrases: {current.get('endCallPhrases', 'Not configured')}")
        print(f"Current tools: {[t.get('type') for t in current.get('model', {}).get('tools', [])]}")
    
    print("\n" + "-" * 60)
    confirm = input("\nProceed with configuration? (y/n): ").strip().lower()
    if confirm == 'y':
        configure_assistant()
    else:
        print("Cancelled.")
