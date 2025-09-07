from pydantic import BaseModel, Field
from typing import List

class PageRegisterInput(BaseModel):
    id: str
    author: str
    local_url: str
    text: str

class PageRegisterResponse(BaseModel):
    id: str
    success: bool

class SearchQuery(BaseModel):
    query: str
    top_k: int = Field(8, gt=0)

class SearchResult(BaseModel):
    id: str
    author: str
    local_url: str
    distance: float

class SearchResponse(BaseModel):
    results: List[SearchResult]
    
class PageUnregister(BaseModel):
    id: str
class PageUnregisterResponse(BaseModel):
    id: str
    author: str
    local_url: str
    success: bool