# RadioStationApp

# RadioStationApp

Welcome to **RadioStationApp** – your local web portal to discover, search, and stream a wide variety of internet radio stations. With a warm, jazzy, and calm design, this app is perfect for setting the mood as you explore your favorite genres.

## Features

- **Search Stations:** Quickly find radio stations by entering keywords in our search box.
- **Detailed Station Info:** Click on a station to view more information, including now playing details like song title, artist, album, and more.
- **Seamless Streaming:** Enjoy your favorite tunes directly in your browser using the HTML5 audio player.
- **Responsive Design:** The site dynamically adjusts into multiple columns to provide a smooth browsing experience on any screen size.

## How It Works

RadioStationApp uses the [Radio Browser API](https://api.radio-browser.info/) (via the **de1** mirror) to fetch a rich list of internet radio stations. With a simple, clean interface built using Python and Flask, you can search for stations, view details, and start streaming your favorite music.

## Getting Started

Follow these steps to get the project running on your computer:

### Prerequisites

- [Python 3](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)

### Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/RadioStationApp.git
   cd RadioStationApp

Set Up a Virtual Environment: python -m venv venv
Activate the Virtual Environment:

On Windows: venv\Scripts\activate


On macOS/Linux: source venv/bin/activate

Install the Dependencies: pip install -r requirements.txt

Running the App
Start your Flask development server by running: python app.py

By default, the app will be available at http://127.0.0.1:5000. Open your web browser, explore the stations, and enjoy the music!

Future Improvements
--Enhanced Now Playing Metadata: Further improve metadata extraction for a more detailed listening experience.
--Favorites & Playlists: Enable users to save their favorite stations (coming soon!).
--Additional Theming Options: More customization options to personalize your listening experience.

Feedback
Feel free to submit issues or pull requests if you have ideas to improve RadioStationApp. Your feedback is welcome and appreciated!


