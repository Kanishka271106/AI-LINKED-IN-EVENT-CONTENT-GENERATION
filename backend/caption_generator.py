import os
import google.generativeai as genai
from typing import List, Optional
import random

class CaptionGenerator:
    """AI-powered caption generator for LinkedIn posts"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.is_configured = False
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.is_configured = True
            except Exception as e:
                print(f"Failed to configure Gemini API: {e}")
    
    def generate_caption(self, event_name: str, num_photos: int, keywords: Optional[List[str]] = None, custom_context: Optional[str] = None) -> str:
        """
        Generate a professional LinkedIn caption based on event context
        """
        if not self.is_configured:
            return self._generate_mock_caption(event_name, num_photos, custom_context)
            
        try:
            prompt = self._create_prompt(event_name, num_photos, keywords, custom_context)
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating caption: {e}")
            return self._generate_mock_caption(event_name, num_photos, custom_context)
            
    def _create_prompt(self, event_name: str, num_photos: int, keywords: Optional[List[str]], custom_context: Optional[str]) -> str:
        """Create a prompt for the LLM"""
        base_prompt = f"""
        Write a professional, engaging LinkedIn post caption for an event.
        - Event Name: {event_name}
        - Context: Sharing {num_photos} highlights from the event.
        """
        
        if custom_context:
            base_prompt += f"\n- User Instructions: {custom_context}\n"
            base_prompt += "- IMPORTANT: Follow the User Instructions above strictly."
        else:
            base_prompt += """
            - Tone: Professional, enthusiastic, grateful, networking-focused.
            - Structure: Hook -> Body (Event highlights) -> Call to Action (Networking).
            """
            
        base_prompt += "\n- Hashtags: Include 3-5 relevant hashtags at the end."
        
        if keywords:
            base_prompt += f"\nKeywords to include: {', '.join(keywords)}\n"
            
        base_prompt += "\noutput only the caption text."
        return base_prompt

    def _generate_mock_caption(self, event_name: str, num_photos: int, custom_context: Optional[str] = None) -> str:
        """Fallback mock caption if API is not configured"""
        
        # Determine the focal point of the event
        display_name = event_name
        if custom_context and len(custom_context.strip()) > 0:
            # If the user provided a short context, it might be the actual event name
            if len(custom_context.split()) <= 4:
                display_name = custom_context.strip()
            # Otherwise use it as part of the context
        
        templates = [
            f"Here are some highlights from {display_name}! 📸\n\n"
            f"Had an amazing time connecting with industry professionals and sharing insights at {display_name}. "
            f"Events like these remind me of the power of networking and community.\n\n"
            f"Enjoy these {num_photos} selected moments!\n\n"
            f"#Networking #{display_name.replace(' ', '')} #ProfessionalDevelopment #EventHighlights",
            
            f"Throwback to {display_name} ✨\n\n"
            f"Incredible energy and great conversations. Grateful to have been part of such a well-organized event. "
            f"Here are my top {num_photos} photos from the day.\n\n"
            f"Which one is your favorite?\n\n"
            f"#Community #{display_name.replace(' ', '')} #Leadership #Growth",
            
            f"Just wrapped up at {display_name}! 🚀\n\n"
            f"So much learning and new connections made. It's always inspiring to be surrounded by driven individuals. "
            f"Sharing a glimpse of the experience through these {num_photos} photos.\n\n"
            f"Let's keep the conversation going in the comments! 👇\n\n"
            f"#Business #Networking #{display_name.replace(' ', '')} #Success"
        ]
        
        caption = random.choice(templates)
        
        # If there's a long custom context, append it or integrate it
        if custom_context and len(custom_context.split()) > 4:
            caption = f"{custom_context}\n\n---\n\n{caption}"
            
        return caption
