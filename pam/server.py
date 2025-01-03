"""
Data Plugin Server
"""

import os
import importlib
import yaml
from setuptools import find_packages
from flask import request, make_response, Flask, jsonify
from pam.utils import log
from pam.models.request_command import RequestCommand
from pam.task_manager import TaskManager
from pam.temp_file_utils import TempfileUtils
from threading import Lock


class Server:
    """
    Data Plugin Server
    """

    app: Flask
    servicePool = {}
    _lock = Lock()

    def __init__(self, app: Flask):
        self.task_manager = TaskManager(self)
        self.app = app
        self.register_service()
        self.task_manager.start_service_monitoring_schedul()

        @app.route('/', methods=['GET'])
        def home():
            return self.response_ok({'message': "Hello, Data plugin v2."})

        @app.route('/service/<service_name>', methods=['POST'])
        def run(service_name):
            TempfileUtils.clean_temp()

            req, error_request = RequestCommand.parse(request, service_name)

            if error_request:
                response = {'message': error_request}
                return self.response_error(response, 400)

            response, code = self.handle_service_cmd(service_name, req)
            return self.response_error(response, code)

        @app.route('/tasks', methods=['GET'])
        def tasks():
            return self.response_ok({'message': "OK"})

        @app.route('/status/<service_name>', methods=['GET'])
        def ping(service_name):
            return self.response_ok({'message': f"OK {service_name}"})

    def get_service_class(self, service_name: str):
        """
        Get service class from service name.
        """
        with self._lock:
            return self.servicePool.get(service_name)

    def handle_service_cmd(self, service_name: str, req: RequestCommand):
        """
        Handle all command types for a service.
        """
        service_class = self.get_service_class(service_name)

        if service_class is not None:
            if req.is_start_command():
                log(f"Request on start {service_name} token={req.token}")
                return self.on_start(service_class, req, service_name)

            if req.is_dataset_command():
                log(f"Request on dataset {service_name} token={req.token} files={req.input_files}")
                return self.on_dataset(req)

        response = {'message': f'Service `{service_name}` Not found.'}
        return response, 404

    def on_start(self, service_class, req: RequestCommand, service_name: str):
        """
        Start a service.
        """
        log(f"{service_name} -> on_start")
        self.task_manager.start_service(service_class, req, service_name)
        return {'acknowledge': True}, 200

    def on_dataset(self, req: RequestCommand):
        """
        TaskManager handles cmd=dataset.
        """
        log(f"{req.service_name} -> on_dataset")
        self.task_manager.on_dataset_input(req)
        return {'acknowledge': True}, 200

    def on_register_service(self, service, end_point: str):
        """
        Register a service.
        """
        log(f'Register service "{service}", endpoint: http://localhost/service/{end_point}')
        with self._lock:
            self.servicePool[end_point] = service

    def run(self, host: str = None, port: int = None):
        """
        Run Flask app.
        """
        host = host or os.getenv('SERVER_HOST', '0.0.0.0')
        port = port or int(os.getenv('SERVER_PORT', '8000'))
        self.app.run(host=host, port=port)

    def response_error(self, json: dict, code: int):
        """
        Create an error response with a custom HTTP status code.
        """
        data = jsonify(json)
        return make_response(data, code)

    def response_ok(self, json: dict, code: int = 200):
        """
        Create a response object with 200 OK.
        """
        data = jsonify(json)
        return make_response(data, code)

    def load_yaml(self, file_path: str) -> dict | None:
        """
        Load a YAML file and return its content.
        """
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        return None

    def get_service_config(self, package: str) -> dict | None:
        """
        Load the service config from `service.yaml` or `service.yml`.
        """
        for ext in ('yaml', 'yml'):
            config_path = f'{package}/service.{ext}'
            if os.path.exists(config_path) and os.path.isfile(config_path):
                return self.load_yaml(config_path)
        return None

    def register_service(self):
        """
        Scan the project to register all plugin services with validation.
        """
        packages = find_packages()
        for package in packages:
            config = self.get_service_config(package)
            if config and self.validate_service_config(config):
                endpoint = config['endpoint']
                class_name = config['class']
                try:
                    module = importlib.import_module(f'{package}.{class_name}')
                    class_ = getattr(module, class_name)
                except (ModuleNotFoundError, AttributeError) as e:
                    log(f"Error loading service '{class_name}': {e}")
                    continue

                if endpoint.startswith("/"):
                    endpoint = endpoint[1:]

                self.on_register_service(class_, endpoint)
            else:
                log(f"Error: Failed to register service from package '{package}'.")

    def validate_service_config(self, config: dict) -> bool:
        """
        Validate the structure of a service configuration.
        """
        required_keys = ['endpoint', 'class']
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            log(f"Error: Missing required keys {missing_keys} in service config.")
            return False
        return True
