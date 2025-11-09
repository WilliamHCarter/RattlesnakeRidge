#!/usr/bin/env python3
"""
Direct test of the LangChain streaming functionality to isolate the issue.
"""

import sys
sys.path.append('.')

from server.routes import *
from server.agents.conversation import Conversation, LLMData
from server.agents.agent import Agent
import logging

# Configure logging to see all debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_langchain_streaming():
    """Test LangChain streaming directly."""
    print("🧪 Testing LangChain streaming functionality...")

    # Create a simple agent for testing
    llm = ChatOpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        model="granite3.1-dense:8b",
        streaming=True,
        model_kwargs={"stop": ["\n"]},
    )

    # Load a character
    agent = Agent('server/data/characters/flint.yaml')

    # Create conversation data
    prompts = {"single_person_conversation_complex": "Test prompt"}
    setting_data = {"game_setting": "Rattlesnake Ridge"}
    llm_data = LLMData(llm, prompts["single_person_conversation_complex"], setting_data)

    # Create conversation
    conversation = Conversation([agent], llm_data)

    print(f"📝 Created conversation with agent: {agent.name}")

    # Test non-streaming first
    print("\n🔄 Testing non-streaming conversation...")
    try:
        responses = conversation.converse("Hello, can you tell me about yourself?", stream=False)
        print(f"✅ Non-streaming worked: {len(responses)} responses")
        for r in responses:
            print(f"   📄 {r.agent}: {r.text}")
    except Exception as e:
        print(f"❌ Non-streaming failed: {e}")
        import traceback
        traceback.print_exc()

    # Test streaming
    print("\n🌊 Testing streaming conversation...")
    try:
        stream_gen = conversation.converse("Hello, can you tell me about yourself?", stream=True)
        print(f"📡 Got stream generator: {stream_gen}")

        if stream_gen is not None:
            print("✅ Stream generator is not None, testing token generation...")
            tokens = []
            for i, token in enumerate(stream_gen):
                tokens.append(token)
                print(f"   🔤 Token {i+1}: '{token}'")
                if i > 10:  # Limit tokens for testing
                    print("   ✂️  Stopping after 10 tokens for testing...")
                    break
            print(f"✅ Streaming worked: got {len(tokens)} tokens")
        else:
            print("❌ Stream generator is None")

    except Exception as e:
        print(f"❌ Streaming failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_langchain_streaming()