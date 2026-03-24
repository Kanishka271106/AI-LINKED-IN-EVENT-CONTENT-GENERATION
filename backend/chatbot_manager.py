from google import genai
import os

from typing import List, Dict, Optional
import uuid

class ChatbotManager:
    """Manages conversational AI sessions for LinkedIn content generation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.sessions: Dict[str, List[Dict[str, str]]] = {}
        self.is_configured = False
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                self.is_configured = True
            except Exception as e:
                print(f"Failed to configure Gemini API: {e}")

    def create_session(self, event_context: str) -> str:
        """Initialize a new chat session with event context"""
        session_id = str(uuid.uuid4())
        system_prompt = f"""
        You are an expert LinkedIn Content Strategist. Your goal is to help the user write a high-impact LinkedIn post.
        
        CONTEXT:
        {event_context}
        
        GUIDELINES:
        1. Keep the tone professional, engaging, and authentic.
        2. Use paragraph breaks for readability.
        3. Aim for 10-15 lines for the final post.
        4. Use bolding for emphasis on key names or the event.
        5. Naturally weave in details from the context.
        6. Include 3-5 relevant hashtags at the end.
        
        Your first message should be a strong, high-quality draft based on the context. 
        Then, wait for user feedback to refine it.
        """
        
        self.sessions[session_id] = [
            {"role": "user", "parts": [system_prompt]}
        ]
        return session_id

    def get_response(self, session_id: str, user_message: str) -> str:
        """Get a response from the AI for a given session and message"""
        if not self.is_configured:
            return "Gemini API not configured. Please check your .env file."
        
        if session_id not in self.sessions:
            return "Session expired or not found. Please start over."

        try:
            # Append user message to history
            self.sessions[session_id].append({"role": "user", "parts": [user_message]})
            
            # Generate response using history
            # Note: Gemini Pro content type is list of dicts with 'role' and 'parts'
            chat = self.model.start_chat(history=self.sessions[session_id][:-1])
            response = chat.send_message(user_message)
            
            # Store AI response in history
            self.sessions[session_id].append({"role": "model", "parts": [response.text]})
            
            return response.text
        except Exception as e:
            print(f"[ERROR] Chatbot failed: {e}")
            return f"I ran into an error: {str(e)}"

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Return the chat history for a session"""
        return self.sessions.get(session_id, [])
