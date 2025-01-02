import os
import tempfile
from datetime import datetime
import re
import pytz


def get_adapter_id(url: str) -> str:
    pattern = r'/api/dataadapter/(\w+)/response'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return ""


def deep_convert_numbers_to_strings(data):
    if isinstance(data, dict):
        return {key: deep_convert_numbers_to_strings(
            value) for key, value in data.items()}

    if isinstance(data, list):
        return [deep_convert_numbers_to_strings(item) for item in data]

    if isinstance(data, tuple):
        return tuple(deep_convert_numbers_to_strings(item) for item in data)

    if isinstance(data, (int, float)):
        return str(data)

    return data


def log(msg: str):
    utc_dt = datetime.now(pytz.utc)  # Get current time in UTC
    tz = pytz.timezone('Asia/Bangkok')
    bangkok_time = utc_dt.astimezone(tz)  # Convert UTC time to Bangkok time
    date_str = bangkok_time.strftime("%m/%d/%Y %H:%M:%S")
    print(f"[{date_str}]: {msg}")
