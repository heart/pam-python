from pathlib import Path
import requests
from pam.utils import log


class API:
    def __init__(self):
        self.session = requests.Session()  # Use a session for connection reuse

    def http_post(self, url: str, data: dict) -> requests.Response | None:
        """
        Sends an HTTP POST request to the specified URL with the given data as JSON.

        :param url: The URL to send the POST request to.
        :param data: A dictionary to be used as the JSON body of the POST request.
        :return: The response from the server, or None if an error occurred.
        """
        headers = {'Content-Type': 'application/json'}
        try:
            response = self.session.post(
                url, json=data, timeout=30, headers=headers
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            log(f"HTTP POST request failed. URL: {url}, Error: {e}")
            return None

    def http_upload(self, url: str, file_path: str) -> requests.Response | None:
        """
        Uploads a file to the specified URL.

        :param url: The URL to upload the file to.
        :param file_path: The path to the file to be uploaded.
        :return: The response from the server, or None if an error occurred.
        """
        if not Path(file_path).is_file():
            log(f"File does not exist: {file_path}")
            return None

        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                response = self.session.post(url, files=files, timeout=300)
                response.raise_for_status()
                return response
        except requests.RequestException as e:
            log(f"File upload failed. URL: {url}, File: {file_path}, Error: {e}")
            return None

    def close(self):
        """Close the session."""
        self.session.close()
