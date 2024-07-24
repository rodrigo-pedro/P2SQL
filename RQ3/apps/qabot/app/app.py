import io
import sys
from fastapi import FastAPI
from pydantic import BaseModel
from qabot import ask_file
import os
import re
import pandas as pd

app = FastAPI()

class CompletionRequest(BaseModel):
    prompt: str
    model: str = "gpt-3.5-turbo-1106"
    attack_type: str = ""

class InjectionRequest(BaseModel):
    injected_prompt: str
    id: int

# llm = ChatOpenAI(
#     model="gpt-3.5-turbo",
#     openai_api_key=api_key,
#     streaming=True,
#     verbose=True,
#     temperature=0.0,
# )

def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)


#CSV_FILE = './customer.csv'
CSV_FILE = './job-postings.csv'

os.environ['OPENAI_API_KEY'] = ""

@app.post("/process_prompt")
async def completion(request: CompletionRequest):
    captured_output = io.StringIO()
    sys.stdout = captured_output


    result = ask_file(request.prompt, CSV_FILE, model_name=request.model, verbose=True)

    sys.stdout = sys.__stdout__
    captured_string = captured_output.getvalue()
    # print the captured string so that it shows up in the terminal
    print(captured_string)

    intermediate_str = captured_string
    raw_intermediate_str = captured_string

    # There is a "query" entry in the results, but it only shows up sometimes. Very odd.
    sql_queries = re.findall(r"""🤖 execute_sql\n\{\s*'query':\s*(?:'|")(.*?)(?:'|")\s*\}""", captured_string, re.DOTALL)

    # escape colons, they sometimes get interpreted as emojis
    # intermediate_str = intermediate_str.replace(':', '\\:')
    # # escape >, it sometimes gets interpreted as a blockquote
    # intermediate_str = intermediate_str.replace('>', '\\>')

    # include both the summary and the detail
    final_answer = f"**Summary:** {result['summary']}\n\n**Detail:** {result['detail']}" # type: ignore

    return {
        "final_answer": final_answer, # type: ignore
        "sql_queries": sql_queries, # type: ignore
        "intermediate_str": intermediate_str,
        "raw_intermediate_str": raw_intermediate_str,
        # "error_message": ""
    }

@app.post("/inject_prompt")
def inject_prompt(request: InjectionRequest):
    df = pd.read_csv(CSV_FILE)

    # Check if the customer_id exists in the DataFrame
    #if request.id in df['customer_id'].values:
    if request.id in df['job_id'].values:
        # Update the biography for the specified customer_id

        #df.loc[df['customer_id'] == request.id, 'biography'] = request.injected_prompt

        df.loc[df['job_id'] == request.id, 'description'] = request.injected_prompt

        # Save the updated DataFrame back to CSV
        df.to_csv(CSV_FILE, index=False)
        #print(f"Biography updated for customer_id {request.id}")
        print(f"Description updated for job_id {request.id}")
    else:
        #print(f"No customer found with customer_id {request.id}")
        print(f"No job found with job_id {request.id}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7000)
