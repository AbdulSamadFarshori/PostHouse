from src.utilies.get_competitors_keywords import CompetitorsAnalysis
from src.scehma.agent import SEOCompetitiveAnalystSchema

def keywords_backlinks_gap(state: SEOCompetitiveAnalystSchema):
    client_backlink = state["client_backlinks"]
    client_keywords = state["client_keywords"]
    true_competitors = state["competitors_list"]
    client_da = state["client_DA"]
    industry = state["industry"]
    ca = CompetitorsAnalysis(true_competitors=true_competitors, 
                             client_DA=client_da,
                             client_keywords=client_keywords, 
                             industry=industry, client_backlinks=client_backlink)
    keyword_gap, backlink_gap = ca.main()
    return {"keyword_gap":keyword_gap, "backlink_gap": backlink_gap}
