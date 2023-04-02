import json
from typing import Dict
from .general import api_request


def get_properties(api_key: str, id_location_to_search: int, day_in: int, month_in: int, year_in: int, day_out: int,
                   month_out: int, year_out: int) -> Dict:
    """ Запрос для получения возможных отелей по искомой локации """
    response = api_request(
        method_type="POST",
        method_endswith="properties/v2/list",
        request_headers={
            "content-type": "application/json",
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
        },
        json_payload={
            "currency": "USD",
            "eapid": 1,
            "locale": "en_US",
            "siteId": 300000001,
            "destination": {
                "regionId": f'{id_location_to_search}'
            },
            "checkInDate": {"day": day_in, "month": month_in, "year": year_in},
            "checkOutDate": {"day": day_out, "month": month_out, "year": year_out},
            "rooms": [{"adults": 1}],
            "resultsStartingIndex": 0,
            "resultsSize": 1000,
            "filters": {
                "availableFilter": "SHOW_AVAILABLE_ONLY",
            }
        }
    )
    return json.loads(response)


def get_properties_custom(api_key: str, id_location_to_search: int, day_in: int, month_in: int, year_in: int,
                          day_out: int,
                          month_out: int, year_out: int, price_min: int, price_max: int) -> Dict:
    response = api_request(
        method_type="POST",
        method_endswith="properties/v2/list",
        request_headers={
            "content-type": "application/json",
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
        },
        json_payload={
            "currency": "USD",
            "eapid": 1,
            "locale": "en_US",
            "siteId": 300000001,
            "destination": {
                "regionId": f"{id_location_to_search}"
            },
            "checkInDate": {
                "day": day_in,
                "month": month_in,
                "year": year_in
            },
            "checkOutDate": {
                "day": day_out,
                "month": month_out,
                "year": year_out
            },
            "rooms": [{"adults": 1}],
            "resultsStartingIndex": 0,
            "resultsSize": 1000,
            "filters": {"price": {
                "max": price_max,
                "min": price_min
            }}
        }
    )
    return json.loads(response)
