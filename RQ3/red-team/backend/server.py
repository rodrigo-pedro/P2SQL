import datetime
import os
import subprocess
from typing import List, Dict

from fastapi import FastAPI
from contextlib import asynccontextmanager

from pydantic import BaseModel
import socket
from colorama import Fore
import gspread
import time

from gspread_functions import init_user_sheet, update_sheet
from prompt_db import write_prompt_to_db


THIS_SCRIPT_NAME: str = os.path.basename(__file__)

def shutdown_cleanup():
    print(Fore.RED + f'[INFO][{THIS_SCRIPT_NAME}] - Ctrl+C received, stopping Red Team Docker ecosystems.' + Fore.RESET, flush=True)

    for client_id in CLIENT_APPS.keys():
        print(Fore.RED + f"[INFO][{THIS_SCRIPT_NAME}] - Closing apps for client '{client_id}'..." + Fore.RESET, flush=True)
        stop_all_apps(client_id)

    print(Fore.RED + f'[INFO][{THIS_SCRIPT_NAME}] - Closed all apps. Exiting.' + Fore.RESET, flush=True)

@asynccontextmanager
async def lifespan(app: FastAPI):

    # We can move the server setup logic here if we want.

    yield # FastAPI is running at this point.

    # Close all the Docker ecosystems.
    shutdown_cleanup()


app = FastAPI(lifespan=lifespan)
# app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

class AppDeploymentRequest(BaseModel):
    app_name: str
    client_id: str

class AppDeploymentResponse(BaseModel):
    port: int
    port_db: int

# networks: nome_da_pasta/network_name --> nome_da_pasta_network_name
APP_CONTAINER_NAMES: Dict[str, Dict] = {
    'dataherald': {
        'compose_file': '../apps/dataherald/docker-compose-test.yaml',
        'post_launch_script': '../apps/dataherald/init_dataherald.sh',
    },
    'na2sql': {
        'compose_file': '../apps/Na2SQL/docker-compose-test.yaml',
        #'post_launch_script': '../apps/Na2SQL/init_dataherald.sh',
    },
    'streamlit_agent-sql_db': {
        'compose_file': '../apps/streamlit_agent-sql_db/docker-compose-test.yaml',
    },
    'streamlit_agent-mrkl': {
        'compose_file': '../apps/streamlit_agent-mrkl/docker-compose-test.yaml',
    },
    'qabot': {
        'compose_file': '../apps/qabot/docker-compose-test.yaml',
    },
}

CLIENT_APPS: Dict[str, List[str]] = {} # client_id -> [app_names]

def stop_specific_app(app_name: str, client_id: str):
    # CUSTOM_PORT set to '' to omit warning about variable not being set. Not actually needed.
    subprocess.run(f"CUSTOM_PORT='' CUSTOM_PORT_DB='' docker compose -f {APP_CONTAINER_NAMES[app_name]['compose_file']} -p {client_id}-{app_name} down -v", shell=True)


def stop_all_apps(client_id: str):
    if client_id not in CLIENT_APPS:
        return

    for app_name in CLIENT_APPS[client_id]:
        stop_specific_app(app_name, client_id)

    CLIENT_APPS[client_id] = []


