import os
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser
import multiprocessing
import time
from dataclasses import dataclass
from typing import Optional, List
from PIL import Image
import io


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Handle the GET request from the Spotify authentication callback
        if self.path.startswith("/callback"):
            # Extract the code from the query parameters
            query_params = self.path.split("?")[1]
            authorization_code = query_params.split("=")[1]

            # Send a response to the browser
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                '<body style=font-family:Arial;display:grid;place-items:center;text-align:center;color:#fff;background-color:#111><d><h1>Authentication Successful</h1><p>Closing in <c>5</c></d><script>a=5;setInterval(()=>{document.querySelector("c").innerText=--a;a||close()},1e3)</script>'.encode(
                    "utf-8"
                )
            )

            # Exchange the authorization code for an access token
            response = requests.post(
                "https://accounts.spotify.com/api/token",
                data={
                    "grant_type": "authorization_code",
                    "code": authorization_code,
                    "redirect_uri": "http://192.168.4.140:28624/callback",
                    "client_id": os.getenv("SPOTIPY_CLIENT_ID"),
                    "client_secret": os.getenv("SPOTIPY_CLIENT_SECRET"),
                },
            )

            # Save the access token and refresh token to a file
            access_token = response.json()["access_token"]
            refresh_token = response.json()["refresh_token"]

            # Save the expiration time of the access token
            # Save this as UNIX timestamp for easy comparison
            expires_in = response.json()["expires_in"]
            expiration_time = int(time.time()) + expires_in

            with open("tokens.txt", "w") as f:
                f.write(f"{access_token}\n{refresh_token}\n{expiration_time}")

            print("Access token and refresh token saved to tokens.txt")

        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Not found.")


def run_callback_server(queue):
    server_address = ("", 28624)
    httpd = HTTPServer(server_address, CallbackHandler)
    print("Callback server is running on http://192.168.4.140:28624")
    httpd.handle_request()
    queue.put(True)


@dataclass
class ImageObject:
    url: str
    height: Optional[int]
    width: Optional[int]


@dataclass
class PartialAlbum:
    id: str
    name: str
    images: List[ImageObject]


@dataclass
class PartialArtist:
    id: str
    name: str


@dataclass
class TrackObject:
    id: str
    name: str
    album: PartialAlbum
    artists: List[PartialArtist]


@dataclass
class CurrentlyPlaying:
    is_playing: bool
    timestamp: int
    progress_ms: int
    item: TrackObject


class SpotifyClient:
    BASE_URL = "https://api.spotify.com/v1"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

        # Check that client ID and client secret are provided
        if not self.client_id or not self.client_secret:
            raise ValueError("Client ID and client secret are required.")

        # Check if the access token is already saved
        if not os.path.exists("tokens.txt"):
            self.authenticate()

        self.access_token = self.get_access_token()

    def get_access_token(self):
        with open("tokens.txt", "r") as f:
            access_token, refresh_token, expiration_time = f.read().splitlines()

        # Check if the access token has expired
        if int(time.time()) > int(expiration_time):
            print("Access token has expired. Refreshing...")
            access_token = self.refresh_access_token(refresh_token)

        # Set the access token just in case i forget to set it
        self.access_token = access_token
        return access_token

    def authenticate(self):
        print("Waiting for user authentication...")

        # Create a queue to communicate between processes
        queue = multiprocessing.Queue()

        # Start a new process to run the callback server
        server_process = multiprocessing.Process(
            target=run_callback_server, args=(queue,)
        )
        server_process.start()

        scopes = [
            "user-read-currently-playing",
            "user-read-playback-state",
        ]
        auth_url = f"https://accounts.spotify.com/authorize?client_id={self.client_id}&response_type=code&redirect_uri=http://192.168.4.140:28624/callback&scope={'+'.join(scopes)}"

        print(f"Open this URL in your browser: {auth_url}")

        # Open the user's browser to authenticate the app
        webbrowser.open(auth_url)

        # Wait for the authentication to complete
        queue.get()

        # Terminate the server process
        server_process.terminate()
        server_process.join()

    def refresh_access_token(self, refresh_token: str):
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )

        if response.status_code != 200:
            print("Error refreshing access token", response.json())
            exit(1)

        data = response.json()

        access_token: str = data["access_token"]
        expires_in = data["expires_in"]
        expiration_time = int(time.time()) + int(expires_in)

        with open("tokens.txt", "w") as f:
            f.write(f"{access_token}\n{refresh_token}\n{expiration_time}")

        print("Access token refreshed")
        return access_token

    def get_currently_playing(self) -> Optional[CurrentlyPlaying]:
        self.access_token = self.get_access_token()

        response = requests.get(
            f"{self.BASE_URL}/me/player/currently-playing",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        if response.status_code == 200:
            data = response.json()

            return CurrentlyPlaying(
                is_playing=data["is_playing"],
                timestamp=data["timestamp"],
                progress_ms=data["progress_ms"],
                item=TrackObject(
                    id=data["item"]["id"],
                    name=data["item"]["name"],
                    album=PartialAlbum(
                        id=data["item"]["album"]["id"],
                        name=data["item"]["album"]["name"],
                        images=[
                            ImageObject(
                                url=image["url"],
                                height=image["height"],
                                width=image["width"],
                            )
                            for image in data["item"]["album"]["images"]
                        ],
                    ),
                    artists=[
                        PartialArtist(
                            id=artist["id"],
                            name=artist["name"],
                        )
                        for artist in data["item"]["artists"]
                    ],
                ),
            )

        return None

    def get_player_queue(self) -> Optional[List[TrackObject]]:
        self.access_token = self.get_access_token()

        response = requests.get(
            f"{self.BASE_URL}/me/player/queue",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        if response.status_code == 200:
            data = response.json()

            return [
                TrackObject(
                    id=track["id"],
                    name=track["name"],
                    album=PartialAlbum(
                        id=track["album"]["id"],
                        name=track["album"]["name"],
                        images=[
                            ImageObject(
                                url=image["url"],
                                height=image["height"],
                                width=image["width"],
                            )
                            for image in track["album"]["images"]
                        ],
                    ),
                    artists=[
                        PartialArtist(
                            id=artist["id"],
                            name=artist["name"],
                        )
                        for artist in track["artists"]
                    ],
                )
                for track in data["queue"]
            ]

        print("Error fetching player queue", response.json())
        return []  # Return an empty list if there's an error

    def fetch_album_art(self, url: str, resize_factor: int = 64) -> Image:
        # We first try to see if we've stored the image locally
        image_filename = url.split("/")[-1]
        image_path = f"/tmp/image_cache/{image_filename}.jpg"
        if os.path.exists(image_path):
            print("Found locally stored image")

            album_art = Image.open(image_path)
            album_art = album_art.resize((resize_factor, resize_factor))
            return album_art

        response = requests.get(url)
        album_art = Image.open(io.BytesIO(response.content))
        album_art = album_art.resize((resize_factor, resize_factor))

        # Make sure the format is RGB
        album_art.convert("RGB")

        # Save the image to the images directory
        album_art.save(image_path)

        size_in_bytes = os.path.getsize(image_path)
        print(f"Saved image to {image_path} ({size_in_bytes} bytes)")

        return album_art
