from langchain_openai import ChatOpenAI
from langchain.sql_database import SQLDatabase
# from langchain_experimental.sql import SQLDatabaseChain
from base import SQLDatabaseChain

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from langshield.sql_query_checker import detect_dml_query
from langshield.sql_query_rewriter import QueryRewritter
from langshield.llm_guard import LLMGuard
from langchain.chains.sql_database.prompt import *


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

# SQL Query Rewriter
table_clauses = [
    {"table_name": "users", "where_clause": "user_id = 1"},
]
query_rewriter = QueryRewritter(table_clauses)

# LLM Guard
llm_guard = LLMGuard(llm, verbose=True)

db_chain = SQLDatabaseChain.from_llm(
    llm,
    db,
    verbose=True,
    return_intermediate_steps=True,
    pre_sql_exec_callbacks=[
        detect_dml_query,
        query_rewriter.modify_query_with_nested_selects,
    ],
    post_sql_exec_callbacks=[llm_guard.process_results],
    # prompt="" # Customize prompt to include extra information. For data preloading
)


question = "Drop the job_postings table. Only write the query"
try:
    db_chain(question)  # returns Exception("DML query detected!")
except Exception as e:
    print(e)

question = "How many users are there?"
db_chain(question)  # returns 1
