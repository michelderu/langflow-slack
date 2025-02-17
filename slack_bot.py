import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv(override=True)

# Initialize the Slack app
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Langflow API configuration
LANGFLOW_API_URL = os.environ.get("LANGFLOW_API_URL")

def query_langflow(message: str) -> str:
    """
    Send a query to Langflow and get the response
    """
    try:
        # Endpoint for your specific flow
        url = f"{LANGFLOW_API_URL}"
        
        # Prepare the inputs based on your flow's requirements
        payload = {
            "input_value": message,
            "output_type": "chat",
            "input_type": "chat"
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        print (f"Calling Langflow {url} with message {message}")
        result = response.json()
        result = result['outputs'][0]['outputs'][0]['outputs']['message']['message']['text']
        print (f"Response from Langflow: {result}")
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"Error querying Langflow: {e}")
        return "Sorry, I encountered an error while processing your request."

# Listens to incoming messages that contain "Hello!"
# To learn available listener arguments,
# visit https://tools.slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html
@app.message("Hello!")
def message_hello(event, say):
    print(f"Mentioned in channel: {event}")
    # say() sends a message to the channel where the event was triggered with markdown
    say(
        text=f"Hey there <@{event['user']}>!",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hey there <@{event['user']}>!"
                }
            }
        ]
    )

@app.event("message")
def handle_direct_message(event, say):
    """
    Handle direct messages to the bot
    """
    print(f"Direct message: {event}")

    # Ignore messages from the bot itself
    if "bot_id" in event:
        return
    
    # Extract the message text (remove the bot mention)
    message = event['text']

    # Get response from Langflow
    response = query_langflow(message)

    # Reply to the direct message with markdown enabled
    say(
        text=response,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": response.replace('**', '*')
                }
            }
        ]
    )

def main():
    """
    Main function to start the bot
    """
    try:
        # Start the app in Socket Mode
        handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
        print("⚡️ Bolt app is running!")
        handler.start()
    except Exception as e:
        print(f"Error starting the bot: {e}")

if __name__ == "__main__":
    main()