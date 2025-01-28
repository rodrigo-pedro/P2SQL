# LLM Guard Final Evaluation

Runs the final implementation of the LLM Guard on 1120 malicious prompts. **WARNING**: This evaluation may incur significant costs to the OpenAI API.

## Folder structure

- [initdb](initdb/): Contains the SQL script to populate the database with the malicious prompts.
- [llm_guard](llm_guard/): Contains the LLM Guard implementation.

## How to run

1. Add your OpenAI API key to the environment variable `OPENAI_API_KEY` in the `.env` file.

2. Run the following command to start the evaluation:

```bash
docker compose up --build --abort-on-container-exit
```

3. The accuracy of the LLM Guard will be printed in the terminal. Output files will be saved in the `output` directory.

4. Clean up the containers by running:

```bash
docker compose down -v
```
