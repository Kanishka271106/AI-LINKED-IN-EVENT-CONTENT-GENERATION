import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    print("API Key not found.")
    exit(1)

genai.configure(api_key=api_key)

print("Listing all generateContent models...")
try:
    models = genai.list_models()
    for m in models:
        if "generateContent" in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Failed to list models: {e}")
