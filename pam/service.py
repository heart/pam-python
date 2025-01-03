from abc import abstractmethod
import json
from typing import TYPE_CHECKING, Union
import pandas as pd
import dask.dataframe as dd
from pam.utils import log, deep_convert_numbers_to_strings, get_adapter_id
from pam.models.request_command import RequestCommand
from pam.temp_file_utils import TempfileUtils

if TYPE_CHECKING:
    from pam.task_manager import TaskManager


class Service:
    """
    Service base class
    """

    def __init__(self, task_manager: 'TaskManager', req: RequestCommand):
        self.request = req
        self.task_manager = task_manager

    # == REQUEST DATA ===
    def _request_data(self, page: str = "") -> None:
        """Requests data for the specified page."""
        log(f"{self.request.service_name}: Requesting data for page={page}")
        self.task_manager.service_request_data(self, page)

    # == UPLOAD RESULT ===
    def _upload_result(self, df: Union[pd.DataFrame, dd.DataFrame]) -> str:
        """
        Uploads the result DataFrame to a temporary file and notifies the task manager.
        """
        if isinstance(df, dd.DataFrame):
            df = df.compute()
        elif not isinstance(df, pd.DataFrame):
            raise ValueError("The input must be a Pandas or Dask DataFrame")

        tmp_file_name = TempfileUtils.get_temp_file_name(
            self.request.service_name, self.request.token, "result_", ".csv"
        )

        try:
            df.to_csv(tmp_file_name, index=False)
            log(f"{self.request.service_name}: Uploading result file: {tmp_file_name}")
            self.task_manager.service_upload_result(self, tmp_file_name)
        except Exception as e:
            log(f"Failed to upload result file: {e}")
            raise

        return tmp_file_name

    # == UPLOAD REPORT ===
    def _upload_report(self, report_name: str, report_json: dict) -> None:
        """
        Uploads a report in JSON format to a temporary file and notifies the task manager.
        """
        if not isinstance(report_json, dict):
            raise ValueError("report_json must be a dictionary")

        adapter_id = get_adapter_id(self.request.response_api)
        service_name = self.request.service_name
        token = self.request.token

        report_json = deep_convert_numbers_to_strings(report_json)
        json_string = json.dumps(report_json)

        formatted_report_name = f"data_{report_name}_no_index"
        df = pd.DataFrame({
            'customer': [adapter_id],
            formatted_report_name: [json_string]
        })

        report_csv_path = TempfileUtils.get_temp_file_name(
            service_name, token, f"report_{report_name}_", '.csv'
        )

        try:
            df.to_csv(report_csv_path, index=False)
            log(f"{self.request.service_name}: Uploading report file: {report_csv_path}")
            self.task_manager.service_upload_report(self, report_csv_path)
        except Exception as e:
            log(f"Failed to upload report: {e}")
            raise

    def _exit(self) -> None:
        """Signals the task manager to exit the service."""
        self.task_manager.service_exit(self)

    # Abstract methods to be implemented by subclasses
    @abstractmethod
    def on_start(self) -> None:
        """
        Define the behavior when the service starts.
        """
        pass

    @abstractmethod
    def on_data_input(self, req: RequestCommand) -> None:
        """
        Define the behavior for handling data input.
        """
        pass

    @abstractmethod
    def on_destroy(self) -> None:
        """
        Define the behavior when the service is destroyed.
        """
        pass

    @abstractmethod
    def on_terminate(self) -> None:
        """
        Define the behavior when the service is terminated.
        """
        pass

    @abstractmethod
    def get_status(self) -> str:
        """
        Define the behavior for retrieving the service status.
        """
        pass
