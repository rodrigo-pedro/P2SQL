from colorama import Fore
import datetime
from google.auth import exceptions as google_auth_exceptions
import gspread
import os
import sys
import time
import traceback
from typing import List, Dict, Tuple

# Number of retries that will be made in the face of the API stating the service
# is unavailable.
MAX_RETRY_COUNT: int = 5

THIS_SCRIPT_NAME: str = os.path.basename(__file__)

def load_sheet(gspread_spreadsheet: gspread.Spreadsheet, sheet_name) -> gspread.Worksheet:
	return gspread_spreadsheet.worksheet(sheet_name)

# Google Sheets Config.
def open_sheet(service_acc: str = ".config/service_account.json", spreadsheet_name: str = "explode.js-vs-odgen") -> gspread.Spreadsheet:


	# Number of retries that will be made in the face of the API stating the service
	# is unavailable.
	MAX_RETRY_COUNT: int = 5
	retry_count: int = MAX_RETRY_COUNT

	# If the gspread API states the service is unavailable, sleep some minutes.
	retry_sleep_time: int = 300

	# Number of seconds to sleep between calls to the gspread API.
	inter_operation_sleep: int = 0

	# Loop until we get the sheet data or the maximum amount of retires was reached.
	trying_to_open: bool = True

	while trying_to_open:

		# We are sleeping 'inter_operation_sleep' seconds between gspread calls
		# to avoid stressing the Google Sheet API.
		# See: https://developers.google.com/sheets/api/limits
		time.sleep(inter_operation_sleep)

		try:

			current_op: str = 'gspread.service_account(filename=service_acc)'

			print(f'[INFO][{THIS_SCRIPT_NAME}] - gspread.service_account(filename={service_acc})')

			service_account: gspread.client.Client = gspread.service_account(filename=service_acc)
			current_op = 'gspread.client.Client.open(spreadsheet_name)'
			sheet: gspread.Spreadsheet = service_account.open(spreadsheet_name)

			print(f'[INFO][{THIS_SCRIPT_NAME}] - service_account.open({spreadsheet_name})')

			# If a 'gspread' operation was successful, reset the retry counter.
			return sheet


		except google_auth_exceptions.TransportError as e:
			print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - unhandled error when trying to open worksheet {spreadsheet_name}' + Fore.RESET)
			print(Fore.RED + f'\n\t{traceback.format_exc()}\n' + Fore.RESET)
			return None
		except gspread.exceptions.APIError as e:

			error_json = e.response.json()

			error_code: int = error_json.get('error', {}).get('code')
			error_status: str = error_json.get('error', {}).get('status')
			error_message: str = error_json.get('error', {}).get('message')

			info_str: str = get_gspread_exception_info_from_json(current_op, error_code, error_status, error_message)

			print(Fore.RED + info_str + Fore.RESET, flush=True)

			# pprint.pprint(error_code)
			# pprint.pprint(error_message)
			# pprint.pprint(type(error_message))
			# pprint.pprint(error_status)

			if error_code == 429:
				print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - too many requests error from Google API, sleeping 60 seconds.' + Fore.RESET)

				time.sleep(60)

				print(Fore.MAGENTA + f'[WARN][{THIS_SCRIPT_NAME}] - retrying the opening of spreadsheet {spreadsheet_name}.' + Fore.RESET)

			elif error_code == 500 and error_status == "INTERNAL" and "error encountered" in error_message:
				print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - failed to open spreadsheet {spreadsheet_name}.' + Fore.RESET)
				retry_count -= 1

				if retry_count == 0:
					print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - All {MAX_RETRY_COUNT} spreadsheet {spreadsheet_name} opening retries failed.' + Fore.RESET)
					return None # failed writing to sheet.




				print(Fore.RED + f'[WARN][{THIS_SCRIPT_NAME}] - service encountered an internal error while opening spreadsheet {spreadsheet_name}, sleeping {retry_sleep_time} seconds.' + Fore.RESET)

				print(Fore.RED + f'\n\t{traceback.format_exc()}\n' + Fore.RESET)

				time.sleep(retry_sleep_time)

				print(Fore.MAGENTA + f'[WARN][{THIS_SCRIPT_NAME}] - retrying the opening of spreadsheet {spreadsheet_name} {retry_count} more times.' + Fore.RESET)
			elif error_code == 503 and error_status == "UNAVAILABLE" and "service is currently unavailable" in error_message:
				print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - operation failed.' + Fore.RESET)
				retry_count -= 1

				if retry_count == 0:
					print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - All {MAX_RETRY_COUNT} operation retries failed.' + Fore.RESET)
					return None # failed opening sheet.




				print(Fore.RED + f'[WARN][{THIS_SCRIPT_NAME}] - service was unavailable, sleeping {retry_sleep_time} seconds.' + Fore.RESET)

				print(Fore.RED + f'\n\t{traceback.format_exc()}\n' + Fore.RESET)

				time.sleep(retry_sleep_time)

				print(Fore.MAGENTA + f'[WARN][{THIS_SCRIPT_NAME}] - retrying the opening of spreadsheet {spreadsheet_name} {retry_count} more times.' + Fore.RESET)
			else:
				print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - unhandled error when trying to open worksheet {spreadsheet_name}' + Fore.RESET)
				print(Fore.RED + f'\n\t{traceback.format_exc()}\n' + Fore.RESET)
				return None


