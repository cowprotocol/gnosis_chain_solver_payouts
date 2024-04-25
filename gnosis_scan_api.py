import requests
import json
import datetime
import time
from constants import header, REQUEST_TIMEOUT, SUCCESS_CODE


def get_block_range(year, month, day):
    date_time = datetime.datetime(year, month, day, 0, 0)
    start_timestamp = int(time.mktime(date_time.timetuple())) + 3 * 60 * 60
    url = (
        "https://api.gnosisscan.io/api?module=block&action=getblocknobytime"
        + "&timestamp="
        + str(start_timestamp)
        + "&closest=after&apikey=YourApiKeyToken"
    )
    try:
        response = requests.get(
            url,
            headers=header,
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == SUCCESS_CODE:
            data = json.loads(response.text)
            start_block = int(data["result"])
    except Exception as e:
        print(e)
        return -1, -1

    end_timestamp = start_timestamp + 7 * 24 * 60 * 60
    url = (
        "https://api.gnosisscan.io/api?module=block&action=getblocknobytime"
        + "&timestamp="
        + str(end_timestamp)
        + "&closest=before&apikey=YourApiKeyToken"
    )
    try:
        response = requests.get(
            url,
            headers=header,
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == SUCCESS_CODE:
            data = json.loads(response.text)
            end_block = int(data["result"])
    except Exception as e:
        print(e)
        return -1, -1

    return start_block, end_block


def fetch_hashes(start_block, end_block) -> list[str]:

    res = []
    url = (
        "https://api.gnosisscan.io/api?module=account&action=txlist"
        + "&address=0x9008D19f58AAbD9eD0D60971565AA8510560ab41"
        + "&startblock="
        + str(start_block)
        + "&endblock="
        + str(end_block)
        + "&sort=desc&apikey=YourApiKeyToken"
    )
    try:
        response = requests.get(
            url,
            headers=header,
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == SUCCESS_CODE:
            data = json.loads(response.text)
            i = 0
            for x in data["result"]:
                res.append(x["hash"])
    except Exception as e:
        print(e)
        return []

    return res
