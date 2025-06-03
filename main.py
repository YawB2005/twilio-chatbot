from twilio.rest import Client
from fastapi import FastAPI, Form
from anthropic import Anthropic
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
client = Client(account_sid, auth_token)

ai_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

app = FastAPI()

@app.post("/webhook")
async def auto_repl(From: str = Form(...), Body: str = Form(...)):
    try:
        prompt = f"Reply to this message: {Body} in a helpful and friendly way"
        
        # Fixed: Added max_tokens parameter
        response = ai_client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Updated to latest model
            max_tokens=1000, 
            system="You are an 18 year old gen z medical student at KNUST called Adwoa. You respond in gen z slang", # This was missing!
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        reply = response.content[0].text

        logger.info(f"Replied to {From}: {reply}")

        # Send WhatsApp message
        message = client.messages.create(
            from_=twilio_phone_number,
            to=From,  # Reply to sender instead of hardcoded number
            body=reply
        )

        print(f"✅ Replied to {From}: {reply}")
        return {"status": "sent", "sid": message.sid}
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return {"status": "error", "message": str(e)}

# Optional: Add a health check endpoint
@app.get("/")
async def health_check():
    return {"status": "WhatsApp bot is running!"}