def get_gspread_exception_str(e: gspread.exceptions.APIError) -> str:
	error_json = e.response.json()

	error_code: int = error_json.get('error', {}).get('code')
	error_status: str = error_json.get('error', {}).get('status')
	error_message: str = error_json.get('error', {}).get('message')

	ret_val: str = f'''gspread.exceptions.APIError
		\tCode: {error_code}
		\tStatus: {error_status}
		\tMessage: {error_message}'''

	return ret_val

def get_gspread_exception_info_from_json(operation: str, error_code: int, error_status: str, error_message: str) -> str:
	ret_str: str = f'[INFO][{THIS_SCRIPT_NAME}] - {operation} produced {error_code}:{error_status}\n\t{error_message}' + Fore.RESET

	return ret_str

def get_gspread_exception_info_from_response(operation: str, e: gspread.exceptions.APIError) -> str:
	error_json = e.response.json()

	error_code: int = error_json.get('error', {}).get('code')
	error_status: str = error_json.get('error', {}).get('status')
	error_message: str = error_json.get('error', {}).get('message')

	ret_str: str = f'[INFO][{THIS_SCRIPT_NAME}] - {operation} produced {error_code}:{error_status}\n\t{error_message}' + Fore.RESET

	return ret_str

def handle_gspread_operation(e: gspread.exceptions.APIError, operation: str) -> int:
	error_json = e.response.json()

	error_code: int = error_json.get('error', {}).get('code')
	error_status: str = error_json.get('error', {}).get('status')
	error_message: str = error_json.get('error', {}).get('message')

	print(Fore.RED + f'[INFO][{THIS_SCRIPT_NAME}] - {operation} produced {error_code}:{error_status}' + Fore.RESET)

	if error_code == 503 and error_status == "UNAVAILABLE" and "service is currently unavailable" in error_message:
		return 300
	else:
		return -1

