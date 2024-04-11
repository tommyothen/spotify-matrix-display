# Spotify Matrix Display

This project is a Python script that displays the album art of the currently playing track on Spotify using a Raspberry Pi and an RGB LED matrix. The script fetches the album art from the Spotify API, caches it locally, and displays it on the LED matrix in real-time.

## Features

- Displays the album art of the currently playing track on Spotify
- Fetches album art using the Spotify API
- Caches album art locally for improved performance
- Supports RGB LED matrix display connected to a Raspberry Pi
- Automatically starts the script on system boot using a systemd service

## Prerequisites

- Raspberry Pi with an RGB LED matrix connected
- Python 3.x installed on the Raspberry Pi
- Spotify API credentials (Client ID and Client Secret)
- RGB Matrix Bonnet and LED Matrix Panel properly set up and configured
  - For detailed instructions on setting up the RGB Matrix Bonnet and LED Matrix Panel, refer to the Adafruit guide: [Driving Matrices](https://learn.adafruit.com/adafruit-rgb-matrix-bonnet-for-raspberry-pi/driving-matrices#step-6-log-into-your-pi-to-install-and-run-software-1745233)

## Hardware Components

- Raspberry Pi Zero 2 W
- WAVESHARERGB Full-Colour LED Matrix Panel - 2mm Pitch, 64x64 Pixels
- Adafruit RGB Matrix Bonnet for Raspberry Pi
- 5V 10A Power Supply

## Installation

1. Clone the repository to your Raspberry Pi:
    ```
    git clone https://github.com/tommyothen/spotify-matrix-display.git
    ```

2. Navigate to the project directory:
    ```
    cd spotify-matrix-display
    ```

3. Install the required Python dependencies:
    ```
    pip3 install -r requirements.txt
    ```

4. Set up your Spotify API credentials:
   - Create a Spotify Developer account and create a new application.
   - Obtain the Client ID and Client Secret for your application.
   - Don't forget to add the appropriate redirect URIs for your application.
   - Create a `.env` file in the project directory and add your credentials:
        ```
        SPOTIPY_CLIENT_ID=your-client-id
        SPOTIPY_CLIENT_SECRET=your-client-secret
        HOST_IP=your-host-ip
        ```

5. Configure the RGB LED matrix:
   - Update the `matrix.py` file with the appropriate configuration for your RGB LED matrix, such as the number of rows, columns, chain length, and parallel count.

6. Set up the systemd service:
   - Copy the `matrix.service` file to `/etc/systemd/system/`:
        ```
        sudo cp matrix.service /etc/systemd/system/
        ```
   - Reload the systemd configuration:
        ```
        sudo systemctl daemon-reload
        ```
   - Enable the service to start on boot:
        ```
        sudo systemctl enable matrix.service
        ```

## Usage

1. Start the script manually:
    ```
    sudo python3 main.py
    ```

    Or start the systemd service:
    ```
    sudo systemctl start matrix.service
    ```

2. The script will authenticate with the Spotify API and display the album art of the currently playing track on the RGB LED matrix.

3. The album art will update in real-time as the track changes on Spotify.

## Demo

Check out the video demonstration of the matrix display in action:
(Clicking the image will take you to the YouTube video)

[![Demo Video](https://img.youtube.com/vi/LTrYFE1vO6U/maxresdefault.jpg)](https://youtu.be/LTrYFE1vO6U)

## Customization

- Adjust the RGB LED matrix configuration in `matrix.py` to match your hardware setup.
- Modify the cache directory path in `album_art.py` if needed.
- Customize the logging settings in `logger.py` to suit your preferences.

## Troubleshooting

- If the script fails to start or encounters issues, check the log files in the `logs` directory for detailed error messages.
- Ensure that your Spotify API credentials are valid and have the necessary permissions.
- Verify that your RGB LED matrix is properly connected and configured.

## License

This project is licensed under the [MIT License](LICENSE).