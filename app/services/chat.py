from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langchain_openai import ChatOpenAI
from app.core.config import settings, ModelType
from app.services.graph.graph_state import GraphState
from app.services.graph.graph_nodes import (
    reasoning_node,
    user_input_node,
    mysql_query_node,
    vectordb_query_node,
    both_db_node,
    response_node,
    determine_state
)
import os

from langsmith import traceable
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
class ChatService:
    def __init__(self):
        self.reasoning_graph = self._build_reasoning_graph()
        self.config = {"configurable": {"thread_id": "cheese_production"}}
        self.model = ChatOpenAI(
            model=ModelType.gpt4o,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def _build_reasoning_graph(self):
        workflow = StateGraph(state_schema=GraphState)
        
        workflow.add_node("reasoning", reasoning_node)
        workflow.add_node("user_input", user_input_node)
        workflow.add_node("mysql_query", mysql_query_node)
        workflow.add_node("vectordb_query", vectordb_query_node)
        workflow.add_node("response", response_node)
        workflow.add_node("both_db", both_db_node)
        workflow.add_conditional_edges(
            "reasoning",
            determine_state,
            {
                'complete': "response",
                'user_input': "user_input",
                "sql_query": "mysql_query",
                "vectordb_query": "vectordb_query",
                "both": "both_db",
                "self": "reasoning"
            }
        )
        workflow.add_edge(START, "reasoning")
        workflow.add_edge("user_input", "reasoning")
        workflow.add_edge("mysql_query", "reasoning")
        workflow.add_edge("vectordb_query", "reasoning")
        workflow.add_edge("both_db", "mysql_query")
        workflow.add_edge("both_db", "vectordb_query")
        workflow.add_edge("response", END)
        
        checkpointer = InMemorySaver()
        return workflow.compile(checkpointer=checkpointer)
    @traceable
    def process_message(self,state: GraphState,handler):
        final_state = self.reasoning_graph.invoke(state, config={"callbacks":[handler], "tags":["cheese productions"], **self.config})
        return final_state
    @traceable
    def user_input(self,user_answer: str, handler):
        final_state =self.reasoning_graph.invoke(Command(resume=user_answer), config={"callbacks":[handler], "tags":["cheese productions"], **self.config})
        return final_state

chat_service = ChatService()