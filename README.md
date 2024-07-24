# Supplementary material for the paper "Prompt-to-SQL Injection Attacks in LLM-Integrated Web Applications: Risks and Defenses"

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
    - [`apps`](./RQ3/red-team/apps/): contains the code for the red team applications
    - [`backend`](./RQ3/red-team/backend/): contains the code to launch the red team server backend
    - [`frontend`](./RQ3/red-team/frontend/): contains the code to launch the red team frontend server
    - [`prompt-db`](./RQ3/red-team/prompt-db/): a docker-compose file to launch the PostgreSQL database to save tester prompts
- [`RQ4`](./RQ4/): contains the code for RQ4
    - [`langchain-mitigations`](./RQ4/langchain-mitigations/): implementation of mitigations in Langchain's SQL chain and agent (v0.1.0)
    - [`llm_guard`](./RQ4/llm_guard/): contains the code and evaluation data for the LLM Guard mitigation
        - [`eval`](./RQ4/llm_guard/eval/): contains the detection rate evaluation code
        - [`false_positives`](./RQ4/llm_guard/false_positives/): contains the false positive evaluation code
        - [`final_implementation`](./RQ4/llm_guard/final_implementation/): contains the final implementation of LLM Guard
            - [`langchain`](./RQ4/llm_guard/final_implementation/langchain/): generic implementation using Langchain
            - [`openai`](./RQ4/llm_guard/final_implementation/openai/): generic implementation using the OpenAI API directly
    - [`plots`](./RQ4/plots/): contains the code to generate the plots in the paper
