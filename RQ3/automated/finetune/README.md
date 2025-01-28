# Mistral-7B Finetune

## Components

- [p2sql-model-mistral-7b-all-attacks-LANGCHAIN](./p2sql-model-mistral-7b-all-attacks-LANGCHAIN) - Finetuned Mistral-7B model using Langchain malicious prompts dataset to perform automated prompt discovery
- [finetune.py](./finetune.py) - Finetune script for Mistral-7B model using Langchain malicious prompts dataset
- [all_attacks_dataset_langchain.json](./all_attacks_dataset_langchain.json) - Dataset for finetuning in JSON form
- [generate_examples_gpt.py](./generate_examples_gpt.py) - Generate examples for finetuning using GPT
- [generate_examples_mistral_parallel.py](./generate_examples_mistral_parallel.py) - Generate examples for finetuning using Mistral-7B (requires GPU)
- [create_dataset_json.py](./create_dataset_json.py) - Take generated examples from the DB and create json dataset
- [test_RD1.py](./test_RD1.py) - Use the finetuned model to attempt RD1 attacks
- [test_RI1.py](./test_RI1.py) - Use the finetuned modelto attempt RI1 attacks
- [test_RI2.py](./test_RI2.py) - Use the finetuned model to attempt RI2 attacks
- [test_RI1_dataherald.py](./test_RI1_dataherald.py) - Use the finetuned model to attempt RI1 attacks in Dataherald

## Usage Notes

For the test scripts, make sure to start the red-team backend server before running the scripts. To see the setup instructions, refer to the following [README](../../red-team/README.md).