# Number of seconds to sleep between calls to the gspread API.
# inter_operation_sleep: int = 5
def deploy_gspread_operation(gspread_op: Tuple[str, Dict], retry_sleep_time: int = 300, inter_operation_sleep: int = 5, retry_count: int = MAX_RETRY_COUNT) -> Dict:

	deployment_result: Dict = {}

	GSPREAD_TOO_MANY_REQUESTS_SLEEP_TIME: int = 60

	starting_op: str = gspread_op[0]
	# Using this variable to control the sequence of calls to make with the gspread package.
	current_op: str = starting_op
	op_details: Dict = gspread_op[1]

	if starting_op in ['ws.col_values', 'ws.update', 'ws.add_rows']:
		ws: gspread.Spreadsheet = op_details['ws']


		if starting_op == 'ws.update':
			result = []
			file_ctr: int = 0
			package_grades: Dict = op_details['package_grades']
			package: str = op_details['package']
			for file, grades in package_grades.items():
				file_ctr += 1
				#sub_array = ["", "/".join(file.split("/")[5:])] + [grades[key] for key in grades]
				target_sheet_path: str = file[file.find("src") : ]
				#sub_array = ["", "/".join(file.split("/")[5:])] + [grades[key] for key in grades]

				sub_array = ["", target_sheet_path] + [grades[key] for key in grades]
				sub_array.insert(4, "")
				result.append(sub_array)
			result[0][0] = package

			# Row position to write within the Google Sheet.
			empty_row_index: int

			# In the event that all rows are used, try to increase the number of rows by 'row_incr' rows.
			row_incr: int = 1000 + file_ctr
		elif starting_op == 'ws.add_rows':
			# In the event that all rows are used, try to increase the number of rows by 'row_incr' rows.
			row_incr: int = 1000 + file_ctr
	elif starting_op == 'load_sheet':
		target_sheet_name: str = op_details['target_sheet_name']
		gspread_spreadsheet: gspread.Spreadsheet = op_details['gspread_spreadsheet']


	trying_operation: bool = True
	while trying_operation:
		# We are sleeping 'inter_operation_sleep' seconds between gspread calls
		# to avoid stressing the Google Sheet API.
		# See: https://developers.google.com/sheets/api/limits
		time.sleep(inter_operation_sleep)

		try:
			if starting_op == 'load_sheet':
				ws: gspread.Worksheet = load_sheet(gspread_spreadsheet, target_sheet_name)
				print(Fore.MAGENTA + f'[INFO][{THIS_SCRIPT_NAME}] - Loaded gspread.Spreadsheet: {target_sheet_name}' + Fore.RESET)

				deployment_result['succeeded'] = True
				deployment_result['ws'] = ws
				return deployment_result

			elif current_op == 'ws.col_values':
				# Necessary to find out where exactly to write within the sheet.
				empty_row_index = max(len(ws.col_values(2)) + 1, 6)

				if not starting_op == current_op:
					current_op = 'ws.update'
				else:
					deployment_result['succeeded'] = True
					return deployment_result
			elif current_op == 'ws.update':
				# The actual attempt to write into the sheet.
				print(Fore.MAGENTA + f'[INFO][{THIS_SCRIPT_NAME}] - Trying to write to sheet {ws.title}.' + Fore.RESET)
				ws.update(f"A{empty_row_index}:F{len(result) + empty_row_index - 1}", result)
				print(Fore.MAGENTA + f'[INFO][{THIS_SCRIPT_NAME}] - Write to {ws.title} successful.' + Fore.RESET)

				# Writing to sheet was successful.
				deployment_result['succeeded'] = True
				return deployment_result

			elif current_op == 'ws.add_rows':
				# If the sheet was full, it produced a specific exception which set the next operation
				# to be 'ws.add_rows'.
				print(Fore.MAGENTA + f'[INFO][{THIS_SCRIPT_NAME}] - Adding {row_incr} rows to {ws.title}.' + Fore.RESET)
				ws.add_rows(row_incr)
				print(Fore.MAGENTA + f'[INFO][{THIS_SCRIPT_NAME}] - Rows added successfully.' + Fore.RESET)

				if not starting_op == current_op:
					current_op = 'ws.update'
				else:
					deployment_result['succeeded'] = True
					return deployment_result

			# If a 'gspread' operation was successful, reset the retry counter.
			retry_count = MAX_RETRY_COUNT



		except gspread.exceptions.APIError as e:

			error_json = e.response.json()

			error_code: int = error_json.get('error', {}).get('code')
			error_status: str = error_json.get('error', {}).get('status')
			error_message: str = error_json.get('error', {}).get('message')

			info_str: str = get_gspread_exception_info_from_json(current_op, error_code, error_status, error_message)

			print(Fore.RED + info_str + Fore.RESET, flush=True)

			# pprint.pprint(error_code)
			# pprint.pprint(error_message)
			# pprint.pprint(type(error_message))
			# pprint.pprint(error_status)

			if error_code == 429:
				print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - too many requests error from Google API, sleeping {GSPREAD_TOO_MANY_REQUESTS_SLEEP_TIME} seconds.' + Fore.RESET)

				time.sleep(GSPREAD_TOO_MANY_REQUESTS_SLEEP_TIME)

				print(Fore.MAGENTA + f'[WARN][{THIS_SCRIPT_NAME}] - retrying \'{current_op}\'.' + Fore.RESET)

			elif error_code == 500 and error_status == "INTERNAL" and "error encountered" in error_message:
				print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - operation failed.' + Fore.RESET)
				retry_count -= 1

				if retry_count == 0:
					print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - All {MAX_RETRY_COUNT} operation retries failed.' + Fore.RESET)
					print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - Last attempted \'gspread\' operation: {current_op}.' + Fore.RESET)

					# Operation failed.
					deployment_result['succeeded'] = False
					return deployment_result





				print(Fore.RED + f'[WARN][{THIS_SCRIPT_NAME}] - service encountered an internal error on \'{current_op}\', sleeping {retry_sleep_time} seconds.' + Fore.RESET)

				print(Fore.RED + f'\n\t{traceback.format_exc()}\n' + Fore.RESET)

				time.sleep(retry_sleep_time)

				print(Fore.MAGENTA + f'[WARN][{THIS_SCRIPT_NAME}] - retrying \'{current_op}\' for {retry_count} more times.' + Fore.RESET)
			elif error_code == 503 and error_status == "UNAVAILABLE" and "service is currently unavailable" in error_message:
				print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - operation failed.' + Fore.RESET)
				retry_count -= 1

				if retry_count == 0:
					print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - All {MAX_RETRY_COUNT} operation retries failed.' + Fore.RESET)
					print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - Last attempted \'gspread\' operation: {current_op}.' + Fore.RESET)

					# Operation failed.
					deployment_result['succeeded'] = False
					return deployment_result




				print(Fore.RED + f'[WARN][{THIS_SCRIPT_NAME}] - service was unavailable on \'{current_op}\', sleeping {retry_sleep_time} seconds.' + Fore.RESET)

				print(Fore.RED + f'\n\t{traceback.format_exc()}\n' + Fore.RESET)

				time.sleep(retry_sleep_time)

				print(Fore.MAGENTA + f'[WARN][{THIS_SCRIPT_NAME}] - retrying \'{current_op}\' for {retry_count} more times.' + Fore.RESET)
			elif error_code == 400 and error_status == "INVALID_ARGUMENT" and "exceeds grid limits" in error_message:
				if starting_op == 'ws.update':
					# If the exception was due to the row limit being hit, need to extend the sheet with more rows.
					current_op = 'ws.add_rows'
			else:
				print(Fore.RED + f'\n\t{traceback.format_exc()}\n' + Fore.RESET)
				# Operation failed.
				deployment_result['succeeded'] = False
				return deployment_result

