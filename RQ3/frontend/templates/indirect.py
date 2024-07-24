import time
import requests
import streamlit as st
import pandas as pd
from abc import ABC, abstractmethod
from typing import Tuple, Dict, List
from utils import attack_success, save_prompt, clear_state, check_login, convert_to_markdown
import uuid
from st_pages import add_page_title

class IndirectTemplate(ABC):
    def __init__(self, app_name: str, chatbot_prompt: str, models: List[str], possible_attack_types: List[str], info_text: str = "", has_history: bool = False):
        self.app_name = app_name
        # self.messages_state = app_name.replace(' ', '_') + "_messages"
        self.info_text = info_text
        self.has_history = has_history
        self.models = models
        self.possible_attack_types = possible_attack_types
        self.api_url = "http://localhost:8000/api"

        self.chatbot_prompt = chatbot_prompt

        self.draw()

    def json_to_dataframe(self, json_data) -> pd.DataFrame:
        if json_data is None:
            return pd.DataFrame()
        columns = json_data.get("columns", [])
        rows = json_data.get("rows", [])
        df = pd.DataFrame(rows, columns=columns)
        return df

    def show_query(self, text):
        text = text.strip()
        answer_container = st.empty()
        answer_container.code(text, language="sql")

    def display_assistant_response_content(self, assistant_content):
        # Display assistant response in chat message container
        for item in assistant_content:
            if item["type"] == "query":
                self.show_query(item["content"])
            elif item["type"] == "text":
                st.markdown(convert_to_markdown(item["content"]))
            elif item["type"] == "divider":
                st.divider()
            elif item["type"] == "expander":
                st.expander(item["title"], expanded=item["expanded"]).markdown(convert_to_markdown(item["content"]))

    @abstractmethod
    def send_message(self, message, model, port, attack_type) -> Tuple[Dict, bool, str, Dict]:
        """
        Subclasses must override this method to handle sending messages.
        Should return a dict with the format:
        {
            "role": "assistant",
            "content": [
                {
                    "type": "query", "text", "divider" or "expander"
                    "content": assistant_query
                },
                ...
            ]
        }
        Also returns a boolean indicating whether the attack was successful.
        """
        pass

    def save_prompt(self, data_to_save):
        if data_to_save:
            save_prompt(
                client_id=data_to_save["client_id"],
                session_id=data_to_save["session_id"],
                app_name=data_to_save["app_name"],
                prompt=data_to_save["prompt"],
                injected_prompt=data_to_save["injected_prompt"],
                intermediate_steps=data_to_save["intermediate_steps"],
                final_answer=data_to_save["final_answer"],
                sql_queries=data_to_save["sql_queries"],
                model=data_to_save["model"],
                effective=data_to_save["effective"],
                attack_type=data_to_save["attack_type"],
                framework=data_to_save["framework"],
            )

    def get_data_to_save_dict(
        self,
        prompt: str,
        intermediate_steps: str,
        final_answer: str,
        sql_queries: List[str],
        model: str,
        effective: bool,
        attack_type: str,
        framework: str,
    ):
        return {
            "client_id": st.session_state["username"],
            "session_id": st.session_state["session_id"],
            "app_name": self.app_name,
            "prompt": prompt,
            "intermediate_steps": intermediate_steps,
            "final_answer": final_answer,
            "sql_queries": sql_queries,
            "model": model,
            "effective": effective,
            "attack_type": attack_type,
            "framework": framework,
        }

    @abstractmethod
    def inject_prompt(self, prompt, port_db) -> None:
        """
        Subclasses must override this method to handle injecting prompts into the database.
        """
        pass


    def draw(self):
        add_page_title(layout="wide")

        check_login()

        if "prev_page" not in st.session_state:
            st.session_state["prev_page"] = self.app_name

        if st.session_state["prev_page"] != self.app_name:
            clear_state()
            st.session_state["prev_page"] = self.app_name
            st.session_state["session_id"] = str(uuid.uuid4())

        if "port" not in st.session_state:
            payload = {"app_name": self.app_name, "client_id": st.session_state["username"]}
            with st.spinner("Loading app..."):
                response = requests.post(
                    self.api_url + "/start_app", json=payload
                ).json()

            st.session_state["port"] = response.get("port")
            st.session_state["port_db"] = response.get("port_db")

        if "session_id" not in st.session_state:
            st.session_state["session_id"] = str(uuid.uuid4())

        # Code below is commented because we want to always show the choice 
        # of model.

        # if len(self.models) > 1:
        #     choose_model = st.sidebar.selectbox(
        #         'Model to use:',
        #         self.models,
        #         index=0)
        # else:
        #     choose_model = self.models[0]
            
        choose_model = st.sidebar.selectbox(
            'Model to use:',
            self.models,
            index=0)


        # Add a clear button to the sidebar
        # if self.has_history:
        #     if st.sidebar.button(
        #         "Clear Chat",
        #     ):
        #         # Clear the chat history in the session state
        #         st.session_state[self.messages_state] = []

        def reload_app():
            # st.session_state[self.messages_state] = []
            del st.session_state["port"]
            time.sleep(1)  # Without this, the "Loadding app..." spinner doesn't show up
            st.experimental_rerun()

        if st.sidebar.button("Reload application", type="primary"):
            reload_app()

        st.sidebar.markdown(self.info_text)

        # Initialize chat history
        # if self.messages_state not in st.session_state:
        #     st.session_state[self.messages_state] = []


        with st.expander('Inject prompt', expanded=True):
            injected_prompt = st.text_area(label='Enter your prompt')

            attack_type = st.radio(
                "Type of attack:",
                self.possible_attack_types,
                horizontal=True,
            )

            submit_button = st.button(label='Submit')

            if submit_button:
                with st.spinner('Injecting prompt into database...'):
                    self.inject_prompt(injected_prompt, st.session_state["port_db"])

            st.session_state["submit"] = submit_button

        # for message in st.session_state[self.messages_state]:
        #     with st.chat_message(message["role"]):
        #         if message["role"] == "assistant":
        #             self.display_assistant_response_content(message["content"])
        #         else:
        #             # For user or other types of messages
        #             st.markdown(message["content"])

        # used in the case of RI1
        def yes_button_clicked(data_to_save):
            with st.spinner('Saving prompt...'):
                self.save_prompt(data_to_save)

        # used in the case of RI1
        def no_button_clicked(data_to_save):
            data_to_save["effective"] = False
            with st.spinner('Saving prompt...'):
                self.save_prompt(data_to_save)



        _ = st.chat_input(self.chatbot_prompt, disabled=True)

        if st.session_state.get("submit", False):
            st.chat_message("user").write(convert_to_markdown(self.chatbot_prompt))

            # Add user message to chat history
            # st.session_state[self.messages_state].append({"role": "user", "content": self.chatbot_prompt, "type": "text"})

            # send message to assistant
            with st.spinner('Waiting for assistant response...'):
                assistant_response, was_attack_successful, error_message, data_to_save = self.send_message(message=self.chatbot_prompt, model=choose_model, port=st.session_state["port"], attack_type=attack_type)

            # add injected prompt to data_to_save
            data_to_save["injected_prompt"] = injected_prompt

            with st.chat_message("assistant"):
                self.display_assistant_response_content(assistant_response["content"])

            if error_message:
                st.error("Something went wrong! Try again.")
                st.error(error_message)
                # st.session_state[self.messages_state] = []
            else:
                # st.session_state[self.messages_state].append(assistant_response)

                # if the attack is RI1, ask the user to confirm whether the attack was successful
                if attack_type == "RI1":
                    if was_attack_successful:
                        attack_success("Attack successful!")

                        st.write("We think the attack was successful. Is this correct?")
                        st.button("Yes", on_click=yes_button_clicked, args=(data_to_save,))
                        st.button("No", on_click=no_button_clicked, args=(data_to_save,))
                    else:
                        self.save_prompt(data_to_save)
                # in the case of RI2, we don't need to ask the user to confirm
                elif attack_type == "RI2":
                    self.save_prompt(data_to_save)
                    if was_attack_successful:
                        attack_success("Attack successful!")
                        st.warning("Please reload the application to reset the database.")