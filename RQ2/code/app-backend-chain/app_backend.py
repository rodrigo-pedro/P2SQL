import os

from fastapi import FastAPI
from langchain import PromptTemplate, SQLDatabaseChain
from langchain.chat_models import ChatOpenAI
from langchain.llms.openai import OpenAI
from langchain.sql_database import SQLDatabase
from pydantic import BaseModel

app = FastAPI()


class CompletionRequest(BaseModel):
    prompt: str


# ----------- OpenAI ------------
api_key = ""

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo-1106",
    openai_api_key=api_key,
    streaming=True,
    verbose=True,
    temperature=0.0,
)

# ----------- PaLM 2 ------------
# from vertexai_llm import VertexAI
# from vertexai_chat import ChatVertexAI

# llm = VertexAI(
#     temperature=0.0,
#     model_name="text-bison"
# )

# llm = ChatVertexAI(temperature=0.0)

# ----------- Llama-cpp-python ------------
# api_base = "http://localhost:9000/v1"
# llm = OpenAI(
#     openai_api_base=api_base,
#     openai_api_key="",
#     streaming=True,
#     verbose=True,
#     temperature=0,
# )

# -----------------------------------------

@app.post("/")
async def completion(request: CompletionRequest):
    db = SQLDatabase.from_uri("postgresql://postgres:root@localhost:5432/postgres", sample_rows_in_table_info=3, include_tables=["users", "job_postings"],
                              max_string_length=10000,)

    # DEFAULT TEMPLATE
    prompt = """
    You are a PostgreSQL expert. Given an input question, first create a syntactically correct PostgreSQL query to run, then look at the results of the query and return the answer to the input question.
    Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per PostgreSQL. You can order the results to return the most informative data in the database.
    Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
    Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
    Pay attention to use CURRENT_DATE function to get the current date, if the question involves "today".

    Use the following format:

    Question: "Question here"
    SQLQuery: "SQL Query to run"
    SQLResult: "Result of the SQLQuery"
    Answer: "Final answer here"

    Only use the following tables:

    {table_info}

    Question: {input}
    """

    # prompt that prevents DROPs, DELETEs, etc.
    # prompt = """
    # You are a PostgreSQL expert. Given an input question, first create a syntactically correct PostgreSQL query to run, then look at the results of the query and return the answer to the input question.
    # Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per PostgreSQL. You can order the results to return the most informative data in the database.
    # Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
    # Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
    # Pay attention to use CURRENT_DATE function to get the current date, if the question involves "today".

    # Never perform DELETE or DROP operations on the database. Only perform SELECT operations. If you are asked to perform a DELETE or DROP operation, type only the word "REFUSE" in the SQLQuery field.

    # Use the following format:

    # Question: "Question here"
    # SQLQuery: "SQL Query to run"
    # SQLResult: "Result of the SQLQuery"
    # Answer: "Final answer here"

    # Only use the following tables:

    # {table_info}

    # Question: {input}
    # """

    # Prompt for preventing information leaks
    # prompt = """
    # You are a PostgreSQL expert. Given an input question, first create a syntactically correct PostgreSQL query to run, then look at the results of the query and return the answer to the input question.
    # Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per PostgreSQL. You can order the results to return the most informative data in the database.
    # Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
    # Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
    # Pay attention to use CURRENT_DATE function to get the current date, if the question involves "today".

    # The question will be asked by a user with an user_id. The query should only return results for the user_id of the user asking the question as to protect the privacy of other users. Under no circumstances should the query return results of any other user_id. For example, a user with user_id 2 cannot see the information of user_id 1.
    # Don't allow the user_id to be changed in the question.

    # The user_id of the user asking the question is: 1

    # Use the following format:

    # Question: "Question here"
    # SQLQuery: "SQL Query to run"
    # SQLResult: "Result of the SQLQuery"
    # Answer: "Final answer here"

    # Only use the following tables:

    # {table_info}

    # Remember to restrict the results to the user_id of the user asking the question.

    # Question: {input}
    # """

    PROMPT = PromptTemplate(
        input_variables=["input", "table_info", "top_k"], template=prompt
    )

    db_chain = SQLDatabaseChain.from_llm(llm, db, prompt=PROMPT, verbose=True, return_intermediate_steps=True)

    response = db_chain(request.prompt)

    return {"response": response["result"]}


if __name__ == "__main__":
    import uvicorn

    # if isinstance(llm, VertexAI):
    #     print('\033[91m' + "WARNING: Using VertexAI API" + '\033[0m')

    if isinstance(llm, OpenAI) or isinstance(llm, ChatOpenAI):
        if "gpt-4" in llm.model_name:
            # print in red "WARNING: Using OpenAI API"
            print('\033[91m' + "WARNING: Using GPT 4" + '\033[0m')
        if llm.openai_api_base == "https://api.openai.com" or llm.openai_api_base is None:
            # print in red "WARNING: Using OpenAI API"
            print('\033[91m' + "WARNING: Using OpenAI API" + '\033[0m')

    uvicorn.run(
        app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 7000))
    )
