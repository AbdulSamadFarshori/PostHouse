import sys
import asyncio
import time
from typing import List, Optional, Dict
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


class ScrapingEngine:
    """
    A web scraping engine using Playwright to fetch HTML and BeautifulSoup for parsing.
    """

    def __init__(
        self,
        headless: bool = True,
        urls: Optional[List[str]] = None,
        tag: str = "p",
        max_retries: int = 1,
        scroll_count: int = 3,
    ):
        """
        Initialize the scraping engine.

        :param headless: Run browser in headless mode.
        :param driver_path: Unused in Playwright; kept to match the Selenium signature.
        :param urls: List of URLs to scrape.
        :param max_retries: Number of retries on failure.
        :param scroll_count: Number of scrolls for dynamic content.
        """
        self.headless = headless
        self.urls = urls or []
        self.tag: str = tag
        self.max_retries = max_retries
        self.scroll_count = scroll_count
        self.page_soups: Dict[str, BeautifulSoup] = {}
        self.cleaned_texts: Dict[str, BeautifulSoup] = {}
        self._all_paragraph_text: List[str] = []

        # Keep the same variable name; use it as Chromium launch args.
        self.options: List[str] = []
        self.options.append("--no-sandbox")
        self.options.append("--disable-dev-shm-usage")
        self.options.append("--disable-gpu")
        self.options.append("--window-size=1920,1080")
        if self.headless:
            # Works with modern Chromium; Playwright also honors headless=True.
            self.options.append("--headless=new")

        # Preserve the attribute name for compatibility; Playwright doesn't use WebDriver.
        self.driver = None

    def engine(self, url: str):
        retry = 0
        success = False
        last_exception = None

        while retry < self.max_retries and not success:
            try:
                with sync_playwright() as pw:
                    browser = pw.chromium.launch(headless=self.headless, args=self.options)
                    context = browser.new_context(viewport={"width": 1920, "height": 1080})
                    page = context.new_page()

                    page.goto(url, wait_until="domcontentloaded")
                    # Let network settle; avoids arbitrary sleeps
                    try:
                        page.wait_for_load_state("networkidle", timeout=5000)
                    except Exception:
                        # Some sites never reach networkidle; it's okay to continue
                        pass

                    for _ in range(self.scroll_count):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                        page.wait_for_timeout(500)  # ~0.5s between scrolls

                    html = page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    print(f"[SUCCESS] Scraped: {url}")
                    success = True

                    # Clean close
                    context.close()
                    browser.close()

                    return soup

            except Exception as e:
                last_exception = e
                retry += 1
                wait_time = 2 ** retry
                print(f"[RETRY {retry}/{self.max_retries}] Error scraping {url}: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)

        if not success:
            print(f"[FAILED] Could not scrape: {url}. Last error: {last_exception}")
        return None


class ScrapClientWebsite(ScrapingEngine):
    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.HTML = None

    def fetch_soup_object(self):
        self.HTML = self.engine(self.url)

    def invoke(self):
        self.fetch_soup_object()
        return self.HTML