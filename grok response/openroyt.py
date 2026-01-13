
import requests
import json

# OpenRouter API configuration
OPENROUTER_API_KEY = "<OPENROUTER_API_KEY>"
OPENROUTER_URL = "https://openrouter.ai/v1/chat/completions"  # Correct URL

def test_openrouter_grok_vision():
    """Test OpenRouter with Grok - Vision (Image)"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Nutrition Analyzer"
    }
    
    payload = {
        "model": "x-ai/grok-4-fast",  # Change model to 'x-ai/grok-4-fast'
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What is in this image?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        print("\n" + "=" * 50)
        print("Testing OpenRouter + Grok Vision API (Image)")
        print("=" * 50)
        
        response = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=60)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Raw Response: {response.text}")  # Print the raw response
        
        if response.status_code == 200:
            try:
                result = response.json()  # Try parsing as JSON
                print("\nSUCCESS! Grok Vision is working!")
                
                # Extract the message
                if 'choices' in result and len(result['choices']) > 0:
                    message = result['choices'][0]['message']['content']
                    print(f"\nGrok's Vision Response:\n{message}")
                
                return True
            except json.JSONDecodeError:
                print("\nError: Could not decode response as JSON.")
                return False
        else:
            print(f"\nERROR: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\nException occurred: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n OPENROUTER + GROK API TEST\n")
    vision_result = test_openrouter_grok_vision()
    print("\n" + "=" * 50)
    print("Testing Complete!")
    print("=" * 50)
