import time
import streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
import sqlite3
import pandas as pd
import os
import config # Put your API key in config.py

# == PROMPT.PY CODE TAKEN DIRECTLY ==

GEMINI_API_KEY = config.GEMINI_API_KEY
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", google_api_key=GEMINI_API_KEY, temperature=0)
df = pd.read_csv("13f_filings.csv")
conn = sqlite3.connect("testdatabase.db")

# Convert DataFrame to a SQLite table named "Filings"
df.to_sql("Filings", conn, if_exists='replace')
my_db = SQLDatabase.from_uri("sqlite:///testdatabase.db")

agent_executor = create_sql_agent(
    llm=llm,
    toolkit=SQLDatabaseToolkit(db=my_db, llm=llm),
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    verbose=True,
    agent_executor_kwargs={"return_intermediate_steps": True} # Added this line for chain of thought
)

# == APP.PY NEW CODE == 

# init streamlit msg stream
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    if message["role"] == "assistant" and message.get("chain"):
        with st.expander("Show chain of thought", expanded=False):
            for step in message["chain"]:
                st.write(step)
# prompt loop     
if prompt := st.chat_input("What's up?"):
    # write user message
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # generate assistant message
    start = time.time()
    with st.spinner("Thinking..."):
        try:
            result  = agent_executor.invoke(prompt)
            answer  = result["output"]
            chain   = result["intermediate_steps"]   # now present
        except Exception as e:
            answer, chain = f"[Error: {e}]", []       
    elapsed = time.time() - start

    with st.chat_message("assistant"):
        # expander shows elapsed time
        with st.expander(f"Thought for {elapsed:.2f} seconds", expanded=False):
            for step in chain:
                st.write(step)
        st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer, "chain": chain})