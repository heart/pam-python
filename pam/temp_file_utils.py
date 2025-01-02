from pathlib import Path
from datetime import datetime, timedelta
import shutil
import uuid
from pam.utils import log


def clean_old_folders(days: int):

    base_folder = Path(TempfileUtils.temp_datasource_path)

    if not base_folder.exists():
        log("No temp dir to clean")
        return
    elif base_folder.is_file():
        log("Something wrong, temp dir is not folder. Plugin will delete it.")
        base_folder.unlink()
        return

    cutoff_date = datetime.now() - timedelta(days=days)

    # Iterate through all subfolders in the base_folder
    for folder in base_folder.iterdir():
        if folder.is_dir():
            try:
                # Extract the date from the folder name
                folder_date = datetime.strptime(folder.name, "%Y_%m_%d")

                # If the folder is older than the cutoff date, remove it
                if folder_date < cutoff_date:
                    shutil.rmtree(folder)
                    log(f"Removed folder: {folder}")
            except ValueError:
                # If folder name doesn't match the expected format, skip it
                log(f"""Skipping folder: {
                    folder} (unexpected name format)""")


class TempfileUtils:

    temp_base_path = "/app/data"
    temp_datasource_path = "/app/data/data_sources"

    @staticmethod
    def clean_temp():
        clean_old_folders(10)

    @staticmethod
    def get_temp_path(service_name, token):
        date_path = datetime.now().strftime("%Y_%m_%d")
        temp_dir = f"""{TempfileUtils.temp_datasource_path}/{date_path}/{service_name}/{
            token}"""
        folder_path = Path(temp_dir)
        folder_path.mkdir(parents=True, exist_ok=True)
        return temp_dir

    @staticmethod
    def get_temp_file_name(service_name, token, prefix="", extension=""):
        unique_filename = uuid.uuid1().hex

        if prefix:
            if prefix.endswith("_"):
                unique_filename = f"{prefix}{unique_filename}"
            else:
                unique_filename = f"{prefix}_{unique_filename}"

        if extension:
            if extension.startswith("."):
                unique_filename = f"{unique_filename}{extension}"
            else:
                unique_filename = f"{unique_filename}.{extension}"

        temp_path = TempfileUtils.get_temp_path(service_name, token)
        full_path = Path(temp_path) / unique_filename
        return full_path
