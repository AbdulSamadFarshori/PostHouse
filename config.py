import os
from dotenv import load_dotenv
import logging



load_dotenv()

OPENAI_API_KEY = os.getenv('OpenAI')

logging.info(f"[INFO] OpenAi  - {OPENAI_API_KEY}")

env_path = './ENV/.env'


load_dotenv(dotenv_path=env_path)


MOZ_API_KEY = os.getenv('MozApi')
SAERCH_API_KEY = os.getenv('TavilyApi')


logging.info(f"[INFO] MOZ API KEY - {MOZ_API_KEY}")

