"""
OrderbookAPI for fetching relevant data using the CoW Swap Orderbook API.
"""

from typing import Any, Optional
from time import sleep
from gnosis_scan_api import get_block_range, fetch_hashes
import json
import requests
from constants import (
    header,
    REQUEST_TIMEOUT,
    SUCCESS_CODE,
    FAIL_CODE,
)

PROD_BASE_URL = "https://api.cow.fi/xdai/api/v1/"
BARN_BASE_URL = "https://barn.api.cow.fi/xdai/api/v1/"


def get_solver_competition_data(
    auction_id: str, environment: str
) -> Optional[dict[str, Any]]:
    """
    Get solver competition data from a transaction hash.
    The returned dict follows the schema outlined here:
    https://api.cow.fi/docs/#/default/get_api_v1_solver_competition_by_tx_hash__tx_hash_
    """
    if environment == "prod":
        url = f"{PROD_BASE_URL}solver_competition/{auction_id}"
    else:
        url = f"{BARN_BASE_URL}solver_competition/{auction_id}"
    solver_competition_data: Optional[dict[str, Any]] = None

    count = 0
    while True:
        try:
            json_competition_data = requests.get(
                url,
                headers=header,
                timeout=REQUEST_TIMEOUT,
            )
            if json_competition_data.status_code == 503:
                if count == 5:
                    print("Cannot recover data for auction " + str(auction_id))
                    return None
                sleep(0.2)
                count += 1
                continue
            if json_competition_data.status_code == 404:
                return None

            if json_competition_data.status_code == SUCCESS_CODE:
                solver_competition_data = json.loads(json_competition_data.text)
                break
            else:
                return None
        except requests.RequestException as err:
            print("Cannot recover data for auction " + str(auction_id))
            return None
    return solver_competition_data
