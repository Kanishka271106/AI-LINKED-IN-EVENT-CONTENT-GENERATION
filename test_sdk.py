import sys
import subprocess

subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai"])

from google import genai
print("genai attributes:", dir(genai))
client = genai.Client(api_key="dummy")
print("client attributes:", dir(client))
print("client.models attributes:", dir(client.models))
print("client.chats attributes:", dir(client.chats))
