import json
import requests
import time
from config import MOZ_API_KEY

class SEOAnalysisEngine:
    """
    SEOAnalysisEngine interfaces with the Moz Link API to fetch backlink data
    for a given target URL. It retrieves external, nofollow backlinks limited to 30 results.
    """

    def __init__(self, url: str):
        """
        Initialize the SEO analysis engine.

        Args:
            url (str): The target URL or domain for which to retrieve backlinks.
        """
        self.target = url
        self.backlinks_endpoint_url = "https://lsapi.seomoz.com/v2/links"
        self.domain_authority_endpoint = "https://lsapi.seomoz.com/v2/url_metrics"
        self.top_page_endpoint = "https://lsapi.seomoz.com/v2/top_pages"
        self.api_token = MOZ_API_KEY
        self.headers = {
            "x-moz-token": self.api_token,
            "Content-Type": "application/json",
        }

        self.data_template = {"jsonrpc":"2.0",
                              "id":"450d067d-b688-4140-81a0-de8836501209",
                              "method":"data.site.metrics.brand.authority.fetch",
                              "params":{
                                  "data":
                                  {"site_query":
                                        {"query":self.target,
                                         "scope":"domain"
                                         }
                                }}
                            }
        self._pages = []

    def _fetch_backlink_data(self, retries: int = 3, delay: int = 2) -> dict:
        """
        Internal method to perform a POST request to the Moz backlink API with retry logic.
        Args:
            retries (int): Number of times to retry the request on failure.
            delay (int): Delay in seconds between retries (increases linearly).

        Returns:
            dict: JSON response from the API.
        Raises:
            Exception: If all retries fail or the response is invalid.
        """
        request_body = {
            "target": self.target,
            "target_scope": "root_domain",
            "source_scope": "root_domain",
            "filter": "external+nofollow",
            "limit": 10
        }

        attempt = 0
        while attempt < retries:
            try:
                response = requests.post(
                    self.backlinks_endpoint_url,
                    headers=self.headers,
                    json=request_body,
                    timeout=10
                )
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                attempt += 1
                print(f"[Attempt {attempt}] Request failed: {e}")
                if attempt < retries:
                    time.sleep(delay * attempt)
                else:
                    raise Exception(f"Failed to fetch backlinks after {retries} attempts.") from e

    def get_backlinks(self):
        """
        Retrieve external, nofollow backlinks pointing to the target URL's root domain.
        Populates the internal _pages list with source page URLs.
        """
        try:
            data = self._fetch_backlink_data()
            results = data.get("results", [])
            for item in results:
                source = item.get("source", {})
                page = source.get("page")
                if page:
                    self._pages.append(page)
            return self._pages
        except Exception as e:
            print(f"Error retrieving backlinks: {e}")

    def _get_url_metrics(self):        
        payload = {
            "targets": [self.target]
        }
        response = requests.post(self.domain_authority_endpoint, json=payload, headers=self.headers)
        return response.json()
    
    def get_url_metrics(self):
        DA = None
        data = self._get_url_metrics()
        results = data.get('results', [])
        if results:
            dicts = results[0]
            if dicts.get('domain_authority', None):
                DA = dicts.get('domain_authority')            
        return DA
    
    def _get_ba_metrics(self):
        response = requests.post("https://api.moz.com/jsonrpc", headers=self.headers, data=json.dumps(self.data_template))
        print(response.json())
        return response.json()
    
    def get_ba_metrics(self):
        BA = None
        data = self._get_ba_metrics()
        results = data.get("result", {})
        sm = results.get("site_metrics", {})
        if sm.get('brand_authority_score', None):
            BA = sm.get('brand_authority_score', None)
        return BA

    def _get_top_page(self):
        payload = {
                    "target": self.target,
                    "scope": "root_domain",
                    "limit": 4}

        response = requests.post(
                    self.top_page_endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=10
                )
        return response.json()

    def get_top_page(self):
        top_url = []
        data = self._get_top_page()
        results = data.get('results', [])
        for page in results:
            top_url.append(page['page'])
        return top_url
    

class KeywordMetrice:

    def __init__(self):
        self.api_token = MOZ_API_KEY 
        self.headers = {
            "x-moz-token": self.api_token,
            "Content-Type": "application/json",
        }
        
    def _metrice(self, data):
        response = requests.post("https://api.moz.com/jsonrpc", headers=self.headers, data=json.dumps(data))
        return response.json()
    
    def metrice(self, keyword):
        data = {
                    "jsonrpc": "2.0",
                    "id": "b33f5210-7e43-4d47-8f6b-8e7749f79691",
                    "method": "data.keyword.metrics.fetch",
                    "params": {
                        "data": {
                            "serp_query": {
                                "keyword": keyword,
                                "locale": "en-US",
                                "device": "desktop",
                                "engine": "google"
                            }
                        }
                    }
                }
        response = self._metrice(data)
        return response
    

class WebsiteKeywordsList:
    
    def __init__(self, scope):
        self.scope = scope
        self.api_token = MOZ_API_KEY 
        self.headers = {
            "x-moz-token": self.api_token,
            "Content-Type": "application/json",
        }

    def _get_keywords(self, data):
        response = requests.post("https://api.moz.com/jsonrpc", headers=self.headers, data=json.dumps(data))
        return response.json()
    
    def get_keywords(self, url):
        data = {
                "jsonrpc": "2.0",
                "id": "e7c90221-5f39-42cf-9234-23b6b3065cbe",
                "method": "data.site.ranking-keyword.list",
                "params": {
                    "data": {
                        "target_query": {
                            "query": url,
                            "scope": self.scope,
                            "locale": "en-US"
                        },
                    "page":
                        {"n":0,"limit":50},
                    }
                }
            }
        res = self._get_keywords(data)
        return res

class KeywordsSuggestion:

    def __init__(self):
        self.api_token = MOZ_API_KEY 
        self.headers = {
            "x-moz-token": self.api_token,
            "Content-Type": "application/json",
        }

    def _get_keywords(self, data):
        response = requests.post("https://api.moz.com/jsonrpc", headers=self.headers, data=json.dumps(data))
        return response.json()
    
    def get_keywords(self, keywords):
        data = {
                "jsonrpc": "2.0",
                "id": "0b661f85-d2a6-49b3-95bd-6ed598ebb501",
                "method": "data.keyword.suggestions.list",
                "params": {
                    "data": {
                        "serp_query": {
                            "keyword": keywords,
                            "locale": "en-US",
                            "device": "desktop",
                            "engine": "google"
                        },
                    "page":
                        {
                            "n":0,
                            "limit":10
                        },
                    }
                }
            }
        res = self._get_keywords(data)
        return res


