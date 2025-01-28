# Red Team Frontend

## Prerequisites

Create a users.yaml file in this directory with the testers login information. See [Streamlit-Authenticator](https://github.com/mkhorasani/Streamlit-Authenticator) for more information.

Additionally, make a copy of the [secrets.toml.template](.streamlit/secrets.toml.template) file and call it `secrets.toml`. Then, fill in the value with your OpenAI API key.

## Setup

```bash
python3 -m venv venv

source venv/bin/activate

pip3 install -r requirements.txt
```

## Run

```bash
streamlit run Home.py
```
