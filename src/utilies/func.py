import re
import time
import markdown
import pdfkit
import json
from typing_extensions import List
from src.scehma.agent import (CompetitorAnalystSchema, 
                              WebSearchQuerySchema, 
                              ListCompanyNameSchema,
                              AnalystOutputScemha, 
                              WritePositionOutputSchema, 
                              WriteSEOOutputSchema, 
                              WriteEngagementOutputSchema,
                              WriteRecOutputSchema
                              )
from src.tools.search_engines import TivalyCrawlerEngine, TivalyExtractEngine, TavilyWebSearchEngine, DuckDuckGoEngine, GoogleSearchEngine
from src.tools.scrapping_engine import ScrapingEngine, CompetitorWebsiteScraper
from src.utilies.chatgpt import ChatGpt
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from src.utilies.prompts import (get_web_search_query, 
                                 get_company_name, 
                                 web_analyst)

from src.tools.seo_engines import SEOAnalysisEngine

llm = ChatGpt().model()

def scrape_client_website(state: CompetitorAnalystSchema):
    client_url = [state["client_url"]]
    crawler = ScrapingEngine(urls=client_url, tag="p")
    content = crawler.invoke()
    return {"client_content": content}

def tavily_scraping(state: CompetitorAnalystSchema):
    client_url = [state["client_url"]]
    crawler = TivalyExtractEngine(urls=client_url)
    content = crawler.invoke()
    return {"client_content": content}

def condition_for_scrape(state: CompetitorAnalystSchema):
    content = state['client_content']
    tokens = content.split(" ")
    if len(tokens) > 10:
        return "skip"
    return "scrape"

def generate_web_search_query(state: CompetitorAnalystSchema):
    content = state["client_content"]
    location = state["location"]
    structured_llm = llm.with_structured_output(WebSearchQuerySchema)
    system_prompt = get_web_search_query().format(content=content, location=location)
    query = structured_llm.invoke([SystemMessage(content=system_prompt)] + [HumanMessage(content="generate the web search query")])
    return {"competitor_search_query": query}

def search_query_on_tavily(state: CompetitorAnalystSchema):
    query = state['competitor_search_query']
    search = TavilyWebSearchEngine(query=query)
    content = search.invoke()
    return {"competitor_contents": content}

def extract_company_name(state: CompetitorAnalystSchema):
    content = state["competitor_contents"]
    structured_llm = llm.with_structured_output(ListCompanyNameSchema)
    system_prompt = get_company_name().format(content=content)
    name_list = structured_llm.invoke([SystemMessage(content=system_prompt)] + [HumanMessage(content="extract names")])
    return {"competitor_names": name_list}

def find_competitor_urls_ddg(state: CompetitorAnalystSchema):
    competitors_website_url = []
    competitors_name_list = state["competitor_names"]
    location = state["location"]
    for name in competitors_name_list["names"]:
        query = f"website of {name} company in {location}"
        urls = DuckDuckGoEngine(query=query).run()
        website = urls[:1] if urls else []
        competitors_website_url.extend(website)
    return {"competitor_urls": competitors_website_url}

def find_competitor_urls_google(state: CompetitorAnalystSchema):
    competitors_website_url = []
    competitors_name_list = state["competitor_names"]
    location = state["location"]
    for name in competitors_name_list["names"]:
        query = f"website of {name} company in {location}"
        url = GoogleSearchEngine(query=query).invoke()
        website = url
        competitors_website_url.extend(website)
    return {"competitor_urls": competitors_website_url}

def search_engine_selector(state: CompetitorAnalystSchema):
    url_list = state['competitor_urls']
    name_list = state["competitor_names"]['names']
    if len(url_list) == len(name_list):
        return 'skip'
    return 'search'

def initialURLPosition(url_state, statename):
    if statename == '1' and url_state is None:
        return 0
    if statename == '2' and url_state is None:
        return 1
    if statename == '3' and url_state is None:
        return 2
    if statename == '4' and url_state is None:
        return 3
    else:
        return url_state + 4


def website_scraper(state: CompetitorAnalystSchema):
    url_list = state['competitor_urls'][:4]
    scraper_obj_arr = []
    
    for url in url_list:
        result = dict()
        seo = SEOAnalysisEngine(url)
        scape = CompetitorWebsiteScraper(url=url)
        html_obj = scape.fetch_soup_object()
        links = scape.get_all_links()
        title = scape.get_title()
        keywords = scape.get_all_keywords()
        desc = scape.get_description()
        robot = scape.get_robots()                
        backlinks = seo.get_backlinks()
        url_metrics = seo.get_url_metrics()
        main_pages = {url:html_obj.text}
        extra_pages_arr = scrape_extra_pages(url, links)
        result["third-pages"] = main_pages
        result["third-extra-pages"] = extra_pages_arr
        result["third-links"] = links
        result["third-title"] = title
        result["third-keywords"] = keywords
        result["third-description"] = desc
        result["third-robot"] = robot
        result["third-backlinks"] = backlinks
        result["third-metrices"] = url_metrics
        scraper_obj_arr.append(result)
    return {'competitors_website_html_content': scraper_obj_arr}


