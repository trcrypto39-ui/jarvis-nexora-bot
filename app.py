import os
from flask import Flask, request
from openai import OpenAI
import requests

app = Flask(__name__)

POE_API_KEY = os.getenv("POE_API_KEY")
BOT_NAME = os.getenv("BOT_NAME", "Jarvis_Nexora")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "nexora123")

client = OpenAI(
    api_key=POE_API_KEY,
    base_url="https://api.poe.com/v1"
)

@app.route("/")
def home():
    return "Jarvis_Nexora is running!"

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        entry = data["entry"][0]["changes"][0]["value"]
        if "messages" not in entry:
            return "OK", 200
        msg_data = entry["messages"][0]
        from_number = msg_data["from"]
        msg_text = msg_data["text"]["body"]

        completion = client.chat.completions.create(
            model=BOT_NAME,
            messages=[{"role": "user", "content": msg_text}]
        )
        reply = completion.choices[0].message.content

        url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
        payload = {"messaging_product": "whatsapp","to": from_number,"type": "text","text": {"body": reply}}
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f"Error: {e}")
    return "OK", 200
