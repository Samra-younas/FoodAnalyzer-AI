import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Test Official Claude API connection
def test_claude_api():
    """
    Test if Claude API (Anthropic) is working with a simple text message
    """
    
    # Get API key from environment variable
    api_key = os.getenv("CLAUDE_API_KEY")  # You need to set this
    
    if not api_key:
        print("❌ ERROR: CLAUDE_API_KEY environment variable not set!")
        print("Set it using: export CLAUDE_API_KEY='sk-ant-api03-...'")
        return False
    
    # Official Anthropic API endpoint
    url = "https://api.anthropic.com/v1/messages"
    
    # Headers for official Anthropic API
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # Simple test payload
    payload = {
        "model": "claude-sonnet-4-20250514",  # Latest Sonnet model
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": "Hello! Please respond with 'Claude API is working!' if you receive this."
            }
        ]
    }
    
    try:
        print("🔄 Testing Claude API connection...")
        print(f"Endpoint: {url}")
        print(f"Model: {payload['model']}")
        print("-" * 50)
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        # Check response status
        if response.status_code == 200:
            result = response.json()
            message = result['content'][0]['text']
            print("✅ SUCCESS! Claude API is working!")
            print(f"Response: {message}")
            print("-" * 50)
            return True
        else:
            print(f"❌ ERROR: Status Code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("CLAUDE API TEST SCRIPT (Official Anthropic)")
    print("=" * 50)
    
    # Test the API
    success = test_claude_api()
    
    if success:
        print("\n✅ Your Claude API is ready to use!")
        print("Next step: We can integrate it into your Flask app.")
    else:
        print("\n❌ Please fix the API connection first.")
        print("Make sure you have:")
        print("1. Valid Claude API key from https://console.anthropic.com")
        print("2. Set environment variable: export CLAUDE_API_KEY='sk-ant-api03-...'")