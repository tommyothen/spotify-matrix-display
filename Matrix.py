from Spotify import SpotifyClient
from PIL import Image
from time import sleep
from rgbmatrix import RGBMatrix, RGBMatrixOptions


class Matrix:
    def __init__(self, spotify: SpotifyClient):
        self.spotify = spotify

        options = RGBMatrixOptions()
        options.rows = 64
        options.cols = 64
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = "adafruit-hat"

        self.matrix = RGBMatrix(options=options)

    def run(self):
        song_id: str = None

        while True:
            current_playback = self.spotify.get_currently_playing()

            if current_playback and current_playback.item:
                # Check if it's a new song
                if current_playback.item.id != song_id:
                    song_id = current_playback.item.id
                    print(
                        f"Now playing: {current_playback.item.artists[0].name} - {current_playback.item.name}"
                    )

                    # Update the screen
                    try:
                        album_art_url = current_playback.item.album.images[-1].url

                        album_art = self.spotify.fetch_album_art(album_art_url)
                        self.display_album_art(album_art)
                    except Exception as e:
                        print("Error displaying album art", e)
                        self.matrix.Clear()
            else:
                self.matrix.Clear()

            sleep(1)

    def display_album_art(self, image: Image):
        # Just in case, set the image to RGB mode
        image = image.convert("RGB")
        self.matrix.SetImage(image)
