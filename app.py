import os
import time
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Load environment variables
load_dotenv()

# Import HOST and PORT from secret.py
from secret import HOST, PORT

app = Flask(__name__)

# Configure requests session with retries
session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=0.3,
    status_forcelist=[500, 502, 503, 504]
)
session.mount('https://', HTTPAdapter(max_retries=retries))

# API configuration (updated)
API_BASE = "https://de1.api.radio-browser.info/json/"
HEADERS = {
    'User-Agent': 'RadioStationWAOH/1.0 (tucky2000@gmail.com)'  # Replace with your contact email
}

# Default metadata fallback
DEFAULT_METADATA = {
    'song': 'Unknown Song',
    'artist': 'Unknown Artist',
    'album': 'Unknown Album',
    'year': 'N/A',
    'graphic': None
}

def fetch_cover_art(song, artist):
    """Fetch album artwork using iTunes Search API."""
    try:
        query = f"{artist} {song}".strip()
        params = {"term": query, "media": "music", "limit": 1}
        response = session.get(
            "https://itunes.apple.com/search",
            params=params,
            timeout=5,
            headers=HEADERS
        )
        response.raise_for_status()
        results = response.json().get('results')
        if results:
            return results[0].get('artworkUrl100', "").replace("100x100", "600x600")
    except Exception as e:
        print(f"Cover art lookup failed: {e}")
    return None

def get_stream_metadata(stream_url):
    """Retrieve metadata from radio stream."""
    try:
        headers = {'Icy-MetaData': '1', **HEADERS}

        with session.get(stream_url, headers=headers, stream=True, timeout=(5, 10)) as response:
            response.raise_for_status()

            metaint_header = response.headers.get('icy-metaint')
            if not metaint_header:
                return DEFAULT_METADATA

            metaint = int(metaint_header)
            _ = response.raw.read(metaint)

            meta_length_byte = response.raw.read(1)
            if not meta_length_byte:
                return DEFAULT_METADATA

            meta_length = ord(meta_length_byte)
            if meta_length == 0:
                return DEFAULT_METADATA

            metadata_bytes = response.raw.read(meta_length * 16)
            metadata_str = metadata_bytes.rstrip(b'\0').decode('utf-8', errors='replace')

            meta_parts = metadata_str.split(';')
            meta_dict = {}
            for part in meta_parts:
                if part and '=' in part:
                    key, value = part.split('=', 1)
                    meta_dict[key.strip()] = value.strip().strip("'")

            stream_title = meta_dict.get("StreamTitle", "")
            if " - " in stream_title:
                artist, song = stream_title.split(" - ", 1)
                artist = artist.strip()
                song = song.strip()
                artwork = fetch_cover_art(song, artist)
            else:
                artist = ""
                song = stream_title.strip()

            return {
                'song': song or DEFAULT_METADATA['song'],
                'artist': artist or DEFAULT_METADATA['artist'],
                'album': DEFAULT_METADATA['album'],
                'year': DEFAULT_METADATA['year'],
                'graphic': artwork
            }

    except Exception as e:
        print("Error retrieving metadata:", e)
        return DEFAULT_METADATA

def get_radio_stations(search_query=None, limit=20):
    """Fetch list of radio stations."""
    endpoint = "stations/search" if search_query else "stations"
    params = {"limit": limit}
    if search_query:
        params["name"] = search_query

    try:
        response = session.get(
            f"{API_BASE}{endpoint}",
            params=params,
            timeout=10,
            headers=HEADERS
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching stations: {e}")
        return []

def get_station_by_uuid(station_uuid):
    """Get station details by UUID."""
    try:
        response = session.get(
            f"{API_BASE}stations/byuuid/{station_uuid}",
            timeout=10,
            headers=HEADERS
        )
        response.raise_for_status()
        station_data = response.json()
        return station_data[0] if station_data else {}
    except requests.RequestException as e:
        print(f"Error fetching station details: {e}")
        return {}

def check_api_health():
    """Check API status using stations endpoint"""
    try:
        response = session.get(
            f"{API_BASE}stations",
            params={"limit": 1},
            timeout=10,
            headers=HEADERS
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Health check error: {e}")
        return False
    
@app.route('/', methods=['GET', 'POST'])
def index():
    """Home route with station list."""
    search_query = ""
    if request.method == 'POST':
        search_query = request.form.get('search', "").strip()

    stations = get_radio_stations(search_query=search_query)
    return render_template('index.html', stations=stations, search_query=search_query)

@app.route('/station/<station_uuid>')
def station_detail(station_uuid):
    """Station detail page."""
    station = get_station_by_uuid(station_uuid)
    if station.get('url'):
        station['now_playing'] = get_stream_metadata(station['url'])
    else:
        station['now_playing'] = DEFAULT_METADATA

    return render_template('station.html', station=station)

@app.route('/metadata/<station_uuid>')
def metadata(station_uuid):
    """JSON metadata endpoint."""
    station = get_station_by_uuid(station_uuid)
    now_playing = get_stream_metadata(station['url']) if station.get('url') else DEFAULT_METADATA
    return jsonify(now_playing)

if __name__ == '__main__':
    if check_api_health():
        print("RadioBrowser API is available")
        app.run(debug=True, host=HOST, port=PORT)
    else:
        print("Error: RadioBrowser API is unavailable. Check your network connection.")