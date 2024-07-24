import psycopg2
from typing import List

def write_prompt_to_db(
    client_id: str,
    session_id: str,
    app_name: str,
    datetime: str,
    prompt: str,
    injected_prompt: str,
    intermediate_steps,
    final_answer: str,
    sql_queries: List[str],
    model: str,
    effective: bool,
    attack_type: str,
    framework: str,
    db_uri="postgresql://postgres:root@localhost:5432/postgres",
) -> bool:
    """
    Write the prompt, intermediate steps, and output to the database.
    """

    query_to_exec = "INSERT INTO public.prompts (client_id, session_id, application, prompt, datetime, intermediate_steps, final_answer, sql_queries, model, effective, attack_type, framework, injected_prompt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(db_uri)
        cur = conn.cursor()
        cur.execute(query_to_exec, (client_id, session_id, app_name, prompt, datetime, str(intermediate_steps), final_answer, sql_queries, model, effective, attack_type, framework, injected_prompt))
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    return True
