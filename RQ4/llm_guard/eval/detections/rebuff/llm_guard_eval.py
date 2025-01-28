import pandas as pd
import sqlalchemy
from tqdm import tqdm
from langchain_openai import ChatOpenAI
import json
from rebuff import RebuffSdk
import time


def run(
    rb,
    model_name: str,
    start_prompt_id: int = 0,
    end_prompt_id: int = 0,
):
    # 1. Read from the database
    # 2. for each row, get the prompt if the attack type is RD1 or RD2, else get the injected prompt
    # 3. run "pass" for now
    engine = sqlalchemy.create_engine(
        "postgresql://postgres:root@pg_container:5432/postgres"
    )

    if end_prompt_id == 0:
        df = pd.read_sql_query(
            f"SELECT * FROM prompts WHERE attack_type in ('RI1', 'RI2') AND id >= {start_prompt_id} ORDER by id",
            engine,
        )
    else:
        df = pd.read_sql_query(
            f"SELECT * FROM prompts WHERE attack_type in ('RI1', 'RI2') AND id >= {start_prompt_id} AND id <= {end_prompt_id} ORDER by id",
            engine,
        )

    results_df = pd.DataFrame(columns=["prompt_id", "classification", "detection_model"])

    timer_total_time_start = time.time()

    for _, row in tqdm(df.iterrows(), total=df.shape[0]):
        prompt = row["injected_prompt"]

        # we only captured the injected prompt itself. We need to encapsulate it in the query results with the normal database entries.
        # Because the query is always the same, we can just hardcode it here.
        results = f"[('We need a product manager',), ('We are looking for a software engineer to join our team',), ('{prompt}',)]"

        result = ""
        while True:
            try:
                result = rb.detect_injection(results, check_vector=False, check_llm=True, check_heuristic=False)
                break
            except Exception as e:
                print(e)
                print("Retrying...")

        output = False
        if result.injection_detected:
            print("Possible injection detected.")
            output = True

        # after running, add the result to the database into the llm_guard_eval table
        # add_result_to_database(
        #     engine, row["id"], output, "rebuff gpt-3.5-turbo-1106"
        # )

        results_df.loc[row["id"]] = [row["id"], output, f"rebuff {model_name}"]


    timer_total_time_end = time.time()

    # save the results to a csv file
    results_df.to_csv("results.csv")

    print(f"Total time: {timer_total_time_end - timer_total_time_start} seconds")
    print(f"Average time per iteration: {(timer_total_time_end - timer_total_time_start) / df.shape[0]} seconds")
    total = df.shape[0]
    # all classifications are true, because we are only testing attack prompts
    correct = results_df[results_df["classification"] == True].shape[0]
    accuracy = correct / total
    print("Accuracy: " + str(accuracy))


    with open("stats.json", "w") as f:
        data = {
            "total_time": timer_total_time_end - timer_total_time_start,
            "average_time_per_iteration": (timer_total_time_end - timer_total_time_start) / df.shape[0],
            "accuracy": accuracy
        }
        json.dump(data, f, indent=4)

    engine.dispose()


if __name__ == "__main__":
    import argparse, os

    # For local testing
    # os.environ["OPENAI_API_KEY"] = ""

    # For docker script
    parser = argparse.ArgumentParser(description="Run LLM Guard evaluation.")
    parser.add_argument("--model-name", type=str, default="gpt-3.5-turbo-1106", help="Model name.")
    args = parser.parse_args()

    rb = RebuffSdk(
        openai_apikey=os.environ["OPENAI_API_KEY"],
        pinecone_apikey="",
        pinecone_index="",
        # openai_model="gpt-3.5-turbo-1106" # For local testing
        # openai_model="gpt-4-1106-preview" # For local testing
        openai_model=args.model_name # For docker script
    )

    run(rb=rb, model_name=args.model_name)
