# Twilio WhatsApp Chatbot

This is a simple WhatsApp chatbot built using Twilio and Flask. The chatbot can respond to basic messages and can be extended with more complex functionality.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your environment variables:
   - Copy the `.env.example` file to `.env`
   - Fill in your Twilio credentials:
     - `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
     - `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
     - `TWILIO_PHONE_NUMBER`: Your Twilio WhatsApp number

3. Run the Flask application:
```bash
python app.py
```

4. Configure your Twilio webhook:
   - Go to your Twilio Console
   - Navigate to WhatsApp > Sandbox Settings
   - Set the webhook URL to your server's URL + `/webhook`
   - Make sure to use HTTPS if deploying to production

## Features

The chatbot currently supports the following commands:
- `hello` or `hi`: Get a greeting
- `help`: See available commands
- `bye` or `goodbye`: End the conversation

## Extending the Chatbot

To add more functionality:
1. Modify the `process_message()` function in `app.py`
2. Add new conditions and responses
3. You can also integrate with external APIs or databases for more complex interactions

## Security Notes

- Never commit your `.env` file to version control
- Always use HTTPS in production
- Keep your Twilio credentials secure 