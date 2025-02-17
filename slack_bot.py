import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import requests
from typing import Optional

# Load environment variables
load_dotenv(override=True)

# Initialize the Slack app
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Run the Langflow flow
def run_flow(message: str, endpoint: str, output_type: str = "chat", input_type: str = "chat", tweaks: Optional[dict] = None, api_key: Optional[str] = None) -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :return: The JSON response from the flow
    """
    api_url = f"{os.environ["LANGFLOW_BASE_API_URL"]}/api/v1/run/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if api_key:
        headers = {"x-api-key": api_key}
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

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

    # You can tweak the flow by adding a tweaks dictionary
    # e.g {"OpenAI-XXXXX": {"model_name": "gpt-4"}}
    TWEAKS = {
        "ChatInput-yBz3m": {},
        "ChatOutput-zpNTB": {},
        "OpenAIModel-rBhAr": {}
    }

    # Call langflow to get the response
    try:
        response = run_flow(message=message, endpoint=os.environ["LANGFLOW_FLOW_ID"], tweaks=TWEAKS)
        response = response['outputs'][0]['outputs'][0]['outputs']['message']['message']['text']
        print (f"Response from Langflow: {response}")
    
    except requests.exceptions.RequestException as e:
        response = "Sorry, I encountered an error calling Langflow."
        print(f"Error querying Langflow: {e}")

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