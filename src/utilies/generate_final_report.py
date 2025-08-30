from src.utilies.factory import ModelFactory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from src.scehma.agent import ReportSchema
from src.utilies.prompts import generate_remaining_report_prompt

class GenerateFinalReport:
    def __init__(self, on_page, keyword_gap, backlink_gap, true_competitors):
        
        self.on_page_report = on_page
        self.keyword_gap = keyword_gap
        self.competitors = true_competitors
        self.backlink_gap = backlink_gap
        core = ModelFactory.create('chatgpt')
        self.llm = core.model()

    def generate_remaining_report(self):
        structured_llm = self.llm.with_structured_output(ReportSchema)
        system_prompt = generate_remaining_report_prompt().format(keywords=self.keyword_gap, backlinks=self.backlink_gap, competitors=self.competitors)
        final_prompt = [SystemMessage(content=system_prompt)] + [HumanMessage(content="generate the report.")]
        res = structured_llm.invoke(final_prompt)
        report = res.get("report", "")
        return report
    
    def merge_all_report(self):
        part_a = self.on_page_report
        part_b = self.generate_remaining_report()
        temp = f"{part_a} \n {part_b}"
        return temp

