from pathlib import Path
from datetime import datetime, timedelta
import shutil
import uuid
import os
from pam.utils import log


def clean_old_folders(days: int, base_folder_path: str):
    """
    Cleans up folders older than the specified number of days in the base folder.

    :param days: Number of days to retain folders.
    :param base_folder_path: The base folder path to clean.
    """
    base_folder = Path(base_folder_path)

    if not base_folder.exists():
        log("No temp dir to clean.")
        return
    elif base_folder.is_file():
        log("Unexpected file at temp dir location. Deleting the file.")
        base_folder.unlink()
        return

    cutoff_date = datetime.now() - timedelta(days=days)
    folders_removed = 0

    for folder in base_folder.iterdir():
        if folder.is_dir():
            try:
                folder_date = datetime.strptime(folder.name, "%Y_%m_%d")
                if folder_date < cutoff_date:
                    shutil.rmtree(folder)
                    log(f"Removed folder: {folder}")
                    folders_removed += 1
            except ValueError:
                log(f"Skipping folder: {folder} (unexpected name format)")
            except Exception as e:
                log(f"Error removing folder {folder}: {e}")

    log(f"Clean-up complete. Total folders removed: {folders_removed}")


class TempfileUtils:
    """
    Utility class for managing temporary files and directories.
    """

    temp_base_path = os.getenv("TEMP_BASE_PATH", "/app/data")
    temp_datasource_path = os.getenv("TEMP_DATASOURCE_PATH", "/app/data/data_sources")

    @staticmethod
    def clean_temp(days=10):
        """
        Cleans up old temporary folders.
        """
        clean_old_folders(days, TempfileUtils.temp_datasource_path)

    @staticmethod
    def get_temp_path(service_name: str, token: str) -> str:
        """
        Gets or creates a temporary path for a service and token.

        :param service_name: The name of the service.
        :param token: The unique token for the service request.
        :return: The path to the temporary directory.
        """
        date_path = datetime.now().strftime("%Y_%m_%d")
        temp_dir = f"{TempfileUtils.temp_datasource_path}/{date_path}/{service_name}/{token}"
        folder_path = Path(temp_dir)
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            log(f"Error creating temp directory {temp_dir}: {e}")
            raise
        return temp_dir

    @staticmethod
    def get_temp_file_name(service_name: str, token: str, prefix: str = "", extension: str = "") -> str:
        """
        Generates a unique temporary file name.

        :param service_name: The name of the service.
        :param token: The unique token for the service request.
        :param prefix: Optional prefix for the file name.
        :param extension: Optional file extension.
        :return: The full path to the temporary file.
        """
        unique_filename = uuid.uuid1().hex

        if prefix:
            unique_filename = f"{prefix.rstrip('_')}_{unique_filename}"

        if extension:
            unique_filename = f"{unique_filename.lstrip('.')}.{extension.lstrip('.')}"

        temp_path = TempfileUtils.get_temp_path(service_name, token)
        full_path = Path(temp_path) / unique_filename
        return str(full_path)
