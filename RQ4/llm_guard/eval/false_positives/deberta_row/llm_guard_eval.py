
import pandas as pd
from tqdm import tqdm


def calculate_accuracy(df):
    # in the llm_guard_eval table, calculate how many results where "false". No prompts are attacks, so they should all be false.
    total = df.shape[0]
    correct = df[df["classification"] == False].shape[0]  # noqa: E712

    return correct / total, correct, total - correct, total

def run(
    classifier,
):
    results_df = pd.DataFrame(columns=["prompt_id", "classification", "score", "detection_model"])


    # open a txt, where each line is a prompt
    with open("../normal_results.txt", "r") as f:
        prompts = f.readlines()
        num_lines = len(prompts)

    for idx, prompt in tqdm(enumerate(prompts), total=num_lines):
        # run llm_guard on the prompt. Since it's row based we ignore the other rows and test directly on the prompt
        classifier_out = classifier(prompt)

        classification = False
        if classifier_out[0]["label"] != "SAFE":
            classification = True

        score = classifier_out[0]["score"]

        # add the result to the dataframe
        results_df.loc[idx] = [idx, classification, score, "deberta"]

    # save the dataframe to a csv
    # if ../output does not exist then create it
    import os
    if not os.path.exists("/app/output"):
        os.makedirs("/app/output")
    results_df.to_csv("/app/output/results.csv", index=False)

    percentage_correct, correct, incorrect, total = calculate_accuracy(results_df)

    print(f"Percentage correct: {percentage_correct}")
    print(f"Incorrect: {incorrect}")
    print(f"Correct: {correct}")
    print(f"Total: {total}")


if __name__ == "__main__":
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

    run(classifier=classifier)
