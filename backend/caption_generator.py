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
        include_hashtags = preferences.get("include_hashtags", True) if preferences else True
        custom_hashtags = preferences.get("custom_hashtags", "") if preferences else ""

        base_prompt = f"""
        Objective: Write a highly engaging, custom LinkedIn post.
        - Event Name: {event_name}
        - Photo count shared: {num_photos}
        """
        
        if custom_context:
            base_prompt += f"\n- User's Specific Details/Opinion: {custom_context}\n"

        base_prompt += f"""
        
        CRITICAL Guidelines:
        1. ANALYZE THE EVENT CATEGORY: Examine the Event Name ({event_name}) and the User's Opinion.
           - If it's a DANCE event: Focus on the rhythm, the performance, the energy, the choreo, the stage, and the artistic expression.
           - If it's a MUSIC / SINGING event: Focus on the vocals, the melody, the vibration, the connection with the audience, and the soul.
           - If it's a SPORTS / FITNESS event: Focus on the sweat, the dedication, the movement, the adrenaline, and the physical achievement.
           - ONLY if it's a TECH / CORPORATE event: Use professional networking or industry language.
        2. ADAPT THE TONE: Your vocabulary and insights MUST perfectly match the specific event type. DO NOT use generic business/tech jargon (e.g. "cutting-edge insights", "networking", "industry leaders") unless it is explicitly an industry/tech event! No "deep dives" or "key takeaways" for a dance performance!
        3. Output Length: The post MUST be substantial, at least 10 to 15 lines long. Break it into multiple paragraphs for readability.
        4. Content Expansion: Elaborate on the event, why the {num_photos} photos matter, the atmosphere, and the memories. Be highly expressive and authentic.
        5. Style: Engaging and authentic for LinkedIn, but perfectly tailored to the event's vibe (e.g. energetic and passionate for dance, appreciative for music, professional for tech).
        6. No Intro/Outro: Do NOT include "Here is your caption".
        7. Formatting: Use **bolding** for emphasis on the event name, and use appropriate emojis (e.g. 💃🕺 for dance, 🎤🎵 for music, ⚽🏋️ for sports, 💻🚀 for tech).
        """
        
        if include_hashtags:
            base_prompt += "\n6. Hashtags: Include 3-5 relevant hashtags at the VERY END, separated from the paragraph by a line break."
            if custom_hashtags:
                base_prompt += f" Must include: {custom_hashtags}"
        else:
            base_prompt += "\n6. No Hashtags: Do NOT include any hashtags."
            
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
