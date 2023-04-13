import os
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_USER_TOKEN = os.environ["SLACK_USER_TOKEN"]
client = WebClient(token=SLACK_USER_TOKEN)
BOT_USER_ID = ""

def send_message(channel, text):
    try:
        return client.chat_postMessage(channel=channel, text=text)
    except SlackApiError as e:
        print(f"Error sending message: {e}")

def fetch_messages(channel, last_message_timestamp):
    response = client.conversations_history(channel=channel, oldest=last_message_timestamp)
    return [msg['text'] for msg in response['messages'] if msg['user'] == BOT_USER_ID]

def get_new_messages(channel, last_message_timestamp):
    while True:
        messages = fetch_messages(channel, last_message_timestamp)
        if messages and not messages[-1].endswith('Typing…_'):
            return messages[-1]
        time.sleep(5)

def find_direct_message_channel(user_id):
    try:
        response = client.conversations_open(users=user_id)
        return response['channel']['id']
    except SlackApiError as e:
        print(f"Error opening DM channel: {e}")

def main():
    dm_channel_id = find_direct_message_channel(BOT_USER_ID)
    if not dm_channel_id:
        print("Could not find DM channel with the bot.")
        return

    last_message_timestamp = None

    while True:
        prompt = input("\n\n--------------------------------\nUSER: ")
        response = send_message(dm_channel_id, prompt)
        if response:
            last_message_timestamp = response['ts']
        new_message = get_new_messages(dm_channel_id, last_message_timestamp)
        print("\n\n---------------------------------\n" + f"Claude: {new_message}")

if __name__ == "__main__":
    main()
