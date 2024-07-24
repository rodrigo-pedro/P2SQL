# How to run the RQ2 experiment

1. Start the postgres database by running `docker compose up -d` in the `postgres` folder.

1. Start the pgAdmin database manager by running `docker compose up -d` in the `pgadmin` folder. You can access the pgAdmin interface at `http://localhost:80/`. The default username is `admin@admin.com` and the default password is `root`.

1. Populate the database by running the queries in `job_postings.sql` in the pgAdmin interface.

1. Before starting the backend, you must change the `app_backend.py` file of either `app-backend-agent` or `app-backend-chain` to use the model you wish to test. The file already provides the necessary code to test GPT models, PaLM2, and local models using llama-cpp-python. Uncomment the relevant lines to set the LLM. If using PaLM2, also uncomment the relevant lines in the Dockerfile and provide the gcloud credentials json file. Then, start the backend by running the `start.sh` script.

1. To change the LLM prompt, modify the `prompt` variable in the `app_backend.py` file (uncomment the prompt you want to use and comment the others). Then, restart the backend.

1. Start the frontend by running the `start.sh` script in the `app-frontend` folder.

1. Open `http://localhost:7860/` in your browser to access the frontend.

1. To perform the attacks, proceed the same way as in RQ1, but using the new prompts.

# How to run local models

1. Edit the `start.sh` script in the `llm` directory and set the PATH_TO_MODELS and MODEL_NAME, as well as the other parameters.

1. To run with CUDA, run `start.sh CUDA`. To run without CUDA, run `start.sh`.

1. Change the app_backend.py file to use the local model.
