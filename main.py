from twilio.rest import Client
from fastapi import FastAPI,Form
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
client = Client(account_sid, auth_token)

ai_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

app = FastAPI()

@app.post("/webhook")
async def auto_repl(From: str = Form(...), Body: str = Form(...)):
    prompt = f"Reply to this message: {Body} in a helpful and friendly way"
    response = ai_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    reply = response.content[0].text

    message = client.messages.create(
        from_=twilio_phone_number,
        to='whatsapp:+233504562522',
        body=reply
    )

    print(f"✅ Replied to {From}: {reply}")
    # return {"status": "sent", "sid": message.sid}
    return message