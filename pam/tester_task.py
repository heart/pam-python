from typing import Callable, Tuple, List
from pam.models.request_command import RequestCommand
from pam.interface_task_manager import ITaskManager
from pam.service import Service


RequestDataCallbackType = Callable[[str], Tuple[List[str], bool, str]]

UploadResultCallbackType = Callable[[str], None]

UploadReportCallbackType = Callable[[str], None]


class TesterTask(ITaskManager):

    def __init__(self):
        self.request_data_callback: RequestDataCallbackType = None
        self.upload_result_calllback: UploadResultCallbackType = None
        self.upload_report_calllback: UploadReportCallbackType = None

    def set_on_request_data(self, request_data_callback: RequestDataCallbackType):
        self.request_data_callback = request_data_callback

    def set_on_upload_result(self, upload_result_calllback: UploadResultCallbackType):
        self.upload_result_calllback = upload_result_calllback

    def set_on_upload_report(self, upload_report_calllback: UploadReportCallbackType):
        self.upload_report_calllback = upload_report_calllback

    def test_service(self, service):
        service.on_start()

    # -----

    def on_dataset_input(self, req: RequestCommand):
        pass

    def start_service(self, service_class, req: RequestCommand, service_name):
        pass

    def terminate_service(self, token):
        pass

    def service_exit(self, service_class):
        print(f"{service_class.request.service_name} Exit.")

    def service_request_data(self, service: Service, page):
        if self.request_data_callback is not None:
            files, is_end, next_page = self.request_data_callback(page)
            req = RequestCommand(service.request.token, "dataset", "",
                                 "", is_end, next_page, files, service.request.service_name)
            service.on_data_input(req)

    def service_upload_result(self, service: Service, file_path):
        if self.upload_result_calllback is not None:
            self.upload_result_calllback(file_path)

    def service_upload_report(self, service: Service, file_path):
        if self.upload_report_calllback is not None:
            self.upload_report_calllback(file_path)
