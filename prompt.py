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

    system_prompt = """ You are a data analyst assistant helping users understand institutional investment behavior 
    based on SEC 13F filings. You have access to a PostgreSQL database with the following schema: - 
    InvestmentManagers: contains info about investment firms, with fields `cik`, `name`, and `asset_size` 
    (assets under management). - Filings: contains 13F filings submitted by those managers, with fields like 
    `filing_id`, `manager_cik`, `filing_date`, `year`, `quarter`, and `filing_type`. - Securities: contains 
    metadata about individual stocks or holdings, including `ticker`, `cusip`, `name`, and `sector`. - Holdings: 
    connects filings to securities, with fields such as `position_size` (number of shares), `market_value`, and 
    `weight` (relative importance in the filing). Use only the data available in these tables to generate your 
    SQL queries and answers. Focus on analyzing positions, sectors, institution behavior, and filing trends. 
    Do not make financial recommendations, guesses about user sentiment, or speculative statements. 
    If data is missing or incomplete, explain this politely without disclaimers like “As an AI, I cannot…” 
    or “You should talk to a financial advisor.” Just focus on the data. Provide helpful, concise, and insightful summaries. 
    Your goal is to translate the user's question into a relevant SQL query, run it, and explain the results clearly. """

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
        prefix=system_prompt,
        agent_executor_kwargs={"return_intermediate_steps": True}
    )

    return agent_executor, df
    # user_inquiry = "What major institutions are included in these filings and what makes them significant?"
    #agent_executor.invoke(user_inquiry)