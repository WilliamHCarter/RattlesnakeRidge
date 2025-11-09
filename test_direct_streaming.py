#!/usr/bin/env python3
"""
Direct test of LangChain streaming with Ollama to isolate the issue.
"""

import sys
sys.path.append('.')

from langchain.chat_models.openai import ChatOpenAI
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_direct_streaming():
    """Test LangChain streaming directly with the LLM."""
    print("🧪 Testing direct LangChain streaming...")

    # Create LLM
    llm = ChatOpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        model="granite3.1-dense:8b",
        streaming=True,
        model_kwargs={"stop": ["\n"]},
    )

    print("✅ Created LLM with streaming=True")

    # Test direct streaming
    print("\n🌊 Testing direct streaming...")
    try:
        from langchain.schema import HumanMessage
        messages = [HumanMessage(content="Hello, who are you? Keep it brief.")]

        print("📡 Calling stream() method...")
        stream = llm.stream(messages)

        print("✅ Got stream object, iterating over tokens...")
        token_count = 0
        full_text = ""

        for token in stream:
            token_count += 1
            print(f"   🔤 Token {token_count}: '{token}' (type: {type(token)})")
            print(f"       - repr: {repr(token)}")
            if hasattr(token, 'content'):
                print(f"       - content: '{token.content}'")
            # Extract the actual content
            if hasattr(token, 'content'):
                actual_token = token.content
            else:
                actual_token = str(token)
            full_text += actual_token
            print(f"       - extracted: '{actual_token}'")

            if token_count >= 20:  # Limit for testing
                print("   ✂️  Stopping after 20 tokens...")
                break

        print(f"✅ Direct streaming worked! Got {token_count} tokens")
        print(f"📄 Full text: '{full_text}'")

    except Exception as e:
        print(f"❌ Direct streaming failed: {e}")
        import traceback
        traceback.print_exc()

    # Test regular invocation for comparison
    print("\n🔄 Testing regular invocation...")
    try:
        messages = [HumanMessage(content="Hello, who are you? Keep it brief.")]

        print("📡 Calling invoke() method...")
        response = llm.invoke(messages)

        print(f"✅ Regular invocation worked!")
        print(f"📄 Response: '{response}'")

    except Exception as e:
        print(f"❌ Regular invocation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_streaming()