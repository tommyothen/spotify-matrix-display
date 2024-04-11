# album_art.py
from typing import Optional
from PIL import Image
import requests
import io
import os
from logger import Logger

logger = Logger("album_art")

class AlbumArt:
    def __init__(self, cache_dir: str = "/home/matrix/matrix/images"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def fetch_and_resize(
        self, url: str, resize_factor: int = 64
    ) -> Optional[Image.Image]:
        # We first check if the image is already in the cache
        image_filename = url.split("/")[-1]
        image_path = f"{self.cache_dir}/{image_filename}.jpg"
        if os.path.exists(image_path):
            return Image.open(image_path)

        try:
            # If the image is not in the cache, we fetch it from the URL
            response = requests.get(url)
            album_art = Image.open(io.BytesIO(response.content))
            album_art = album_art.resize((resize_factor, resize_factor))

            # Make sure the format is RGB
            album_art = album_art.convert("RGB")

            # Save the image to the cache
            album_art.save(image_path)

            size_kb = os.path.getsize(image_path) / 1024
            logger.debug(f"Saved album art to {image_path} ({size_kb:.2f} KB)")

            return album_art
        except (requests.exceptions.RequestException, IOError) as e:
            logger.error(f"Error fetching or processing album art: {e}")
            return self.get_default_album_art()

    def get_default_album_art(self) -> Image.Image:
        # For now, just return a blank image
        logger.warning("No album art found, returning default image")
        return Image.new("RGB", (64, 64), (0, 0, 0))
