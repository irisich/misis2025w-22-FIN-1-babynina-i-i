import os
from pathlib import Path
import json
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

BASE_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = BASE_DIR / "data"
STATIC_DIR: Path = BASE_DIR / "static"

BOT_KEY: str = os.getenv("BOT_KEY", "")

MESSAGES_PATH: Path = STATIC_DIR / "message.json"

CF_K_NEIGHBORS: int = 50

def json_loader() -> Dict[str, Any]:
    """Загружает JSON со всеми строковыми сообщениями для бота

    Возвращает:
        dict: Словарь сообщений
    """
    with open(MESSAGES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


MESSAGES: Dict[str, Any] = json_loader()