def load_gspread_sheet(gspread_spreadsheet, target_sheet_name: str) -> gspread.Worksheet:
	try:
		ws: gspread.Worksheet = load_sheet(gspread_spreadsheet, target_sheet_name)

		print(Fore.MAGENTA + f'[INFO][{THIS_SCRIPT_NAME}] - Loaded gspread.Worksheet: {target_sheet_name}.' + Fore.RESET)
	except gspread.exceptions.WorksheetNotFound:

		# Copy 'ZDC-Template' sheet which should be already formatted.
		template_sheet: gspread.Worksheet = None

		try:
			template_sheet = load_sheet(gspread_spreadsheet, "ZDC-Template")

			# We want to store the new worksheet at the end of the Google Sheet tabs.
			target_index: int = len(gspread_spreadsheet.worksheets())

			ws: gspread.Worksheet = template_sheet.duplicate(insert_sheet_index=target_index, new_sheet_name=target_sheet_name)

		except gspread.exceptions.WorksheetNotFound:
			print(Fore.RED + f'[WARN][{THIS_SCRIPT_NAME}] - template gspread.Worksheet {"ZDC-Template"} not found in gspread.Spreadsheet {str(gspread_spreadsheet)}.' + Fore.RESET)
			print(Fore.RED + f'[WARN][{THIS_SCRIPT_NAME}] - gspread.Worksheet: {target_sheet_name} will start blank.' + Fore.RESET)

		print(Fore.MAGENTA + f'[INFO][{THIS_SCRIPT_NAME}] - gspread.Worksheet {target_sheet_name} not found. Created one.' + Fore.RESET)

	return ws

