from typing import List, Tuple
from src.utilies.factory import ModelFactory
from langchain_community.vectorstores import FAISS


class SimilarKeywords:
    def __init__(self, keywords: List[str], query: str, k: int):

        core = ModelFactory.create('embedding')
        self.emb = core.model() 
        self.keywords = keywords
        self.query = query
        self.k = k
        self.min_sim = 0.35
        self.fetch_k = 40

    def build_store(self) -> FAISS:
        keywords = [k.strip() for k in dict.fromkeys(k.strip().lower() for k in self.keywords)]
        return FAISS.from_texts(texts=keywords, embedding=self.emb)
    
    def similar_keywords(self) -> List[Tuple[str, float]]:
        store = self.build_store()
        docs_scores = store.similarity_search_with_score(self.query, k=self.k)
        out = []
        for doc, dist in docs_scores:
            sim = 1.0 - float(dist) / 2.0
            out.append((doc.page_content, sim))
        out = [i for i in out if i[1] >= self.min_sim]
        return out
    
    def similar_keywords_diverse(self) -> List[str]:
        store = self.build_store()
        docs = store.max_marginal_relevance_search(self.query, k=self.k, fetch_k=self.fetch_k)
        return [d.page_content for d in docs]


if __name__ == "__main__":
    dicts = ["solar", "new", "england", "green", "energy", "panel"]
    sk = SimilarKeywords(keywords=dicts, query='solar energy installation', k=5)
    print("Top similar:")
    print(sk.similar_keywords())
    print("\nDiverse (MMR):")
    print(sk.similar_keywords_diverse())
