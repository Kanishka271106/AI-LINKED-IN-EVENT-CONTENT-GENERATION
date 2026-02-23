from backend.linkedin_api import LinkedInAPI
import os
from dotenv import load_dotenv

load_dotenv()
api = LinkedInAPI()
url = api.get_authorization_url(state="test_state")
print(f"Generated URL: {url}")
print(f"Client ID: '{api.client_id}'")
print(f"Redirect URI: '{api.redirect_uri}'")
print(f"Scopes: {api.scopes}")
