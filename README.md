# Artifact for "Prompt-to-SQL Injection Attacks in LLM-Integrated Web Applications: Risks and Defenses"

## Folder structure

- [`RQ1`](./RQ1/): contains all files related to the replication of the RQ1 attacks
    - [`code`](./RQ1/code/): code for the replication of the RQ1 attacks
        - [`app-backend-agent`](./RQ1/code/app-backend-agent/): the Langchain backend using SQLDatabaseAgent
        - [`app-backend-chain`](./RQ1/code/app-backend-chain/): the Langchain backend using SQLDatabaseChain
        - [`app-frontend`](./RQ1/code/app-frontend/): used to launch the Gradio chatbot frontend
        - [`postgres`](./RQ1/code/postgres/): a docker-compose file to launch the PostgreSQL database
        - [`pgadmin`](./RQ1/code/pgadmin/): a docker-compose file to launch the pgAdmin database manager for easy database inspection
    - [`prompts`](./RQ1/prompts/): contains the prompts used in the RQ1 attacks
- [`RQ2`](./RQ2/): contains the code, prompts, and list of models used in RQ2
    - [`code`](./RQ2/code/): the same code, but with support for more models
    - [`prompts`](./RQ2/prompts/): contains the prompts used in the RQ2, grouped by model
- [`RQ3`](./RQ3/): contains the red team application testing code used in RQ3
    - [`automated`](./RQ3/automated/): contains the code for the automated generation of malicious prompts
        - [`finetune`](./RQ3/automated/finetune/): finetuned Mistral-7B model (code, dataset, and model)
        - [`generated_prompts`](./RQ3/automated/generated_prompts/): contains successful malicious prompts generated by model
    - [`red-team`](./RQ3/red-team/): contains the code for the red team testing
        - [`apps`](./RQ3/red-team/apps/): contains the code for the red team applications
        - [`backend`](./RQ3/red-team/backend/): contains the code to launch the red team server backend
        - [`dataset`](./RQ3/red-team/dataset/): contains the prompts created by the red team
        - [`frontend`](./RQ3/red-team/frontend/): contains the code to launch the red team frontend server
        - [`prompt-db`](./RQ3/red-team/prompt-db/): a docker-compose file to launch the PostgreSQL database to save tester prompts
- [`RQ4`](./RQ4/): contains the code for RQ4
    - [`langshield-langchain`](./RQ4/langshield-langchain/): implementation of Langshield in Langchain's SQL chain and agent (v0.1.0)
    - [`llm_guard`](./RQ4/llm_guard/): contains the code and evaluation data for the LLM Guard mitigation. Also contains the our results for the evaluation of the LLM Guard mitigations.
        - [`eval`](./RQ4/llm_guard/eval/): contains the LLM Guard evaluation code and data
            - [`all_prompts`](./RQ4/llm_guard/eval/all_prompts/): evaluation of final LLM Guard implementation over 1120 prompts
            - [`detections`](./RQ4/llm_guard/eval/detections/): evaluation of intermediate LLM Guard implementation over 60 prompts
            - [`false_positives`](./RQ4/llm_guard/eval/false_positives/): evaluation of false positives of deberta-v3-base-prompt-injection over 120 prompts
        - [`final_implementation_standalone`](./RQ4/llm_guard/final_implementation_standalone/): contains the final standalone implementation of the LLM Guard component of Langshield
            - [`langchain`](./RQ4/llm_guard/final_implementation/langchain/): generic implementation using Langchain
            - [`openai`](./RQ4/llm_guard/final_implementation/openai/): generic implementation using the OpenAI API directly
