"""
Global settings and constants
"""
import os
from pathlib import Path

# Base paths
ROOT_DIR = Path(__file__).parent.parent.parent  # Go up to parent folder
CONFIG_FILE = ROOT_DIR / "config.yaml"

import yaml

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f)
    return {}

def save_config(config_data):
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config_data, f, default_flow_style=False)

def _get_path(config_dict, key, default_name):
    path_str = config_dict.get('paths', {}).get(key, default_name)
    path_obj = Path(path_str)
    if path_obj.is_absolute():
        return path_obj
    return ROOT_DIR / path_obj

_config = load_config()

RAW_DATA_DIR = _get_path(_config, 'raw_data', "_RawData")
PHOTOS_DIR = _get_path(_config, 'photos', "Photos")
VIDEOS_DIR = _get_path(_config, 'videos', "Videos")
AUDIO_DIR = _get_path(_config, 'audio', "Audio")

def update_paths(config_data):
    """Update global paths after config change"""
    global RAW_DATA_DIR, PHOTOS_DIR, VIDEOS_DIR, AUDIO_DIR
    RAW_DATA_DIR = _get_path(config_data, 'raw_data', "_RawData")
    PHOTOS_DIR = _get_path(config_data, 'photos', "Photos")
    VIDEOS_DIR = _get_path(config_data, 'videos', "Videos")
    AUDIO_DIR = _get_path(config_data, 'audio', "Audio")

# File type extensions (same as before)
PHOTO_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
    '.heic', '.webp', '.raw', '.cr2', '.nef', '.dng', '.arw'
}

VIDEO_EXTENSIONS = {
    '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.m4v',
    '.mpg', '.mpeg', '.3gp', '.webm', '.mts', '.m2ts', '.ts'
}

AUDIO_EXTENSIONS = {
    '.mp3', '.m4a', '.flac', '.wav', '.aac', '.ogg', '.wma',
    '.aiff', '.alac', '.opus', '.mka', '.amr', '.m4b'
}

# Date extraction priorities
DATE_SOURCES = [
    'EXIF', 'Video Metadata', 'Audio Metadata',
    'File Created', 'File Modified'
]

# Audio categories
AUDIO_CATEGORIES = ['Music', 'Recordings', 'Podcasts', 'Audiobooks']

# Structure - UPDATED FOR YEAR/YEAR-MONTH-DAY
DATE_FORMAT = "%Y-%m-%d"  # YYYY-MM-DD folder name
FOLDER_PATTERN = "{year}/{year}-{month:02d}-{day:02d}"

# Safety settings
DRY_RUN = False
BACKUP_BEFORE_MOVE = True
MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024  # 10GB

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"