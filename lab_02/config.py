import os                                            
from pathlib import Path
from dotenv import load_dotenv

# .env с токенами
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# подтягиваем эти токены для доступа к апишкам
API_KEY = os.getenv("HF_TOKEN")  
BOT_KEY = os.getenv("TELEGRAM_TOKEN")

# настройки моделей
MODELS = {
    "gpt": {
        "model_name": "openai/gpt-oss-20b:groq"
    },
    "llama": {
        "model_name": "IlyaGusev/saiga_llama3_8b:featherless-ai"
    }
}