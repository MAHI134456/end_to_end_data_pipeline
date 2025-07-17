# telegram_scraper.py

import os, json, asyncio, logging
from datetime import datetime
from telethon import TelegramClient, errors
from dotenv import load_dotenv

# Load credentials
load_dotenv()
API_ID, API_HASH = int(os.getenv("TELEGRAM_API_ID")), os.getenv("TELEGRAM_API_HASH")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# Channels to scrape
CHANNELS = [
    "Chemed",
    "lobelia4cosmetics",
    "tikvahpharma"
    # Add more channels from https://et.tgstat.com/medicine
]

async def scrape_channel(client, name):
    date_str = datetime.now().strftime("%Y-%m-%d")
    msg_path = f"data/raw/telegram_messages/{date_str}/{name}.json"
    img_dir = f"data/raw/telegram_images/{date_str}/{name}"
    os.makedirs(os.path.dirname(msg_path), exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    try:
        ch = await client.get_entity(name)
    except errors.UsernameNotOccupiedError:
        log.error(f"[{name}] Channel not found")
        return

    records = []
    count = 0
    image_count = 0

    async for msg in client.iter_messages(ch, reverse=False):
        rec = msg.to_dict()
        
        media_saved = None
        # Only download images
        if msg.photo:
            try:
                media_saved = await client.download_media(msg, img_dir)
                image_count += 1
            except Exception as e:
                log.error(f"[{name}] Image download failed for msg {msg.id}: {e}")

        rec["media_saved"] = media_saved
        records.append(rec)
        count += 1

    # Write JSON using default=str to handle datetime
    with open(msg_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2, default=str)

    log.info(f"[{date_str}] {name}: scraped {count} msgs, downloaded {image_count} images")

async def main():
    client = TelegramClient("scraper_session", API_ID, API_HASH)
    await client.start()
    for channel in CHANNELS:
        await scrape_channel(client, channel)
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
