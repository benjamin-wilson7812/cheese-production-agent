import sys, os;
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from langgraph.types import interrupt
from langchain_openai import ChatOpenAI
from app.core.config import settings, ModelType
from app.core.prompt_templates.generate_reasoning_step import reasoning_prompt
from app.db.vectordb import vector_db
from app.db.mysql import mysql_db
from .graph_state import GraphState
from langchain_core.callbacks.manager import (
    dispatch_custom_event,
)
model = ChatOpenAI(
    model=ModelType.gpt4o,
    openai_api_key=settings.OPENAI_API_KEY
)
def cut(sen, bound = 2000):
    if len(sen)>=bound:
        return sen[:bound]+"\n\n... ... ..."
    else:
        return sen
def reasoning_node(state: GraphState):
    #Result add
    result_add_flag = False
    try:
        if state["reasoning_history"][-1][-1]["state"] == "self":
            state["result_history"][-1].append("")
            result_add_flag =True
        elif state["reasoning_history"][-1][-1]["state"] == "both":
            state["result_history"][-1].append(state["sql_result"]+ "\n" + state["vector_result"])
            dispatch_custom_event("step_result", {"data": cut(state["sql_result"])+ "\n\n" + cut(state["vector_result"]), "type": "both"})
            result_add_flag =True
        elif state["reasoning_history"][-1][-1]["state"] == "sql_query":
            state["result_history"][-1].append(state["sql_result"])
            dispatch_custom_event("step_result", {"data": cut(state["sql_result"]), "type": "sql_query"})
            result_add_flag =True
        elif state["reasoning_history"][-1][-1]["state"] == "vectordb_query":
            state["result_history"][-1].append(state["vector_result"])
            dispatch_custom_event("step_result", {"data": cut(state["vector_result"]), "type": "vectordb_query"})
            result_add_flag =True
    except:
        pass
    #Get next reasoning
    history = ""
    for i in range(len(state["user_history"])):
        history += "user: "+state["user_history"][i]+"\n"
        if len(state["reasoning_history"][i]) != 0:
            history += "assistant:\nThe reasoning step executed is following."
            for j in range(len(state["reasoning_history"][i])):
                history += str(state["reasoning_history"][i][j])+"\n"
                if i == len(state["user_history"])-1:
                    if state["reasoning_history"][i][j]["state"] == "user_input":
                        history += "The user input of this step is following."
                    elif state["reasoning_history"][i][j]["state"] == "vectordb_query" or "sql_query" or "both":
                        history += "The result of this step is following."
                    history += state["result_history"][i][j]
    context = reasoning_prompt.format(query=history)
    response = model.invoke(context)
    state["reasoning_history"][-1].append(json.loads(response.content.strip('`').replace("json", "")))
    dispatch_custom_event("reasoning_step", {"data": state["reasoning_history"][-1][-1]})
    #Return
    if result_add_flag:
        return {
            "reasoning_history": state["reasoning_history"],
            "result_history": state["result_history"]
            }
    else:
        return {
            "reasoning_history": state["reasoning_history"]
            }

def mysql_query_node(state: GraphState):
    #Case of using both sql and vectordb
    if state["reasoning_history"][-1][-1]["state"] == "both":
        #Retrieve data
        query = state["reasoning_history"][-1][-1]['query']["sql"]
        result = mysql_db.query(query)
        #Return
        return {
            "sql_result": "This is result of sql query.\n" + str(result)
            }
    #Case of using only sql
    else:
        #Retrieve data
        query = state["reasoning_history"][-1][-1]['query']
        result = mysql_db.query(query)
        #Return
        return {
            "sql_result": str(result)
            }

def vectordb_query_node(state: GraphState):
    #Case of using both sql and vectordb
    if state["reasoning_history"][-1][-1]["state"] == "both":
        #Retrieve data
        query = state["reasoning_history"][-1][-1]['query']["vectordb"]
        result = vector_db.query(query, top_k = 5)
        #Return
        return {
            "vector_result": "This is result of vector db search.\n" + result
            }
    #Case of using only vectordb
    else:
        #Retrieve data
        query = state["reasoning_history"][-1][-1]['query']
        result = vector_db.query(query, top_k = 5)
        #Return
        return {
            "vector_result": result 
            }

def both_db_node(state: GraphState):
    return {}

def determine_state(state: GraphState):
    return state["reasoning_history"][-1][-1]["state"]

def response_node(state: GraphState):
    state["result_history"][-1].append("")
    #Return
    return {
        "result_history" : state["result_history"]
        }

def user_input_node(state: GraphState):
    user_input = interrupt({
        "input" : state.get("resume","")
    })
    state["result_history"][-1].append(user_input)
    dispatch_custom_event("step_result", {"data": user_input, "type": "input"})
    return {
        "result_history" : state["result_history"]
        }