@app.post("/api/start_app")
def start_app(app: AppDeploymentRequest):

    stop_all_apps(app.client_id)

    sock = socket.socket()
    sock.bind(('', 0))
    port: int = sock.getsockname()[1]
    sock.close()

    # new_uuid = uuid.uuid4()
    compose_uuid = app.client_id

    compose_file: str = os.path.join(APP_CONTAINER_NAMES[app.app_name]['compose_file'])

    sock = socket.socket()
    sock.bind(('', 0))
    port_db: int = sock.getsockname()[1]
    sock.close()

    launch_cmd: str = f'CUSTOM_PORT={port} CUSTOM_PORT_DB={port_db} docker compose -f {compose_file} -p {compose_uuid}-{app.app_name} up -d --wait --build'

    print(Fore.MAGENTA + f'[INFO][{THIS_SCRIPT_NAME}] - launch command:\n\t{launch_cmd}' + Fore.RESET)

    subprocess.run(launch_cmd, shell=True)

    time.sleep(6)

    if 'post_launch_script' in APP_CONTAINER_NAMES[app.app_name]:
        subprocess.run(f'bash {APP_CONTAINER_NAMES[app.app_name]["post_launch_script"]} {port} {port_db}', shell=True)

    if app.client_id not in CLIENT_APPS:
        CLIENT_APPS[app.client_id] = []
    CLIENT_APPS[app.client_id].append(app.app_name)

    print(Fore.MAGENTA + f'[INFO][{THIS_SCRIPT_NAME}] - launching {app.app_name} on port {port}' + Fore.RESET)
    # print(Fore.MAGENTA + f'\t{main_yaml}\n\t{filled_template}\n' + Fore.RESET)

    return AppDeploymentResponse(port=port, port_db=port_db)


@app.post("/api/stop_app")
def stop_app(app: AppDeploymentRequest):
    if app.client_id not in CLIENT_APPS: # if user not running any apps
        return #TODO: error

    if app.app_name in CLIENT_APPS[app.client_id]: # if user tries to stop an app that is running
        CLIENT_APPS[app.client_id].remove(app.app_name)
    else: # the app is not running
        return #TODO: error

    stop_specific_app(app.app_name, app.client_id)


class SavePromptRequest(BaseModel):
    client_id: str
    session_id: str
    app_name: str
    prompt: str
    injected_prompt: str
    intermediate_steps: str
    final_answer: str
    sql_queries: List[str]
    model: str
    effective: bool
    attack_type: str
    framework: str

@app.post("/api/save_prompt")
def save_prompt(app: SavePromptRequest):
    current_time: datetime.datetime = datetime.datetime.now()

    # save prompt to postgres db
    db_write_succeeded: bool = write_prompt_to_db(
        client_id=app.client_id,
        session_id=app.session_id,
        app_name=app.app_name,
        prompt=app.prompt,
        injected_prompt=app.injected_prompt,
        datetime=current_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
        intermediate_steps=app.intermediate_steps,
        final_answer=app.final_answer,
        sql_queries=app.sql_queries,
        model = app.model,
        effective=app.effective,
        attack_type=app.attack_type,
        framework=app.framework
    )

    if db_write_succeeded:
        print(Fore.MAGENTA + f'[INFO][{THIS_SCRIPT_NAME}] - wrote prompt to db for user {app.client_id}' + Fore.RESET)

    else:
        print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - failed to write prompt to db for user {app.client_id}' + Fore.RESET)

    # save prompt to google sheet
    # ws: gspread.Spreadsheet = init_user_sheet(client_id=app.client_id)

    # field_order: List[str] = ['client_id', 'session_id', 'app_name', 'datetime', 'prompt', 'intermediate_steps', 'final_answer', 'query', 'model', 'effective', 'attack_type', 'framework', 'injected_prompt']

    # fields: Dict = {
	# 	'client_id': app.client_id,
	# 	'session_id': app.session_id,
	# 	'app_name': app.app_name,
	# 	'datetime': current_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
	# 	'prompt': app.prompt,
    #     'injected_prompt': app.injected_prompt,
	# 	'intermediate_steps': app.intermediate_steps,
	# 	'final_answer': app.final_answer,
	# 	'query': '\n'.join(app.sql_queries), # convert array of queries into a string with each query separated by a newline
    #     'model': app.model,
	# 	'effective': app.effective,
	# 	'attack_type': app.attack_type,
    #     'framework': app.framework
	# }
    # sheet_write_succeeded: bool = update_sheet(ws, fields, field_order)

    # if sheet_write_succeeded:
	# 	# successfully wrote to the sheet.
    #     print(Fore.MAGENTA + f'[INFO][{THIS_SCRIPT_NAME}] - wrote prompt to sheet {ws.title} for user {app.client_id}' + Fore.RESET)

    # else:
    #     print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - failed to write prompt to sheet {ws.title} for user {app.client_id}' + Fore.RESET)





if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
