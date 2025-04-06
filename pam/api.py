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

    def http_upload(self, url: str, file_path: str, payload: dict = None) -> requests.Response | None:
        """
        Uploads a file to the specified URL with optional form data (payload).

        :param url: The URL to upload the file to.
        :param file_path: The path to the file to be uploaded.
        :param payload: Optional dictionary of form fields to include in the request.
        :return: The response from the server, or None if an error occurred.
        """
        if not Path(file_path).is_file():
            log(f"File does not exist: {file_path}")
            return None

        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                response = self.session.post(
                    url,
                    files=files,
                    data=payload or {},  # optional form data
                    timeout=300
                )
                response.raise_for_status()
                return response
        except requests.RequestException as e:
            log(f"File upload failed. URL: {url}, File: {file_path}, Error: {e}")
            return None

    def download_sqlite_from_post(self, url: str, data: dict, output_path: str) -> bool:
        """
        Sends a POST request with JSON data and expects a SQLite file in response.
        Saves the response content as a .sqlite file.

        :param url: The URL to send the POST request to.
        :param data: Dictionary to send as JSON in the body.
        :param output_path: File path to save the .sqlite file.
        :return: True if successful, False otherwise.
        """
        headers = {'Content-Type': 'application/json'}
        try:
            response = self.session.post(url, json=data, timeout=60, headers=headers)
            response.raise_for_status()

            # Save response content to file
            with open(output_path, "wb") as f:
                f.write(response.content)

            log(f"SQLite file saved to {output_path}")
            return True
        except requests.RequestException as e:
            log(f"Failed to download SQLite. URL: {url}, Error: {e}")
            return False
        except IOError as e:
            log(f"Failed to save SQLite file. Path: {output_path}, Error: {e}")
            return False

    def close(self):
        """Close the session."""
        self.session.close()