def open_google_sheet_connection(service_acc: str, spreadsheet_name: str) -> gspread.Spreadsheet:
	# Open connection to Google Sheet API using gspread.
	gspread_spreadsheet: gspread.Spreadsheet = open_sheet(service_acc = service_acc, spreadsheet_name = spreadsheet_name)
	if gspread_spreadsheet == None:
		print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - could not use Google Sheet API, exiting.' + Fore.RESET)
		sys.exit(1)
	else:
		print(Fore.MAGENTA + f'[INFO][{THIS_SCRIPT_NAME}] - opened Google Sheet API sheet {spreadsheet_name} sucessfully.' + Fore.RESET)

	return gspread_spreadsheet

def update_sheet(ws: gspread.Spreadsheet, fields: Dict, field_order: List[str]) -> bool:
# def update_zeroday_sheet(ws: gspread.Spreadsheet, package: str, package_grades: Dict[str, Dict[str, Dict]]) -> bool:


	row: List[str] = []
	for fn in field_order:
		row.append(fields[fn])

	result: List[List[str]] = [row]# list(fields.values())

	trying_to_write: bool = True

	# Using this variable to control the sequence of calls to make with the gspread package.
	current_op: str = 'ws.col_values'

	# Row position to write within the Google Sheet.
	empty_row_index: int

	# Number of retries that will be made in the face of the API stating the service
	# is unavailable.
	MAX_RETRY_COUNT: int = 5
	retry_count: int = MAX_RETRY_COUNT

	# If the gspread API states the service is unavailable, sleep some minutes.
	retry_sleep_time: int = 300

	# Number of seconds to sleep between calls to the gspread API.
	inter_operation_sleep: int = 0

	# In the event that all rows are used, try to increase the number of rows by 'row_incr' rows.
	row_incr: int = 1000 #+ file_ctr

	while trying_to_write:

		# We are sleeping 'inter_operation_sleep' seconds between gspread calls
		# to avoid stressing the Google Sheet API.
		# See: https://developers.google.com/sheets/api/limits
		time.sleep(inter_operation_sleep)

		try:
			if current_op == 'ws.col_values':
				# Necessary to find out where exactly to write within the sheet.
				empty_row_index = max(len(ws.col_values(2)) + 1, 6)
				current_op = 'ws.update'
			elif current_op == 'ws.update':
				# The actual attempt to write into the sheet.
				print(Fore.MAGENTA + f'[INFO][{THIS_SCRIPT_NAME}] - Trying to write to sheet {ws.title}.' + Fore.RESET)
				#ws.update(f"A{empty_row_index}:F{len(result) + empty_row_index - 1}", result)
				#ws.update(f"A{empty_row_index}", result)
				ws.update(values = result, range_name = f"A{empty_row_index}")
				print(Fore.MAGENTA + f'[INFO][{THIS_SCRIPT_NAME}] - Write to {ws.title} successful.' + Fore.RESET)
				return True # writing to sheet was successful.
			elif current_op == 'ws.add_rows':
				# If the sheet was full, it produced a specific exception which set the next operation
				# to be 'ws.add_rows'.
				print(Fore.MAGENTA + f'[INFO][{THIS_SCRIPT_NAME}] - Adding {row_incr} rows to {ws.title}.' + Fore.RESET)
				ws.add_rows(row_incr)
				print(Fore.MAGENTA + f'[INFO][{THIS_SCRIPT_NAME}] - Rows added successfully.' + Fore.RESET)
				current_op = 'ws.update'

			# If a 'gspread' operation was successful, reset the retry counter.
			retry_count = MAX_RETRY_COUNT



		except gspread.exceptions.APIError as e:

			error_json = e.response.json()

			error_code: int = error_json.get('error', {}).get('code')
			error_status: str = error_json.get('error', {}).get('status')
			error_message: str = error_json.get('error', {}).get('message')

			info_str: str = get_gspread_exception_info_from_json(current_op, error_code, error_status, error_message)

			print(Fore.RED + info_str + Fore.RESET, flush=True)

			# pprint.pprint(error_code)
			# pprint.pprint(error_message)
			# pprint.pprint(type(error_message))
			# pprint.pprint(error_status)

			if error_code == 429:
				print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - too many requests error from Google API, sleeping 60 seconds.' + Fore.RESET)

				time.sleep(60)

				print(Fore.MAGENTA + f'[WARN][{THIS_SCRIPT_NAME}] - retrying \'{current_op}\'.' + Fore.RESET)

			elif error_code == 500 and error_status == "INTERNAL" and "error encountered" in error_message:
				print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - operation failed.' + Fore.RESET)
				retry_count -= 1

				if retry_count == 0:
					print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - All {MAX_RETRY_COUNT} operation retries failed.' + Fore.RESET)
					print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - Last attempted \'gspread\' operation: {current_op}.' + Fore.RESET)
					return False # failed writing to sheet.




				print(Fore.RED + f'[WARN][{THIS_SCRIPT_NAME}] - service encountered an internal error on \'{current_op}\', sleeping {retry_sleep_time} seconds.' + Fore.RESET)

				print(Fore.RED + f'\n\t{traceback.format_exc()}\n' + Fore.RESET)

				time.sleep(retry_sleep_time)

				print(Fore.MAGENTA + f'[WARN][{THIS_SCRIPT_NAME}] - retrying \'{current_op}\' for {retry_count} more times.' + Fore.RESET)
			elif error_code == 503 and error_status == "UNAVAILABLE" and "service is currently unavailable" in error_message:
				print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - operation failed.' + Fore.RESET)
				retry_count -= 1

				if retry_count == 0:
					print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - All {MAX_RETRY_COUNT} operation retries failed.' + Fore.RESET)
					print(Fore.RED + f'[ERROR][{THIS_SCRIPT_NAME}] - Last attempted \'gspread\' operation: {current_op}.' + Fore.RESET)
					return False # failed writing to sheet.




				print(Fore.RED + f'[WARN][{THIS_SCRIPT_NAME}] - service was unavailable on \'{current_op}\', sleeping {retry_sleep_time} seconds.' + Fore.RESET)

				print(Fore.RED + f'\n\t{traceback.format_exc()}\n' + Fore.RESET)

				time.sleep(retry_sleep_time)

				print(Fore.MAGENTA + f'[WARN][{THIS_SCRIPT_NAME}] - retrying \'{current_op}\' for {retry_count} more times.' + Fore.RESET)
			elif error_code == 400 and error_status == "INVALID_ARGUMENT" and "exceeds grid limits" in error_message:
				# If the exception was due to the row limit being hit, need to extend the sheet with more rows.
				current_op = 'ws.add_rows'
			else:
				print(Fore.RED + f'\n\t{traceback.format_exc()}\n' + Fore.RESET)
				return False


