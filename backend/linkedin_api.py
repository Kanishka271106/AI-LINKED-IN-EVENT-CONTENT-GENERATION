import os
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict
from dotenv import load_dotenv
from urllib.parse import urlencode

load_dotenv()


class LinkedInAPI:
    """Handle LinkedIn OAuth and posting"""
    
    def __init__(self):
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID", "").strip()
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "").strip()
        self.redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "").strip()
        
        # LinkedIn OAuth URLs
        self.auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.api_base = "https://api.linkedin.com/v2"
        
        # Required scopes (OpenID Connect + w_member_social)
        self.scopes = ["openid", "profile", "email", "w_member_social"]
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Generate LinkedIn OAuth authorization URL
        User will be redirected here to authorize the app
        """
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
        }
        
        if state:
            params["state"] = state
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str) -> Dict:
        """
        Exchange authorization code for access token
        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        
        # Calculate expiration time
        expires_in = token_data.get("expires_in", 5184000)  # Default 60 days
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        return {
            "access_token": token_data["access_token"],
            "expires_at": expires_at,
            "expires_in": expires_in
        }
    
    def get_user_info(self, access_token: str) -> Dict:
        """
        Get user profile information using OpenID Connect
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Use OpenID Connect userinfo endpoint
        response = requests.get(
            "https://api.linkedin.com/v2/userinfo",
            headers=headers
        )
        response.raise_for_status()
        user_data = response.json()
        
        return {
            "id": user_data.get("sub"), # 'sub' is the unique ID in OIDC
            "firstName": user_data.get("given_name"),
            "lastName": user_data.get("family_name"),
            "email": user_data.get("email"),
            "picture": user_data.get("picture")
        }
    
    def upload_image(self, access_token: str, image_path: str, person_urn: str) -> str:
        """
        Upload image to LinkedIn and get asset URN
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Register upload
        register_data = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": person_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        
        register_response = requests.post(
            f"{self.api_base}/assets?action=registerUpload",
            headers=headers,
            json=register_data
        )
        register_response.raise_for_status()
        register_result = register_response.json()
        
        # Get upload URL and asset URN
        upload_url = register_result["value"]["uploadMechanism"][
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
        ]["uploadUrl"]
        asset_urn = register_result["value"]["asset"]
        
        # Upload the actual image
        with open(image_path, "rb") as image_file:
            upload_response = requests.put(
                upload_url,
                data=image_file,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            upload_response.raise_for_status()
        
        return asset_urn
    
    def create_image_post(self, access_token: str, person_urn: str, 
                         image_paths: list, caption: str = "") -> Dict:
        """
        Create a LinkedIn post with images
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # Upload all images
        media_assets = []
        for image_path in image_paths:
            asset_urn = self.upload_image(access_token, image_path, person_urn)
            media_assets.append({
                "status": "READY",
                "media": asset_urn
            })
        
        # Create post
        post_data = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": caption or "Event photos 📸 #professional #networking"
                    },
                    "shareMediaCategory": "IMAGE",
                    "media": media_assets
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        response = requests.post(
            f"{self.api_base}/ugcPosts",
            headers=headers,
            json=post_data
        )
        response.raise_for_status()
        
        return response.json()
    
    def create_text_post(self, access_token: str, person_urn: str, text: str) -> Dict:
        """
        Create a simple text post
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        post_data = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        response = requests.post(
            f"{self.api_base}/ugcPosts",
            headers=headers,
            json=post_data
        )
        response.raise_for_status()
        
        return response.json()
    
    def validate_token(self, access_token: str) -> bool:
        """
        Check if access token is still valid
        """
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers)
            return response.status_code == 200
        except:
            return False
