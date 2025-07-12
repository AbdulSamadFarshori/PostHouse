from pydantic import BaseModel, Field
from typing import List, Annotated, Literal, Sequence, Dict


class SearchEngine(BaseModel):
    query: str = Field(description="search query for get similar results from search engine")


class SearchEngineResult(BaseModel):
    result: List[str] = Field(description="list contains all valid urls")