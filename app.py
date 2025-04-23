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
from prompt import init_agent

# == INTEGRATING WITH PROMPT.PY ==
agent_executor, df = init_agent()

# == APP.PY NEW CODE == 

# page setup
st.set_page_config(page_title="FinBot")
st.title("FinBot Chat")
st.markdown("Ask about institutional investor behaviors and get answers derived from analyzing **13F filings**!")
with st.expander("ℹ️   What are 13F filings?", expanded=False):
    st.markdown("""
        **13F filings** are quarterly reports that institutional investment managers with over $100 million in assets must file with the Securities and Exchange Commision (SEC).
        
        These filings disclose:
        - Equity holdings
        - Investment strategies
        - Portfolio changes
        
        FinBot Chat analyzes these filings to help you identify trends, track specific investors, and understand market movements.
    """)

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

# sidebar
with st.sidebar:
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()
    # later include sample queries?

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