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


class Server:
    """
    Data Plugin Server
    """

    app: Flask
    servicePool = {}

    def __init__(self, app):
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

            if error_request != "":
                response = {
                    'message': error_request
                }
                return self.response_error(response, 400)

            response, code = self.handle_service_cmd(service_name, req)
            return self.response_error(response, code)

        @app.route('/tasks', methods=['GET'])
        def tasks():
            return self.response_ok({'message': "OK"})

        @app.route('/status/<service_name>', methods=['GET'])
        def ping(service_name):
            # TODO: check the service status
            return self.response_ok({'message': f"OK {service_name}"})

    def get_service_class(self, service_name):
        """
        Get service class from service name
        """
        if service_name in self.servicePool:
            return self.servicePool[service_name]

        return None

    def handle_service_cmd(self, service_name, req: RequestCommand):
        """
        Handle all cmd type
        """
        service_class = self.get_service_class(service_name)

        if service_class is not None:
            if req.is_start_command():
                log(f"Request on start {service_name} token={req.token}")
                return self.on_start(service_class, req, service_name)

            if req.is_dataset_command():

                log(f"""Request on dataset {service_name} token={
                    req.token} files={req.input_files}""")

                return self.on_dataset(req)

        response = {'message': f'Service `{service_name}` Notfound. '}
        return response, 404

    def on_start(self, service_class, req, service_name):
        """
        start a service
        """
        log(f"{service_name} -> on_start")
        self.task_manager.start_service(service_class, req, service_name)
        return {'acknowledge': True}, 200

    def on_dataset(self, req):
        """
        task_manager handle cmd=dataset
        """
        log(f"{req.service_name} -> on_dataset")
        self.task_manager.on_dataset_input(req)
        return {'acknowledge': True}, 200

    def on_register_service(self, service, end_point):
        """
        register a service
        """
        log(f"register service \"{service}\", endpoint: http://localhost/service/{end_point}")
        self.servicePool[end_point] = service

    def run(self, host='0.0.0.0', port=8000):
        """
        run flask app
        """
        self.app.run(host=host, port=port)

    def response_error(self, json, code):
        """
        create error response with custom http status code
        """
        data = jsonify(json)
        return make_response(data, code)

    def response_ok(self, json, code=200):
        """
        create response object with 200OK
        """
        data = jsonify(json)
        return make_response(data, code)

    def get_service_config(self, package):
        """
        load the service config from service.yml
        """
        config_path_1 = f'{package}/service.yaml'
        config_path_2 = f'{package}/service.yml'
        if os.path.exists(config_path_1) and os.path.isfile(config_path_1):
            with open(config_path_1, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                return config
        elif os.path.exists(config_path_2) and os.path.isfile(config_path_2):
            with open(config_path_2, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                return config
        return None

    def register_service(self):
        """
        scan project to register all plugin services
        """
        packages = find_packages()
        for package in packages:
            config = self.get_service_config(package)
            if config is not None:
                endpoint = config['endpoint']
                class_name = config['class']
                module = importlib.import_module(
                    f'{package}.{class_name}')

                try:
                    class_ = getattr(module, class_name)
                except AttributeError:
                    log(
                        f"Error: Class '{class_name}' not found in module '{module}'.")
                    class_ = None

                if endpoint.startswith("/"):
                    endpoint = endpoint[1:]

                self.on_register_service(class_, endpoint)
