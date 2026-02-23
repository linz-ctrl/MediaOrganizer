"""
Unified date extraction from all media types
"""
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional
import mimetypes

# Try to import optional dependencies
try:
    import exifread
    HAS_EXIFREAD = True
except ImportError:
    HAS_EXIFREAD = False

try:
    from PIL import Image, ExifTags
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import mutagen
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False

def get_image_date(file_path: Path) -> Tuple[Optional[int], Optional[int], Optional[int], str]:
    """
    Extract date from image EXIF data
    Returns: (year, month, day, source)
    """
    # Method 1: exifread
    if HAS_EXIFREAD:
        try:
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f, stop_tag='DateTimeOriginal', details=False)
                
                date_tags = ['EXIF DateTimeOriginal', 'EXIF DateTimeDigitized', 'Image DateTime']
                
                for tag in date_tags:
                    if tag in tags:
                        date_str = str(tags[tag])
                        try:
                            date_obj = datetime.strptime(date_str.split()[0], "%Y:%m:%d")
                            return date_obj.year, date_obj.month, date_obj.day, 'EXIF (exifread)'
                        except (ValueError, IndexError):
                            continue
        except:
            pass
    
    # Method 2: PIL
    if HAS_PIL:
        try:
            image = Image.open(file_path)
            exif = image.getexif()
            
            if exif:
                exif_data = {}
                for tag_id, value in exif.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    exif_data[tag] = value
                
                date_tags = ['DateTimeOriginal', 'DateTimeDigitized', 'DateTime']
                for tag in date_tags:
                    if tag in exif_data:
                        date_str = str(exif_data[tag])
                        try:
                            date_obj = datetime.strptime(date_str.split()[0], "%Y:%m:%d")
                            return date_obj.year, date_obj.month, date_obj.day, 'EXIF (PIL)'
                        except (ValueError, IndexError):
                            continue
        except:
            pass
    
    return None, None, None, "No EXIF data"

def get_video_date(file_path: Path) -> Tuple[Optional[int], Optional[int], Optional[int], str]:
    """
    Extract date from video metadata
    """
    # Try ffprobe
    try:
        import subprocess
        import json
        
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_entries', 'format_tags=creation_time',
            str(file_path)
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if 'format' in data and 'tags' in data['format']:
                creation_time = data['format']['tags'].get('creation_time')
                if creation_time:
                    try:
                        date_str = creation_time.split('T')[0]
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        return date_obj.year, date_obj.month, date_obj.day, 'Video Metadata'
                    except (ValueError, IndexError):
                        pass
    except:
        pass
    
    return None, None, None, "No video metadata"

def get_audio_date(file_path: Path) -> Tuple[Optional[int], Optional[int], Optional[int], str]:
    """
    Extract date from audio metadata
    """
    if HAS_MUTAGEN:
        try:
            audio = mutagen.File(file_path)
            if audio:
                date_tags = ['date', 'creation_date', 'recording_date', 'year']
                
                for tag in date_tags:
                    if tag in audio:
                        date_str = str(audio[tag][0]) if isinstance(audio[tag], list) else str(audio[tag])
                        
                        date_formats = ["%Y-%m-%d", "%Y/%m/%d", "%Y%m%d", "%Y"]
                        
                        for fmt in date_formats:
                            try:
                                date_obj = datetime.strptime(date_str[:len(fmt)], fmt)
                                day = date_obj.day if fmt != "%Y" else 1
                                month = date_obj.month if fmt != "%Y" else 1
                                return date_obj.year, month, day, 'Audio Metadata'
                            except ValueError:
                                continue
        except:
            pass
    
    return None, None, None, "No audio metadata"

def get_fallback_date(file_path: Path) -> Tuple[int, int, int, str]:
    """
    Fallback to file system dates
    """
    try:
        stat = file_path.stat()
        
        # Get creation time based on platform
        if sys.platform == "win32":
            creation_time = datetime.fromtimestamp(stat.st_ctime)
            source = 'File Created (Windows)'
        elif sys.platform == "darwin":
            creation_time = datetime.fromtimestamp(stat.st_birthtime)
            source = 'File Created (macOS)'
        else:
            creation_time = datetime.fromtimestamp(stat.st_ctime)
            source = 'File Metadata'
        
        return creation_time.year, creation_time.month, creation_time.day, source
    except:
        # Last resort
        current = datetime.now()
        return current.year, current.month, current.day, 'Current Date (Fallback)'

def get_media_date(file_path: Path) -> Tuple[int, int, int, str]:
    """
    Get date from any media file with fallbacks
    Returns: (year, month, day, source)
    """
    mime_type, _ = mimetypes.guess_type(str(file_path))
    
    if mime_type and mime_type.startswith('image/'):
        year, month, day, source = get_image_date(file_path)
    elif mime_type and mime_type.startswith('video/'):
        year, month, day, source = get_video_date(file_path)
    elif mime_type and mime_type.startswith('audio/'):
        year, month, day, source = get_audio_date(file_path)
    else:
        year = month = day = None
        source = "Unknown type"
    
    # Fallback if no date found
    if year is None or month is None or day is None:
        year, month, day, source = get_fallback_date(file_path)
    
    return year, month, day, source