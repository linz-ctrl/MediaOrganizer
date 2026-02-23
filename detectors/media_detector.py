"""
Media file type detection
"""
import mimetypes
from pathlib import Path
from config.settings import PHOTO_EXTENSIONS, VIDEO_EXTENSIONS, AUDIO_EXTENSIONS

class MediaDetector:
    """Detect media file types"""
    
    def detect(self, file_path: Path) -> str:
        """
        Detect file type
        Returns: 'photo', 'video', 'audio', or 'unknown'
        """
        # Check by extension first (fast)
        ext = file_path.suffix.lower()
        
        if ext in PHOTO_EXTENSIONS:
            return 'photo'
        elif ext in VIDEO_EXTENSIONS:
            return 'video'
        elif ext in AUDIO_EXTENSIONS:
            return 'audio'
        
        # Fallback to MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        
        if mime_type:
            if mime_type.startswith('image/'):
                return 'photo'
            elif mime_type.startswith('video/'):
                return 'video'
            elif mime_type.startswith('audio/'):
                return 'audio'
        
        return 'unknown'
    
    def is_media_file(self, file_path: Path) -> bool:
        """Check if file is a media file"""
        file_type = self.detect(file_path)
        return file_type in ['photo', 'video', 'audio']