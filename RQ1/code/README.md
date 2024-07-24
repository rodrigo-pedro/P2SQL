# How to run the RQ1 experiment

1. Start the postgres database by running `docker compose up -d` in the `postgres` folder.

1. Start the pgAdmin database manager by running `docker compose up -d` in the `pgadmin` folder. You can access the pgAdmin interface at `http://localhost:80/`. The default username is `admin@admin.com` and the default password is `root`.

1. Populate the database by running the queries in `job_postings.sql` in the pgAdmin interface.

1. Start the backend by choosing either `app-backend-agent` or `app-backend-chain` and running the `start.sh` script in the corresponding folder. Before starting, insert your OpenAI API key in the `api_key` variable in the `app_backend.py` file located in each of the backend folders. To change the LLM prompt, modify the `prompt` variable in the `app_backend.py` file (uncomment the prompt you want to use and comment the others). Then, restart the backend.

1. Start the frontend by running the `start.sh` script in the `app-frontend` folder.

1. Open `http://localhost:7860/` in your browser to access the frontend.

1. To perform the direct injection attacks, simply write the attack prompts in the frontend and press enter. To perform the indirect injection attacks, use PgAdmin to change the description of one of the job postings to the attack prompt. Then, ask the chatbot to list the job postings. The attack will be performed automatically.
