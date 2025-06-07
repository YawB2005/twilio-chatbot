import twilio.rest 
from fastapi import FastAPI, Form
from anthropic import Anthropic
from openai import OpenAI
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
client = twilio.rest.Client(account_sid, auth_token)

openai_client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))
supabaseUrl = 'https://ddvvubbwhjtummtwlqtj.supabase.co'
supabaseKey = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabaseUrl, supabaseKey)

ai_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

app = FastAPI()

@app.post("/create-user")
async def create_user(
    name: str = Form("user"),
    age: int = Form(18),
    businessType: str = Form("Retail"),
    snapchatUsername: str = Form("none"),
    about: str = Form("none"),
    school: str = Form("university"),
):
    
    response = openai_client.embeddings.create(
        input=about,
        model="text-embedding-3-small"  # or "text-embedding-3-large"
    )
    embedding = response.data[0].embedding

    response = (
        supabase.table("users")
        .insert({
                "name": name,
                "snapchat": snapchatUsername,
                "age": age,
                "school": school,
                "business_area": businessType,
                "about": embedding,
                })
        .execute()
    )

    return {"status": "success"}

functions = [
    { 
            "type": "function",
            "function": {
                "name": "search",
                "description": "Find a user based on semantic match from the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "User's request like 'I want someone selling cakes at KNUST'"
                        }
                    },
                    "required": ["query"]
            }
            }
            
        }
]


async def search(message):
    print(message)
    embedding_response = openai_client.embeddings.create(
        input=message,
        model="text-embedding-3-small",
    )

    query_embedding = embedding_response.data[0].embedding

    result = supabase.rpc("match_users", {
        "query_embedding": query_embedding,
        "match_threshold": 0.75,
        "match_count": 5
    }).execute()

    person = result.data[0]


    if person:
        prompt = f"""You are an assistant helping users find relevant people from a database, this is to enable them to find people with similar interest 
        based on what they want here {message}. Here’s a match you found:

            Name: {person["name"]}
            School: {person["school"]}
            snapchat handle: {person["snapchat"]}

            Write a short, friendly response that introduces this person naturally.
            Let your message be cool and should some gen z. Don't do too much just cool professional gen z talk
        """
        completion = openai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
        )

        answer = completion.choices[0].message.content

        return answer

    else:
        return "Sorry, I couldn't find anyone matching that."


@app.post("/webhook")
async def auto_repl(From: str = Form(...), Body: str = Form(...)):
    try:
        # prompt = f"Reply to this message: {Body} in a helpful and friendly way"
        
        # # Fixed: Added max_tokens parameter
        # response = ai_client.messages.create(
        #     model="claude-3-5-sonnet-20241022",  # Updated to latest model
        #     max_tokens=1000, 
        #     system="You are an 18 year old gen z medical student at KNUST called Adwoa. You respond in gen z slang", # This was missing!
        #     messages=[
        #         {"role": "user", "content": prompt}
        #     ]
        # )

        # reply = response.content[0].text

        input = [{"role": "user", "content": Body}]


        completion = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=input,
            tools=functions,
            tool_choice="auto"
        )

        response = completion.choices[0].message

        logger.info(f"Replied to {From}: {response}")

        if response.tool_calls:
            arguments = json.loads(response.tool_calls[0].function.arguments)
            result = await search(arguments['query'])
            
            # Return friendly response
            reply = result
        else:
            # Normal friendly chat
            reply = response.content
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
