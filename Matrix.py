# matrix.py
import threading
from time import sleep
from typing import Optional
from album_art import AlbumArt
from PIL import Image
from logger import Logger
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from spotify import SpotifyClient

logger = Logger("matrix")


class Matrix:
    def __init__(self, spotify: SpotifyClient, album_art: AlbumArt):
        self.spotify = spotify
        self.album_art = album_art
        self.next_album_art = None
        self.next_album_art_thread = None

        options = RGBMatrixOptions()
        options.rows = 64
        options.cols = 64
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = "adafruit-hat"

        self.matrix = RGBMatrix(options=options)

    def fetch_next_album_art(self, next_track):
        try:
            next_album_art_url = next_track.album.images[-1].url
            logger.debug(
                f"Optimistically fetching artwork for: {next_track.artists[0].name} - {next_track.name}"
            )
            self.next_album_art = self.album_art.fetch_and_resize(next_album_art_url)
        except Exception as e:
            logger.error(f"Error fetching next album art: {e}")
            self.next_album_art = None

    def run(self):
        song_id: str = None
        next_song_id: str = None

        while True:
            current_playback = self.spotify.get_currently_playing()

            if current_playback and current_playback.item:
                if current_playback.is_playing:
                    current_song_id = current_playback.item.id

                    # Check if it's a new song
                    if current_song_id != song_id:
                        song_id = current_song_id
                        logger.info(
                            f"Now playing: {current_playback.item.artists[0].name} - {current_playback.item.name}"
                        )

                        # Reset next_album_art when the current song changes
                        self.next_album_art = None

                        # Update the screen with the current album art
                        try:
                            album_art_url = current_playback.item.album.images[-1].url
                            album_art = self.album_art.fetch_and_resize(album_art_url)
                            self.display_album_art(album_art)
                        except Exception as e:
                            logger.error(f"Error displaying album art: {e}")
                            self.display_album_art(
                                self.album_art.get_default_album_art()
                            )

                        # Fetch the next track in the queue
                        queue = self.spotify.get_player_queue()
                        if queue:
                            next_track = queue[0] if queue else None
                            if next_track and next_track.id != next_song_id:
                                next_song_id = next_track.id

                                # Start a new thread to fetch the next album art
                                if self.next_album_art_thread is not None:
                                    self.next_album_art_thread.join()
                                self.next_album_art_thread = threading.Thread(
                                    target=self.fetch_next_album_art, args=(next_track,)
                                )
                                self.next_album_art_thread.start()
                            else:
                                logger.info("No next track in the queue")
                                self.next_album_art = None
                        else:
                            logger.info("Queue is empty")
                            self.next_album_art = None
                    # If it's the same song, do nothing
                else:
                    if song_id is not None:
                        logger.info("Paused, clearing display")
                        song_id = None
                        next_song_id = None
                        self.next_album_art = None
                    self.display_blank()
            else:
                self.display_blank()

            sleep(0.5)

    def display_album_art(self, image: Optional[Image.Image]):
        if image:
            # Just in case, set the image to RGB mode
            image = image.convert("RGB")
            self.matrix.SetImage(image)
        else:
            self.display_blank()

    def display_blank(self):
        self.matrix.Clear()
