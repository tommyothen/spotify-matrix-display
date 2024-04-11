# main.py
from spotify import SpotifyClient
from matrix import Matrix
from album_art import AlbumArt
import dotenv
import os
import time
import requests
from logger import Logger

dotenv.load_dotenv()
logger = Logger("main")

def run_matrix():
    spotify = SpotifyClient(
        os.getenv("SPOTIPY_CLIENT_ID"),
        os.getenv("SPOTIPY_CLIENT_SECRET"),
    )

    logger.debug("Successfully created Spotify client")

    album_art = AlbumArt()
    matrix = Matrix(spotify=spotify, album_art=album_art)

    matrix.run()


if __name__ == "__main__":

    while True:
        try:
            run_matrix()
        except requests.exceptions.ConnectionError as e:
            logger.critical(f"Connection error occurred: {e}")
            logger.critical("Retrying in 30 seconds...")
            time.sleep(30)
        except Exception as e:
            logger.critical(f"An error occurred: {e}")
            logger.critical("Retrying in 30 seconds...")
            time.sleep(30)
