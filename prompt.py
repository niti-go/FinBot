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

def init_agent(): 
    GEMINI_API_KEY = config.GEMINI_API_KEY
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

    #genai.configure(api_key=GEMINI_API_KEY)
    # for m in genai.list_models():
    #     print(m.name, "-", m.supported_generation_methods)

    #llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name="gpt-3.5-turbo", temperature=0)

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
        agent_executor_kwargs={"return_intermediate_steps": True}
    )

    return agent_executor, df
    # user_inquiry = "What major institutions are included in these filings and what makes them significant?"
    #agent_executor.invoke(user_inquiry)