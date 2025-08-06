#!/usr/bin/env python3

import asyncio, websockets, ssl, json, os

# === Configuration ===
TV_IP = "IP_HERE"
COMMAND = "KEY_POWER"  # Example: KEY_VOLUP, KEY_MUTE
TOKEN_FILE = "token.json"
APP_NAME_B64 = "ZHVtbXktcHktcmVtb3Rl"  # base64("dummy-py-remote")

def load_token():
    if os.path.exists(TOKEN_FILE):
        try: return json.load(open(TOKEN_FILE)).get("token")
        except: pass
    return None

def save_token(tok):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"token": tok}, f)
    print("💾 Token saved.")

async def main():
    token = load_token()
    print(f"📦 Token: {token}")
    url = f"wss://{TV_IP}:8002/api/v2/channels/samsung.remote.control?name={APP_NAME_B64}"
    if token: url += f"&token={token}"

    ssl_ctx = ssl._create_unverified_context()
    async with websockets.connect(url, ssl=ssl_ctx) as ws:
        print("💬 Connected.")
        resp = await ws.recv()
        print("👋 TV:", repr(resp))

        try:
            new_tok = json.loads(resp).get("data", {}).get("token")
            if new_tok and new_tok != token:
                save_token(new_tok)
        except: pass

        await asyncio.sleep(1)

        payload = {
            "method": "ms.remote.control",
            "params": {
                "Cmd": "Click", "DataOfCmd": COMMAND,
                "Option": "false", "TypeOfRemote": "SendRemoteKey"
            }
        }

        print(f"🔌 Sending: {COMMAND}")
        await ws.send(json.dumps(payload))

        try:
            await asyncio.wait_for(ws.recv(), timeout=2)
        except:
            print("✅ Command sent. Exiting...")
            await asyncio.sleep(0.1)

if __name__ == "__main__":
    try: asyncio.run(main())
    except Exception as e: print("❌ Error:", e)
