import requests
import json

# Grok API configuration
GROK_API_KEY = "<GROK_API_KEY>"
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

def test_grok_api():
    """Simple test to verify Grok API is working"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROK_API_KEY}"
    }
    
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are a test assistant."
            },
            {
                "role": "user",
                "content": "Testing. Just say hi and hello world and nothing else."
            }
        ],
        "model": "grok-beta",
        "stream": False,
        "temperature": 0
    }
    
    try:
        print("Testing Grok API...")
        print(f"Sending request to: {GROK_API_URL}")
        
        response = requests.post(GROK_API_URL, json=payload, headers=headers, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nSUCCESS! Grok API is working!")
            print("\nFull Response:")
            print(json.dumps(result, indent=2))
            
            # Extract the message
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0]['message']['content']
                print(f"\nGrok's Response: {message}")
            
            return True
        else:
            print(f"\nERROR: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\nException occurred: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("GROK API TEST")
    print("=" * 50)
    test_grok_api()
    print("\n" + "=" * 50)