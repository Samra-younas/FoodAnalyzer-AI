# import os
# import base64
# import requests
# from io import BytesIO
# from flask import Flask, request, render_template
# from PIL import Image
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # ---------------------- Flask setup ------------------------
# app = Flask(__name__)

# # ---------------------- Claude API setup ------------------------
# CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
# CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

# def analyze_food_with_claude(image_bytes):
#     """
#     Send image to Claude API for nutrition analysis
#     Returns: response text or error message
#     """
#     # Encode image to base64
#     encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    
#     # Claude API headers
#     headers = {
#         "x-api-key": CLAUDE_API_KEY,
#         "anthropic-version": "2023-06-01",
#         "content-type": "application/json"
#     }
    
#     # Nutrition analysis prompt
#     prompt = """
# You are a skilled nutrition analyst. Please follow these exact instructions for analyzing the food or dish in the image:

# 1. **Identify the dish**: Based on the visible ingredients, provide the **name** or **best guess** for the dish. Do not say "unsure," just provide the best guess.
# 2. **Provide a short factual description** (2-3 sentences), including the **portion** or **presentation**. If identification is unclear, state: "Please Retake Picture" and stop further analysis.
# ----  
# Based on the image:        
#    - **Calories**: Estimate based on the visible portion size and food type.
#    - **Fat**: Include fat content based on the visual presentation.
#    - **Carbohydrates, Sugars, Fiber, Protein**: Estimate based on the visible ingredients.
#    - For **solid foods** (e.g., fruits, meat, vegetables), use typical values based on visual cues.
#    - For **liquids** (e.g., juices, milk, soups, smoothies), treat them as liquids.
#    - For **mixed/semi-liquid foods** (e.g., yogurt, porridge), treat them as liquids.

# # Format the macronutrient breakdown as:
# Calories: xx-xx kcal  
# Carbohydrates: xx-xx g  
# Sugars: xx-xx g  
# Fiber: xx-xx g  
# Protein: xx-xx g  
# Fat: xx-xx g  
# ---  
# Based on the visible amount: Provide **one single line** estimating the portion size and calories based only on the visible amount, explaining briefly. For example: "Looks like ~200–250 kcal, about one medium glass (~250 ml)."

# ### **Strict Rules:**
# - **NO markdown or no extra words add.**
# - **Be concise, factual, and clear**.
# - **Do not make any health claims or guess the brand**.
# - **Do not invent ingredients or toppings** that cannot be seen in the image.
# - If you're **uncertain** about the food type, say: "May not be right", but must answer and continue with your best estimate.
# - Base all estimates solely on the **visible food** in the image, using typical values.
# """
    
#     # Claude API payload
#     payload = {
#         "model": "claude-sonnet-4-20250514",
#         "max_tokens": 1024,
#         "messages": [
#             {
#                 "role": "user",
#                 "content": [
#                     {
#                         "type": "image",
#                         "source": {
#                             "type": "base64",
#                             "media_type": "image/jpeg",
#                             "data": encoded_image
#                         }
#                     },
#                     {
#                         "type": "text",
#                         "text": prompt
#                     }
#                 ]
#             }
#         ]
#     }
    
#     try:
#         # Send request to Claude
#         response = requests.post(CLAUDE_API_URL, json=payload, headers=headers, timeout=60)
        
#         if response.status_code == 200:
#             result = response.json()
#             # Extract text from Claude's response structure
#             return result['content'][0]['text']
#         else:
#             return f"API Error: {response.status_code} - {response.text}"
            
#     except Exception as e:
#         return f"Error: {str(e)}"


# # ---------------------- Routes ------------------------
# @app.route("/", methods=["GET", "POST"])
# def index():
#     nutrition_info = []
#     description = None
#     portion_estimate = None
#     img_src = None
#     dish_name = None

#     if request.method == "POST":
#         if "file" not in request.files:
#             return "No file uploaded", 400

#         file = request.files["file"]
#         if file.filename == "":
#             return "No file selected", 400

#         # Read image in memory
#         image_bytes = file.read()
#         image = Image.open(BytesIO(image_bytes))

#         # Save uploaded image
#         upload_folder = os.path.join("static", "uploads")
#         os.makedirs(upload_folder, exist_ok=True)
#         file_path = os.path.join(upload_folder, file.filename)
#         file.seek(0)
#         file.save(file_path)
#         img_src = f"/{file_path.replace(os.sep, '/')}"

#         # Convert image to base64 for display
#         encoded_img = base64.b64encode(image_bytes).decode("utf-8")
#         img_src = f"data:image/jpeg;base64,{encoded_img}"

#         # Analyze with Claude
#         result_text = analyze_food_with_claude(image_bytes)

