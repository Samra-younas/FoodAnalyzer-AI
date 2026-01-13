#Import Libraries
import os
import base64
from io import BytesIO
from flask import Flask, request, render_template
from PIL import Image
import google.generativeai as genai

# ---------------------- Flask setup ------------------------
app = Flask(__name__)

# ---------------------- Gemini setup ------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-001")

# ---------------------- Routes ------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    nutrition_info = []
    description = None
    portion_estimate = None
    img_src = None
    dish_name = None  # Variable for the dish name

    if request.method == "POST":                                                                                                                                                    
        if "file" not in request.files:
            return "No file uploaded", 400

        file = request.files["file"]
        if file.filename == "":
            return "No file selected", 400

        # Read image in memory (not saving permanently)
        image_bytes = file.read()
        image = Image.open(BytesIO(image_bytes))

        # ---------------- Save uploaded image ----------------
        upload_folder = os.path.join("static", "uploads")
        file_path = os.path.join(upload_folder, file.filename)
        file.seek(0)  # reset file pointer before saving
        file.save(file_path)
        # Optionally update img_src to use saved file
        img_src = f"/{file_path.replace(os.sep, '/')}"

        # Convert image to base64 so it can be shown in HTML
        encoded_img = base64.b64encode(image_bytes).decode("utf-8")
        img_src = f"data:image/jpeg;base64,{encoded_img}"

        # Send image to Gemini with structured prompt
        response = model.generate_content(
            [
                """
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
Protein:xx-xx g  
Fat: xx-xx g  
---  
Based on the visible amount: Provide **one single line** estimating the portion size and calories based only on the visible amount, explaining briefly. For example: "Looks like ~200–250 kcal, about one medium glass (~250 ml)."
### **Strict Rules:**
- ** NO markdown or no extra words add.
- **Be concise, factual, and clear**.
- **Do not make any health claims or guess the brand**.
- **Do not invent ingredients or toppings** that cannot be seen in the image.
- If you're **uncertain** about the food type, say: "May not be right", but must answer and continue with your best estimate.
- Base all estimates solely on the **visible food** in the image, using typical values.
""",
                {"mime_type": "image/jpeg", "data": image_bytes},
            ]
        )
        
        # Get response text safely
        result_text = response.text.strip()

        # If Gemini says retake or uncertain → show message only
        if "Please Retake Picture" in result_text or "Uncertain" in result_text:
            description = "Please Retake Picture"
            nutrition_info = []
            portion_estimate = None
            dish_name = "Unknown Dish"  # Set a fallback dish name if unclear
        else:
            # Split response into lines
            lines = [line.strip("*•- ").strip() for line in result_text.split("\n") if line.strip()]
            if lines:
                dish_name = lines[0]  # First line should be the dish name
                description = lines[1]  # Second line = description
                if len(lines) > 2:
                    portion_estimate = lines[-1]  # Last line = portion estimate
                    nutrition_info = lines[2:-1]  # All lines except the first and last
                else:
                    nutrition_info = []
                    portion_estimate = None

    return render_template(
        "index.html",
        img_src=img_src,
        description=description,
        nutrition_info=nutrition_info,
        portion_estimate=portion_estimate,
        dish_name=dish_name  # Pass the dish name to the template
    )

# ---------------------- Run ------------------------
if __name__ == "__main__":
    app.run(debug=True)
