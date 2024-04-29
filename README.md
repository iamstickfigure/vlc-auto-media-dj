# AutoMediaDJ

AutoMediaDJ is a Python application for automatically playing media files based on tags and metadata stored in a TagStudio library. It uses the VLC media player through the `python-vlc-http` library to control playback.

## Features

- Play media files (audio, video) based on tags and metadata
- Support for different playback modes (audio, video)
  - Note: Image and GIF support is planned but not yet fully implemented
- Various DJ modes for different playback scenarios (funny, music and visuals, music videos, sexy)
- Weighted random selection of media files based on play history to avoid repetition
- Separate playback of visuals and background music
- Integration with TagStudio library for media metadata

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/iamstickfigure/vlc-auto-media-dj.git
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # For Unix/Linux
   venv\Scripts\activate.bat  # For Windows
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the VLC media player with the HTTP interface enabled.

5. Create a `.env` file in the project root directory and configure the necessary environment variables (see `.env.example` for reference).

## Usage

1. Make sure your `.env` file is properly configured with the required environment variables.

2. Run the application:
   ```
   python main.py
   ```

3. The application will automatically select and play media files based on the configured DJ mode and play history.

## Configuration

The application uses environment variables for configuration. Create a `.env` file in the project root directory and set the following variables:

- `VLC_HOST`: The hostname or IP address of the main VLC player (default: `http://localhost`).
- `VLC_AUDIO_HOST`: The hostname or IP address of the audio-only VLC player (default: same as `VLC_HOST`).
- `VLC_PORT`: The port number for the main VLC player (default: `8080`).
- `VLC_AUDIO_PORT`: The port number for the audio-only VLC player (default: `8081`).
- `VLC_PASSWORD`: The password for the main VLC player.
- `VLC_AUDIO_PASSWORD`: The password for the audio-only VLC player (default: same as `VLC_PASSWORD`).
- `BASE_PATH`: The path to your TagStudio library directory.

## Classes

- `HttpVLCExt`: An extension of the `HttpVLC` class from the `python-vlc-http` library with additional methods for media playback control.
- `VlcPlayerDataSnapshot`: Represents a snapshot of the VLC player data at a given moment, providing access to various properties of the player state.
- `Entry`: Represents a media entry in the TagStudio library with computed fields for tags and metadata.
- `PlaybackInfo`: Represents information about a media playback event, including the entry, playback mode, DJ mode, and additional settings.
- `AutoMediaDJ`: The main class for the AutoMediaDJ application, handling media selection and playback based on the configured DJ mode and play history.

## Enums

- `DJMode`: Enumeration of DJ modes for different playback scenarios.
- `DJState`: Enumeration of DJ states for tracking the playback state.
- `FieldIds`: Enumeration of field IDs used in the TagStudio library.
- `PlaybackMode`: Enumeration of playback modes (audio, video).
- `TagId`: Enumeration of tag IDs used in the TagStudio library.
