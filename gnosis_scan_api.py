import requests
import json
import datetime
import time
from constants import REQUEST_TIMEOUT, SUCCESS_CODE


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
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == SUCCESS_CODE:
            data = json.loads(response.text)
            if data["status"] == "1":
                start_block = int(data["result"])
            else:
                print("Start timestamp. " + data["result"])
                exit()
    except Exception as e:
        print(f"Fetching block range failed with error: {e}")
        raise e

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
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == SUCCESS_CODE:
            data = json.loads(response.text)
            if data["status"] == "1":
                end_block = int(data["result"])
            else:
                print("End timestamp. " + data["result"])
                exit()
    except Exception as e:
        print(f"Fetching block range failed with error: {e}")
        raise e

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
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == SUCCESS_CODE:
            data = json.loads(response.text)
            for x in data["result"]:
                res.append(x["hash"])
    except Exception as e:
        print(e)
        return []

    return res
