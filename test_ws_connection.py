import asyncio
import websockets
import json

# Your REST API key (might also be the WebSocket key)
API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJ1dWlkIjoibjFhMWIxQGdtYWlsLmNvbSIsInBsYW4iOiJwcm8iLCJuZXdzZmVlZF9lbmFibGVkIjp0cnVlLCJ3ZWJzb2NrZXRfc3ltYm9scyI6Miwid2Vic29ja2V0X2Nvbm5lY3Rpb25zIjoxfQ.1plJVdP20wrCTL5-HrKH8pEqnWnbJdZqnB9CILG5VCc"

WS_URL = "wss://realtime.insightsentry.com/live"

async def test_websocket():
    print(f"Connecting to {WS_URL}...")

    try:
        async with websockets.connect(WS_URL) as websocket:
            print("[OK] Connected successfully!")

            # Send subscription message
            subscription = {
                "api_key": API_KEY,
                "subscriptions": [
                    {
                        "code": "CME_MINI:MNQ1!",
                        "type": "series",
                        "bar_type": "minute",
                        "bar_interval": 1
                    }
                ]
            }

            print(f"Sending subscription for CME_MINI:MNQ1!...")
            await websocket.send(json.dumps(subscription))
            print("[OK] Subscription sent!")

            # Wait for responses
            print("\nWaiting for data (30 seconds)...")
            try:
                message_count = 0
                start_time = asyncio.get_event_loop().time()

                while asyncio.get_event_loop().time() - start_time < 30:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        message_count += 1

                        if response == "pong":
                            continue

                        data = json.loads(response)
                        print(f"\n--- Message {message_count} ---")
                        print(json.dumps(data, indent=2))

                        # Check if we got actual series data
                        if "series" in data and len(data["series"]) > 0:
                            print("\n[SUCCESS] Received MNQ1! data!")
                            break

                    except asyncio.TimeoutError:
                        elapsed = asyncio.get_event_loop().time() - start_time
                        print(f"Still waiting... ({elapsed:.1f}s elapsed)")
                        continue

                print(f"\nTotal messages received: {message_count}")

            except Exception as e:
                print(f"Error receiving data: {e}")

    except websockets.exceptions.ConnectionClosed as e:
        print(f"[ERROR] Connection closed: {e}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
