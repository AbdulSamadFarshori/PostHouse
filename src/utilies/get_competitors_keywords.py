import re
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from src.tools.scrapping_engine import ScrapClientWebsite
from src.utilies.similar_keywords import SimilarKeywords
from src.tools.seo_engines import SEOAnalysisEngine
class CounterDict:
    def __init__(self):
        self.dict = dict()

    def insert(self, key):
        if key in self.dict:
            self.dict[key] += 1
        else:
            self.dict[key] = 0

    def sortValue(self):
        self.dict = dict(sorted(self.dict.items(), key= lambda x: x[1], reverse=True))

    def filter_values(self):
        self.dict = {k:v for k, v in self.dict.items() if v > 1}

    def __call__(self, *args, **kwds):
        return self.dict
        

class CompetitorsAnalysis:

    def __init__(self, true_competitors, client_DA, client_keywords, industry, client_backlinks):
        self.true_competitors = true_competitors
        self.client_DA = client_DA
        self.client_keywords = client_keywords
        self.industry = industry
        self.client_backlinks = client_backlinks
        self.filtered_competitors = []
        self.links = []
        self.competitors_keywords = []
        self.counter = CounterDict()
        self.backlinks = []
        self.keywords_gap = []
        self.backlinks_gap = []

    def qualified_links(self):
        temp = []
        for item in self.true_competitors:
            if item.get('domain_authority') >= self.client_DA:
                temp.append(item.get('url'))
        self.filtered_competitors = temp

    def scrap_pages(self, url):
        web = ScrapClientWebsite(url)
        scrape_data = web.invoke()
        return scrape_data
    
    def find_relavent_nav_link(self, links):
        page_name = list(links.keys())
        sk = SimilarKeywords(keywords=page_name, query=self.industry, k=5)
        page_tuple = sk.similar_keywords()
        final_page = [links[i[0]] for i in page_tuple]
        return final_page

    
    def get_nav_anchor_tags(self, soup, url):
        links_dict = {}
        nav = soup.find("nav")
        nav_links = nav.find_all("a") if nav else []
        if nav_links:
            links_dict = {a.get_text(strip=True).lower() : a['href'] for a in nav_links if a.has_attr('href')}
            if url not in links_dict.values():
                links_dict["home"] = url
        else:
            links_dict["home"] = [url]
        print(links_dict)
        links = self.find_relavent_nav_link(links_dict)
        return links
    
    def clean_text(self, text: str) -> str:
        stop_words = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        text = re.sub(r'\d+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        words = text.split()
        cleaned_words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
        return ' '.join(cleaned_words)
    
    def get_text_from_html(self, soup) -> str:
        all_text = list()
        Bsoup = soup
        keywords_meta = Bsoup.find("meta", attrs={"name": "keywords"})
        if keywords_meta and keywords_meta.get("content"):
            all_text.append(keywords_meta["content"].strip())
        description_meta = Bsoup.find("meta", attrs={"name": "description"})
        if description_meta and description_meta.get("content"):
            all_text.append(description_meta["content"].strip())
        if Bsoup.title:
            all_text.append(soup.title.get_text().strip())
        for tag in Bsoup.find_all(["h1", "h2", "h3"]):
            all_text.append(tag.get_text().strip())
        text = " ".join(all_text)
        cleaned_text = self.clean_text(text)
        return cleaned_text
    
    def keywords_count(self, text):
        splitted_tokens = text.split(" ")
        for token in splitted_tokens:
            self.counter.insert(token)
    
    def find_relavent_keywords(self):
        temp = []
        top_three_keywords = self.client_keywords[:3]
        WORDS = list(self.counter.dict.keys())
        for token in top_three_keywords:
            sm = SimilarKeywords(keywords=WORDS, query=token, k=5)   
            smiliar_token = sm.similar_keywords()
            print(smiliar_token)
            foo = [i[0] for i in smiliar_token]
            temp.extend(foo)
        self.competitors_keywords = temp

    def get_backlinks(self, url):
        engine = SEOAnalysisEngine(url)
        bl = engine.get_backlinks()
        self.backlinks.append(bl)
    
    def main(self):
        self.qualified_links()
        for url in self.filtered_competitors:
            self.get_backlinks(url)
            soup = self.scrap_pages(url)
            if soup:
                nav_links = self.get_nav_anchor_tags(soup, url)
                print(nav_links)
                for a_tags in nav_links:
                    soup_2 = self.scrap_pages(a_tags)
                    if soup_2:
                        text = self.get_text_from_html(soup_2)
                        self.keywords_count(text)
        self.counter.filter_values()
        self.counter.sortValue()
        print(self.counter.dict)
        self.find_relavent_keywords()
        self.keywords_gap = [ k for k in self.competitors_keywords if k not in self.client_keywords]
        
        if self.backlinks:
            for ele in self.backlinks:
                temp_back = [b for b in ele if b not in self.client_backlinks]
                self.backlinks_gap.extend(temp_back)

        return self.keywords_gap, self.backlinks_gap





    
        






