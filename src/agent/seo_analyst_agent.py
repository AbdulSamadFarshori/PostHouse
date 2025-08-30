from src.scehma.agent import SEOCompetitiveAnalystSchema
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from src.utilies.on_page_audit import client_website_data, on_page_seo_audit_report
from src.utilies.true_competitors import find_true_competitors
from src.utilies.keywords_and_backlinks_gap import keywords_backlinks_gap
from src.utilies.keyword_report import keywords_metrice
from  src.utilies.final_report import final_report

class CompetitorFinderAgent:

    def __init__(self):
        self.builder = StateGraph(SEOCompetitiveAnalystSchema)

    def graph(self):
        self.builder.add_node("collect_Client_Website_data", client_website_data)
        self.builder.add_node("generate_on_page_seo_aduit_report", on_page_seo_audit_report)
        self.builder.add_node("find_true_competitors", find_true_competitors)
        self.builder.add_node("keywords_and_backlinks_gap", keywords_backlinks_gap)
        self.builder.add_node("keywords_metrice", keywords_metrice)
        self.builder.add_node("final_report", final_report)
        
        self.builder.add_edge(START, "collect_Client_Website_data")
        self.builder.add_edge("collect_Client_Website_data", "generate_on_page_seo_aduit_report")
        self.builder.add_edge("generate_on_page_seo_aduit_report", END)
        self.builder.add_edge("collect_Client_Website_data", "find_true_competitors")
        self.builder.add_edge("find_true_competitors", "keywords_and_backlinks_gap")
        self.builder.add_edge("keywords_and_backlinks_gap", "keywords_metrice")
        self.builder.add_edge("keywords_metrice", "final_report")
        self.builder.add_edge("final_report", END)

        return self.builder

    


