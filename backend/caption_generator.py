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
            print(f"[ERROR] Caption generation failed: {e}")
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
        """Fallback mock caption if API is not configured"""
        
        # Log notice without emojis for terminal safety on some Windows systems
        print("[NOTICE] Gemini API Key not found. Using pre-defined professional templates.")
        
        # Determine the focal point of the event
        display_name = event_name
        opinion = ""
        if custom_context and len(custom_context.strip()) > 0:
            opinion = f" {custom_context}."
        
        templates = [
            f"It was an absolute privilege to participate in **{display_name}** this week! 🎉{opinion}\n\nFrom the moment the event kicked off, the energy was palpable. I had the incredible opportunity to connect with some of the brightest minds and most forward-thinking industry leaders in our space. 🚀 We explored innovative ideas, tackled complex challenges, and shared insights that I know will shape the future of our work.\n\nEvents like these are a powerful reminder of why I love what I do—it’s not just about the technology or the strategy; it’s about the fantastic community of professionals who drive progress forward every single day. 🤝\n\nI’m walking away with fresh perspectives, actionable takeaways, and a renewed sense of purpose. A huge thank you to the organizers, speakers, and everyone I had the pleasure of meeting. Let’s keep the conversation going! 💬\n\nSharing these {num_photos} photos to capture the vibrant energy and unforgettable moments of the day. 📸✨\n\n#Networking #EventHighlights #{display_name.replace(' ', '')} #ProfessionalGrowth #Community #Innovation",
            
            f"I am still buzzing from the incredible experience at **{display_name}** today! ✨{opinion}\n\nThe sessions were absolutely packed with value, delivering deep dives into the trends and strategies that are redefining our industry. 📈 I'm walking away with several key takeaways that I am eager to implement with my team immediately.\n\nIt’s always so inspiring to see so much raw talent, passion, and dedication gathered in one place. The conversations I had between sessions were just as valuable as the keynotes—proving once again that the power of connection is unmatched. 🤝💡\n\nI want to extend my gratitude to the hosts for putting together such a seamless and impactful event. The insights gained here will undoubtedly drive my work forward in the coming months. 🚀\n\nHere are {num_photos} highlights from the event that really stood out to me and captured the essence of the experience. 📸👇\n\n#Learning #Innovation #{display_name.replace(' ', '')} #Success #TechTrends #Leadership",
            
            f"What a phenomenal day at **{display_name}**! 🌟{opinion}\n\nBeyond the cutting-edge technical insights and deeply informative presentations, the true highlight for me was definitely the meaningful conversations and the wealth of new connections made. 🤝 Building relationships with peers who share the same drive for excellence is invaluable.\n\nWe discussed everything from emerging industry shifts to practical problem-solving strategies, and I couldn't be more energized. ⚡ It is environments like this that foster real innovation and collaborative breakthroughs.\n\nI am really looking forward to carrying this incredible momentum into my future projects and seeing where these new collaborations might lead. 🚀\n\nI put together a carousel of {num_photos} moments from the experience—swipe through to see some of my favorite highlights! 📸✨\n\n#Business #Connectivity #{display_name.replace(' ', '')} #CareerDevelopment #Networking #FutureOfWork"
        ]
        
        return random.choice(templates)
