import os
from google import genai
from typing import List, Optional
import random

class CaptionGenerator:
    """AI-powered caption generator for LinkedIn posts"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.is_configured = False
        
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                self.is_configured = True
            except Exception as e:
                print(f"Failed to configure Gemini API: {e}")
    
    def generate_caption(self, event_name: str, num_photos: int, keywords: Optional[List[str]] = None, custom_context: Optional[str] = None, preferences: Optional[dict] = None) -> str:
        """
        Generate a professional LinkedIn caption based on event context and user preferences
        """
        if not self.is_configured:
            return self._generate_mock_caption(event_name, num_photos, custom_context)
            
        try:
            prompt = self._create_prompt(event_name, num_photos, keywords, custom_context, preferences)
            response = self.client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")
            return response.text
        except Exception as e:
            print(f"[CRITICAL ERROR] Gemini API call failed: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._generate_mock_caption(event_name, num_photos, custom_context)
            
    def _create_prompt(self, event_name: str, num_photos: int, keywords: Optional[List[str]], custom_context: Optional[str], preferences: Optional[dict]) -> str:
        """Create a precision prompt for the LLM to generate paragraph-style captions"""
        preferences = preferences or {}
        include_hashtags = preferences.get("include_hashtags", True)
        custom_hashtags = preferences.get("custom_hashtags", "")
        event_type = preferences.get("event_type", "General")
        post_vibe = preferences.get("post_vibe", "Professional")

        base_prompt = f"""
        Objective: Write a highly engaging, custom LinkedIn post.
        - Event Name: {event_name}
        - Event Category: {event_type}
        - Post Tone/Vibe: {post_vibe}
        - Photo count shared: {num_photos}
        """
        
        if custom_context:
            base_prompt += f"\n- User's Specific Details/Opinion: {custom_context}\n"

        base_prompt += f"""
        
        CRITICAL Guidelines:
        1. STYLE THE VOICE: Your vocabulary and tone MUST match the Event Category ({event_type}) and Post Vibe ({post_vibe}).
           - If it's DANCE: Focus on choreography, rhythm, and stage presence.
           - If it's MUSIC: Focus on vocals, instruments, and the auditory experience.
           - If it's SPORTS: Focus on movement, athleticism, and the "win".
           - Use the Vibe ({post_vibe}) to determine if you should be serious, excited, humble, or tell a narrative story.
        2. NO TECH JARGON: Do NOT use generic business/tech jargon (e.g. "cutting-edge", "networking", "industry leaders") unless the category is explicitly Tech!
        3. Output Length: The post MUST be substantial, at least 10 to 15 lines long. Break it into multiple paragraphs.
        4. Content Expansion: Elaborate on the event atmosphere and the {num_photos} highlights shared. Be expressive.
        5. Formatting: Use **bolding** for the event name ({event_name}). Use appropriate emojis for the category ({event_type}).
        6. No Intro/Outro: Do NOT include "Here is your caption".
        """
        
        if include_hashtags:
            base_prompt += "\n7. Hashtags: Include 3-5 relevant hashtags at the VERY END."
            if custom_hashtags:
                base_prompt += f" Must include: {custom_hashtags}"
        else:
            base_prompt += "\n7. No Hashtags: Do NOT include any hashtags."
            
        if keywords:
            base_prompt += f"\nKeywords to include: {', '.join(keywords)}\n"

        return base_prompt.strip()

    def _generate_mock_caption(self, event_name: str, num_photos: int, custom_context: Optional[str] = None) -> str:
        """Fallback mock caption that is flexible for all event types"""
        
        # Log notice
        print(f"[FALLBACK] Using generic flexible template for: {event_name}")
        
        opinion = ""
        if custom_context and len(custom_context.strip()) > 0:
            opinion = f" {custom_context}."
        
        # Simple category detection
        name_lower = event_name.lower()
        context_lower = (custom_context or "").lower()
        
        is_arts = any(k in name_lower or k in context_lower for k in ["dance", "music", "sing", "art", "performance", "concert", "stage"])
        is_sports = any(k in name_lower or k in context_lower for k in ["sport", "game", "match", "fit", "gym", "run", "race"])
        
        if is_arts:
            return f"What an incredible experience at **{event_name}**! 🎭✨{opinion}\n\nThe energy in the room was absolutely electric, and seeing such raw talent and passion on display was truly inspiring. It's moments like these that remind us how powerful creative expression can be in bringing people together.\n\nEvery performance was a testament to hard work and dedication. I feel so lucky to have been there to witness it all! 👏\n\nSharing these {num_photos} highlights that captured the beautiful vibration and soul of the event. 📸💖\n\n#Passion #ArtsAndCulture #Highlights #Memories"
        
        if is_sports:
            return f"Still buzzing from the adrenaline at **{event_name}**! 🏆🔥{opinion}\n\nThe level of dedication and competitive spirit shown today was second to none. There's nothing quite like the feeling of being part of such a high-energy environment where everyone is pushing their limits.\n\nWhether it was the teamwork or the individual brilliance, today was a win for everyone involved. ⚽💪\n\nHere are {num_photos} shots capturing the sweat, the cheers, and the pure excitement of the day! 📸🚀\n\n#Sports #Dedication #GameDay #Success"
            
        # Default high-quality professional but GENERIC template (Not tech-only)
        return f"Truly honored to have attended **{event_name}** recently! 🌟{opinion}\n\nIt was a day filled with meaningful interactions, fresh perspectives, and a shared sense of purpose. Being surrounded by such an engaged community always brings a new level of motivation to the work we do.\n\nWe explored so many interesting ideas and the atmosphere was perfect for genuine connection. A big thank you to everyone who made this event so special! 💼🤝\n\nCaptured {num_photos} moments that represent the best highlights of the experience. Swipe through to see them! 📸👇\n\n#Event #Networking #Growth #Community"
