import os
from io import BytesIO

from slack_bolt import App


def image_bytes_to_buffer(image_bytes: bytes) -> BytesIO:
    image_buffer = BytesIO(image_bytes)
    return image_buffer


def send_monthly_pr_table(table_bytes: BytesIO) -> None:

    app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

    app.client.files_upload(
        title="Monthly PR Report",
        file=table_bytes,
        channels=os.environ.get("SLACK_CHANNEL"),
        initial_comment="Monthly PR update! Congrats to those who contributed.",
    )
