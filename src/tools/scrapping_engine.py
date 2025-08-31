import asyncio
import sys
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from langchain_core.tools import tool


class ScrapingEngine:
    """
    Async web scraping engine using Playwright + BeautifulSoup
    for LangGraph compatibility.
    """

    def __init__(
        self,
        headless: bool = True,
        urls: Optional[List[str]] = None,
        tag: str = "p",
        max_retries: int = 1,
        scroll_count: int = 3,
    ):
        self.headless = headless
        self.urls = urls or []
        self.tag = tag
        self.max_retries = max_retries
        self.scroll_count = scroll_count

        self.options: List[str] = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--window-size=1920,1080",
        ]

    async def engine(self, url: str) -> Optional[BeautifulSoup]:
        """
        Core scraping logic with retries.
        """

        if sys.platform.startswith("win"):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


        attempts = self.max_retries + 1
        last_exception = None

        for attempt in range(1, attempts + 1):
            browser, context = None, None
            try:
                async with async_playwright() as pw:
                    browser = await pw.chromium.launch(
                        headless=self.headless, args=self.options
                    )
                    context = await browser.new_context(
                        viewport={"width": 1920, "height": 1080}
                    )
                    page = await context.new_page()

                    await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
                    try:
                        await page.wait_for_load_state("networkidle", timeout=5_000)
                    except Exception:
                        pass  # some sites never reach 'networkidle'

                    for _ in range(self.scroll_count):
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                        await asyncio.sleep(0.5)

                    html = await page.content()
                    soup = BeautifulSoup(html, "html.parser")
                    print(f"[SUCCESS] Scraped: {url}")
                    return soup

            except Exception as e:
                last_exception = e
                if attempt < attempts:
                    backoff = min(2 ** attempt, 8)
                    print(f"[RETRY {attempt}/{attempts-1}] {e} -> retrying in {backoff}s")
                    await asyncio.sleep(backoff)
                else:
                    print(f"[FAILED] Could not scrape: {url}. Last error: {e}")
                    return None

            finally:
                try:
                    if context:
                        await context.close()
                except Exception:
                    pass
                try:
                    if browser:
                        await browser.close()
                except Exception:
                    pass


class ScrapClientWebsite(ScrapingEngine):
    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.HTML = None

    async def fetch_soup_object(self):
        self.HTML = await self.engine(self.url)

    async def invoke(self):
        await self.fetch_soup_object()
        return self.HTML
