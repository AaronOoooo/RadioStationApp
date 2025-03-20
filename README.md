# Paisley Pulse

Welcome to **Paisley Pulse** – your local web portal to discover, search, and stream a wide variety of internet radio stations. With a warm, jazzy, and calm design, this app is perfect for setting the mood as you explore your favorite genres.

## Features

- **Search Stations:** Quickly find radio stations by entering keywords in our search box.
- **Detailed Station Info:** Click on a station to view more information, including now playing details like song title, artist, album, and more.
- **Seamless Streaming:** Enjoy your favorite tunes directly in your browser using the HTML5 audio player.
- **Responsive Design:** The site dynamically adjusts into multiple columns to provide a smooth browsing experience on any screen size.
- **Network Accessibility:** The app is configured (via `secret.py`) to listen on all network interfaces, making it available on any device on your home network.

## How It Works

Paisley Pulse uses the [Radio Browser API](https://api.radio-browser.info/) (via the **de1** mirror) to fetch a rich list of internet radio stations. With a simple, clean interface built using Python and Flask, you can search for stations, view details, and start streaming your favorite music.

## Getting Started

Follow these steps to get the project running on your computer:

### Prerequisites

- [Python 3](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)

### Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/PaisleyPulse.git
   cd PaisleyPulse
   ```

2. **Set Up a Virtual Environment:**

   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment:**

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install the Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Network Settings:**

   The app’s host and port are configured in a separate `secret.py` file. Create a `secret.py` file in the project root with content similar to:

   ```python
   # secret.py
   HOST = '0.0.0.0'  # Listen on all network interfaces
   PORT = 8080       # Change this to any port you prefer
   ```

   Ensure that `secret.py` is added to your `.gitignore` file to keep it private.

### Running the App

Start your Flask development server by running:

```bash
python app.py
```

With the settings in `secret.py`, the app will listen on all network interfaces. This means you can access it on your home network by entering:

```
http://<YOUR_LOCAL_IP>:8080
```

Replace `<YOUR_LOCAL_IP>` with your computer's local IP address (e.g., `192.168.1.15`). To find your local IP address on Windows, run `ipconfig` in the Command Prompt.

## Future Improvements

- **Enhanced Now Playing Metadata:** Further improve metadata extraction for a more detailed listening experience.
- **Favorites & Playlists:** Enable users to save their favorite stations (coming soon!).
- **Additional Theming Options:** More customization options to personalize your listening experience.

## Feedback

Feel free to submit issues or pull requests if you have ideas to improve RadioStationApp. Your feedback is welcome and appreciated!

---

Enjoy your musical journey with RadioStationApp, and thank you for checking it out!
```