import os
import time
import random
import requests
from flask import Flask, render_template, request, jsonify, url_for, Response
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# For dynamic image generation
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

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
API_BASE = "https://all.api.radio-browser.info/json/"
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
            # Return a higher-resolution version of the image.
            return results[0].get('artworkUrl100', "").replace("100x100", "600x600")
    except Exception as e:
        print(f"Cover art lookup failed: {e}")
    return None

def generate_placeholder_album_art(artist, song, width=600, height=600):
    """
    Generate a dynamic, creative placeholder album art that includes:
      - A gradient background
      - A few random creative shapes
      - Overlaid artist and song text with a semi-transparent background box,
        with the vertical placement randomized.
    """
    import random, os
    from io import BytesIO
    from PIL import Image, ImageDraw, ImageFont

    # --- Create a gradient background ---
    start_color = tuple(random.randint(0, 100) for _ in range(3))
    end_color = tuple(random.randint(150, 255) for _ in range(3))
    gradient = Image.new('RGBA', (width, height))
    for y in range(height):
        r = int(start_color[0] + (end_color[0] - start_color[0]) * (y / height))
        g = int(start_color[1] + (end_color[1] - start_color[1]) * (y / height))
        b = int(start_color[2] + (end_color[2] - start_color[2]) * (y / height))
        for x in range(width):
            gradient.putpixel((x, y), (r, g, b, 255))
    
    draw = ImageDraw.Draw(gradient, 'RGBA')

    # --- Draw a few random creative shapes ---
    # Draw random color streaks (lines) – 10 of them.
    for _ in range(10):
        start_point = (random.randint(0, width), random.randint(0, height))
        end_point = (random.randint(0, width), random.randint(0, height))
        line_color = tuple(random.randint(0, 255) for _ in range(3)) + (random.randint(100, 200),)
        thickness = random.randint(3, 8)
        draw.line([start_point, end_point], fill=line_color, width=thickness)

    # Draw a few ovals – 3 of them.
    for _ in range(3):
        x0 = random.randint(0, width - 100)
        y0 = random.randint(0, height - 100)
        x1 = x0 + random.randint(50, 150)
        y1 = y0 + random.randint(50, 150)
        oval_color = tuple(random.randint(0, 255) for _ in range(3)) + (random.randint(100, 180),)
        draw.ellipse([x0, y0, x1, y1], fill=oval_color)

    # Draw a couple of rectangles with semi-transparent fills.
    for _ in range(2):
        x0 = random.randint(0, width - 50)
        y0 = random.randint(0, height - 50)
        x1 = x0 + random.randint(30, 150)
        y1 = y0 + random.randint(30, 150)
        rect_color = tuple(random.randint(0, 255) for _ in range(3)) + (random.randint(50, 150),)
        draw.rectangle([x0, y0, x1, y1], fill=rect_color)

    # Draw one random polygon.
    points = [(random.randint(0, width), random.randint(0, height)) for _ in range(4)]
    poly_color = tuple(random.randint(0, 255) for _ in range(3)) + (random.randint(50, 150),)
    draw.polygon(points, fill=poly_color)

    # --- Load font and measure text ---
    font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'OpenSans-Bold.ttf')
    try:
        font_size = 40
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print("Error loading font, using default.", e)
        font = ImageFont.load_default()

    text_artist = artist
    text_song = song

    # Use draw.textbbox() to measure text dimensions.
    artist_bbox = draw.textbbox((0, 0), text_artist, font=font)
    artist_width = artist_bbox[2] - artist_bbox[0]
    artist_height = artist_bbox[3] - artist_bbox[1]

    song_bbox = draw.textbbox((0, 0), text_song, font=font)
    song_width = song_bbox[2] - song_bbox[0]
    song_height = song_bbox[3] - song_bbox[1]

    spacing = 10  # space between lines
    total_text_height = artist_height + song_height + spacing

    # --- Randomize vertical placement for text ---
    # Choose a random y position ensuring text is fully visible (with a 20px margin).
    y_text = random.randint(20, height - total_text_height - 20)
    
    # Center text horizontally.
    x_artist = (width - artist_width) / 2
    x_song = (width - song_width) / 2

    # --- Draw semi-transparent rectangle behind text ---
    overlay_margin = 10
    overlay_x0 = min(x_artist, x_song) - overlay_margin
    overlay_y0 = y_text - overlay_margin
    overlay_x1 = max(x_artist + artist_width, x_song + song_width) + overlay_margin
    overlay_y1 = y_text + total_text_height + overlay_margin
    draw.rectangle([overlay_x0, overlay_y0, overlay_x1, overlay_y1], fill=(0, 0, 0, 150))

    # --- Draw the text in white ---
    text_color = (255, 255, 255, 255)
    draw.text((x_artist, y_text), text_artist, font=font, fill=text_color)
    draw.text((x_song, y_text + artist_height + spacing), text_song, font=font, fill=text_color)

    # --- Save the image to a bytes buffer ---
    from io import BytesIO
    buffer = BytesIO()
    gradient.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer.getvalue()

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
                artist = artist.strip() or DEFAULT_METADATA['artist']
                song = song.strip() or DEFAULT_METADATA['song']
                artwork = fetch_cover_art(song, artist)
            else:
                artist = DEFAULT_METADATA['artist']
                song = stream_title.strip() or DEFAULT_METADATA['song']
                artwork = None

            # If no artwork found, use the dynamic placeholder.
            if not artwork:
                artwork = url_for('placeholder_art', artist=artist, song=song)
            
            return {
                'song': song,
                'artist': artist,
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

@app.route('/placeholder_art')
def placeholder_art():
    """
    Route to generate and return the dynamic placeholder album art.
    Accepts 'artist' and 'song' as query parameters.
    """
    artist = request.args.get('artist', 'Unknown Artist')
    song = request.args.get('song', 'Unknown Song')
    img_bytes = generate_placeholder_album_art(artist, song)
    return Response(img_bytes, mimetype='image/png')

if __name__ == '__main__':
    if check_api_health():
        print("RadioBrowser API is available")
        app.run(debug=True, host=HOST, port=PORT)
    else:
        print("Error: RadioBrowser API is unavailable. Check your network connection.")
