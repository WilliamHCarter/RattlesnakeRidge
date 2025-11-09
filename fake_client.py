#!/usr/bin/env python3
"""
Simple test client to debug the streaming system.
This simulates the frontend behavior to test streaming endpoints directly.
"""

import json
import time
from typing import Optional

import requests
import sseclient

BASE_URL = "http://localhost:5001"


def start_game() -> Optional[str]:
    """Start a new game session and return the game ID."""
    try:
        response = requests.get(f"{BASE_URL}/start")
        if response.status_code == 200:
            data = response.json()
            game_id = data.get("game_id")
            print(f"✅ Started game with ID: {game_id}")
            return game_id
        else:
            print(f"❌ Failed to start game: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error starting game: {e}")
        return None


def send_message(game_id: str, message: str) -> Optional[dict]:
    """Send a message to the game and return the command response."""
    try:
        response = requests.post(f"{BASE_URL}/play/{game_id}", json={"input": message})
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(
                f"❌ Failed to send message: {response.status_code} - {response.text}"
            )
            return None
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return None


def test_streaming(stream_id: str, game_id: str):
    """Test the streaming endpoint directly."""
    url = f"{BASE_URL}/stream/{game_id}/{stream_id}"
    print(f"🌡️  Testing streaming at: {url}")

    try:
        # Make GET request to streaming endpoint
        response = requests.get(url, stream=True)
        print(f"📡 Stream response status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Stream connected successfully!")

            # Use sseclient to parse Server-Sent Events
            client = sseclient.SSEClient(response)

            token_count = 0
            full_text = ""

            for event in client.events():
                try:
                    data = json.loads(event.data)
                    print(f"📨 Received event: {data}")

                    if data.get("type") == "token":
                        token = data.get("token", "")
                        token_count += 1
                        full_text += token
                        print(f"🔤 Token #{token_count}: '{token}'")
                        print(f"📝 Full text so far: '{full_text}'")

                    elif data.get("type") == "done":
                        print("✅ Streaming completed!")
                        print(f"📊 Total tokens: {token_count}")
                        print(f"📄 Final text: '{data.get('full_text', '')}'")
                        break

                    elif data.get("type") == "error":
                        print(
                            f"❌ Streaming error: {data.get('message', 'Unknown error')}"
                        )
                        break

                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse JSON: {e}")
                    print(f"Raw event data: {event.data}")

        else:
            print(f"❌ Stream connection failed: {response.status_code}")
            print(f"Response text: {response.text}")

    except Exception as e:
        print(f"❌ Error testing stream: {e}")


