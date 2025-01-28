import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from utils import clear_state
from st_pages import Page, Section, show_pages, add_page_title, hide_pages


add_page_title(layout="wide")

show_pages(
    [
        Page("Home.py", "Home", "🏠"),
        Page("pages/dataherald.py", "Dataherald", ""),
        Section("Na2SQL", icon=""),
        Page("pages/Na2SQL-direct.py", "Direct Attacks", ""),
        Page("pages/Na2SQL-indirect.py", "Indirect Attacks", ""),
        Section("Chat with SQL DB", icon=""),
        Page("pages/streamlit_agent-sql_db-direct.py", "Direct Attacks", ""),
        Page("pages/streamlit_agent-sql_db-indirect.py", "Indirect Attacks", ""),
        Section("MRKL Demo", icon=""),
        Page("pages/streamlit_agent-mrkl-direct.py", "Direct Attacks", ""),
        Page("pages/streamlit_agent-mrkl-indirect.py", "Indirect Attacks", ""),
        Section("Qabot", icon=""),
        Page("pages/qabot-direct.py", "Direct Attacks", ""),
        Page("pages/qabot-indirect.py", "Indirect Attacks", ""),
    ]
)


with open('./users.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    # config['preauthorized']
)

st.session_state['authenticator'] = authenticator


name, authentication_status, username = authenticator.login('Login', 'main')


if authentication_status:
    with st.sidebar:
        authenticator.logout('Logout', 'main', key='unique_key')
    st.write(f'Welcome **{name}**')
    st.title('Instructions:')
    st.markdown('''
        1. Click on the left sidebar to navigate to the different pages. They may take a while to load, since we are launching a new instance every time.
        2. You can choose with model to use for each attack. Feel free to try all combinations.
        3. You can reset the state of the app by clicking on the "Reload application" button on the sidebar.
    ''')

    st.divider()

    # load the job_postings.csv file, convert it to a dataframe, and display it
    st.header('Job Postings')
    job_postings = pd.read_csv('job_postings.csv')
    st.dataframe(job_postings, width=1300, hide_index=True)

    # do the same for users.csv
    st.header('Users')
    users = pd.read_csv('users.csv')
    st.dataframe(users, hide_index=True)





elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')
