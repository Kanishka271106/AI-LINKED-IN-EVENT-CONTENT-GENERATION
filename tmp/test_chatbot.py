import os
import sys
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.chatbot_manager import ChatbotManager

def test_chatbot_session():
    """Test that chatbot creates sessions and handles messages"""
    # Mock GenAI
    mgr = ChatbotManager(api_key="mock_key")
    mgr.model = MagicMock()
    mgr.is_configured = True
    
    # Init session
    session_id = mgr.create_session("Testing event context")
    assert session_id is not None
    assert session_id in mgr.sessions
    
    # Check history
    history = mgr.get_history(session_id)
    assert len(history) == 1
    assert "You are an expert LinkedIn Content Strategist" in history[0]["parts"][0]
    
    # Mock response
    mock_response = MagicMock()
    mock_response.text = "This is a mock AI response"
    mgr.model.start_chat.return_value.send_message.return_value = mock_response
    
    # Send message
    response = mgr.get_response(session_id, "Make it better")
    assert response == "This is a mock AI response"
    
    # Check updated history
    history = mgr.get_history(session_id)
    assert len(history) == 3 # System prompt, user message, AI response
    assert history[1]["parts"][0] == "Make it better"
    assert history[2]["parts"][0] == "This is a mock AI response"
    
    print("Chatbot Manager Test: PASSED")

if __name__ == "__main__":
    test_chatbot_session()
