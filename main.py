from Spotify import SpotifyClient
from Matrix import Matrix
import dotenv
import os

dotenv.load_dotenv()


if __name__ == "__main__":
    spotify = SpotifyClient(
        os.getenv("SPOTIPY_CLIENT_ID"),
        os.getenv("SPOTIPY_CLIENT_SECRET"),
    )

    print("Successfully created Spotify client")

    matrix = Matrix(
        spotify=spotify,
    )

    matrix.run()
