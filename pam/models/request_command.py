"""
This module defines the RequestCommand class, 
which wraps an HTTP request to simplify access to its parameters and files.

Classes:
    RequestCommand: A dataclass that represents an HTTP request command 
    with various attributes and methods to process the request.

Methods:
    is_start_command(self): Determine if this command is a start command.
    is_dataset_command(self): Determine if this command is a dataset command.
    __safe_str_to_bool(value): Safely convert a string to a boolean.
    __extract_data_from_request(request: Request): Extract data from a Flask request object 
        based on its content type.
    __allowed_file(filename): Check if the file has an allowed extension.
    __extract_input_file(zip_file, service_name, token): Extract a zip file 
        into a temporary directory and return the file paths.
    parse(request, service_name): Create a RequestCommand object from an HTTP request.

"""
import os
from pathlib import Path
from dataclasses import dataclass
import zipfile
from flask import Request
from pam.utils import log
from pam.temp_file_utils import TempfileUtils

@dataclass
class RequestCommand:
    """
    Wraps an HTTP request to simplify access to its parameters and files.
    """
    runtime_parameters: dict
    token: str
    cmd: str
    data_api: str
    response_api: str
    is_end: bool
    next: str
    input_files: list[str]
    service_name: str

    def is_start_command(self):
        """Determine if this command is a start command."""
        return self.cmd == "start"

    def is_dataset_command(self):
        """Determine if this command is a dataset command."""
        return self.cmd == "dataset"

    @staticmethod
    def __safe_str_to_bool(value):
        """Safely convert a string to a boolean."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            value_lower = value.lower()
            if value_lower in {'true', '1', 'yes'}:
                return True
            if value_lower in {'false', '0', 'no'}:
                return False
        return False

    @staticmethod
    def __extract_data_from_request(request: Request):
        """
        Extract data from a Flask request object based on its content type.
        """
        if request.content_type == 'application/json':
            return request.get_json() or {}
        elif request.content_type.startswith('multipart/form-data'):
            return request.form.to_dict()
        return {}

    @staticmethod
    def __allowed_file(filename):
        """Check if the file has an allowed extension."""
        return filename.lower().endswith('.zip')

    @staticmethod
    def __extract_input_file(zip_file, service_name, token):
        """
        Extract a zip file into a temporary directory and return the file paths.
        """
        if not zip_file.filename:
            log("No file selected for upload.")
            return [], "No selected file"

        if not RequestCommand.__allowed_file(zip_file.filename):
            log("Invalid file type uploaded.")
            return [], "Invalid file type"

        temp_dir = TempfileUtils.get_temp_file_name(service_name, token, "dataset_")
        zip_file_path = f"{temp_dir}.zip"
        zip_file.save(zip_file_path)

        extract_dir = Path(temp_dir)
        extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            # Remove unnecessary files or directories
            for unwanted in ['__MACOSX', '.DS_Store']:
                unwanted_path = extract_dir / unwanted
                if unwanted_path.exists():
                    if unwanted_path.is_dir():
                        os.rmdir(unwanted_path)
                    else:
                        unwanted_path.unlink()

            input_files = sorted(str(file) for file in extract_dir.iterdir() if file.is_file())
            log(f"Extracted files: {input_files}")
            return input_files, ""

        except zipfile.BadZipFile:
            log("Failed to extract zip file.")
            return [], "Invalid or corrupted zip file"

    @staticmethod
    def parse(request, service_name):
        """
        Create a RequestCommand object from an HTTP request.
        """
        params = RequestCommand.__extract_data_from_request(request)

        token = params.pop("token", "")
        cmd = params.pop("cmd", "")
        data_api = params.pop("data", "")
        response_api = params.pop("response", "")
        is_end = RequestCommand.__safe_str_to_bool(params.pop("is_end", "true"))
        next_page = params.pop("next", "")

        input_files = []
        error_message = ""

        if not token:
            error_message = "The `token` parameter is required."
        elif cmd == "dataset":
            zip_file = request.files.get('file')
            if not zip_file:
                error_message = "A file must be uploaded for the `dataset` command."
            else:
                input_files, error_message = RequestCommand.__extract_input_file(
                    zip_file, service_name, token
                )

        return RequestCommand(
            runtime_parameters=params,
            token=token,
            cmd=cmd,
            data_api=data_api,
            response_api=response_api,
            is_end=is_end,
            next=next_page,
            input_files=input_files,
            service_name=service_name,
        ), error_message
