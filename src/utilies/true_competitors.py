from src.utilies.find_competitors import FindTrueCompetitors
from src.scehma.agent import SEOCompetitiveAnalystSchema

def find_true_competitors(state: SEOCompetitiveAnalystSchema):
    url = state['client_url']
    loc = state['location']
    docs = state['client_website_data']
    client_keywords = state['client_keywords']
    comp = FindTrueCompetitors(docs=docs, location=loc, root_url=url, client_keywords=client_keywords)
    industry, report, arr, client_keywords, total_hit = comp.main()
    return {'industry': industry, 'true_competitors': report, 'competitors_list': arr, 'client_keywords':client_keywords, 'moz_api_hits':total_hit}