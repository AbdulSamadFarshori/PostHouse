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
        tag: str = "p",
        max_retries: int = 1,
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
        self.options = Options()
        self.headless = headless
        
        self.urls = urls or []
        self.tag: str = tag
        self.max_retries = max_retries
        self.scroll_count = scroll_count
        self.page_soups: Dict[str, BeautifulSoup] = {}
        self.cleaned_texts: Dict[str, BeautifulSoup] = {}
        self._all_paragraph_text: List[str] = []
        
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")    # mostly for Windows
        self.options.add_argument("--window-size=1920,1080")

        if self.headless:
            self.options.add_argument("--headless=new")   # use "--headless" if your Chrome is older

        self.driver = webdriver.Chrome(service=Service(driver_path), options=self.options)


    def engine(self, url: str):
        retry = 0
        success = False
        while retry < self.max_retries and not success:
            try:
                self.driver.get(url)
                time.sleep(3)

                for _ in range(self.scroll_count):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                html = self.driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                print(f"[SUCCESS] Scraped: {url}")
                success = True
                self.driver.quit()
                return soup
            except Exception as e:
                retry += 1
                wait_time = 2 ** retry
                print(f"[RETRY {retry}/{self.max_retries}] Error scraping {url}: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
        self.driver.quit()
    
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

    # urls = ["https://www.linkedin.com/feed/"]
    
    x = ScrapClientWebsite(url="https://www.sunsave.energy/solar-panels-advice/installation/best-installers")
    doc = x.invoke()
    with open('doc2.txt', 'w', encoding="utf-8") as f:
        f.write(doc)
    
    
    

