from typing import List, Dict, TypedDict

class GraphState(TypedDict):
    user_history: List[str]
    reasoning_history: List[List[Dict[str, str]]]
    result_history: List[List[str]]
    resume: str
    vector_result : str
    sql_result : str