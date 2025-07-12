from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY

class ChatGpt:

    def __init__(self):
        self.api_key = OPENAI_API_KEY

    def model(self):
        llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=self.api_key)
        return llm    