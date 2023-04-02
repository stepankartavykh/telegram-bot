import json
from typing import List
from .general import api_request


def get_locations(api_key: str, city: str) -> List[dict]:
    """ Запрос для получения доступных локаций по определённому городу """
    response = api_request(
        method_type="GET",
        method_endswith="locations/v3/search",
        request_headers={
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
        },
        params={'q': city, 'locale': 'ru_RU'}
    )
    return json.loads(response)["sr"]