# def add_prompt(gspread_spreadsheet: gspread.Spreadsheet, client_id: str, fields: Dict, field_order: List[str]) -> bool:
def init_user_sheet(
		client_id: str,
		service_acc: str = '.config/service_account.json',
		spreadsheet_name: str = 'Red-Team-Prompts') -> gspread.Worksheet:

	# Open connection to Google Sheet API using gspread.
    gspread_spreadsheet: gspread.Spreadsheet = open_google_sheet_connection(service_acc = service_acc, spreadsheet_name = spreadsheet_name)

	# Create worksheet if it does not exist.
    target_sheet_name = f"prompts-{client_id}"

    try:
		# NOTE: need to share the spreadsheet or directory in Google Drive with the email in .config/service_account.json.
		# See: https://stackoverflow.com/a/68071735/1708550
        ws: gspread.Worksheet = load_sheet(gspread_spreadsheet, target_sheet_name)
        print(f'[INFO][{THIS_SCRIPT_NAME}] - Loaded gspread.Spreadsheet: {target_sheet_name}')
    except gspread.exceptions.WorksheetNotFound:

		# Copy 'ZDC-Template' sheet which is already formatted.
        template_sheet: gspread.Worksheet = load_sheet(gspread_spreadsheet, "P2SQL-Template")

		# We want to store the new worksheet at the end of the Google Sheet tabs.
        target_index: int = len(gspread_spreadsheet.worksheets())

        ws: gspread.Worksheet = template_sheet.duplicate(insert_sheet_index=target_index, new_sheet_name=target_sheet_name)

        print(f'[INFO][{THIS_SCRIPT_NAME}] - gspread.Spreadsheet {target_sheet_name} not found. Created one.')

    return ws

