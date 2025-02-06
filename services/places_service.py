import os

import requests

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


def get_place_coordinates(place_name: str) -> dict:
    """
    Google Places API を使用して、指定された場所の緯度と経度を取得する。

    :param place_name: 検索する場所の名前
    :return: 緯度・経度、Place ID、住所を含む辞書（エラー時は None）
    """
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": place_name,
        "inputtype": "textquery",
        "fields": "geometry,place_id,formatted_address",
        "key": GOOGLE_MAPS_API_KEY,
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") == "OK":
        candidate = data["candidates"][0]  # 最も適した候補を取得
        return {
            "latitude": candidate["geometry"]["location"]["lat"],
            "longitude": candidate["geometry"]["location"]["lng"],
            "place_id": candidate["place_id"],
            "address": candidate["formatted_address"],
        }
    else:
        print(f"Error: {data.get('status')}, {data.get('error_message', '')}")
        return None


def get_tourist_spots(api_key, location, radius=5000, language="ja"):
    """
    Google Places API を使用して、指定された場所の周辺の観光スポットを取得する。

    Args:
        api_key (str): Google Cloud Platform で作成した API キー
        location (str): 緯度,経度（例: "35.6895,139.6917" は東京の中心）
        radius (int): 検索半径（メートル単位）
        language (str): 言語コード（デフォルトは "ja"）

    Returns:
        dict: 観光スポットのリスト（エラー時は None）

    # 使用例

    api_key = "AIzaSyCBGzcVWp3SZFKS1TixOfBOgjkIuKtz_wM"  # 取得した API キー
    location = "35.6895,139.6917"  # 東京駅周辺
    radius = 5000  # 半径 5km

    tourist_spots = get_tourist_spots(api_key, location, radius)

    if tourist_spots:
        for spot in tourist_spots[:10]:  # 上位10件を表示
            print(f"名前: {spot['name']}")
            print(f"住所: {spot.get('vicinity', '住所なし')}")
            print(f"評価: {spot.get('rating', 'なし')}")
            print("-" * 40)

    """

    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    params = {
        "location": location,  # 緯度,経度（例: "35.6895,139.6917" は東京の中心）
        "radius": radius,  # 半径 (メートル単位)
        "type": "tourist_attraction",  # 観光スポット
        "language": language,  # 日本語で情報取得
        "key": api_key,
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if data["status"] == "OK":
        return data["results"]
    else:
        print(f"Error: {data['status']}")
        return None


def get_directions(
    api_key, origin, destination, waypoints=None, mode="driving", transit_mode=None
):
    """
    Google Directions API を使用して、指定された場所間の経路情報を取得する。公共交通機関は日本は非対応。

    Args:
        api_key (str): Google Cloud Platform で作成した API キー
        origin (str): 出発地の住所または緯度,経度（例: "東京駅" または "35.681236,139.767125"）
        destination (str): 到着地の住所または緯度,経度
        waypoints (list): 経由地の住所または緯度,経度のリスト
        mode (str): 交通手段（"driving", "walking", "bicycling", "transit"）
        transit_mode (str): 公共交通機関の種類（"bus", "subway", "train", "tram", "rail"）


    Returns:
        dict: 経路情報を含む辞書（エラー時は None）


    # 使用例
    api_key = "AIzaSyCBGzcVWp3SZFKS1TixOfBOgjkIuKtz_wM"  # 取得した API キーを設定
    origin = "Tokyo Station"
    destination = "Osaka Station"
    waypoints = ["Nagoya Station", "Kyoto Station"]  # 経由地
    mode = "walking"  # "driving", "walking", "bicycling", "transit"


    route_data = get_directions(api_key, origin, destination, waypoints, mode)

    if route_data:
        # ルート情報の表示
        for i, leg in enumerate(route_data["routes"][0]["legs"]):
            print(f"Leg {i+1}: {leg['start_address']} → {leg['end_address']}")
            print(f"距離: {leg['distance']['text']}, 所要時間: {leg['duration']['text']}\n")
    """
    base_url = "https://maps.googleapis.com/maps/api/directions/json"

    params = {
        "origin": origin,
        "destination": destination,
        "mode": mode,  # "driving", "walking", "bicycling", "transit"
        "key": api_key,
    }

    # 経由地がある場合、追加
    if waypoints:
        params["waypoints"] = "|".join(waypoints)

    if mode == "transit" and transit_mode:
        params["transit_mode"] = transit_mode

    response = requests.get(base_url, params=params)
    data = response.json()

    if data["status"] == "OK":
        return data
    else:
        print(f"Error: {data['status']}")
        return None
