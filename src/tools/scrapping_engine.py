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
        max_retries: int = 1,   # meaning: extra retries besides the first try
        scroll_count: int = 3,
    ):
        self.headless = headless
        self.urls = urls or []
        self.tag: str = tag
        self.max_retries = max_retries
        self.scroll_count = scroll_count
        self.page_soups: Dict[str, BeautifulSoup] = {}
        self.cleaned_texts: Dict[str, BeautifulSoup] = {}
        self._all_paragraph_text: List[str] = []

        # Chromium launch args
        self.options: List[str] = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--window-size=1920,1080",
        ]

        self.driver = None  # kept for API compatibility

    async def engine(self, url: str):

        attempts = self.max_retries + 1
        last_exception = None

        for attempt in range(1, attempts + 1):
            browser = None
            context = None
            try:
                with sync_playwright() as pw:
                    browser = pw.chromium.launch(headless=self.headless, args=self.options)
                    context = browser.new_context(viewport={"width": 1920, "height": 1080})
                    page = context.new_page()

                    page.goto(url, wait_until="domcontentloaded", timeout=30_000)
                    try:
                        page.wait_for_load_state("networkidle", timeout=5_000)
                    except Exception:
                        pass  # some sites never reach 'networkidle'

                    for _ in range(self.scroll_count):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                        page.wait_for_timeout(500)

                    html = page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    print(f"[SUCCESS] Scraped: {url}")
                    return soup

            except Exception as e:
                last_exception = e
                if attempt < attempts:
                    backoff = min(2 ** attempt, 8)
                    print(f"[RETRY {attempt}/{attempts-1}] {e} -> retrying in {backoff}s")
                    time.sleep(backoff)
                else:
                    print(f"[FAILED] Could not scrape: {url}. Last error: {e}")
                    return None

            finally:
                # Make sure we always close resources even on failure
                try:
                    if context:
                        context.close()
                except Exception:
                    pass
                try:
                    if browser:
                        browser.close()
                except Exception:
                    pass


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
