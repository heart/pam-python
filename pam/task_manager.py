from datetime import datetime, timedelta
import time
import threading
from typing import Dict
from pam.utils import log
from pam.api import API
from pam.service import Service
from pam.models.request_command import RequestCommand
from pam.interface_task_manager import ITaskManager


class ServiceHolder:
    def __init__(self, service: Service):
        self.service = service
        self.last_activity = datetime.now()

    def update_timestamp(self):
        self.last_activity = datetime.now()

    def has_timed_out(self, timeout=2):
        """Check if the service has been inactive longer than the timeout (in hours)."""
        return datetime.now() - self.last_activity > timedelta(hours=timeout)


class TaskManager(ITaskManager):
    """
    Manages service threads.
    """

    def __init__(self, server, monitoring_interval=600, timeout=2):
        self.services: Dict[str, ServiceHolder] = {}
        self.api = API()
        self.server = server
        self.thread_lock = threading.Lock()
        self.monitoring_interval = monitoring_interval
        self.timeout = timeout
        self.stop_event = threading.Event()

    # ==== Service Management ====
    def _add_service(self, token, service):
        with self.thread_lock:
            self.services[token] = ServiceHolder(service)

    def _get_service_holder(self, token):
        with self.thread_lock:
            return self.services.get(token)

    def _update_service(self, token):
        with self.thread_lock:
            if token in self.services:
                self.services[token].update_timestamp()

    def _check_timeout(self, token):
        with self.thread_lock:
            if token in self.services:
                return self.services[token].has_timed_out(self.timeout)
        return False

    def _remove_service(self, token):
        with self.thread_lock:
            if token in self.services:
                service_holder = self.services[token]
                log(f"Service Exit: {service_holder.service.request.service_name}, {service_holder.service.request.token}")
                service_holder.service.on_destroy()
                del self.services[token]

    # ==== Monitoring ====
    def start_service_monitoring_schedul(self):
        """
        Starts the service monitoring thread.
        """
        self.stop_event.clear()
        schedule_thread = threading.Thread(
            target=self._monitor_services, args=(self.monitoring_interval, self.stop_event)
        )
        schedule_thread.daemon = True
        schedule_thread.start()

    def stop_service_monitoring(self):
        """
        Stops the service monitoring thread.
        """
        self.stop_event.set()

    def _monitor_services(self, interval, stop_event):
        """
        Periodically checks for services that have timed out.
        """
        while not stop_event.is_set():
            time.sleep(interval)
            log("Service Monitor running.")
            tokens_to_remove = [
                token for token in self.services if self._check_timeout(token)
            ]
            log(f"Found: {len(tokens_to_remove)} services timed out.")
            for token in tokens_to_remove:
                log(f"Service {token} has timed out. Removing...")
                self._remove_service(token)

    # ==== Command Handlers ====
    def on_dataset_input(self, req: RequestCommand):
        """
        Handles cmd=dataset for an existing service.
        """
        service_holder = self._get_service_holder(req.token)
        if service_holder is not None:
            service_holder.update_timestamp()
            service_holder.service.on_data_input(req)

    def start_service(self, service_class, req: RequestCommand, service_name):
        """
        Starts a new service.
        """
        log(f"Start Service: {service_name}, Token: {req.token}")
        service_instance = service_class(self, req)
        service_instance.on_start()
        self._add_service(req.token, service_instance)

    def terminate_service(self, token):
        """
        Terminates a service by token.
        """
        service_holder = self._get_service_holder(token)
        if service_holder is not None:
            service_holder.service.on_terminate()
            self._remove_service(token)

    # ==== Service Callbacks ====
    def service_request_data(self, service: Service, page):
        """
        Makes an asynchronous request for data from a service.
        """
        endpoint = service.request.data_api
        token = service.request.token
        json_data = {"page": page, "token": token}

        log(f"Requesting Data from: {endpoint}, page: {page}, token={token}")
        http_thread = threading.Thread(target=self.api.http_post, args=(endpoint, json_data))
        http_thread.start()

    def service_upload_result(self, service: Service, file_path):
        """
        Uploads a result file asynchronously.
        """
        endpoint = service.request.response_api
        log(f"Uploading Result to: {endpoint}")
        http_thread = threading.Thread(target=self.api.http_upload, args=(endpoint, file_path))
        http_thread.start()

    def service_upload_report(self, service: Service, file_path):
        """
        Uploads a report file asynchronously.
        """
        endpoint = service.request.response_api
        log(f"Uploading Report to: {endpoint}")
        http_thread = threading.Thread(target=self.api.http_upload, args=(endpoint, file_path))
        http_thread.start()

    def service_exit(self, service: Service):
        """
        Removes a service from the manager and handles cleanup.
        """
        self._remove_service(service.request.token)
