from langchain_ollama import ChatOllama, OllamaLLM

class QwenModel:

    name="qwen"

    def __init__(self, temperature=0.2, reasoning=False):
        self.temperature = temperature
        self.reasoning = reasoning

    def model(self):
        llm = OllamaLLM(
                        model='qwen3:latest', 
                        temperature=self.temperature,  
                        reasoning=self.reasoning
                        )
        return llm
    
