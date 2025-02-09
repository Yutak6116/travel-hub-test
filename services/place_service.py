import requests

def get_place_coordinates(place_name: str) -> dict:
    """
    Google Places API を使用して、指定された場所の緯度と経度を取得する。
    """
    url = "https://get-coordinates-kxsgzuno2a-uc.a.run.app"
    data = {"place_name": place_name}
    response = requests.post(url, json=data)
    result = response.json()
    return result.get('place_id')

