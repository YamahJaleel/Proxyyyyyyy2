from fastapi import FastAPI, Request
import requests
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI()

# System prompt to keep the model on track
SYSTEM_PROMPT = {
    "role": "user",
    "parts": [{
        "text": "You are a helpful AI assistant. Answer clearly and concisely. "
                "Give practical responses. Do not write long stories unless I explicitly ask for it."
    }]
}

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()

    # If frontend sends full conversation history
    if "contents" in body:
        contents = [SYSTEM_PROMPT] + body["contents"]
    else:  # If only one message is sent
        user_message = body.get("message", "")
        contents = [SYSTEM_PROMPT, {"role": "user", "parts": [{"text": user_message}]}]

    payload = {"contents": contents}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(f"{API_URL}?key={API_KEY}", json=payload, headers=headers)
        data = response.json()
        print("Gemini API response:", data)  # Debugging log

        # Try extracting model reply
        reply = data["candidates"][0]["content"]["parts"][0]["text"]
        return {"reply": reply}

    except Exception as e:
        # If Gemini sends an error, return it
        error_message = data.get("error", {}).get("message", str(e))
        return {"reply": f"Error: {error_message}"}
