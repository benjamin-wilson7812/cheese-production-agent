import streamlit as st
from app.services.chat import chat_service
from app.services.graph.graph_state import GraphState
from langchain_core.callbacks import BaseCallbackHandler
from typing import Any, Dict, List, Optional
from uuid import UUID
class StreamHandler(BaseCallbackHandler):
    def on_custom_event(
        self,
        name: str,
        data: Any,
        *,
        run_id: UUID,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        # print(
        #     f"Received event {name} with data: {data}, with tags: {tags}, with metadata: {metadata} and run_id: {run_id}"
        # )
        if name == "reasoning_step":
            if data["data"]["state"] != "user_input":
                if data["data"]["state"] == "complete":
                    st.session_state["history"].append({"role": "assistant", "content": "--- Reasoning STEP ---\n\n" + data["data"]["reasoning_step_description"] + "\n\nThe reasoning ends. Let's generate final response!\n\n"})
                    st.session_state["history"].append({"display":"markdown", "role": "assistant", "content": str(data["data"]["responds"])})
                    st.chat_message("assistant").write("--- Reasoning STEP ---\n\n" + data["data"]["reasoning_step_description"] + "\n\nThe reasoning ends. Let's generate final response!\n\n")
                    st.markdown(data["data"]["responds"], unsafe_allow_html= True)
                elif data["data"]["state"] == "self":
                    st.session_state["history"].append({"role": "assistant", "content": "--- Reasoning STEP ---\n\n" + data["data"]["reasoning_step_description"] + "\n\nThis reasoning step is executed by AI"})
                    st.chat_message("assistant").write("--- Reasoning STEP ---\n\n" + data["data"]["reasoning_step_description"] + "\n\nThis reasoning step is executed by AI")
                elif data["data"]["state"] == "sql_query":
                    st.session_state["history"].append({"role": "assistant", "content": "--- Reasoning STEP ---\n\n" + data["data"]["reasoning_step_description"] + "\n\nThe sql query is used in this step." + "\n\nSql query is '" + data["data"]["query"] + "'"})
                    st.chat_message("assistant").write("--- Reasoning STEP ---\n\n" + data["data"]["reasoning_step_description"] + "\n\nThe sql query is used in this step." + "\n\nSql query is '" + data["data"]["query"] + "'")
                elif data["data"]["state"] == "vectordb_query":
                    st.session_state["history"].append({"role": "assistant", "content": "--- Reasoning STEP ---\n\n" + data["data"]["reasoning_step_description"] + "\n\nThe vector db is used in this step." + "\n\nI'v done search with '" + data["data"]["query"] + "'"})
                    st.chat_message("assistant").write("--- Reasoning STEP ---\n\n" + data["data"]["reasoning_step_description"] + "\n\nThe vector db is used in this step." + "\n\nI'v done search with '" + data["data"]["query"] + "'")
                elif data["data"]["state"] == "both":
                    st.session_state["history"].append({"role": "assistant", "content": "--- Reasoning STEP ---\n\n" + "This reasoning step use mysql database and vector db both.\n\n" + data["data"]["reasoning_step_description"] + "Sql query used is '" + data["data"]["query"]["vectordb"] + "', and vector db search query is '" + data["data"]["query"]["vectordb"] + "'"})
                    st.chat_message("assistant").write("--- Reasoning STEP ---\n\n" + "This reasoning step use mysql database and vector db both.\n\n" + data["data"]["reasoning_step_description"] + "\n\nSql query used is '" + data["data"]["query"]["sql"] + "', and vector db search query is '" + data["data"]["query"]["vectordb"] + "'\n\n")
            else:
                st.session_state["history"].append({"role": "assistant", "content": "--- Reasoning STEP ---\n\n" + "Information is not enough and ask human input\n\n" + data["data"]["reasoning_step_description"]})
                st.chat_message("assistant").write("--- Reasoning STEP ---\n\n" + "Information is not enough and ask human input\n\n" + data["data"]["reasoning_step_description"])
        else:
            if data["type"] == "input":
                st.session_state["history"].append({"role": "assistant", "content": "User input '" + data["data"]+"'"})
                st.chat_message("assistant").write("User input '" + data["data"]+"'")
            elif data["type"] == "both":
                st.session_state["history"].append({"role": "assistant", "content": "The result is following.\n\n '" + data["data"]+"'"})
                st.chat_message("assistant").write("The result is following.\n\n '" + data["data"]+"'")
            elif data["type"] == "sql_query":
                st.session_state["history"].append({"role": "assistant", "content": "These are result of mysql query.\n\n '" + data["data"]+"'"})
                st.chat_message("assistant").write("These are result of mysql query.\n\n '" + data["data"]+"'")
            elif data["type"] == "vectordb_query":
                st.session_state["history"].append({"role": "assistant", "content": "These are result of vector db search.\n\n '" + data["data"]+"'"})
                st.chat_message("assistant").write("These are result of vector db search.\n\n '" + data["data"]+"'")
handler=StreamHandler()

gradient_text_html = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700;900&display=swap');

.snowchat-title {
  font-family: 'Poppins', sans-serif;
  font-weight: 900;
  font-size: 2.5em;
  background: linear-gradient(90deg, #ff6a00, #ffffff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3);
  margin: 0;
  padding: 20px 0;
  text-align: center;
}
.snowchat-ico {
  font-family: 'Poppins', sans-serif;
  font-weight: 900;
  font-size: 2.5em;
  margin: 0;
  padding: 20px 0;
}
</style>
<div><div class="snowchat-title">Cheese Production Agent</div></div>
"""
st.markdown(gradient_text_html, unsafe_allow_html=True)
if not "message" in st.session_state:
    state = GraphState(
        user_history=[],
        reasoning_history=[],
        result_history=[]
    )
    st.session_state["message"] = state

if not "history" in st.session_state:
    st.session_state["history"] =[]
    st.session_state["history"].append({"role": "assistant", "content": "I am cheese production agent👋"})
for msg in st.session_state.history:
    if "display" in msg:
        st.markdown(msg["content"], unsafe_allow_html=True)
    else:
        st.chat_message(msg["role"]).write(msg["content"])
        

st.sidebar.title(":chart_with_upwards_trend: Trace by Langsmith")
st.sidebar.link_button("Go to Langsmith board", "https://smith.langchain.com/o/5c243fe0-83fe-433a-ac45-ae1845fcc353/dashboards/projects/c1b56000-22ec-4149-8bba-23286fd6c1bd")
st.sidebar.header("", divider=True)
st.sidebar.title("Agent Graph")
st.sidebar.image("graph.png", width = 2500)
st.sidebar.header("", divider=True)


def message_input_init(prompt):
    st.session_state["message"]["user_history"].append(prompt)
    st.session_state["message"]["reasoning_history"].append([])
    st.session_state["message"]["result_history"].append([])
    
if prompt := st.chat_input("Query:"):
    try:
        if len(st.session_state["message"]["user_history"]) == 0 or st.session_state["message"]["reasoning_history"][-1][-1]["state"] != "user_input":
            st.session_state.history.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            message_input_init(prompt)
            with st.spinner("Thinking..."):
                response = chat_service.process_message(st.session_state["message"],handler)
                if response:
                    pass
        else:
            with st.spinner("Thinking..."):
                response = chat_service.user_input(prompt,handler)
                if response:
                    st.session_state["message"] =  GraphState(
                                                        user_history=[],
                                                        reasoning_history=[],
                                                        result_history=[]
                                                    )
                    st.session_state["message"] = response
    except:
        st.session_state["history"].append({"role": "assistant", "content": "There are wrong problem in system or communication."})
        st.chat_message("assistant").write("There are wrong problem in system or communication.")