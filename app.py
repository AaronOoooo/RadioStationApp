from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Home route: displays a list of radio stations and a search form
@app.route('/', methods=['GET', 'POST'])
def index():
    search_query = request.form.get('search', '')
    # Placeholder: You would call the Radio Browser API here to fetch station data.
    stations = []  # Replace with actual API call and data parsing.
    if search_query:
        # Filter stations based on the search query
        stations = [station for station in stations if search_query.lower() in station.get('name', '').lower()]
    return render_template('index.html', stations=stations, search_query=search_query)

# Station details route: displays detailed info about a selected station
@app.route('/station/<station_id>')
def station_detail(station_id):
    # Placeholder: Fetch station details and metadata (including now playing info)
    station = {}  # Replace with actual API call or metadata extraction.
    return render_template('station.html', station=station)

if __name__ == '__main__':
    app.run(debug=True)
