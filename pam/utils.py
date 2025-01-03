import os
import tempfile
from datetime import datetime
import re
import pytz
from typing import Any


def get_adapter_id(url: str) -> str:
    """
    Extracts the adapter ID from a given URL.

    :param url: The URL to parse.
    :return: The extracted adapter ID or an empty string if not found.
    """
    pattern = r'/api/dataadapter/(\w+)/response'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    log(f"Adapter ID not found in URL: {url}", level="WARNING")
    return ""


def deep_convert_numbers_to_strings(data: Any) -> Any:
    """
    Recursively converts all numeric values in a nested structure to strings.

    :param data: The input data structure (dict, list, tuple, etc.).
    :return: The transformed data structure with numbers as strings.
    """
    if isinstance(data, dict):
        return {key: deep_convert_numbers_to_strings(value) for key, value in data.items()}

    if isinstance(data, list):
        return [deep_convert_numbers_to_strings(item) for item in data]

    if isinstance(data, tuple):
        return tuple(deep_convert_numbers_to_strings(item) for item in data)

    if isinstance(data, (int, float)):
        return str(data)

    return data


def log(msg: str, level: str = "INFO"):
    """
    Logs a message with a timestamp in Bangkok time.

    :param msg: The message to log.
    :param level: The log level (e.g., INFO, WARNING, ERROR).
    """
    try:
        utc_dt = datetime.now(pytz.utc)  # Get current time in UTC
        tz = pytz.timezone('Asia/Bangkok')
        bangkok_time = utc_dt.astimezone(tz)  # Convert UTC time to Bangkok time
        date_str = bangkok_time.strftime("%m/%d/%Y %H:%M:%S")
        print(f"[{date_str}] [{level}]: {msg}")
    except Exception as e:
        print(f"Failed to log message: {msg}. Error: {e}")
