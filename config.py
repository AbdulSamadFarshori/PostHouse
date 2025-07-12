import os
from dotenv import load_dotenv

env_path = './.env'
load_dotenv(dotenv_path=env_path)


OPENAI_API_KEY = os.getenv('OpenAI')
MOZ_API_KEY = os.getenv('MozApi')
SAERCH_API_KEY = os.getenv('TavilyApi')