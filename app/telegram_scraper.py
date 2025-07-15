# app/telegram_scraper.py

import os
import json
import logging
from datetime import datetime
from telethon import TelegramClient, errors
from dotenv import load_dotenv

# load environment variables
load_dotenv()
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")

# configure logging
logging.basicConfig(level=logging.INFO, filename="scraper.log",
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


# list your channels here
CHANNELS = [
    "https://t.me/CheMed123",
    "https://t.me/lobelia4cosmetics",
    "https://t.me/tikvahpharma",
    "https://t.me/chemed"
]

# Helper to extract a safe channel name for directory use
import re
def get_safe_channel_name(channel_ref):
    # Extract username from t.me URL, else use as-is
    match = re.match(r"https?://t\.me/([\w_]+)", channel_ref)
    if match:
        return match.group(1)
    # Remove any unsafe characters if not a URL
    return re.sub(r'[^\w\-_]', '_', channel_ref)


async def scrape_channel(client, channel_name):
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_name = get_safe_channel_name(channel_name)
    base_dir = f"data/raw/telegram_messages/{date_str}/{safe_name}"
    img_dir = f"data/raw/telegram_images/{date_str}/{safe_name}/images"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    try:
        channel = await client.get_entity(channel_name)
    except errors.UsernameNotOccupiedError:
        log.error(f"Channel not found: {channel_name}")
        return

    all_msgs = []
    async for msg in client.iter_messages(channel):
        rec = {
            "id": msg.id,
            "date": msg.date.isoformat(),
            "text": msg.text,
            "sender_id": msg.sender_id,
            "media": None
        }
        if msg.media:
            try:
                file_path = await client.download_media(msg, img_dir)
                rec["media"] = {
                    "type": msg.media.__class__.__name__,
                    "file_path": file_path
                }
            except Exception as e:
                log.error(f"Failed media download in {channel_name} msg {msg.id}: {e}")
        all_msgs.append(rec)

    # save JSON
    file_path = os.path.join(base_dir, "messages.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(all_msgs, f, ensure_ascii=False, indent=2)

    log.info(f"Scraped {len(all_msgs)} messages + media from {channel_name}")

async def main():
    client = TelegramClient("scraper_session", API_ID, API_HASH)
    await client.start()

    for ch in CHANNELS:
        await scrape_channel(client, ch)

    await client.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
