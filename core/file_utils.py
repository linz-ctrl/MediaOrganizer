"""
File operations utilities - FIXED PATH DISPLAY
"""
import shutil
import hashlib
import os
from pathlib import Path
from typing import Optional, Tuple
from config.settings import DRY_RUN, BACKUP_BEFORE_MOVE

def calculate_hash(file_path: Path, algorithm: str = 'sha256') -> Optional[str]:
    """
    Calculate file hash
    """
    if algorithm.lower() == 'sha256':
        hash_obj = hashlib.sha256()
    elif algorithm.lower() == 'md5':
        hash_obj = hashlib.md5()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        print(f"Error calculating hash for {file_path.name}: {e}")
        return None

def safe_move(src: Path, dst: Path) -> Tuple[bool, str]:
    """
    Safely move file with duplicate handling - FIXED PATH DISPLAY
    """
    if src.resolve() == dst.resolve():
        return True, "Already in correct location"
    
    # Create parent directories
    dst.parent.mkdir(parents=True, exist_ok=True)
    
    # Handle duplicates
    counter = 1
    original_dest = dst
    while dst.exists():
        stem = original_dest.stem
        suffix = original_dest.suffix
        dst = original_dest.parent / f"{stem}_{counter}{suffix}"
        counter += 1
    
    if DRY_RUN:
        # Show simple path without relative calculation
        print(f"[DRY RUN] Would move: {src.name}")
        print(f"          From: {src.parent}")
        print(f"          To: {dst.parent}")
        return True, "Dry run completed"
    
    try:
        # Backup if enabled
        if BACKUP_BEFORE_MOVE and dst.exists():
            backup_path = dst.with_suffix(dst.suffix + '.bak')
            shutil.copy2(str(dst), str(backup_path))
        
        shutil.move(str(src), str(dst))
        return True, "File moved successfully"
    except Exception as e:
        return False, f"Error moving file: {e}"

def get_file_info(file_path: Path) -> dict:
    """
    Get comprehensive file information
    """
    try:
        stat = file_path.stat()
        return {
            'path': str(file_path),
            'name': file_path.name,
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'hash_sha256': calculate_hash(file_path, 'sha256'),
            'hash_md5': calculate_hash(file_path, 'md5')
        }
    except Exception as e:
        print(f"Error getting file info: {e}")
        return {}