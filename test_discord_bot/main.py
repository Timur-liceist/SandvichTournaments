import threading

import requests
from dotenv import load_dotenv

load_dotenv()


GUILD_ID = "404692069701910528"
ROLE_ID = "1436392296676331681"

def _give_role_thread(discord_user_id):
    """Внутренняя функция для потока"""
    url = f"https://discord.com/api/guilds/{GUILD_ID}/members/{discord_user_id}/roles/{ROLE_ID}"
    headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}
    try:
        response = requests.put(url, headers=headers, timeout=5)
        if response.status_code not in [204, 200]:
            print(f"Discord API Error: {response.status_code}")
    except Exception as e:
        print(f"Connection error: {e}")

def give_discord_role_async(discord_user_id):
    """Запускает выдачу роли в фоновом потоке"""
    thread = threading.Thread(target=_give_role_thread, args=(discord_user_id,))
    thread.daemon = True # Поток умрет вместе с основным процессом
    thread.start()
_give_role_thread("875043365815717888")