def main():
    """Main test flow."""
    print("🚀 Starting streaming system test...")

    # Install sseclient if needed
    try:
        import sseclient
    except ImportError:
        print("📦 Installing sseclient-py...")
        import subprocess

        subprocess.check_call(["pip", "install", "sseclient-py"])
        import sseclient

    # Step 1: Start a game
    game_id = start_game()
    if not game_id:
        return

    print("\n" + "=" * 50)
    print("📝 Testing initial conversation flow...")
    print("=" * 50)

    # Step 2: Send initial empty message to get first response
    print("\n📤 Sending initial empty message...")
    response_data = send_message(game_id, "")

    if response_data:
        print(f"📬 Full response data: {json.dumps(response_data, indent=2)}")
        command = response_data.get("response", {})
        print(f"📬 Received command type: {command.get('type')}")

        if command.get("type") == "StreamingMessageCommand":
            stream_id = command.get("stream_id")
            agent_name = command.get("agent_name")
            print(f"🎬 Got streaming command!")
            print(f"   - Stream ID: {stream_id}")
            print(f"   - Agent: {agent_name}")

            # Step 3: Test the streaming
            print(f"\n🌡️  Testing streaming for {agent_name}...")
            test_streaming(stream_id, game_id)

        elif command.get("type") == "MessageDelayCommand":
            print(f"💬 Got non-streaming message: {command.get('message', '')}")

        elif command.get("type") == "SelectOptionCommand":
            print(f"🎛️  Got selection options!")
            options = command.get("options", [])
            for i, option in enumerate(options):
                print(f"   {i + 1}. {option}")

            # Auto-select the first option to test streaming
            if options:
                selected_option = options[0]
                print(f"🎯 Auto-selecting first option: '{selected_option}'")

                # Extract the option identifier (usually a number)
                if isinstance(selected_option, list) and len(selected_option) > 0:
                    option_identifier = selected_option[0]
                else:
                    option_identifier = str(selected_option)

                print(f"📤 Sending option identifier: '{option_identifier}'")
                # Send the selected option identifier
                response_data = send_message(game_id, option_identifier)
                if response_data:
                    command = response_data.get("response", {})
                    print(
                        f"📬 Full response after selection: {json.dumps(response_data, indent=2)}"
                    )
                    print(
                        f"📬 Received command type after selection: {command.get('type')}"
                    )

                    if command.get("type") == "StreamingMessageCommand":
                        stream_id = command.get("stream_id")
                        agent_name = command.get("agent_name")
                        print(f"🎬 Got streaming command!")
                        print(f"   - Stream ID: {stream_id}")
                        print(f"   - Agent: {agent_name}")

                        # Test the streaming
                        print(f"\n🌡️  Testing streaming for {agent_name}...")
                        test_streaming(stream_id, game_id)
            else:
                print("❌ No options available")

        else:
            print(f"❓ Unknown command type: {command.get('type')}")

    print("\n" + "=" * 50)
    print("📝 Testing second turn...")
    print("=" * 50)

    # Step 4: Send a dummy response to trigger next agent
    print("\n📤 Sending dummy response...")
    response_data = send_message(game_id, "dummy response")

    if response_data:
        command = response_data.get("response", {})
        print(f"📬 Received command type: {command.get('type')}")

        if command.get("type") == "StreamingMessageCommand":
            stream_id = command.get("stream_id")
            agent_name = command.get("agent_name")
            print(f"🎬 Got streaming command!")
            print(f"   - Stream ID: {stream_id}")
            print(f"   - Agent: {agent_name}")

            # Step 5: Test the second streaming
            print(f"\n🌡️  Testing streaming for {agent_name}...")
            test_streaming(stream_id, game_id)

        elif command.get("type") == "SelectOptionCommand":
            print(f"🎛️  Got selection options!")
            options = command.get("options", [])
            for i, option in enumerate(options):
                print(f"   {i + 1}. {option}")

            # Auto-select the first option to test streaming
            if options:
                selected_option = options[0]
                print(f"🎯 Auto-selecting first option: '{selected_option}'")

                # Extract the option identifier (usually a number)
                if isinstance(selected_option, list) and len(selected_option) > 0:
                    option_identifier = selected_option[0]
                else:
                    option_identifier = str(selected_option)

                print(f"📤 Sending option identifier: '{option_identifier}'")
                # Send the selected option identifier
                response_data = send_message(game_id, option_identifier)
                if response_data:
                    command = response_data.get("response", {})
                    print(
                        f"📬 Full response after selection: {json.dumps(response_data, indent=2)}"
                    )
                    print(
                        f"📬 Received command type after selection: {command.get('type')}"
                    )

                    if command.get("type") == "StreamingMessageCommand":
                        stream_id = command.get("stream_id")
                        agent_name = command.get("agent_name")
                        print(f"🎬 Got streaming command!")
                        print(f"   - Stream ID: {stream_id}")
                        print(f"   - Agent: {agent_name}")

                        # Test the streaming
                        print(f"\n🌡️  Testing streaming for {agent_name}...")
                        test_streaming(stream_id, game_id)
            else:
                print("❌ No options available")

        else:
            print(f"❓ Unknown command type: {command.get('type')}")

    print("\n" + "=" * 50)
    print("📝 Testing third turn (actual conversation)...")
    print("=" * 50)

    # Step 6: Send empty message to get past introduction text
    print("\n📤 Sending empty message to get past introduction...")
    response_data = send_message(game_id, "")

    if response_data:
        command = response_data.get("response", {})
        print(
            f"📬 Full response for introduction: {json.dumps(response_data, indent=2)}"
        )
        print(f"📬 Received command type for introduction: {command.get('type')}")

        if command.get("type") == "MessageDelayCommand":
            print(f"💬 Got introduction message: {command.get('message', '')}")

    # Step 7: Send another empty message to trigger actual conversation
    print("\n📤 Sending another empty message to start actual conversation...")
    response_data = send_message(game_id, "")

    if response_data:
        command = response_data.get("response", {})
        print(
            f"📬 Full response for conversation: {json.dumps(response_data, indent=2)}"
        )
        print(f"📬 Received command type for conversation: {command.get('type')}")

        if command.get("type") == "StreamingMessageCommand":
            stream_id = command.get("stream_id")
            agent_name = command.get("agent_name")
            print(f"🎬 Got streaming command!")
            print(f"   - Stream ID: {stream_id}")
            print(f"   - Agent: {agent_name}")

            # Test the streaming
            print(f"\n🌡️  Testing streaming for {agent_name}...")
            test_streaming(stream_id, game_id)

        elif command.get("type") == "MessageDelayCommand":
            print(f"💬 Got non-streaming message: {command.get('message', '')}")

            # This is the initial greeting. Send a message to trigger streaming response
            print(
                "\n📤 Sending test message to trigger Marshal Flint's streaming response..."
            )
            response_data = send_message(game_id, "Tell me about what happened.")

            if response_data:
                command = response_data.get("response", {})
                print(
                    f"📬 Full response for streaming: {json.dumps(response_data, indent=2)}"
                )
                print(f"📬 Received command type for streaming: {command.get('type')}")

                if command.get("type") == "StreamingMessageCommand":
                    stream_id = command.get("stream_id")
                    agent_name = command.get("agent_name")
                    print(f"🎬 Got streaming command!")
                    print(f"   - Stream ID: {stream_id}")
                    print(f"   - Agent: {agent_name}")

                    # Test the streaming
                    print(f"\n🌡️  Testing streaming for {agent_name}...")
                    test_streaming(stream_id, game_id)

                elif command.get("type") == "MessageDelayCommand":
                    print(
                        f"💬 Still got non-streaming message: {command.get('message', '')}"
                    )
                elif command.get("type") == "MessageCommand":
                    print(f"💬 Received message command: {command.get('message', '')}")
                    print("📤 Message command received - this is asking for user input")
                    print("   Sending response to trigger streaming...")

                    # Send a response to trigger streaming
                    response_data = send_message(game_id, "Tell me about what happened.")
                    if response_data:
                        command = response_data.get("response", {})
                        print(f"📬 Full response after sending message: {json.dumps(response_data, indent=2)}")
                        print(f"📬 Received command type after sending message: {command.get('type')}")

                        if command.get("type") == "StreamingMessageCommand":
                            stream_id = command.get("stream_id")
                            agent_name = command.get("agent_name")
                            print(f"🎬 Got streaming command!")
                            print(f"   - Stream ID: {stream_id}")
                            print(f"   - Agent: {agent_name}")

                            # Test the streaming
                            print(f"\n🌡️  Testing streaming for {agent_name}...")
                            test_streaming(stream_id, game_id)

                        elif command.get("type") == "MessageDelayCommand":
                            print(f"💬 Still got non-streaming message: {command.get('message', '')}")

                        else:
                            print(f"❓ Unknown command type: {command.get('type')}")
                else:
                    print(f"❓ Unknown command type: {command.get('type')}")

        else:
            print(f"❓ Unknown command type: {command.get('type')}")

    print("\n🎯 Test completed!")


if __name__ == "__main__":
    main()
