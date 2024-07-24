from langchain_openai import ChatOpenAI
from langchain.sql_database import SQLDatabase
from toolkit import SQLDatabaseToolkit

# from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from langshield.sql_query_checker import detect_dml_query
from langshield.sql_query_rewriter import QueryRewritter
from langshield.llm_guard import LLMGuard


api_key = ""
db_uri = "postgresql://postgres:root@localhost:5432/postgres"


db = SQLDatabase.from_uri(db_uri, max_string_length=10000)

llm = ChatOpenAI(
    model="gpt-3.5-turbo-1106",
    openai_api_key=api_key,
    streaming=True,
    verbose=True,
    temperature=0.0,
)

table_clauses = [
    {"table_name": "users", "where_clause": "user_id = 1"},
]
query_rewriter = QueryRewritter(table_clauses)

llm_guard = LLMGuard(llm, verbose=True)

toolkit = SQLDatabaseToolkit(
    db=db,
    llm=llm,
    pre_sql_exec_callbacks=[
        detect_dml_query,
        query_rewriter.modify_query_with_nested_selects,
    ],
    post_sql_exec_callbacks=[llm_guard.process_results_no_user_question],
)


agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_executor_kwargs={
        "return_intermediate_steps": True,
        "handle_parsing_errors": True,
    },
    # suffix="" # Add extra suffix to the prompt, for data preloading
)


question = "How many users are there?"

agent_executor(question)
