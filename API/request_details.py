import json
from typing import Dict
from .general import api_request


def get_details(api_key: str, property_id: str) -> Dict:
    """ Запрос для получения полной информации об одном отеле """
    response = api_request(
        method_type="POST",
        method_endswith="properties/v2/detail",
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
            "propertyId": property_id
        }
    )
    return json.loads(response)
