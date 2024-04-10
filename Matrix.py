from Spotify import SpotifyClient
from PIL import Image
from time import sleep
from rgbmatrix import RGBMatrix, RGBMatrixOptions


class Matrix:
    def __init__(self, spotify: SpotifyClient):
        self.spotify = spotify
        self.next_album_art = None

        options = RGBMatrixOptions()
        options.rows = 64
        options.cols = 64
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = "adafruit-hat"

        self.matrix = RGBMatrix(options=options)

    def run(self):
        song_id: str = None
        next_song_id: str = None

        while True:
            current_playback = self.spotify.get_currently_playing()

            if current_playback and current_playback.item:
                # Check if it's a new song
                if current_playback.item.id != song_id:
                    song_id = current_playback.item.id
                    print(
                        f"Now playing: {current_playback.item.artists[0].name} - {current_playback.item.name}"
                    )

                    # Update the screen with the next album art if available, otherwise fetch the current album art
                    if self.next_album_art is not None:
                        print("Using optimistically fetched artwork")
                        self.display_album_art(self.next_album_art)
                        self.next_album_art = None
                    else:
                        try:
                            album_art_url = current_playback.item.album.images[-1].url
                            album_art = self.spotify.fetch_album_art(album_art_url)
                            self.display_album_art(album_art)
                        except Exception as e:
                            print("Error displaying album art", e)
                            self.matrix.Clear()

                    # Fetch the next track in the queue
                    queue = self.spotify.get_player_queue()
                    if queue:
                        next_track = queue[0] if queue else None
                        if next_track and next_track.id != next_song_id:
                            next_song_id = next_track.id
                            try:
                                next_album_art_url = next_track.album.images[-1].url
                                print(f"Optimistically fetching artwork for: {next_track.artists[0].name} - {next_track.name}")
                                self.next_album_art = self.spotify.fetch_album_art(next_album_art_url)
                            except Exception as e:
                                print("Error fetching next album art", e)
                                self.next_album_art = None
                        else:
                            print("No next track in the queue")
                            self.next_album_art = None
                    else:
                        print("Queue is empty")
                        self.next_album_art = None
            else:
                self.matrix.Clear()

            sleep(0.5)

    def display_album_art(self, image: Image):
        # Just in case, set the image to RGB mode
        image = image.convert("RGB")
        self.matrix.SetImage(image)
