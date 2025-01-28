# Evaluation of multiple LLM Guard implementations

Runs accuracy evaluations of 4 LLM Guard implementations and Rebuff (https://github.com/protectai/rebuff) on 60 malicious prompts. The implementations are:

1. [Only Results](only_results/): Only the SQL query results are forwarded to the LLM.
2. [Question and Results](question_results/): Both the user question and the SQL query results are forwarded to the LLM.
3. [Question Results and Thought (Deberta Full)](question_results_thought_deberta_full/): The user question and SQL query results are forwarded to the LLM. The LLM is also instructed to generate a textual thought before determining if a prompt is malicious. This implementation optionally uses the [deberta-v3-base-prompt-injection](https://huggingface.co/protectai/deberta-v3-base-prompt-injection) model for detection of malicious prompts with the entire query results for lower latency and cost.
4. [Question Results and Thought (Deberta Row)](question_results_thought_deberta_row/): The user question and SQL query results are forwarded to the LLM. The LLM is also instructed to generate a textual thought before determining if a prompt is malicious. This implementation optionally uses the [deberta-v3-base-row-prompt-injection](https://huggingface.co/protectai/deberta-v3-base-row-prompt-injection) model over each row of the query results.
5. [Rebuff](rebuff/): We test Rebuff as a baseline for comparison.

This experiment also tests the latency and number of LLM calls for the Question Results and Thought implementation without DeBERTA, with DeBERTA on the entire query results, and with DeBERTA on each row of the query results.

## How to run

1. Add your OpenAI API key to the environment variable `OPENAI_API_KEY` in the `.env` file.

2. Run the following command to start the evaluation:

```bash
docker compose up --build --abort-on-container-exit
```

3. Output files will be saved in the `output` directory. The generated plots are also saved in this directory.

4. Clean up the containers by running:

```bash
docker compose down -v
```

## Note

Do not execute the experiment_script.py file directly. It is used by the docker container to run the evaluations.
