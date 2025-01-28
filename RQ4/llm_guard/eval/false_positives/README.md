# Evaluation of DeBERTA model on false positives

Tests the DeBERTA model for false positives on 150 LLM generated benign prompts.

## How to run

1. Run the following command to start the evaluation:

```bash
docker compose up --build --abort-on-container-exit
```

2. Output files will be saved in the `output` directory. The accuracy of the DeBERTA model will be printed in the terminal.

3. Clean up the containers by running:

```bash
docker compose down -v
```
