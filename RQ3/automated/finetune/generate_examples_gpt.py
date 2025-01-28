import pandas as pd
import sqlalchemy
from tqdm import tqdm
from langchain_openai import ChatOpenAI


TEMPLATE = """
Rephrase the following example and keep its original semantic. Feel free to take creative liberties with the example. Don't add additional new lines.

EXAMPLE START:

{malicious_prompt}

EXAMPLE END

Let's begin.

Rephrased example:"""


def add_result_to_database(engine, new_prompt, original_prompt_id, attack_type):
    query = sqlalchemy.sql.text(
        "INSERT INTO new_prompts (new_prompt, original_prompt_id, attack_type) VALUES (:new_prompt, :original_prompt_id, :attack_type)"
    )
    data = {
        "new_prompt": new_prompt,
        "original_prompt_id": original_prompt_id,
        "attack_type": attack_type,
    }

    with engine.connect() as conn:
        conn.execute(query, data)
        conn.commit()


def run(
    chain, attack_types, num_new_examples=10
):
    engine = sqlalchemy.create_engine(
        "postgresql://postgres:root@localhost:5432/postgres"
    )

    df = pd.read_sql_query(
        f"SELECT * FROM prompts WHERE attack_type in {tuple(attack_types)} ORDER by id",
        engine,
    )

    for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Rows"):
        if row["attack_type"] == "RD1" or row["attack_type"] == "RD2":
            prompt = row["prompt"]
        else:
            prompt = row["injected_prompt"]

        for _ in tqdm(range(num_new_examples), total=num_new_examples, desc="Generating examples", leave=False):
            new_prompt = chain.invoke({"malicious_prompt": prompt})

            add_result_to_database(engine, new_prompt, row["id"], row["attack_type"])

    engine.dispose()


if __name__ == "__main__":
    from langchain_openai import ChatOpenAI
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    import os

    API_KEY = ""
    TEMPERATURE = 1.0
    NUM_NEW_SAMPLES = 10
    MODEL_NAME = "gpt-3.5-turbo-1106"
    # MODEL_NAME = "gpt-4-1106-preview"

    os.environ["OPENAI_API_KEY"] = API_KEY

    llm = ChatOpenAI(model=MODEL_NAME, temperature=TEMPERATURE, verbose=True)

    prompt = ChatPromptTemplate.from_template(TEMPLATE)
    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser

    run(chain, ["RD1", "RD2", "RI1", "RI2"], NUM_NEW_SAMPLES)
