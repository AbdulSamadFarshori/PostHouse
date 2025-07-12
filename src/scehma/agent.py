import operator 
from typing import List, Annotated, Sequence, Dict
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from operator import add

class WebSearchQuerySchema(TypedDict):
    query: str 

class CompetitorAnalystSchema(TypedDict):
    client_url: str 
    location: str 
    client_content: List[str] 
    industry: str 
    competitor_search_query: str
    competitor_contents: str  
    competitor_names: List[str] 
    competitor_urls: List[str] 
    # instructions: str 
    competitors_website_html_content: List[Dict]
    analyst_content: List[str]
    analyst_report: str
    report: List[str]

class ListCompanyNameSchema(TypedDict):
    names : List[str]

class AnalystOutputScemha(TypedDict):
    content: str


class WritePositionOutputSchema(TypedDict):
    content: str

class WriteSEOOutputSchema(TypedDict):
    content: str

class WriteEngagementOutputSchema(TypedDict):
    content: str

class WriteRecOutputSchema(TypedDict):
    content: str




    