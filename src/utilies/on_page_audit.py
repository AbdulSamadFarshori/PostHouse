from src.utilies.factory import ModelFactory
from src.utilies.prompts import create_on_page_audit_report
from src.scehma.agent import OnPageSeoAuditReport, SEOCompetitiveAnalystSchema
from src.utilies.client_data_collector import CollectClientWebsiteData
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


def client_website_data(state: SEOCompetitiveAnalystSchema):
    url = state["client_url"]
    pages = state["pages"]
    collecter = CollectClientWebsiteData(url, pages)
    docs, keywords, organic_keywords, backlinks, da, hits = collecter.main()
    return {
            "client_website_data": docs, 
            "client_keywords": keywords, 
            "top_client_organic_keywords": organic_keywords, 
            "client_backlinks": backlinks, 
            "client_DA": da,
            "moz_api_hits": hits 

            }

def on_page_seo_audit_report(state: SEOCompetitiveAnalystSchema):
    data = state["client_website_data"]
    core = ModelFactory.create('chatgpt')
    llm = core.model()
    structured_llm = llm.with_structured_output(OnPageSeoAuditReport)
    system_prompt = create_on_page_audit_report().format(docs=data)
    res = structured_llm.invoke([SystemMessage(content=system_prompt)] + [HumanMessage(content="generate the on-page seo audit report")])
    query = res.get('report', "") 
    # query = "i am working but rightnow i am on rest."
    return {"on_page_audit_report": query}