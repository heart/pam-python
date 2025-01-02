from abc import ABC, abstractmethod
from pam.models.request_command import RequestCommand
from pam.service import Service


class ITaskManager(ABC):

    @abstractmethod
    def on_dataset_input(self, req: RequestCommand):
        pass

    @abstractmethod
    def start_service(self, service_class, req: RequestCommand, service_name):
        pass

    @abstractmethod
    def terminate_service(self, token):
        pass

    @abstractmethod
    def service_request_data(self, service: Service, page):
        pass

    @abstractmethod
    def service_upload_result(self, service: Service, file_path):
        pass

    @abstractmethod
    def service_upload_report(self, service: Service, file_path):
        pass
