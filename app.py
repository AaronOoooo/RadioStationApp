import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv
import os

# Load environment variables from .env file (if needed)
load_dotenv()

# Import host and port settings from secret.py
from secret import HOST, PORT

app = Flask(__name__)

def get_radio_stations(search_query=None, limit=20):
    """
    Fetch a list of radio stations.
    If a search query is provided, use the search endpoint; otherwise, get a default list.
    """
    if search_query:
        # Use the search endpoint to filter by station name.
        url = "https://de1.api.radio-browser.info/json/stations/search"
        params = {"name": search_query, "limit": limit}
    else:
        # Get a default list of stations.
        url = "https://api.radio-browser.info/json/stations"
        params = {"limit": limit}
        
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching stations: {e}")
        return []

def get_station_by_uuid(station_uuid):
    """
    Retrieve station details by UUID.
    """
    url = f"https://de1.api.radio-browser.info/json/stations/byuuid/{station_uuid}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        station_data = response.json()
        if station_data:
            return station_data[0]
        else:
            return {}
    except requests.RequestException as e:
        print(f"Error fetching station details: {e}")
        return {}

def get_stream_metadata(stream_url):
    """
    Placeholder function to extract now playing metadata from the stream.
    In a production version, you'd implement a method to fetch metadata from
    the stream's ICY headers or use a dedicated library.
    For now, we return dummy data.
    """
    # NOTE: Many streams do not provide metadata in a consistent way.
    # Here we simply return placeholder values.
    return {
        'song': 'Unknown Song',
        'artist': 'Unknown Artist',
        'album': 'Unknown Album',
        'year': 'N/A',
        'graphic': None  # URL to album art if available
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Home route: displays a list of radio stations with an optional search filter.
    """
    search_query = ""
    if request.method == 'POST':
        search_query = request.form.get('search', "").strip()
    
    stations = get_radio_stations(search_query=search_query)
    return render_template('index.html', stations=stations, search_query=search_query)

@app.route('/station/<station_uuid>')
def station_detail(station_uuid):
    """
    Station detail route: displays detailed information about a station, including now playing metadata.
    """
    station = get_station_by_uuid(station_uuid)
    if station.get('url'):
        station['now_playing'] = get_stream_metadata(station['url'])
    else:
        station['now_playing'] = {}
    return render_template('station.html', station=station)

if __name__ == '__main__':
    # For development purposes, run in debug mode.
     app.run(debug=True, host=HOST, port=PORT)
