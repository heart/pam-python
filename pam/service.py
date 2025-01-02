"""
Service base class
"""

import os
import tempfile
import uuid
from abc import abstractmethod
import json
from typing import TYPE_CHECKING
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

    # pylint: disable=too-many-instance-attributes
    def __init__(self, task_manager: 'TaskManager', req: RequestCommand):
        self.request = req
        self.task_manager = task_manager

    # == REQUEST DATA ===
    def _request_data(self, page=""):
        log(f"{self.request.service_name}: Request data page={page}")
        self.task_manager.service_request_data(self, page)

    # == UPLOAD RESULT ===
    def _upload_result(self, df):
        if isinstance(df, dd.DataFrame):
            df = df.compute()
        elif not isinstance(df, pd.DataFrame):
            raise ValueError("The input must be a Pandas or Dask DataFrame")

        tmp_file_name = TempfileUtils.get_temp_file_name(
            self.request.service_name, self.request.token, "result_", ".csv")

        df.to_csv(tmp_file_name, index=False)

        log(f"{self.request.service_name}: Upload Result File {tmp_file_name}")
        self.task_manager.service_upload_result(self, tmp_file_name)

        return tmp_file_name

    # == UPLOAD REPORT ===

    def _upload_report(self, report_name: str, report_json: str):
        adapter_id = get_adapter_id(self.request.response_api)
        service_name = self.request.service_name
        token = self.request.token

        # important need to recursive and convert numbers to str
        report_json = deep_convert_numbers_to_strings(
            report_json)

        json_string = json.dumps(report_json)

        report_name = f"data_{report_name}_no_index"

        df = pd.DataFrame({
            'customer': [adapter_id],
            report_name: [json_string]
        })

        report_csv_path = TempfileUtils.get_temp_file_name(
            service_name, token, f"report_{report_name}_", '.csv')

        df.to_csv(report_csv_path, index=False)
        self.task_manager.service_upload_report(self, report_csv_path)
    # =========

    def _exit(self):
        self.task_manager.service_exit(self)

    @abstractmethod
    def on_start(self):
        """on sstart"""

    @abstractmethod
    def on_data_input(self, req):
        """on_data_input"""

    @abstractmethod
    def on_destroy(self):
        """on_destroy"""

    @abstractmethod
    def on_terminate(self):
        """on_terminate"""

    @abstractmethod
    def get_status(self):
        """get_status"""
