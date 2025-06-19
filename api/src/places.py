import requests
import os
from dotenv import load_dotenv
API_KEY = os.getenv("CLOUD_API_KEY")

def get_places_nearby(lat, long, type):
    radius = 4828 #3 miles in meters

    
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{long}",
        "radius": radius,
        "keyword": type,
        "key": API_KEY

    }
    try: 
        data = requests.get(url, params=params)
        response = data.json()
        places = response.get("results", [])
        return places
    except Exception as e:
        return {"error": str(e)}