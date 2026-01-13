# import os
# import base64
# from PIL import Image
# from openai import OpenAI
# from dotenv import load_dotenv
# from io import BytesIO

# load_dotenv()

# # Initialize OpenRouter API client
# client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",  # Verify this URL
#     api_key=os.getenv("OPENROUTER_API_KEY"),
# )

# # LLaMA model for food analysis
# model = "meta-llama/llama-3.3-70b-instruct"  # Ensure this is the correct model

# # Image processing function
# def process_image(image_path):
#     # Open and resize the image
#     image = Image.open(image_path)
#     image = image.resize((800, 800))  # Resize the image for faster processing

#     # Convert the image to base64
#     buffered = BytesIO()
#     image.save(buffered, format="JPEG")
#     img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
#     return img_base64

# # Food analysis function
# def analyze_food(image_path):
#     # Convert image to base64
#     img_base64 = process_image(image_path)

#     # Define a simple prompt for the model to match the required format
#     simple_prompt = """You are a skilled nutrition analyst.

# OUTPUT FORMAT:
# - Return ONE JSON object ONLY. No markdown, no code fences, no headings, no extra words.

# SCHEMA (use exactly these keys):
# {
#   "dish": "<best guess single short name of the visible main dish>",
#   "description": "<2–3 factual sentences about what is visibly present and the portion/presentation. If identification is unclear, set exactly to 'Please Retake Picture'>",
#   "macros": {
#     "calories": "xx–xx kcal",
#     "carbohydrates": "xx–xx g",
#     "sugars": "xx–xx g",
#     "fiber": "xx–xx g",
#     "protein": "xx–xx g",
#     "fat": "xx–xx g"
#   },
#   "portion_estimate": "<one concise line giving portion size and kcal based only on the visible amount>"
# }

# HARD CONSTRAINTS:
# - Provide the best guess dish name. NEVER use uncertainty phrases (e.g., "unsure", "maybe", "probably", "guess", "may not be right", "(?)").
# - If identification is unclear, set "description" to exactly "Please Retake Picture" AND set:
#   - "dish" = ""
#   - each field inside "macros" = ""
#   - "portion_estimate" = ""
# """

#     # Send request to OpenRouter with the image and prompt
#     response = client.chat.completions.create(
#         model=model,
#         messages=[
#             {
#                 "role": "user",
#                 "content": simple_prompt,
#             },
#             {
#                 "role": "user",
#                 "content": img_base64,  # Send the base64 encoded image
#             },
#         ],
#     )

#     # Retrieve the response and ensure it's in the correct format
#     response_text = response.choices[0].message.content
#     return response_text

# # Test with a sample image
# image_path = "2.jpg"  # Replace this with the path to your image
# result = analyze_food(image_path)

# # Print the result, which should be in the exact format you requested
# print(result)



import os
import base64
from flask import Flask, request, render_template
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()

# Initialize OpenRouter API client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",  # Ensure this URL is correct
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# LLaMA model for food analysis
model = "meta-llama/llama-3.3-70b-instruct"  # Ensure this is the correct model

app = Flask(__name__)

# Image processing function
def process_image(image):
    # Resize image for better processing
    image = image.resize((800, 800))
    
    # Convert the image to base64 for API submission
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_base64

# Function to call LLaMA model
def analyze_food(img_base64):
    # Define a simple prompt for the model to match the required format
    simple_prompt = """You are a skilled nutrition analyst.
Identify the food in this image and macronutrient based upon quantity give a detail in short. (3 sentence).
                Then provide the macronutrient based on picture provide food quantity  in this format:

                Calories: xx kcal
                Carbohydrates: xx g
                Sugars: xx g
                Fiber: xx g
                Protein: xx g
                Fat: xx g
           NO extra text.

"""

    # Send the request to OpenRouter
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": simple_prompt},
            {"role": "user", "content": img_base64}
        ],
    )
    
    # Parse the response and return the result
    return response.choices[0].message.content

@app.route("/", methods=["GET", "POST"])
def index():
    img_src = None
    response_text = None

    if request.method == "POST":
        if "file" not in request.files:
            return "No file uploaded", 400
        file = request.files["file"]
        if file.filename == "":
            return "No file selected", 400

        # Open and process the uploaded image
        image = Image.open(file)
        img_base64 = process_image(image)
        
        # Send image to the LLaMA model and get response
        response_text = analyze_food(img_base64)
        
        # Prepare image source for rendering
        img_src = "data:image/jpeg;base64," + img_base64

    # Render the page with the uploaded image and model response
    return render_template("test.html", img_src=img_src, response_text=response_text)

if __name__ == "__main__":
    app.run(debug=True)
