**🍽️ Food Nutrition Analyzer AI**

A smart web app that analyzes food images and provides detailed nutritional information using AI.

**🚀 Project Overview**

This project leverages the Qwen AI model via OpenRouter to analyze images of food, automatically estimating:

Dish name and description

Calories, macronutrients, and portion size

Ingredients visible in the image

It’s perfect for nutrition tracking, meal planning, or AI-powered food research.

Pro Tip: All nutritional estimates are based solely on visible ingredients. Hidden items are not assumed.

**📸 Features**
<img width="959" height="780" alt="5 (1)" src="https://github.com/user-attachments/assets/30a1e60b-ad55-404b-b64b-40bed2ed99c9" />

<img width="971" height="879" alt="1 (1)" src="https://github.com/user-attachments/assets/703bd0a3-ce6a-4be9-882a-39160fdcf50d" />

**AI returns:**

Dish name and description

Nutritional breakdown (calories, protein, fat, carbs, fiber, sugars)

Portion estimate

Handles mixed dishes intelligently

Optimized image compression to ensure fast AI response

**🎥 Demo**

https://github.com/user-attachments/assets/7c64f381-44e0-42d9-af78-3e117ceeb846


**🛠️ Tech Stack**

Backend: Python, Flask

AI Model: Qwen AI (via OpenRouter API)

Image Processing: Pillow (PIL)

Environment Management: Python-dotenv

Frontend: Jinja2 templates for easy HTML rendering

**⚡ How It Works**

Upload Image: Users select an image of their meal.

Compress Image: Ensures it’s under 5 MB for fast processing.

AI Analysis: Image sent to Qwen API for nutrition extraction.

Parse JSON Response: Structured nutrition info returned and displayed.

