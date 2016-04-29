import requests, json
from datetime import datetime, timedelta
import pytz

from .models import *

URL = "http://dota2lounge.com/api/matches"


def err(message):
    print(message)
    return None


def get_data():
    response = requests.get(URL)
    data = json.loads(response.text)
    print("data received")
    return data


def assign_dates():
    matches_data = get_data()
    for match_data in matches_data:
        try:
            match = Match.objects.get(id=match_data["match"])
        except Match.DoesNotExist:
            continue

        date = datetime.strptime(match_data["when"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.UTC)
        delta = timedelta(hours=10)
        date += delta

        match.when = date
        match.event = match_data["event"]
        match.save()
        print(match.id)


