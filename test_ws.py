import asyncio
import websockets
import json
import requests

API_KEY = "sk_515cd33aa27c368a98b71df6df9624249ee161e5a8edce2c"
AGENT_ID = "agent_6101kkdmyfwmf0sap11vr8jxktbk"

async def test_ws():
    r = requests.get(
        f"https://api.elevenlabs.io/v1/convai/conversation/get-signed-url?agent_id={AGENT_ID}",
        headers={"xi-api-key": API_KEY}
    )
    url = r.json()["signed_url"]
    
    async with websockets.connect(url) as ws:
        try:
            # Send initial message to provoke speech
            import base64
            dummy_pcm = b'\x00' * 4096
            b64 = base64.b64encode(dummy_pcm).decode('utf-8')
            await ws.send(json.dumps({"user_audio_chunk": b64}))
            
            for _ in range(10):  # loop to get multiple messages
                raw = await asyncio.wait_for(ws.recv(), timeout=10.0)
                msg = json.loads(raw)
                if msg["type"] == "audio":
                    print("AUDIO EVENT:", msg.keys())
                    if "audio_event" in msg:
                        print("audio_event inner:", msg["audio_event"].keys())
                else:
                    print("EVENT:", msg["type"])
                    if msg["type"] == "ping":
                        ping_id = msg.get("ping_event", {}).get("event_id")
                        if ping_id:
                            await ws.send(json.dumps({"type": "pong", "event_id": ping_id}))
        except Exception as e:
            print("Finished:", e)

asyncio.run(test_ws())
