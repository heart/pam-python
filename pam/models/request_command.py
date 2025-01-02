
"""
RequestCommand is object that Wrap the http request to object that simple to access the parameters
"""

import os
from dataclasses import dataclass
import zipfile
from pathlib import Path
from pam.utils import log
from pam.temp_file_utils import TempfileUtils


@dataclass
class RequestCommand:
    """
    RequestCommand is object that Wrap the http request
    """

    token: str
    cmd: str
    data_request_api: str
    response_api: str
    is_end: bool
    next: str
    input_files: list[str]
    service_name: str

    def is_start_command(self):
        """Determine is this command is start command"""
        return self.cmd == "start"

    def is_dataset_command(self):
        """Determine is this command is dataset command"""
        return self.cmd == "dataset"

    @staticmethod
    def __safe_str_to_bool(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.lower() in ['true', '1', 'yes']:
                return True
            if value.lower() in ['false', '0', 'no']:
                return False
        return False

    @staticmethod
    def __extract_data_from_request(request, keys):
        result = {}

        if request.content_type == 'application/json':
            data = request.get_json()
            for key in keys:
                if key in data:
                    result[key] = data[key]
                else:
                    result[key] = ""
        elif request.content_type.startswith('multipart/form-data'):
            for key in keys:
                data_str = request.form.get(key, '')
                if data_str:
                    result[key] = data_str
                else:
                    result[key] = ""

        return result

    @staticmethod
    def __allowed_file(filename):
        return '.' in filename and filename.rsplit(
            '.', 1)[1].lower() in {'zip'}

    @staticmethod
    def __extract_input_file(zip_file, service_name, token):

        if zip_file.filename == '':
            log("handle_file_upload 'No selected file'")
            return ([], "No selected file")

        if not RequestCommand.__allowed_file(zip_file.filename):
            log("handle_file_upload 'Invalid file type'")
            return ([], "Invalid file type")

        zip_file_dir = TempfileUtils.get_temp_file_name(
            service_name, token, "dataset_")

        zip_file_name = f"{zip_file_dir}.zip"
        zip_file.save(zip_file_name)

        extract_dir = Path(zip_file_dir)
        extract_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:

            zip_ref.extractall(zip_file_dir)

            if os.path.exists(f"{extract_dir}/__MACOSX"):
                os.rmdir(f"{extract_dir}/__MACOSX")
            if os.path.exists(f"{extract_dir}/.DS_Store"):
                os.rmdir(f"{extract_dir}/.DS_Store")

        input_files = sorted([os.path.join(extract_dir, name)
                              for name in os.listdir(extract_dir)])

        log(f"Extract dir: {extract_dir}")
        log(f"File save to: {input_files}")

        return (input_files, "")

    @staticmethod
    def parse(request, service_name):
        """Create RequestCommand object from http request"""
        params = RequestCommand.__extract_data_from_request(
            request, ["cmd", "token", "data", "response", "is_end", "next"])

        token = params["token"]
        cmd = params["cmd"]
        data = params["data"]
        response = params["response"]
        is_end = RequestCommand.__safe_str_to_bool(params["is_end"])
        next_page = params["next"]
        input_files = []
        error_message = ""

        if not token:
            error_message = 'The `token` parameter is required.'
        else:
            if cmd == "dataset":
                zip_file = request.files['file']
                (files, error) = RequestCommand.__extract_input_file(
                    zip_file, service_name, token)
                error_message = error
                input_files = files

        return RequestCommand(
            token, cmd, data, response, is_end, next_page, input_files, service_name
        ), error_message
