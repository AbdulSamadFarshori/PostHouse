import time
from typing import List, Optional, Dict
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


class ScrapingEngine:
    """
    A web scraping engine using Selenium to fetch HTML and BeautifulSoup for parsing.
    """

    def __init__(
        self,
        headless: bool = True,
        driver_path: str = "./drive/chromedriver.exe",
        urls: Optional[List[str]] = None,
        max_retries: int = 3,
        scroll_count: int = 3,
    ):
        """
        Initialize the scraping engine.

        :param headless: Run Chrome in headless mode.
        :param driver_path: Path to ChromeDriver.
        :param urls: List of URLs to scrape.
        :param max_retries: Number of retries on failure.
        :param scroll_count: Number of scrolls for dynamic content.
        """
        options = Options()
        options.headless = headless
        self.driver = webdriver.Chrome(service=Service(driver_path), options=options)
        self.urls = urls or []
        self.max_retries = max_retries
        self.scroll_count = scroll_count
        self.page_soups: Dict[str, BeautifulSoup] = {}
        self.cleaned_texts: Dict[str, BeautifulSoup] = {}

    def fetch_and_parse(self):
        """
        Fetch HTML content from URLs and parse it using BeautifulSoup.
        Stores the parsed soup object in self.page_soups.
        """
        for url in self.urls:
            retry = 0
            success = False
            while retry < self.max_retries and not success:
                try:
                    self.driver.get(url)
                    time.sleep(3)

                    for _ in range(self.scroll_count):
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)

                    html = self.driver.page_source
                    soup = BeautifulSoup(html, "html.parser")
                    for tag in soup(["script", "style", "noscript"]):
                        tag.decompose()
                    for tag in soup.find_all(["nav", "footer", "header", "aside"]):
                        tag.decompose()
                    keywords = ["navbar", "nav", "footer", "header", "menu", "sidebar"]
                    for keyword in keywords:
                        for tag in soup.find_all(attrs={"class": lambda x: x and keyword in x.lower()}):
                            tag.decompose()
                        for tag in soup.find_all(attrs={"id": lambda x: x and keyword in x.lower()}):
                            tag.decompose()
                    self.page_soups[url] = soup
                    clean_text = soup.get_text(separator="\n", strip=True)
                    self.cleaned_texts[url] = clean_text
                    print(f"[SUCCESS] Scraped: {url}")
                    success = True
                except Exception as e:
                    retry += 1
                    wait_time = 2 ** retry
                    print(f"[RETRY {retry}/{self.max_retries}] Error scraping {url}: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)

        self.driver.quit()






if __name__ == "__main__":
    # urls = ['https://www.yelp.com/search?cflt=afghani&find_loc=London', 
    #  'https://restaurantguru.com/afghan-London-c1', 
    #  'https://www.thefork.com/restaurants/london-c665790/afghan-t2292', 
    #  'https://autoreserve.com/en/gb/afghan', 
    #  'https://www.balkhkenton.com/', 
    #  'https://halalgems.com/10-afghan-owned-restaurants-around-london/', 
    #  'https://dineawardslondon.com/afghan', 
    #  'https://blog.resy.com/2021/11/london-afghan-restaurants-guide/', 
    #  'https://www.halaljoints.com/browse/afghan-in-london-united-kingdom', 
    #  'https://getonbloc.com/nearby/the-best-afghan-restaurants-in-london/'
    #  ]

    urls = ["https://www.linkedin.com/feed/"]
    
    scraper = ScrapingEngine(headless=True, urls=urls)
    scraper.fetch_and_parse()
    x = scraper.page_soups
    y = scraper.cleaned_texts
    print(f"{'@'*100}")
    print(y)

    

