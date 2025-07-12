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
        temp = []
        data = self._get_url_metrics()
        results = data.get('results', [])
        if results:
            for dicts in results:
                for k, v in dicts.items():
                    temp.append(f"{k} : {v}")
        metric = "\n".join(temp)
        return metric

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