import re
from fastapi import FastAPI
from langchain.chat_models import ChatOpenAI
from langchain import SQLDatabase
from langchain.agents import AgentType
from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain
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
db_uri = "postgresql://postgres:root@streamlit_agent-mrkl-db:5432/postgres"

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
    db = SQLDatabase.from_uri(database_uri=db_uri)

    llm = ChatOpenAI(
        model=request.model,
        openai_api_key=api_key,
        streaming=True,
        verbose=True,
        temperature=0.0,
    )

    db_chain = SQLDatabaseChain.from_llm(llm, db, return_intermediate_steps=True)


    final_answer = ""
    sql_queries = []
    error_message = ""
    # execution_successful = False # whether the execution ran without errors before the max number of attempts was reached

    MAX_ATTEMPTS = 3
    cur_attempt = 0

    def modified_db_chain_run(arg):
        response = db_chain(arg)
        for i in response["intermediate_steps"]:
            # if i is a dict that contains the key called "sql_cmd"
            if isinstance(i, dict) and "sql_cmd" in i:
                # save executed_query to the session state, so that we can read it later once the LLM has finished answering
                # executed_query is stored in a list because we might have multiple queries executed in a single run
                sql_queries.append(i["sql_cmd"])

        return response["result"] # output needs to only be the result, otherwise it breaks the agent

    tools = [
        # Tool(
        #     name="Search",
        #     func=search.run,
        #     description="useful for when you need to answer questions about current events. You should ask targeted questions",
        # ),
        # Tool(
        #     name="Calculator",
        #     func=llm_math_chain.run,
        #     description="useful for when you need to answer questions about math",
        # ),
        Tool(
            name="database",
            # func=db_chain.run,
            func=modified_db_chain_run,
            description="useful for when you need to answer questions about FooBar. Input should be in the form of a question containing full context",
        ),
    ]

    # agent = create_sql_agent(
    #     llm=llm,
    #     toolkit=toolkit,
    #     verbose=True,
    #     agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    #     agent_executor_kwargs={"return_intermediate_steps": True},
    # )
    mrkl = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True,)





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

            agent_output = mrkl(request.prompt)
            final_answer = agent_output["output"]
            error_message = "" # if there was an error before, reset it
            break
        except OutputParserException as e:
            error_message = f"Retried {MAX_ATTEMPTS} times. Error: {str(e)}."

    # reset stdout
    sys.stdout = sys.__stdout__
    captured_string = captured_output.getvalue()
    # print the captured string so that it shows up in the terminal
    print(captured_string)

    # # get the intermediate steps, which are between "Entering new AgentExecutor chain..." and "> Finished chain."
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
    # intermediate_str = re.sub(r'(Action:|Action Input:|Observation:|Thought:|Final Answer:)(\S)', r'\1 \2', intermediate_str)
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
