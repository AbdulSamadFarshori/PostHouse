from langchain_community.embeddings import HuggingFaceEmbeddings

class EmbeddingModel:
    def __init__(self):
        pass
        
    def model(self):
        EMBEDDING_MODEL = HuggingFaceEmbeddings(
                                model_name="sentence-transformers/all-MiniLM-L6-v2",
                                encode_kwargs={"normalize_embeddings": True}
                                )
        return EMBEDDING_MODEL