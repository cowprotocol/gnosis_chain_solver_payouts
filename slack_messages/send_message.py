import os
import slack_sdk
from dotenv import load_dotenv
from slack_sdk import WebClient

load_dotenv()


class SlackClient:
    def __init__(self):
        self.channel = os.environ['SLACK_CHANNEL_ID'] 
        self.client = WebClient(token=os.environ['SLACK_OAUTH'])

    def send_message(self, message: str) -> dict:
        result = self.client.chat_postMessage(
                channel=self.channel,
                text=message,
        )
        return result

    def send_csv(self, message: str) -> dict:
        file = self.client.files_upload_v2(
            title="Solver Rewards",
            filename="solver_rewards.csv",
            content=message,
        )
        file_url = file.get("file").get("permalink")
        new_message = self.client.chat_postMessage(
            channel=self.channel,
            text=f"File: {file_url}",
        )
