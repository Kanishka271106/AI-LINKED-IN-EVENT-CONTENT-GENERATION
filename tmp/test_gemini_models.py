import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("NO API KEY")
    exit(1)

genai.configure(api_key=api_key)
try:
    print("Available models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print("-", m.name)
            
    print("\nTesting gemini-1.5-flash connection:")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello")
    print("Success:", response.text[:20])
except Exception as e:
    print("ERROR:", str(e))
