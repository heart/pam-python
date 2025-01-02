import requests
from pam.utils import log


class API:

    def http_post(self, url, data):
        """
        Sends an HTTP POST request to the specified URL with the given data as JSON.

        :param url: The URL to send the POST request to.
        :param data: A dictionary to be used as the JSON body of the POST request.
        :return: The response from the server.
        """
        headers = {
            'Content-Type': 'application/json'}
        try:
            response = requests.post(
                url, json=data, timeout=30, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response
        except requests.RequestException as e:
            log(f"HTTP POST request failed: {e}")
            return None

    def http_upload(self, url, file_path):
        """
        Uploads a file to the specified URL.

        :param url: The URL to upload the file to.
        :param file_path: The path to the file to be uploaded.
        :return: The response from the server.
        """
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                response = requests.post(url, files=files, timeout=300)
                response.raise_for_status()  # Raise an exception for HTTP errors
                return response
        except requests.RequestException as e:
            log(f"File upload failed: {e}")
            return None