if __name__ == "__main__":
	service_acc: str = '.config/service_account.json'
	spreadsheet_name: str = 'Red-Team-Prompts'

	# Open connection to Google Sheet API using gspread.
	gspread_spreadsheet: gspread.Spreadsheet = open_google_sheet_connection(service_acc = service_acc, spreadsheet_name = spreadsheet_name)

	# Create worksheet if it does not exist.
	client_id: str = 'johndoe42'
	target_sheet_name = f"prompts-{client_id}"

	try:
		# NOTE: need to share the spreadsheet or directory in Google Drive with the email in .config/service_account.json.
		# See: https://stackoverflow.com/a/68071735/1708550
		ws: gspread.Worksheet = load_sheet(gspread_spreadsheet, target_sheet_name)
		print(f'[INFO][{THIS_SCRIPT_NAME}] - Loaded gspread.Spreadsheet: {target_sheet_name}')
	except gspread.exceptions.WorksheetNotFound:

		# Copy 'ZDC-Template' sheet which is already formatted.
		template_sheet: gspread.Worksheet = load_sheet(gspread_spreadsheet, "P2SQL-Template")

		# We want to store the new worksheet at the end of the Google Sheet tabs.
		target_index: int = len(gspread_spreadsheet.worksheets())

		ws: gspread.Worksheet = template_sheet.duplicate(insert_sheet_index=target_index, new_sheet_name=target_sheet_name)


		print(f'[INFO][{THIS_SCRIPT_NAME}] - gspread.Spreadsheet {target_sheet_name} not found. Created one.')

	field_order: List[str] = ['client_id', 'session_id', 'app_name', 'datetime', 'prompt', 'intermediate_steps', 'final_answer', 'query', 'effective', 'attack_type']


	fields: Dict = {
		'client_id': client_id,
		'session_id': 'totally-uncollidable-hash',
		'app_name': 'streamlit_agent-sql_db',
		'datetime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
		'prompt': 'How do you feel today, robot?',
		'intermediate_steps': 'all of the spam',
		'final_answer': 'Dandy!',
		'query': 'SELECT * FROM table_name',
		'effective': 'True',
		'attack_type': 'RD1'
	}


	write_succeeded: bool = update_sheet(ws, fields, field_order)
	if write_succeeded:
		# successfully wrote to the sheet.
		pass
	else:
		# some error happened, need to handle it.
		closing_pool_from_error = True
