from langgraph.graph import START, END, StateGraph
from src.scehma.agent import CompetitorAnalystSchema
from langgraph.checkpoint.memory import MemorySaver
from src.utilies.func import (scrape_client_website, 
                            generate_web_search_query, 
                            tavily_scraping, 
                            condition_for_scrape, 
                            search_query_on_tavily, 
                            extract_company_name, 
                            find_competitor_urls_ddg, 
                            find_competitor_urls_google,
                            search_engine_selector,
                            website_scraper,
                            checkpoint, data_organizer, create_text_file, web_seo_analyst)

class CompetitorFinderAgent:

    def __init__(self):
        self.builder = StateGraph(CompetitorAnalystSchema)

    def graph(self):
        self.builder.add_node("Scrap_Client_Website", scrape_client_website)
        self.builder.add_node("Generate_Web_Search_Query", generate_web_search_query)
        self.builder.add_node("Tavily_Website_Scaping", tavily_scraping)
        self.builder.add_node("Query_search", search_query_on_tavily)
        self.builder.add_node("Extract_Companies_Names", extract_company_name)
        self.builder.add_node("DuckDuckGo_URL_Search", find_competitor_urls_ddg)
        self.builder.add_node("Google_URL_Search", find_competitor_urls_google)

        self.builder.add_edge(START, "Scrap_Client_Website")
        self.builder.add_conditional_edges(
                    "Scrap_Client_Website",
                    condition_for_scrape, {"skip":"Generate_Web_Search_Query","scrape":"Tavily_Website_Scaping"})
        self.builder.add_edge("Tavily_Website_Scaping", "Generate_Web_Search_Query")
        self.builder.add_edge("Generate_Web_Search_Query", "Query_search")
        self.builder.add_edge("Query_search", "Extract_Companies_Names")
        self.builder.add_edge("Extract_Companies_Names", "Google_URL_Search")
        self.builder.add_conditional_edges(
                    "Google_URL_Search",
                    search_engine_selector, {"skip":END,"search":"DuckDuckGo_URL_Search"})
        self.builder.add_edge("DuckDuckGo_URL_Search", END)
        return self.builder


class CompetitorWebsiteScraperAngent(CompetitorFinderAgent):

    def __init__(self):
        super().__init__()
        self.scraper = StateGraph(CompetitorAnalystSchema)
        self.search = self.graph()

    def scraper_graph(self):
        self.scraper.add_node("Competitors_Finder", self.search.compile())
        self.scraper.add_node("Scraper", website_scraper)
        
        # self.scraper.add_node("Human_Feedback", human_feedback)
        self.scraper.add_node("Checkpoint", checkpoint)

        self.scraper.add_edge(START ,"Competitors_Finder")
        self.scraper.add_edge("Competitors_Finder", "Scraper")
        self.scraper.add_edge("Scraper", "Checkpoint")
        # self.scraper.add_conditional_edges("Human_Feedback", validate_HTML_object, ["First_Scraper","Second_Scraper","Third_Scraper","Fourth_Scraper", "URL_Extractor"])
        self.scraper.add_edge("Checkpoint", END)
        
        return self.scraper

class DataPreprocessor(CompetitorWebsiteScraperAngent):
    def __init__(self):
        super().__init__()
        self.developer = StateGraph(CompetitorAnalystSchema)
        self.scraper_agent = self.scraper_graph()

    def developer_graph(self):
        self.developer.add_node('Competitor_Data_Scraper', self.scraper_agent.compile())
        self.developer.add_node('Data_Organizer', data_organizer)
        self.developer.add_node('SEO_Analyst', web_seo_analyst)
        self.developer.add_node('Generate_Text_File', create_text_file)
        

        self.developer.add_edge(START, 'Competitor_Data_Scraper')
        self.developer.add_edge('Competitor_Data_Scraper', 'Data_Organizer')
        self.developer.add_edge('Data_Organizer', 'SEO_Analyst')
        
        self.developer.add_edge('SEO_Analyst',  'Generate_Text_File')
        self.developer.add_edge('Generate_Text_File', END)

        return self.developer



agent = DataPreprocessor().developer_graph()
memory = MemorySaver()
graph = agent.compile()



