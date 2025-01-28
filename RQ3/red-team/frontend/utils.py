import sqlparse
import streamlit as st
import requests
from streamlit_extras.switch_page_button import switch_page

def detect_dml_query(query):
    """
    Detects DML query in the user query.
    """
    parsed = sqlparse.parse(query)
    for p in parsed:
        if p.get_type() in ("DROP", "ALTER", "TRUNCATE", "DELETE", "INSERT", "UPDATE"):
            return True
    return False

def attack_success(message):
    st.balloons()
    st.success(message)

def save_prompt(client_id, session_id, app_name, prompt, injected_prompt, intermediate_steps, final_answer, sql_queries, model, effective, attack_type, framework, api_url="http://localhost:8000/api"):
    payload = {
        "client_id": client_id,
        "session_id": session_id,
        "app_name": app_name,
        "prompt": prompt,
        "injected_prompt": injected_prompt,
        "intermediate_steps": str(intermediate_steps),
        "final_answer": final_answer,
        "sql_queries": sql_queries,
        "model": model,
        "effective": effective,
        "attack_type": attack_type,
        "framework": framework,
    }

    save_prompt_response = requests.post(api_url + "/save_prompt", json=payload)
    return save_prompt_response.status_code == 200


def clear_state():
    keys_to_keep = ['client_id', 'authentication_status', 'authenticator', 'username', 'name']
    for key in st.session_state.keys():
        if key not in keys_to_keep:
            del st.session_state[key]


def check_login():
    if "authentication_status" not in st.session_state or st.session_state["authentication_status"] is None: # not logged in
        # https://arnaudmiribel.github.io/streamlit-extras/extras/switch_page_button/
        switch_page("Home")
    with st.sidebar:
        st.session_state['authenticator'].logout('Logout', 'main', key='unique_key')
        pass

# def convert_newlines_to_markdown(text):
#     return text.replace("\n", "  \n")
    
def convert_to_markdown(text):

    final: str = text.replace("\n", "  \n").replace(':', '\\:').replace('>', '\\>').replace('$', '\\$')

    return final
