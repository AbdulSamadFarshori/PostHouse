import re
import json
from urllib.parse import urlparse
from src.utilies.prompts import classify_industry, generate_search_query, classify_search_results, classify_search_root_domain
from src.utilies.factory import ModelFactory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from src.scehma.agent import IndustryClassification, SearchQuery, ClassifySearchOuput
from typing import List, Annotated, Sequence, Dict
from src.tools.search_engines import GoogleSearchEngine
from src.tools.seo_engines import SEOAnalysisEngine
from src.tools.scrapping_engine import ScrapClientWebsite
from src.utilies.similar_keywords import SimilarKeywords


class FindTrueCompetitors:
    
    def __init__(self, docs: List[str], location: str, root_url: str, client_keywords: List):
        
        self.url = root_url
        self.docs = docs
        self.location = location
        self.specific_paragraph = None
        core = ModelFactory.create('chatgpt')
        self.llm = core.model()
        self.industry = None
        self.query = None
        self.google_search_results = []
        self.classified_search_urls = []
        self.bw_url = []
        self.url_with_moz_score = []
        self.report = None
        self.root_domain = []
        self.classified_search_root_urls = []
        self.r_urls = []
        self.client_keywords = client_keywords
        self.relavent_client_keywords_list = []
        self.total_hits = 0

    def find_doc(self):
        target_url = f"<Document url={self.url} page_name=Home >"
        self.specific_paragraph = next((p for p in self.docs if target_url in p), None)

    # def llm_response(self, prompt):
    #     res = self.llm.invoke(prompt)
    #     print(res)
    #     content = res
    #     json_output = json.loads(content)
    #     return json_output

    def classify_industry(self):
        home_page = self.specific_paragraph
        structured_llm = self.llm.with_structured_output(IndustryClassification)
        system_prompt = classify_industry().format(docs=home_page)
        final_prompt = [SystemMessage(content=system_prompt)] + [HumanMessage(content="find the industry type of the give company")]
        res = structured_llm.invoke(final_prompt)
        self.industry = res.get('industry', None)
        print(f"---------Industry--------{self.industry}")

    def create_search_query(self):
        industry = self.industry
        structured_llm = self.llm.with_structured_output(SearchQuery)
        system_prompt = generate_search_query().format(industry=industry, location=self.location)
        final_prompt = [SystemMessage(content=system_prompt)] + [HumanMessage(content="create query for search engine")]
        res = structured_llm.invoke(final_prompt)
        self.query = res.get('query', None) + f" in {self.location}"
        print(f"---------query--------{self.query}")
    
    def search_via_google(self):
        engine = GoogleSearchEngine(query=self.query)
        self.google_search_results = engine.invoke()

    def classify_the_search_ouput(self):
        structured_llm = self.llm.with_structured_output(ClassifySearchOuput)
        example = "[{url:..., classification:...}, {url:..., classification:...}, ....]"
        system_prompt = classify_search_results().format(arr=self.google_search_results, example=example, industry=self.industry)
        final_prompt = [SystemMessage(content=system_prompt)] + [HumanMessage(content="classify blog, article and business website urls")]
        res = structured_llm.invoke(final_prompt)
        self.classified_search_urls = res.get('urls', None)
        print(f"---------classified_url--------{self.classified_search_urls}")

    def get_root_domain(self):
        temp = [u.get('url') for u in self.classified_search_urls]
        root_domains = [f"https://{urlparse(url).netloc}" for url in temp]
        print(root_domains)
        self.root_domain = root_domains

    def scrap_pages(self, url):
        web = ScrapClientWebsite(url)
        scrape_data = web.invoke()
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

    def classify_the_search_root_ouput(self, arr):
        structured_llm = self.llm.with_structured_output(ClassifySearchOuput)
        example = "[{url:..., classification:...}, {url:..., classification:...}, ....]"
        system_prompt = classify_search_root_domain().format(arr=arr, example=example, industry=self.industry)
        final_prompt = [SystemMessage(content=system_prompt)] + [HumanMessage(content="classify relavent ot irrelavent urls")]
        res = structured_llm.invoke(final_prompt)
        self.classified_search_root_urls = res.get('urls', None)
        print(f"---------classified_root_url--------{self.classified_search_root_urls}")

    def relavent_urls(self):
        temp = []
        for url in self.root_domain:
            soup =self.scrap_pages(url)
            if soup:
                title = self.get_title(soup)
                desc = self.get_description(soup)
                text = f"url - {url}, title - {title}, description - {desc}"
                temp.append(text)
        self.classify_the_search_root_ouput(temp)
        self.r_urls = [has.get('url') for has in self.classified_search_root_urls if has.get('classification') == 'relavent']

    def business_website_url(self):
        temp = []
        for data in self.classified_search_urls:
            classification = data.get('classification', None)
            if classification and classification == 'business-website':
                url = data.get('url', None)
                if url:
                    temp.append(url)
        self.bw_url = temp

    def calculate_moz_score(self):
        total_hit_in_this_method = 0
        MOZ_URL_SCORE = []
        for url in self.r_urls:
            temp = {}
            moz_obj = SEOAnalysisEngine(url)
            # BA = moz_obj.get_ba_metrics()
            DA, hit = moz_obj.get_url_metrics()
            temp['url'] = url
            temp['domain_authority'] = DA
            MOZ_URL_SCORE.append(temp)
            total_hit_in_this_method += hit
        self.total_hits = total_hit_in_this_method
        SORTED_MOZ_URL_SCORE = sorted(MOZ_URL_SCORE, key=lambda x: x['domain_authority'], reverse=True)
        self.url_with_moz_score = SORTED_MOZ_URL_SCORE
        print(f"---------Moz scores--------{self.url_with_moz_score}")

    def report_in_text_form(self):
        temp = "URL DA\n"
        for result in self.url_with_moz_score:
            temp += f"{result.get('url')} {result.get('domain_authority')} \n"
        self.report = temp

    def relavent_client_keywords(self):
        sk = SimilarKeywords(self.client_keywords, self.industry, 10)
        arr = sk.similar_keywords_diverse()
        self.relavent_client_keywords_list = arr

    def main(self):
        self.find_doc()
        self.classify_industry()
        self.create_search_query()
        self.search_via_google()
        self.classify_the_search_ouput()
        self.get_root_domain()
        self.relavent_urls()
        # self.business_website_url()
        self.calculate_moz_score()
        self.report_in_text_form()
        self.relavent_client_keywords()
        return self.industry, self.report, self.url_with_moz_score, self.relavent_client_keywords_list, self.total_hits



