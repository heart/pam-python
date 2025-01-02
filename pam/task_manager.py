from datetime import datetime, timedelta
import time
import threading
from typing import Dict
from pam.utils import log
from pam.api import API
from pam.service import Service
from pam.models.request_command import RequestCommand
from pam.interface_task_manager import ITaskManager
from pam.temp_file_utils import TempfileUtils


class ServiceHolder:
    def __init__(self, service: Service):
        self.service = service
        self.last_activity = datetime.now()

    def update_timestamp(self):
        self.last_activity = datetime.now()

    def has_timed_out(self, timeout=2):
        # ตรวจสอบว่า service นี้ไม่เคลื่อนไหวเกินกว่า timeout ชั่วโมงหรือไม่
        return datetime.now() - self.last_activity > timedelta(hours=timeout)


class TaskManager(ITaskManager):
    """
    Manage service thread
    """

    def __init__(self, server):
        self.services: Dict[str, ServiceHolder] = {}
        self.api = API()
        self.server = server
        self.thread_lock = threading.Lock()

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

    def _check_timeout(self, token, timeout=2):
        with self.thread_lock:
            if token in self.services:
                return self.services[token].has_timed_out(timeout)
        return False

    def _remove_service(self, token):
        with self.thread_lock:
            if token in self.services:
                service_holder = self.services[token]
                log(f"Service Exit: {
                    service_holder.service.request.service_name}, {service_holder.service.request.token}")
                service_holder.service.on_destroy()
                del self.services[token]

    def start_service_monitoring_schedul(self):
        schedule_thread = threading.Thread(target=self._monitor_services)
        schedule_thread.daemon = True
        schedule_thread.start()

    def _monitor_services(self, interval=600, timeout=2):
        while True:
            time.sleep(interval)
            log("Service Monitor running.")
            tokens_to_remove = [
                token for token in self.services if self._check_timeout(token, timeout)
            ]
            log(f"Found: {len(tokens_to_remove)} services timeout.")
            for token in tokens_to_remove:
                log(f"Service {token} has timed out. Removing...")
                self._remove_service(token)

    def on_dataset_input(self, req: RequestCommand):
        """
        handle cmd dataset
        """
        service_holder = self._get_service_holder(req.token)
        if service_holder is not None:
            service_holder.update_timestamp()
            service_holder.service.on_data_input(req)

    def start_service(self, service_class, req: RequestCommand, service_name):
        """
        Start new service
        """
        log(f"Start Services {service_name}, Token: {req.token}")
        service_instance = service_class(self, req)
        service_instance.on_start()
        self._add_service(req.token, service_instance)

    def terminate_service(self, token):
        """
        stop service that started from a token
        """
        service_holder = self._get_service_holder(token)
        if service_holder is not None:
            service_holder.service.on_terminate()
            self._remove_service(token)

    # ======= Service Callback function ======
    def service_request_data(self, service: Service, page):
        endpoint = service.request.data_request_api
        token = service.request.token

        json_data = {"page": page, "token": token}

        log(f"Request Data to: {endpoint}, page: {page}, token={token}")
        http_thread = threading.Thread(
            target=self.api.http_post, args=(endpoint, json_data, ))
        http_thread.start()
        http_thread.join()

    def service_upload_result(self, service: Service, file_path):
        endpoint = service.request.response_api

        log(f"Upload Data to: {endpoint}")
        http_thread = threading.Thread(
            target=self.api.http_upload, args=(endpoint, file_path, ))
        http_thread.start()
        http_thread.join()

    def service_upload_report(self, service: Service, file_path):
        endpoint = service.request.response_api

        log(f"Upload Report to: {endpoint}")
        http_thread = threading.Thread(
            target=self.api.http_upload, args=(endpoint, file_path, ))
        http_thread.start()
        http_thread.join()

    def service_exit(self, service: Service):
        self._remove_service(service.request.token)
