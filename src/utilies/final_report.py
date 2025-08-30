from src.utilies.generate_final_report import GenerateFinalReport
from src.scehma.agent import SEOCompetitiveAnalystSchema


def final_report(state : SEOCompetitiveAnalystSchema):
    backlinks = state['backlink_gap']
    keywords = state['keyword_metrice_list']
    competitors = state['competitors_list']
    on_page = state['on_page_audit_report']
    gen_report = GenerateFinalReport(on_page, keyword_gap=keywords, backlink_gap=backlinks, true_competitors=competitors)
    text = gen_report.merge_all_report()
    return {"final_report": text}


