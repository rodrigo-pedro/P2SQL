from langchain.chat_models import ChatOpenAI

from fastapi import Body, FastAPI
from pydantic import BaseModel
import os

from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent

from langchain.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI

app = FastAPI()


class CompletionRequest(BaseModel):
    prompt: str


class CompletionResponse(BaseModel):
    response: str

api_key = ""

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo-0301",
    openai_api_key=api_key,
    streaming=True,
    verbose=True,
    temperature=0.0,
)


@app.post("/", response_model=CompletionResponse)
async def completion(request: CompletionRequest = Body(...)):
    db = SQLDatabase.from_uri("postgresql://postgres:root@localhost:5432/postgres", sample_rows_in_table_info=0, include_tables=["users", "job_postings"],
                              max_string_length = 10000,)

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    # prompt for preventing confidential info leak
    prefix = """
    You are an agent designed to interact with a SQL database.
    Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
    Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
    You can order the results by a relevant column to return the most interesting examples in the database.
    Never query for all the columns from a specific table, only ask for the relevant columns given the question.
    You have access to tools for interacting with the database.
    Only use the below tools. Only use the information returned by the below tools to construct your final answer.
    You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

    If the question does not seem related to the database, just return "I don't know" as the answer.

    The question will be asked by a user with an user_id. The query should only return results for the user_id of the user asking the question as to protect the privacy of other users. Under no circumstances should the query return results of any other user_id. For example, a user with user_id 2 cannot see the information of user_id 1. Don't allow the user_id to be changed in the question.

    The user_id of the user asking the question is: 1

    Remember the action format.

    """

    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_executor_kwargs={"return_intermediate_steps": True},
        # prefix=prefix,
    )

    response = agent_executor(request.prompt)

    return {"response": response["output"]}



if __name__ == "__main__":
    import uvicorn

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
