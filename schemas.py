from pydantic import BaseModel
from typing import List, Dict, Union

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    sql_query: str
    result: Union[List[Dict], Dict]
