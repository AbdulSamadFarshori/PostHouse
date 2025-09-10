from src.scehma.agent import SEOCompetitiveAnalystSchema
from src.utilies.keywords_metrice import KeywordsAnalysis

def keywords_metrice(state: SEOCompetitiveAnalystSchema):
    keywords = state['keyword_gap']
    organic_keywords = state["suggested_organic_keywords"]
    kr = KeywordsAnalysis(keywords=keywords, organic_keywords=organic_keywords)
    report, keyword_list, hits = kr.get_keyword_metrice()
    return {"keywords_metrice_report": report, "keyword_metrice_list": keyword_list, "moz_api_hits": hits}