def url_separators(root_url: str, url: str):
    full_urls = set([])
    relative_paths = set([])
    absolute_url_pattern = r'^https?://'
    for link in url:
        if re.match(absolute_url_pattern, link):
            full_urls.add(link)
        else:
            new_link = link.replace('/', '')
            new_link = f"{new_link}"
            relative_paths.add(new_link)

    for u in full_urls:
        url_without_root = u.replace(root_url, "")
        url_comps = url_without_root.split("/")
        remaining_path = url_comps[0] if url_comps else []
        r_url = f"{remaining_path}/"
        relative_paths.add(r_url)
    
    return relative_paths


def scrape_extra_pages(root_url:str, urls: List[str]):
    relative_paths = url_separators(root_url, urls)
    pages = []
    categories = ['about', 'product', 'service', 
                  'pricing','solution', 
                  'FAQ', 'testimonials', 
                  'ratings', 'reviews', 'blog']
    
    for path in relative_paths:
        for token in categories:
            if re.search(rf'{re.escape(token)}', path, re.IGNORECASE):
                temp = dict()
                temp_url = f"{root_url}{path}"
                time.sleep(1)
                html =CompetitorWebsiteScraper(url=temp_url).fetch_soup_object()
                temp[temp_url] = html.text if html else ''
                pages.append(temp)
    return pages

def checkpoint(state: CompetitorAnalystSchema):
    filename = "./data_files/data.json"
    with open(filename, 'w') as file:
        json.dump(state["competitors_website_html_content"], file, indent=4)
    return state
        

# def human_feedback(state: CompetitorAnalystSchema):
#     """ No-op node that should be interrupted on """
#     print(state['competitors_website_html_content'])
#     pass

# def validate_HTML_object(state:CompetitorAnalystSchema):
#     human_feedback = state.get("hunam_feedback", None)
#     if human_feedback == "first":
#         return "First_Scraper"
    
#     if human_feedback == "second":
#         return "Second_Scraper"
    
#     if human_feedback == "third":
#         return "Third_Scraper"
    
#     if human_feedback == "Fourth":
#         return "Fourth_Scraper"
    
#     # else:
#     #     return "URL_Extractor"
    
#     return "URL_Extractor"

def data_organizer(state: CompetitorAnalystSchema):
    data = state['competitors_website_html_content']
    sufix_label = ['-pages', '-extra-pages']
    arr = []
    for idx, hashs in enumerate(data):
        temp = dict()
        pages = []
        name = list(hashs.keys())[0].split('-')[0]
        home_page_dict = hashs[f"{name}{sufix_label[0]}"]
        for k, v in home_page_dict.items():
            cont = v.replace('\n','')
            home_content = f"<Document source={k} page='Home'/>\n{cont}\n</Document>"
            pages.append(home_content)
        
        extra_page_dict = hashs[f"{name}{sufix_label[1]}"]
        for idx in range(len(extra_page_dict)):
            for k, v in extra_page_dict[idx].items():
                last_ele = k.split('/')
                page_name = last_ele[-1] if last_ele[-1] != "" else last_ele[-2]
                cont = v.replace('\n','')
                extra_content = f"<Document source={k} page={page_name}/>\n{cont}\n</Document>"
                pages.append(extra_content)
        title =  f"Website Title:- {hashs[f'{name}-title']}\n\n"
        kw = hashs[f'{name}-keywords']
        keywords = f"Website Keywords:- {kw}\n\n"
        d = hashs[f'{name}-description']
        desc = f"Website Description:- {d}\n\n"
        b = hashs[f'{name}-robot']
        robot = f"Website Robots:- {b}\n\n"
        m = hashs[f'{name}-metrices']
        metrics = f"Website URL MOZ Metrics Report:- {m}\n\n"
        text = "-------------\n-----------".join(pages)
        urls = "\n".join([i for i in hashs[f'{name}-links']])
        links =  f"\n\nWebsite Links:- \n{urls}\n"
        bl = "\n".join([i for i in hashs[f'{name}-backlinks']]) if hashs[f'{name}-backlinks'] else "No backlink present"
        backlinks = f"\n\nWebsite Backinks:- \n{bl}\n\n"
        content = f"{title} {desc} {text} {links} {backlinks} {metrics}"
        arr.append(content)
    return {'analyst_content': arr}


def web_seo_analyst(state: CompetitorAnalystSchema):
    content = state.get('analyst_content', [])
    content = "----------------------\n Next Competitor Website Conten \n-----------------------".join(content)
    structured_llm = llm.with_structured_output(AnalystOutputScemha)
    prompt = web_analyst()
    system_prompt = prompt.format(website_data=content)
    query = structured_llm.invoke([SystemMessage(content=system_prompt)] + [HumanMessage(content="generate your analysis and answers paragraph")])
    return {"report": query['content']}


def create_text_file(state: CompetitorAnalystSchema):
    text = state.get('report')
    html_text = markdown.markdown(text)
    with open("./data_files/report.html", "w") as html_file:
        html_file.write(html_text)
    pdfkit.from_string(html_text, "report.pdf")
    print(f"[SUCCESS]: successfully file generated...!!")
    return state







    


















