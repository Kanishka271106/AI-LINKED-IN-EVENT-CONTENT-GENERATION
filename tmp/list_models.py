import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get('GEMINI_API_KEY')
print(f"API Key present: {bool(api_key)}")

if api_key:
    try:
        genai.configure(api_key=api_key)
        for m in genai.list_models():
            print(f"Model: {m.name}, Supported Methods: {m.supported_generation_methods}")
    except Exception as e:
        print(f"Error: {e}")
