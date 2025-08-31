import os
from dotenv import load_dotenv, dotenv_values
import logging

# env_path = './ENV/.env'
load_dotenv()


OPENAI_API_KEY = os.getenv('OpenAI')
logging.info(f"[INFO] OpenAi  - {OPENAI_API_KEY}")
MOZ_API_KEY = os.getenv('MozApi')
SAERCH_API_KEY = os.getenv('TavilyApi')

logging.info(f"[INFO] MOZ API KEY - {MOZ_API_KEY}")

config = dotenv_values()

for key, value in config.items():
    logging.info(f"[secret] - {key}: {value}")


