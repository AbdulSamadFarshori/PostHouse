from langchain_openai import ChatOpenAI


class ChatGpt:

    def __init__(self):
        self.api_key = "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"

    def model(self):
        llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=self.api_key)
        return llm    