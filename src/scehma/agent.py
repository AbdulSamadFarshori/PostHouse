import operator 
from typing import List, Annotated, Sequence, Dict, Union
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from operator import add

class SEOCompetitiveAnalystSchema(TypedDict):
    
    client_url: str
    track: Union[List, str]
    location: str
    industry: str
    client_DA: int
    client_website_data : List[str]
    on_page_audit_report : str
    client_keywords : List[str]
    client_backlinks : List[str]
    competitors_list : List[Dict]
    true_competitors : str
    keyword_gap : List
    backlink_gap : List
    keyword_metrice_list: List
    keyword_metrice_report: str
    final_report: str
    

class IndustryClassification(TypedDict):
    industry: str

class SearchQuery(TypedDict):
    query: str

class ClassifySearchOuput(TypedDict):
    urls: List[Dict]

class OnPageSeoAuditReport(TypedDict):
    report : str


class ReportSchema(TypedDict):
    report : str