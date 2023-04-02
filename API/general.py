from typing import Dict

import requests
from requests import exceptions


def api_request(method_type: str, method_endswith: str, request_headers: Dict, params: Dict = None,
                json_payload: Dict = None) -> str:
    """ Функция для формирования запроса к API """
    url = f"https://hotels4.p.rapidapi.com/{method_endswith}"
    try:
        if method_type == 'GET':
            response = requests.request("GET", url, headers=request_headers, params=params)
        else:
            response = requests.request("POST", url, headers=request_headers, params=params, json=json_payload)
        if response.status_code == requests.codes.ok:
            return response.text
    except exceptions.HTTPError as http_error:
        print(http_error)
    except exceptions.ConnectionError as connection_error:
        print(connection_error)
    except exceptions.InvalidJSONError as json_error:
        print(json_error)
    except exceptions.Timeout as timeout_error:
        print(timeout_error)
