import re
from fastapi import FastAPI
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.schema.output_parser import OutputParserException
from pydantic import BaseModel
from sqlalchemy import exc
import io
import sys

app = FastAPI()

class CompletionRequest(BaseModel):
    prompt: str
    model: str = "gpt-3.5-turbo-1106"
    attack_type: str = ""


api_key = ""
db_uri = "postgresql://postgres:root@streamlit_agent-sql_db-db:5432/postgres"

# llm = ChatOpenAI(
#     model="gpt-3.5-turbo",
#     openai_api_key=api_key,
#     streaming=True,
#     verbose=True,
#     temperature=0.0,
# )

# llm = OpenAI(
#     openai_api_base=api_base,
#     openai_api_key=api_key,
#     streaming=True,
#     verbose=True,
#     temperature=0,
# )



def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

@app.post("/process_prompt")
async def completion(request: CompletionRequest):
    def configure_db(db_uri):
        return SQLDatabase.from_uri(database_uri=db_uri)


    db = configure_db(db_uri)

    llm = ChatOpenAI(
        model=request.model,
        openai_api_key=api_key,
        streaming=True,
        verbose=True,
        temperature=0.0,
    )

    toolkit = SQLDatabaseToolkit(db=db, llm=llm, )


    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        agent_executor_kwargs={"return_intermediate_steps": True},
    )



    final_answer = ""
    sql_queries = []
    error_message = ""

    MAX_ATTEMPTS = 3
    cur_attempt = 0

    # redirect stdout to a string. Used to capture the intermediate steps in a pretty format
    captured_output = io.StringIO()
    sys.stdout = captured_output

    # Sometimes LLM uses incorrect syntax, so we retry a few times
    while cur_attempt < MAX_ATTEMPTS:
        try:
            cur_attempt += 1
            sys.stdout = sys.__stdout__
            captured_output = io.StringIO() # reset stdout for every loop. This is needed in case there was an error before
            sys.stdout = captured_output

            agent_output = agent(request.prompt)
            final_answer = agent_output["output"]
            for step in agent_output["intermediate_steps"]:
                if step[0].tool == "sql_db_query": # add the query to the list of executed queries
                    sql_queries.append(step[0].tool_input)
            error_message = "" # if there was an error before, reset it
            break
        except OutputParserException as e:
            error_message = f"Retried {MAX_ATTEMPTS} times. Error: {str(e)}."


    # reset stdout
    sys.stdout = sys.__stdout__
    captured_string = captured_output.getvalue()
    # print the captured string so that it shows up in the terminal
    print(captured_string)

    # get the intermediate steps, which are between "Entering new AgentExecutor chain..." and "> Finished chain."
    intermediate_str = captured_string.split("Entering new AgentExecutor chain...")[1].split("> Finished chain.")[0]
    # remove the ANSI color codes from the string
    intermediate_str = escape_ansi(intermediate_str)
    # remove the beginning and trailing newlines
    intermediate_str = intermediate_str.strip()

    raw_intermediate_str = intermediate_str

    # Before every "Thought:" add a divider ---
    # intermediate_str = re.sub(r'(Thought:)', r'\n\n---\n\1', intermediate_str)
    intermediate_str = re.sub(r'(?<!Observation:\n)(?<!Thought:\n)\nThought:', '\n\n---\nThought:', intermediate_str)
    # make sure there is a space after every colon of Action:, Action Input:, Observation:, and Thought:
    intermediate_str = re.sub(r'(Action:|Action Input:|Observation:|Thought:|Final Answer:)(\S)', r'\1 \2', intermediate_str)
    # # enclose every Action:, Action Input:, Observation:, and Thought: in bold
    # intermediate_str = re.sub(r'(Action:|Action Input:|Observation:|Thought:|Final Answer:)', r'**\1**', intermediate_str)
    # escape colons, they sometimes get interpreted as emojis
    # intermediate_str = intermediate_str.replace(':', '\\:')

    print(f"Tried {cur_attempt} times")

    return {
        "final_answer": final_answer,
        "sql_queries": sql_queries,
        "intermediate_str": intermediate_str, # markdown intermediate_strings
        "raw_intermediate_str": raw_intermediate_str, # raw intermediate_strings
        "error_message": error_message,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7000)
