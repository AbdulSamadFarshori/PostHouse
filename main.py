from src.utilies.client_data_collector import CollectClientWebsiteData
from src.utilies.chatgpt import ChatGpt
from src.utilies.qwen_model import QwenModel
from src.utilies.embedding_model import EmbeddingModel
from src.utilies.factory import ModelFactory
from src.agent.seo_analyst_agent import CompetitorFinderAgent


ModelFactory.register("chatgpt", ChatGpt)
ModelFactory.register("qwen", QwenModel)
ModelFactory.register("embedding", EmbeddingModel)

agent= CompetitorFinderAgent()
graph = agent.graph()


