import os
from typing import List, Annotated, Literal, Sequence, Dict
from ddg import Duckduckgo
from pydantic import BaseModel, Field
from tavily import TavilyClient


class SearchEngine(BaseModel):
    query: str = Field(description="search query for get similar results from search engine")


class SearchEngineResult(BaseModel):
    result: List[str] = Field(description="list contains all valid urls")


class DuckDuckGoEngine:
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
        try:
            self.get_results()
            urls = self.get_urls()
            if validate:
                urls = [url for url in urls if self.validate_url(url)]
            return urls
        except Exception as e:
            print(f"[Failed] : {e}")


class TivalyEngine:

    def __init__(self):
        self.tavily_client = TavilyClient(api_key="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")

    
class TavilyWebSearchEngine(TivalyEngine):

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
        super().__init__()
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
        self._content: List[str] = []

    def get_results(self) -> List[SearchEngineResult]:
        """
        Fetches search results from tavily.
        """
        try:
            self._results = self.tavily_client.search(self.query, search_depth=self.search_depth,
                                                topic=self.topic, days=self.days,
                                                max_result=self.max_results, include_domains=self.include_domains, 
                                                exclude_domains=self.exclude_domains, include_answer=self.include_answer,
                                                include_raw_content=self.include_raw_content, include_images=self.include_images, 
                                                timeout=self.timeout).get('results', [])
            return self._results
        except Exception as e:
            print(f"[Failed] Scraped: {e}")

    def invoke(self):
        """
        Invoke the function which fetch the all contents.
        """
        try:
            self.get_results()
            self._content = [page.get("content", "") for page in self._results]
            return self._content
        except Exception as e:
            print(f"[Failed] Scraped: {e}")


class TivalyExtractEngine(TivalyEngine):
    """
    Engine to extract raw textual content (and optionally images) from a list of URLs
    using the Tavily extraction API.
    """

    def __init__(self, urls: List[str] = [], include_images: bool=False):

        """
        Initialize the extract engine.

        Args:
            urls (List[str]): A list of URLs to extract content from.
            include_images (bool): Whether to include image extraction in the results.
        """
        super().__init__()
        self.urls = urls
        self.include_images = include_images
        self._results: List[SearchEngineResult] = []
        self._content: List[str] = []

    def get_results(self):

        """
        Call the Tavily extract API and store the results.

        Returns:
            List[SearchEngineResult]: A list of extracted search engine results.
        """
        try:
            self._results = self.tavily_client.extract(urls=self.urls, include_images=self.include_images).get("results", [])
            return  self._results
        except Exception as e:
            print(f"[Failed] Scraped: {e}")

    def invoke(self):
        
        """
        Invoke the extraction process and extract raw content from the results.

        Returns:
            List[SearchEngineResult]: The full list of results including raw content.
        """
        try:
            self.get_results()
            self._content = [page.get("raw_content", "") for page in self._results]
            return self._results
        except Exception as e:
            print(f"[Failed] Scraped: {e}")

class TivalyCrawlerEngine(TivalyEngine):
    
    """
    Engine to crawl web pages starting from a given URL and extract content
    with control over depth, format, domains, and instructions.
    """

    def __init__(self, start_url: str, 
                max_depth: int = 1, 
                limit: int = 10,
                select_paths: str = None,
                select_domains: str = None,
                exclude_paths: str = None,
                exclude_domains: str = None,
                allow_external: bool = False,
                format = "markdown",
                extract_depth = "basic",
                instruction: str = None):
        
        """
        Initialize the crawler engine.

        Args:
            start_url (str): The URL from which to start crawling.
            max_depth (int): The maximum crawl depth.
            limit (int): Maximum number of pages to crawl.
            select_paths (str): Specific URL paths to include.
            select_domains (str): Specific domains to include.
            exclude_paths (str): URL paths to exclude from crawling.
            exclude_domains (str): Domains to exclude from crawling.
            allow_external (bool): Whether to allow external links outside base domain.
            format (str): Format of extracted content ('markdown', 'html', etc.).
            extract_depth (str): Extraction detail level ('basic', 'detailed', etc.).
            instruction (str): Custom instruction to guide content extraction.
        """
        super().__init__()
        self.url = start_url
        self.max_depth = max_depth
        self.limit = limit
        self.format = format
        self.extract_depth = extract_depth
        self.categories = ['Blog', 'About', 'Pricing', 'Community', 'Developers', 'Contact', 'Services', 'Products']
        self.instruction = instruction
        self._results = []
        self._content = []


    def get_results(self):

        """
        Call the Tavily crawl API and retrieve results based on crawl parameters.

        Returns:
            List[dict]: A list of result dictionaries containing extracted page data.
        """
        try:
            self._results = self.tavily_client.crawl(
                                            url=self.url,
                                            max_depth=self.max_depth,
                                            limit=self.limit,
                                            format = self.format,
                                            extract_depth= self.extract_depth,
                                            instructions=self.instruction
                                            ).get("results", [])
            return self._results
        
        except Exception as e:
            print(f"[Failed] Scraped: {e}")
    
    def invoke(self):

        """
        Invoke the crawling process and extract raw content from each page.

        Returns:
            List[str]: A list of raw content strings from the crawled pages.
        """
        try:
            self.get_results()
            self._content = [page.get("raw_content", "") for page in self._results]
            return self._content
        except Exception as e:
            print(f"[Failed] Scraped: {e}")


if __name__ == "__main__":
    
    queries = ["top solar and green energy companies in uk", "top afghan resturants in uk"]


    def test():
        for query in queries:
            engine = SearchEngine(query=query)
            urls = engine.run()
            print(urls)
            print(f"{'*'*50}")
    test()