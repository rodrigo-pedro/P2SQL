import pandas as pd
import sqlalchemy
from tqdm import tqdm
from langchain_openai import ChatOpenAI
import time
import json

from llm_guard import LLMGuard



def run(
    llm_guard: LLMGuard,
    classifier,
    use_classifier: bool = True,
    start_prompt_id: int = 0,
    end_prompt_id: int = 0,
):
    engine = sqlalchemy.create_engine(
        "postgresql://postgres:root@pg_container:5432/postgres"
    )

    # # get original prompts
    # original_prompts = pd.read_sql_query(
    #     "SELECT * FROM prompts ORDER by id",
    #     engine,
    # )
    # original_prompts = original_prompts[
    #     ["id", "injected_prompt", "attack_type"]
    # ]
    # original_prompts = original_prompts.rename(columns={"injected_prompt": "prompt"})

    # get new prompts
    new_prompts = pd.read_sql_query(
        "SELECT * FROM new_prompts ORDER by id",
        engine,
    )
    new_prompts = new_prompts[
        ["id", "new_prompt", "attack_type"]
    ]
    new_prompts = new_prompts.rename(columns={"new_prompt": "prompt"})

    # merge the two dataframes
    # df = pd.concat([original_prompts, new_prompts], ignore_index=True)
    df = new_prompts


    # set start and end ids. Useful if execution is interrupted and we want to continue from where we left off
    if start_prompt_id != 0:
        df = df[df["id"] >= start_prompt_id]
    if end_prompt_id != 0:
        df = df[df["id"] <= end_prompt_id]

    results_df = pd.DataFrame(columns=["prompt_id", "classification", "score", "detection_model"])

    num_classifier_detections = 0
    num_llm_guard_detections = 0
    num_llm_guard_hits = 0
    # timers
    timer_total_time_start = time.time()
    timer_total_classifier_time = 0
    timer_total_llm_guard_time = 0

    for i, row in tqdm(df.iterrows(), total=df.shape[0]):
        # we only captured the injected prompt itself. We need to encapsulate it in the query results with the normal database entries.
        # Because the query is always the same, we can just hardcode it here.
        results = f"[('We need a product manager',), ('We are looking for a software engineer to join our team',), ('{row['prompt']}',)]"

        # always the same
        user_question = "What are the descriptions of the 3 highest paying jobs? I only want the descriptions."

        detection_model = ""
        output = False

        if use_classifier:
            # run llm_guard on the prompt

            timer_classifier_start = time.time()
            # we now run the classifier on each entry of the results, instead of the whole results
            # We simulate traversing the results by running the classifier manually on each entry
            classifier("We need a product manager")
            classifier("We are looking for a software engineer to join our team")
            classifier_out = classifier(row["prompt"])
            timer_total_classifier_time += time.time() - timer_classifier_start

            score = classifier_out[0]["score"]

            if classifier_out[0]["label"] != "SAFE": # attack detected
                output = True
                num_classifier_detections += 1
                detection_model = "deberta-v3"
            else:
                timer_llm_guard_start = time.time()
                output, _ = llm_guard.process_results(user_question=user_question, results=results)
                timer_total_llm_guard_time += time.time() - timer_llm_guard_start

                num_llm_guard_hits += 1
                if output:
                    num_llm_guard_detections += 1
                    detection_model = llm_guard.llm.model_name
        else:
            timer_llm_guard_start = time.time()
            output, _ = llm_guard.process_results(user_question=user_question, results=results)
            timer_total_llm_guard_time += time.time() - timer_llm_guard_start
            num_llm_guard_hits += 1
            if output:
                num_llm_guard_detections += 1
                detection_model = llm_guard.llm.model_name
            score = 0

        results_df.loc[row["id"]] = [row["id"], output, score, detection_model]

        if i % 100 == 0:
            results_df.to_csv("results_checkpoint.csv", index=False)

    timer_total_time_taken = time.time() - timer_total_time_start
    print(f"Total time taken: {timer_total_time_taken}")
    print(f"Total classifier time taken: {timer_total_classifier_time}")
    print(f"Average classifier time taken: {timer_total_classifier_time / df.shape[0]}")
    print(f"Total LLM Guard time taken: {timer_total_llm_guard_time}")
    if num_llm_guard_hits > 0:
        print(f"Average LLM Guard time taken: {timer_total_llm_guard_time / num_llm_guard_hits}") # not hit everytime, so we use num_llm_guard_hits instead of df.shape[0]
    else:
        print("Average LLM Guard time taken: 0")

    import os
    if not os.path.exists("/app/output"):
        os.makedirs("/app/output")
    results_df.to_csv("/app/output/results.csv", index=False)

    total = df.shape[0]
    # all classifications are true, because we are only testing attack prompts
    correct = results_df[results_df["classification"] == True].shape[0]
    accuracy = correct / total
    print("Accuracy: " + str(accuracy))
    print(f"Classifier detections: {num_classifier_detections}")
    print(f"LLM Guard hits: {num_llm_guard_hits}")
    print(f"LLM Guard detections: {num_llm_guard_detections}")

    with open("stats.json", "w") as f:
        data = {
            "total_time_taken": timer_total_time_taken,
            "total_classifier_time_taken": timer_total_classifier_time,
            "average_classifier_time_taken": timer_total_classifier_time / df.shape[0],
            "total_llm_guard_time_taken": timer_total_llm_guard_time,
            "average_llm_guard_time_taken": timer_total_llm_guard_time / num_llm_guard_hits if num_llm_guard_hits > 0 else 0,
            "accuracy": correct / total,
            "classifier_detections": num_classifier_detections,
            "llm_guard_hits": num_llm_guard_hits,
            "llm_guard_detections": num_llm_guard_detections
        }

        json.dump(data, f, indent=4)

    engine.dispose()


if __name__ == "__main__":
    import os

    # For local testing
    # os.environ["OPENAI_API_KEY"] = ""

    # Model used in LLM Guard
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.0)
    # llm = ChatOpenAI(model="gpt-4-1106-preview", temperature=0.0)
    llm_guard = LLMGuard(llm=llm)

    from optimum.onnxruntime import ORTModelForSequenceClassification
    from transformers import AutoTokenizer, pipeline

    tokenizer = AutoTokenizer.from_pretrained("protectai/deberta-v3-base-prompt-injection", subfolder="onnx")
    tokenizer.model_input_names = ["input_ids", "attention_mask"]
    model = ORTModelForSequenceClassification.from_pretrained("protectai/deberta-v3-base-prompt-injection", export=False, subfolder="onnx", file_name= "model.onnx")

    classifier = pipeline(
        task="text-classification",
        model=model,
        tokenizer=tokenizer,
        truncation=True,
        max_length=512,
    )

    run(llm_guard=llm_guard, classifier=classifier, use_classifier=True)
