import os
import time
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables (if any)
load_dotenv()

# Import HOST and PORT from secret.py
from secret import HOST, PORT

app = Flask(__name__)

# Default metadata fallback
DEFAULT_METADATA = {
    'song': 'Unknown Song',
    'artist': 'Unknown Artist',
    'album': 'Unknown Album',
    'year': 'N/A',
    'graphic': None
}

def get_stream_metadata(stream_url):
    """
    Attempts to retrieve metadata (e.g., current song info) from a streaming URL.
    This function sends a request with the 'Icy-MetaData' header and reads the
    metadata block from the response.
    """
    try:
        headers = {'Icy-MetaData': '1', 'User-Agent': 'Mozilla/5.0'}

        with requests.get(stream_url, headers=headers, stream=True, timeout=(5, 10)) as response:
            response.raise_for_status()

            metaint_header = response.headers.get('icy-metaint')
            if not metaint_header:
                return DEFAULT_METADATA

            metaint = int(metaint_header)

            # Skip the initial audio data up to the metadata block
            _ = response.raw.read(metaint)

            # Next byte indicates metadata block length in 16-byte units
            meta_length_byte = response.raw.read(1)
            if not meta_length_byte:
                return DEFAULT_METADATA

            meta_length = ord(meta_length_byte)
            if meta_length == 0:
                return DEFAULT_METADATA

            metadata_bytes = response.raw.read(meta_length * 16)
            metadata_str = metadata_bytes.rstrip(b'\0').decode('utf-8', errors='replace')

            # Parse metadata like: "StreamTitle='Artist - Song';StreamUrl='';"
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
            else:
                artist = ""
                song = stream_title.strip()

            return {
                'song': song or DEFAULT_METADATA['song'],
                'artist': artist or DEFAULT_METADATA['artist'],
                'album': DEFAULT_METADATA['album'],
                'year': DEFAULT_METADATA['year'],
                'graphic': DEFAULT_METADATA['graphic']
            }

    except Exception as e:
        print("Error retrieving metadata:", e)
        return DEFAULT_METADATA


def get_radio_stations(search_query=None, limit=20):
    """
    Fetch a list of radio stations.
    If a search query is provided, use the search endpoint; otherwise, return a default list.
    """
    if search_query:
        url = "https://de1.api.radio-browser.info/json/stations/search"
        params = {"name": search_query, "limit": limit}
    else:
        url = "https://de1.api.radio-browser.info/json/stations"
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
    Retrieve station details by UUID using the de1 mirror.
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
    Station detail route: displays detailed information about a station,
    including now playing metadata if available.
    """
    station = get_station_by_uuid(station_uuid)
    if station.get('url'):
        station['now_playing'] = get_stream_metadata(station['url'])
    else:
        station['now_playing'] = DEFAULT_METADATA

    return render_template('station.html', station=station)


@app.route('/metadata/<station_uuid>')
def metadata(station_uuid):
    """
    Returns the current stream metadata for the given station as JSON.
    """
    station = get_station_by_uuid(station_uuid)
    if station.get('url'):
        now_playing = get_stream_metadata(station['url'])
    else:
        now_playing = {
            'song': DEFAULT_METADATA['song'],
            'artist': DEFAULT_METADATA['artist']
        }

    return jsonify(now_playing)


if __name__ == '__main__':
    # Run using host and port from secret.py
    app.run(debug=True, host=HOST, port=PORT)
