import json
import nltk
import re
import pandas as pd
from typing_extensions import List, Dict, Annotated, Union 
from src.tools.scrapping_engine import ScrapClientWebsite
from src.tools.seo_engines import SEOAnalysisEngine
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from src.utilies.prompts import url_filter_prompt
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from src.utilies.factory import ModelFactory
from src.scehma.agent import UrlFilterSchema
import logging
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

class CollectClientWebsiteData:

    def __init__(self, url: str, pages: List):
        core = ModelFactory.create('chatgpt')
        self.llm = core.model()
        self.url = url
        self.title_count = 60
        self.description_count = 160
        self.HTML = None
        self.links = []
        self.top_rank_links = []
        self.h1_tags = []
        self.h2_tags = []
        self.og_tag = {}
        self.twc = {}
        self.title = {}
        self.desc = {}
        self.text = {}
        self.top_keywords = []
        self.keywords = []
        self.og_tags_is_present = {}
        self.title_char = {}
        self.desc_char = {}
        self.canonical_url = None
        self.robust_tag = None
        self.schema = []        
        self.backlinks = []
        self.DA = None

        self.scraping_pages = pages

    async def init_scrape(self):
        web = ScrapClientWebsite(self.url)
        self.HTML = await web.invoke()
    
    def get_navbar_links(self):
        links_dict = {}
        nav = self.HTML.find("nav")
        nav_links = nav.find_all("a") if nav else []
        if nav_links:
            links_dict = {a.get_text(strip=True).lower() : a['href'] for a in nav_links if a.has_attr('href')}
        
        if self.url not in links_dict.values():
            links_dict["home"] = self.url
        self.links = [v for k, v in links_dict.items() if k in self.scraping_pages]

        logging.info(f"[INFO] -- URLS {self.links}")

    def get_top_rank_page_link(self):
        top_page = SEOAnalysisEngine(self.url)
        top_pages_link = top_page.get_top_page()
        self.top_rank_links.extend(top_pages_link)
        print(f"[top-page-link] : - {self.top_rank_links}")
    
    def url_checkpoint(self):
        root = self.url
        if root.endswith('/'):
            root = root[0:len(root)-1]

        for idx, link in enumerate(self.links):
            if link.startswith("https://"):
                pass
            else:
                full_url = f"{root}{link}"
                self.links[idx] = full_url

    # def qwen_llm_response(self, prompt):
    #     llm = ModelFactory.create('qwen')
    #     core = llm.model()
    #     res = core.invoke(prompt)
    #     content = res
    #     json_output = json.loads(content)
    #     return json_output

    def filter_urls(self):
        prompt = url_filter_prompt()
        system_prompt = prompt.format(urls=self.links)
        final_prompt = [SystemMessage(content=system_prompt)] + [HumanMessage(content="please find the useful urls")]
        structured_llm = self.llm.with_structured_output(UrlFilterSchema)
        res = structured_llm.invoke(final_prompt)
        self.links = res.get('urls', self.links)
        logging.info(f"[Links]: - {self.links}")

    async def scrap_pages(self, url):
        web = ScrapClientWebsite(url)
        scrape_data = await web.invoke()  # ✅ await async scraper
        return scrape_data
        
    def get_title(self, soup) -> str:
        title = soup.title.string
        return title

    def get_description(self, soup) -> str:
        description = ""
        desc = soup.find("meta", attrs={"name": "description"})
        if desc and desc.get("content"):
            description = desc["content"]
        return description

    def get_og_tags(self, soup) -> dict:
        og_tags = {}
        for tag in soup.find_all('meta'):
            prop = tag.get('property')
            if prop and prop.startswith('og:'):
                og_tags[prop] = tag.get('content', '')
        return og_tags

    def get_h1_tags(self, soup):
        h1_tags = soup.find_all('h1')
        h1_tags = [tag.get_text() for tag in h1_tags]
        return h1_tags

    def get_h2_tags(self, soup):
        h2_tags = soup.find_all('h2')
        h2_tags = [tag.get_text() for tag in h2_tags]
        return h2_tags

    def get_h3_tags(self, soup):
        h3_tags = soup.find_all('h3')
        h3_tags = [tag.get_text() for tag in h3_tags]
        return h3_tags

    def get_h4_tags(self, soup):
        h4_tags = soup.find_all('h4')
        return h4_tags

    def get_h5_tags(self, soup):
        h5_tags = soup.find_all('h5')
        return h5_tags

    def get_h6_tags(self, soup):
        h6_tags = soup.find_all('h6')
        return h6_tags

    def get_twitter_card(self, soup) -> dict:
        twitter_tags = {}
        for tag in soup.find_all('meta'):
            name = tag.get('name')
            if name and name.startswith('twitter:'):
                twitter_tags[name] = tag.get('content', '')
        return twitter_tags

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

    # def extract_keywords(arr, n_grams: int = 0):
    #     words = []
    #     k = 0
    #     for idx in range(1, len(arr), n_grams):
    #         word = " ".join(arr[k:idx+1])
    #         words.append(word)
    #         k = idx
    #     return words
        
    def keywords_count(self, arr):
        data = {"ngrm":arr}
        df = pd.DataFrame(data)
        value_counts = df["ngrm"].value_counts()
        return value_counts[value_counts.values > 1]

    def get_keywords(self, cleaned_text):
        keywords = cleaned_text.split(" ")
        counts = self.keywords_count(keywords)
        kwds = counts.to_dict()
        sorted_keywords = dict(sorted(kwds.items(), key=lambda item: item[1], reverse=True))
        return list(sorted_keywords.keys())[:10]

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
        for tag in Bsoup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p"]):
            all_text.append(tag.get_text().strip())
        text = " ".join(all_text)
        cleaned_text = self.clean_text(text)
        return cleaned_text
    
    def website_top_keywords(self):
        keyword = {'keywords': self.keywords}
        df = pd.DataFrame(keyword)
        vc = df['keywords'].value_counts()
        more_than_one = vc[vc.values > 1].to_dict()
        self.top_keywords = list(more_than_one.keys())
    
    def get_canonical_tag(self):
        canonical = self.HTML.find('link', rel='canonical')
        canonical_url = canonical['href'] if canonical else None
        return canonical_url
    
    def get_robust_tag(self):
        robots_tag = self.HTML.find('meta', attrs={'name': 'robots'})
        robots_content = robots_tag['content'] if robots_tag else None
        return robots_content
    
    def get_schema(self):
        structured_data = self.HTML.find_all('script', type='application/ld+json')
        schemas = []
        for data in structured_data:
            try:
                schema = json.loads(data.string)
                schemas.append(schema)
            except json.JSONDecodeError:
                pass
        return schemas
    
    def get_viewport(self):
        viewport_tag = self.HTML.find('meta', attrs={'name': 'viewport'})
        viewport_content = viewport_tag['content'] if viewport_tag else None
        return viewport_content
    
    def get_client_backlinks(self):
        engine = SEOAnalysisEngine(self.url)
        self.backlinks = engine.get_backlinks()

    async def fetch_data(self):
        await self.init_scrape()
        self.get_navbar_links()
        self.url_checkpoint()
        self.filter_urls()

        all_links = self.links + self.top_rank_links
        for link in all_links:
            soup = await self.scrap_pages(link)   # ✅ async call
            if not soup:
                continue
            title = self.get_title(soup)
            og_tag = self.get_og_tags(soup)
            desc = self.get_description(soup)
            h1 = self.get_h1_tags(soup)
            h2 = self.get_h2_tags(soup)
            twitter_card = self.get_twitter_card(soup)
            text = self.get_text_from_html(soup)
            keywords_list = self.get_keywords(text)

            self.keywords.extend(keywords_list)
            self.og_tag[link] = og_tag
            self.twc[link] = twitter_card
            self.title[link] = title
            self.desc[link] = desc
            self.h1_tags.extend(h1)
            self.h2_tags.extend(h2)
            self.text[link] = text
            self.canonical_url = self.get_canonical_tag()
            self.robust_tag = self.get_robust_tag()
            self.schema = self.get_schema()
            self.viewport = self.get_viewport()

        self.website_top_keywords()
        self.get_client_backlinks()


    def is_og_tags_present(self):
        temp = {}
        for link, item in self.og_tag.items():
            if item.get('og:title', None) and item.get('og:description', None):
                temp[link] = True
            else:
                temp[link] = False
        self.og_tags_is_present = temp

    def is_twitter_card_present(self):
        temp = {}
        for link, item in self.twc.items():
            if item.get('twitter:card', None):
                temp[link] = True
            else:
                item[link] = False

    def is_keywords_present_in_h_tags(self):
        status = False
        all_h1_tags = " ".join(self.h1_tags)
        all_h1_tokens = all_h1_tags.split() 
        for keyword in self.top_keywords:
            if keyword in all_h1_tokens:
                status = True
        return status
    
    def is_keywords_present_in_title(self, link):
        temp = False
        title = self.title.get(link, None)
        if title:
            cleaned_title = self.clean_text(title)
            arr = cleaned_title.split(" ")
            for keyword in self.top_keywords:
                if keyword in arr:
                    temp = True
        return temp

    def is_keywords_present_in_description(self, link):
        temp = False
        description = self.desc.get(link, None)
        if description:
            cleaned_desc = self.clean_text(description)
            arr = cleaned_desc.split(" ")
            for keyword in self.top_keywords:
                if keyword in arr:
                    temp = True
        return temp

    def title_char_length(self):
        temp = {}
        for k, v in self.title.items():
            title_char  = len(v)
            temp[k] = title_char
        self.title_char = temp

    def description_char_length(self):
        temp = {}
        for k, v in self.desc.items():
            temp[k] = len(v)
        self.desc_char = temp

    def get_page_name(self, link):
        name = ""
        root = self.url
        if root == link:
            name = 'Home'
            return name
        else:
            root_removed = link.replace(root, '')
            name = root_removed.replace('/', '')
            print(name)
        return name

    def generate_doc(self, link):
        temp = ""
        temp += f"Canonical Meta Tag: {self.canonical_url} \n "
        temp += f"Robots Meta Tag: {self.robust_tag} \n " 
        temp += f"Structure Data: {self.schema} \n "
        temp += f"Viewport Tag: {self.viewport} \n "

        if self.is_keywords_present_in_h_tags():
            temp += "Keywords Observation 1.1: keywords are present in h tags. \n "
        else:
            temp += "Keywords Observation 1.1: keywords are not present in h tags. \n "

        if self.is_keywords_present_in_title(link):
            temp += "Keywords Observation 1.2 : keywords are present in title. \n "
        else:
            temp += "Keywords Observation 1.2 : keywords are not present in title. \n "

        if self.is_keywords_present_in_description(link):
            temp += "Keywords Observation 1.3 : keywords are present in description. \n "
        else:
            temp += "Keywords Observation 1.2 : keywords are not present in description. \n "
        
        self.is_og_tags_present()
        og_status = self.og_tags_is_present.get(link, False)
        if og_status:
            temp += "OG meta Tag : OG meta tags are present. \n "
        else:
            temp += "OG meta Tag : OG meta tags are not present. \n "
            
        self.is_twitter_card_present()
        twitter_card = self.twc.get(link, False)
        if twitter_card:
            temp += "twitter card meta tag: twitter card meta tag is present. \n "
        else:
            temp += "twitter card meta tag: twitter card meta tag is not present. \n "

        self.title_char_length()
        if self.title_char.get(link, 0) < self.title_count and self.title_char.get(link, 0) >= 49:
            temp += f"Title Observation : title characters are {self.title_char.get(link, 0)} which is less than 60 characters and more than 50 characters which is suitable for seo. \n "
        else:
            temp += f"Title Observation : title characters are {self.title_char.get(link, 0)} which is  less than 50 characters or more than 60 characters which is not suitable for seo. \n "

        self.description_char_length()
        if self.desc_char.get(link, 0) < self.description_count and self.desc_char.get(link, 0) >= 149:
            temp += f"Description Observation : Description characters are {self.desc_char.get(link, 0)} which is less than 160 characters and more than 150 characters which is suitable for seo. \n "
        else:
            temp += f"Description Observation : Description characters are {self.desc_char.get(link, 0)} which is less than 150 characters or more than 160 characters which is not suitable for seo. \n "
        keywords = self.top_keywords if len(self.links) > 1 else self.keywords
        temp += f"H1 Tags: {self.h1_tags} \n "
        temp += f"H2 Tags: {self.h2_tags} \n "
        temp += f"Top keywords Observation : {", ".join(keywords)} \n "
        temp += f"<title> {self.title.get(link, None)} </title> \n "
        temp += f"<description> {self.desc.get(link, None)} </description> \n "
        temp += f"<content> {self.text.get(link, "")} </content> \n "
        name = self.get_page_name(link)
        temp = f"<Document url={link} page_name={name} > {temp} </Document>"
        return temp

    async def main(self):
        docs = []
        await self.fetch_data()   # ✅ async
        domain = SEOAnalysisEngine(self.url)
        self.DA = domain.get_url_metrics()
        for link in self.links:
            doc = self.generate_doc(link)
            docs.append(doc)
        return docs, self.keywords, self.backlinks, self.DA
        


        