#         # Parse response
#         if "Please Retake Picture" in result_text or "Uncertain" in result_text:
#             description = "Please Retake Picture"
#             nutrition_info = []
#             portion_estimate = None
#             dish_name = "Unknown Dish"
#         else:
#             lines = [line.strip("*•- ").strip() for line in result_text.split("\n") if line.strip()]
#             if lines:
#                 dish_name = lines[0]
#                 description = lines[1] if len(lines) > 1 else "No description available"
#                 if len(lines) > 2:
#                     portion_estimate = lines[-1]
#                     nutrition_info = lines[2:-1]
#                 else:
#                     nutrition_info = []
#                     portion_estimate = None

#     return render_template(
#         "claude.html",
#         img_src=img_src,
#         description=description,
#         nutrition_info=nutrition_info,
#         portion_estimate=portion_estimate,
#         dish_name=dish_name
#     )

# # ---------------------- Run ------------------------
# if __name__ == "__main__":
#     app.run(debug=True)



import os
import base64
import requests
from io import BytesIO
from flask import Flask, request, render_template
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---------------------- Flask setup ------------------------
app = Flask(__name__)

# ---------------------- Claude API setup ------------------------
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

def compress_image(image_bytes, max_size_mb=5):
    """
    Compress image to be under max_size_mb (default 5 MB for Claude API)
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


def analyze_food_with_claude(image_bytes):
    """
    Send image to Claude API for nutrition analysis
    Returns: response text or error message
    """
    # Compress image if needed (Claude limit: 5 MB)
    compressed_image = compress_image(image_bytes, max_size_mb=4.5)  # Use 4.5 MB to be safe
    
    # Encode image to base64
    encoded_image = base64.b64encode(compressed_image).decode("utf-8")
    
    # Claude API headers
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # Nutrition analysis prompt
    prompt = """
You are a skilled nutrition analyst. Please follow these exact instructions for analyzing the food or dish in the image:

1. **Identify the dish**: Based on the visible ingredients, provide the **name** or **best guess** for the dish. Do not say "unsure," just provide the best guess.
2. **Provide a short factual description** (2-3 sentences), including the **portion** or **presentation**. If identification is unclear, state: "Please Retake Picture" and stop further analysis.
----  
Based on the image:        
   - **Calories**: Estimate based on the visible portion size and food type.
   - **Fat**: Include fat content based on the visual presentation.
   - **Carbohydrates, Sugars, Fiber, Protein**: Estimate based on the visible ingredients.
   - For **solid foods** (e.g., fruits, meat, vegetables), use typical values based on visual cues.
   - For **liquids** (e.g., juices, milk, soups, smoothies), treat them as liquids.
   - For **mixed/semi-liquid foods** (e.g., yogurt, porridge), treat them as liquids.

# Format the macronutrient breakdown as:
Calories: xx-xx kcal  
Carbohydrates: xx-xx g  
Sugars: xx-xx g  
Fiber: xx-xx g  
Protein: xx-xx g  
Fat: xx-xx g  
---  
Based on the visible amount: Provide **one single line** estimating the portion size and calories based only on the visible amount, explaining briefly. For example: "Looks like ~200–250 kcal, about one medium glass (~250 ml)."

### **Strict Rules:**
- **NO markdown or no extra words, detail add"
- **Be concise, factual, and clear**.
- **Do not make any health claims or guess the brand**.
- **Do not invent ingredients or toppings** that cannot be seen in the image.
- If you're **uncertain** about the food type, say: "May not be right", but must answer and continue with your best estimate.
- Base all estimates solely on the **visible food** in the image, using typical values.
"""
    
    # Claude API payload
    payload = {
        "model": "claude-3-5-haiku-20241022",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": encoded_image
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    }
    
    try:
        # Send request to Claude
        response = requests.post(CLAUDE_API_URL, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            # Extract text from Claude's response structure
            return result['content'][0]['text']
        else:
            return f"API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Error: {str(e)}"


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
        img_src = f"/{file_path.replace(os.sep, '/')}"

        # Convert image to base64 for display
        encoded_img = base64.b64encode(image_bytes).decode("utf-8")
        img_src = f"data:image/jpeg;base64,{encoded_img}"

        # Analyze with Claude
        result_text = analyze_food_with_claude(image_bytes)

        # Parse response
        if "Please Retake Picture" in result_text or "Uncertain" in result_text:
            description = "Please Retake Picture"
            nutrition_info = []
            portion_estimate = None
            dish_name = "Unknown Dish"
        else:
            lines = [line.strip("*•- ").strip() for line in result_text.split("\n") if line.strip()]
            if lines:
                dish_name = lines[0]
                description = lines[1] if len(lines) > 1 else "No description available"
                if len(lines) > 2:
                    portion_estimate = lines[-1]
                    nutrition_info = lines[2:-1]
                else:
                    nutrition_info = []
                    portion_estimate = None

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