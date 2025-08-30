from src.scehma.agent import SEOCompetitiveAnalystSchema
from src.utilies.keywords_metrice import KeywordsAnalysis

def keywords_metrice(state: SEOCompetitiveAnalystSchema):
    keywords = state['keyword_gap']
    kr = KeywordsAnalysis(keywords=keywords)
    report, keyword_list = kr.get_keyword_metrice()
    return {"keywords_metrice_report": report, "keyword_metrice_list": keyword_list}

