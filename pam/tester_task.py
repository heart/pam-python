from typing import Callable, Tuple, List, Optional
from pam.models.request_command import RequestCommand
from pam.interface_task_manager import ITaskManager
from pam.service import Service


RequestDataCallbackType = Callable[[str], Tuple[List[str], bool, str]]
UploadResultCallbackType = Callable[[str], None]
UploadReportCallbackType = Callable[[str], None]


class TesterTask(ITaskManager):
    """
    Mock implementation of ITaskManager for testing services.

    Allows simulation of task manager behaviors via callbacks.
    """

    def __init__(self):
        self.request_data_callback: Optional[RequestDataCallbackType] = None
        self.upload_result_callback: Optional[UploadResultCallbackType] = None
        self.upload_report_callback: Optional[UploadReportCallbackType] = None

    def set_on_request_data(self, request_data_callback: RequestDataCallbackType):
        """
        Set the callback for simulating data requests.
        """
        self.request_data_callback = request_data_callback

    def set_on_upload_result(self, upload_result_callback: UploadResultCallbackType):
        """
        Set the callback for simulating result uploads.
        """
        self.upload_result_callback = upload_result_callback

    def set_on_upload_report(self, upload_report_callback: UploadReportCallbackType):
        """
        Set the callback for simulating report uploads.
        """
        self.upload_report_callback = upload_report_callback

    def test_service(self, service: Service):
        """
        Simulate starting the service.

        :param service: The service to test.
        """
        service.on_start()

    # Interface Method Implementations
    def on_dataset_input(self, req: RequestCommand):
        pass

    def start_service(self, service_class, req: RequestCommand, service_name: str):
        pass

    def terminate_service(self, token: str):
        pass

    def service_exit(self, service: Service):
        print(f"{service.request.service_name} Exit.")

    def service_request_data(self, service: Service, page: str):
        """
        Simulate a service data request.

        :param service: The service requesting data.
        :param page: The page identifier for the data request.
        """
        if self.request_data_callback is not None:
            try:
                files, is_end, next_page = self.request_data_callback(page)
                req = RequestCommand(
                    runtime_parameters={},
                    token=service.request.token,
                    cmd="dataset",
                    data_api="",
                    response_api="",
                    is_end=is_end,
                    next=next_page,
                    input_files=files,
                    service_name=service.request.service_name,
                )
                service.on_data_input(req)
            except Exception as e:
                print(f"Error in request_data_callback: {e}")
        else:
            print("Request data callback is not set.")

    def service_upload_result(self, service: Service, file_path: str):
        """
        Simulate a service result upload.

        :param service: The service uploading the result.
        :param file_path: The path of the file being uploaded.
        """
        if self.upload_result_callback is not None:
            try:
                self.upload_result_callback(file_path)
            except Exception as e:
                print(f"Error in upload_result_callback: {e}")
        else:
            print("Upload result callback is not set.")

    def service_upload_report(self, service: Service, file_path: str):
        """
        Simulate a service report upload.

        :param service: The service uploading the report.
        :param file_path: The path of the report file being uploaded.
        """
        if self.upload_report_callback is not None:
            try:
                self.upload_report_callback(file_path)
            except Exception as e:
                print(f"Error in upload_report_callback: {e}")
        else:
            print("Upload report callback is not set.")
