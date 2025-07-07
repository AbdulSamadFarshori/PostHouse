import os
from typing import List, Annotated, Literal, Sequence
from ddg import Duckduckgo
from pydantic import BaseModel, Field
from tavily import TavilyClient
from PostHouse.src.scehma.search import *


class SearchEngine(BaseModel):
    query: str = Field(description="search query for get similar results from search engine")


class SearchEngineResult(BaseModel):
    result: List[str] = Field(description="list contains all valid urls")


class SearchEngine:
    """
    Search engine interface using DuckDuckGo API.
    """

    def __init__(self, query: str):
        """
        Initializes the search engine with a query.
        """
        self.query: str = query
        self.ddg = Duckduckgo()
        self._results: List[SearchEngineResult] = []

    def get_results(self) -> List[SearchEngineResult]:
        """
        Fetches search results from DuckDuckGo.
        """
        self._results = self.ddg.search(self.query).get('data', [])
        return self._results

    def get_urls(self) -> List[str]:
        """
        Extracts URLs from the fetched results.
        """
        return [result.get('url') for result in self._results if result.get('url')]

    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Placeholder for URL validation logic.
        """
        return True

    def run(self, validate: bool = False) -> List[str]:
        """
        Runs the search and returns a list of URLs.

        :param validate: whether to filter URLs through validation.
        :return: list of URLs.
        """
        self.get_results()
        urls = self.get_urls()
        if validate:
            urls = [url for url in urls if self.validate_url(url)]
        return urls


class TivalyEngine:

    def __init__(self):
        self.tavily_client = TavilyClient(api_key="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")

    
class WebSearchEngine(TivalyEngine):

    """
    Search engine interface using Tivaly API.
    """
    def __init__(self, 
                 query: SearchEngine,
                 search_depth: Literal['basic', 'advanced'] = "basic",     
                 topic: Literal['general', 'news', 'finance'] = "general", 
                 days: int = 7,
                 max_results: int = 5, 
                 include_domains: Sequence[str] = None,
                 exclude_domains: Sequence[str] = None,
                 include_answer: bool | Literal['basic', 'advanced'] = False,
                 include_raw_content: bool = False, 
                 include_images: bool = False, 
                 timeout: int = 60):
        
        """
        Initializes the web search engine with a query and params.
        """
        super.__init__()
        self.query = query
        self._results: List[SearchEngineResult] = []
        self.search_depth = search_depth
        self.topic = topic
        self.days = days
        self.max_results = max_results
        self.include_domains = include_domains
        self.exclude_domains = exclude_domains
        self.include_answer = include_answer
        self.include_raw_content = include_raw_content
        self.include_images = include_images
        self.timeout = timeout
        self.content: List[str] = []

    def get_results(self) -> List[SearchEngineResult]:
        """
        Fetches search results from tavily.
        """
        self._results = self.tavily_client.search(self.query, search_depth=self.search_depth,
                                             topic=self.topic, days=self.days,
                                             max_result=self.max_results, include_domains=self.include_domains, 
                                             exclude_domains=self.exclude_domains, include_answer=self.include_answer,
                                             include_raw_content=self.include_raw_content, include_images=self.include_images, 
                                             timeout=self.timeout).get('results', [])
        return self._results




if __name__ == "__main__":
    
    queries = ["top solar and green energy companies in uk", "top afghan resturants in uk"]


    def test():
        for query in queries:
            engine = SearchEngine(query=query)
            urls = engine.run()
            print(urls)
            print(f"{'*'*50}")
    test()