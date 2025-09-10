from src.utilies.get_competitors_keywords import CompetitorsAnalysis
from src.scehma.agent import SEOCompetitiveAnalystSchema

def keywords_backlinks_gap(state: SEOCompetitiveAnalystSchema):
    client_backlink = state["client_backlinks"]
    client_keywords = state["client_keywords"]
    true_competitors = state["competitors_list"]
    client_organic_keywords = state["top_client_organic_keywords"]
    client_da = state["client_DA"]
    industry = state["industry"]
    business_type = "any"
    ca = CompetitorsAnalysis(true_competitors=true_competitors, 
                             client_DA=client_da,
                             client_keywords=client_keywords,
                             client_organic_keywords=client_organic_keywords,
                             industry=industry, 
                             client_backlinks=client_backlink, 
                             business_type=business_type
                             )
    keyword_gap, backlink_gap, organic_keywords, hits = ca.main()
    return {"keyword_gap":keyword_gap, "backlink_gap": backlink_gap, "suggested_organic_keywords": organic_keywords, "moz_api_hits": hits}
