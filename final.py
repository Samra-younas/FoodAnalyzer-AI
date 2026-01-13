import os
import base64
import requests
import json
from io import BytesIO
from flask import Flask, request, render_template
from PIL import Image
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# ---------------------- Flask setup ------------------------
app = Flask(__name__)


# ---------------------- OpenRouter API setup ------------------------
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_API_URL = "https://openrouter.ai/api/v1/chat/completions"


def compress_image(image_bytes, max_size_mb=5):
    """
    Compress image to be under max_size_mb
    Returns: compressed image bytes
    """
    img = Image.open(BytesIO(image_bytes))
    
    # Convert RGBA to RGB if necessary
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    
    # Start with quality 95
    quality = 95
    output = BytesIO()
    
    while True:
        output.seek(0)
        output.truncate()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        size_mb = output.tell() / (1024 * 1024)
        
        if size_mb <= max_size_mb or quality <= 20:
            break
        
        # Reduce quality by 10 each iteration
        quality -= 10
    
    return output.getvalue()


def analyze_food_with_qwen(image_bytes):
    """
    Send image to Qwen API via OpenRouter for nutrition analysis
    Returns: response text or error message
    """
    # Compress image if needed
    compressed_image = compress_image(image_bytes, max_size_mb=4.5)
    
    # Encode image to base64
    encoded_image = base64.b64encode(compressed_image).decode("utf-8")
    
    # OpenRouter API headers (OpenAI format)
    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # ===== UPDATED JSON PROMPT =====
    prompt = """You are a professional nutrition analyst AI. Analyze the food in the image and return your response in STRICT JSON format.

OUTPUT FORMAT (Must be valid JSON):
{
  "dish_name": "Name of the dish or food item",
  "description": "2-3 sentences describing the dish, visible ingredients, and presentation style",
  "nutrition": {
    "calories": "150-180 kcal",
    "carbohydrates": "20-25 g",
    "sugars": "3-5 g",
    "fiber": "2-4 g",
    "protein": "15-20 g",
    "fat": "5-8 g"
  },
  "portion_estimate": "Single serving, approximately 200g, total estimated 300-350 kcal"
}

CRITICAL RULES:
1. ALWAYS return valid JSON - no markdown, no code blocks, no extra text
2. If food is unclear or image quality is poor, return: {"error": "Please retake picture with better lighting and clear view of food"}
3. Use ranges for all nutritional values (e.g., "150-180" not just "150")
4. Base ALL estimates on VISIBLE food only - do not assume hidden ingredients
5. Be specific about ingredients you can identify in the image
6. Include portion size and total calorie estimate in "portion_estimate"
7. For mixed dishes, provide combined nutritional values
8. If multiple items visible, analyze as one complete meal

Remember: Output MUST be parseable JSON with no additional formatting or explanation."""
    
    # OpenRouter API payload (OpenAI format)
    payload = {
        "model": "qwen/qwen3-vl-235b-a22b-instruct",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.3
    }
    
    try:
        # Send request to OpenRouter
        response = requests.post(QWEN_API_URL, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            # Extract text from OpenAI-style response structure
            return result['choices'][0]['message']['content']
        else:
            return f"API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Error: {str(e)}"


def parse_nutrition_response(result_text):
    """
    Parse the JSON nutrition analysis response
    Returns: dict with dish_name, description, nutrition_info, portion_estimate
    """
    try:
        # Try to parse as JSON first
        data = json.loads(result_text)
        
        # Check for error response
        if "error" in data:
            return {
                'dish_name': 'Error',
                'description': data['error'],
                'nutrition_info': [],
                'portion_estimate': None
            }
        
        # Extract nutrition info as list of strings for display
        nutrition_info = []
        if "nutrition" in data:
            nutrition = data["nutrition"]
            nutrition_info = [
                f"Calories: {nutrition.get('calories', 'N/A')}",
                f"Carbohydrates: {nutrition.get('carbohydrates', 'N/A')}",
                f"Sugars: {nutrition.get('sugars', 'N/A')}",
                f"Fiber: {nutrition.get('fiber', 'N/A')}",
                f"Protein: {nutrition.get('protein', 'N/A')}",
                f"Fat: {nutrition.get('fat', 'N/A')}"
            ]
        
        return {
            'dish_name': data.get('dish_name', 'Unknown Dish'),
            'description': data.get('description', 'No description available'),
            'nutrition_info': nutrition_info,
            'portion_estimate': data.get('portion_estimate', None)
        }
        
    except json.JSONDecodeError:
        # Fallback: If response is not JSON, handle as error
        if "API Error" in result_text or "Error:" in result_text:
            return {
                'dish_name': 'Error',
                'description': result_text,
                'nutrition_info': [],
                'portion_estimate': None
            }
        
        # Try to extract any useful info from non-JSON response
        return {
            'dish_name': 'Parsing Error',
            'description': 'AI returned non-JSON response. Please try again.',
            'nutrition_info': [],
            'portion_estimate': None
        }


# ---------------------- Routes ------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    nutrition_info = []
    description = None
    portion_estimate = None
    img_src = None
    dish_name = None

    if request.method == "POST":
        if "file" not in request.files:
            return "No file uploaded", 400

        file = request.files["file"]
        if file.filename == "":
            return "No file selected", 400

        # Read image in memory
        image_bytes = file.read()
        image = Image.open(BytesIO(image_bytes))

        # Save uploaded image
        upload_folder = os.path.join("static", "uploads")
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, file.filename)
        file.seek(0)
        file.save(file_path)

        # Convert image to base64 for display
        encoded_img = base64.b64encode(image_bytes).decode("utf-8")
        img_src = f"data:image/jpeg;base64,{encoded_img}"

        # Analyze with Qwen
        result_text = analyze_food_with_qwen(image_bytes)
        
    
        
        # Parse response using JSON parser
        parsed_result = parse_nutrition_response(result_text)
        
        dish_name = parsed_result['dish_name']
        description = parsed_result['description']
        nutrition_info = parsed_result['nutrition_info']
        portion_estimate = parsed_result['portion_estimate']

    return render_template(
        "claude.html",
        img_src=img_src,
        description=description,
        nutrition_info=nutrition_info,
        portion_estimate=portion_estimate,
        dish_name=dish_name
    )


# ---------------------- Run ------------------------
if __name__ == "__main__":
    app.run(debug=True)