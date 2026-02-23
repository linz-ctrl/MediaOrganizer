"""
QUICK FIX: Organize MediaOrganizer to work with parent folder structure
Makes MediaOrganizer work with folders at same level: _RawData, Photos, Videos, Audio
"""
import os
import sys
import shutil
from pathlib import Path

# Get current directory (MediaOrganizer folder)
current_dir = Path(__file__).parent
parent_dir = current_dir.parent

print("🔧 QUICK FIX FOR MEDIA ORGANIZER")
print("="*60)
print(f"MediaOrganizer folder: {current_dir}")
print(f"Parent folder: {parent_dir}")
print("="*60)

def check_current_structure():
    """Check what folders exist where"""
    print("\n📁 CURRENT STRUCTURE:")
    
    folders = ["_RawData", "Photos", "Videos", "Audio"]
    
    for folder in folders:
        # Check parent directory
        parent_path = parent_dir / folder
        current_path = current_dir / folder
        
        if parent_path.exists():
            print(f"✓ {folder}/ exists in PARENT folder")
            print(f"  Location: {parent_path}")
            
            # Count files
            if folder != "_RawData":
                files = list(parent_path.rglob("*"))
                files = [f for f in files if f.is_file()]
                if files:
                    print(f"  Contains: {len(files)} files")
        elif current_path.exists():
            print(f"⚠ {folder}/ exists in MediaOrganizer folder")
            print(f"  Location: {current_path}")
            
            # Count files
            files = list(current_path.rglob("*"))
            files = [f for f in files if f.is_file()]
            if files:
                print(f"  Contains: {len(files)} files (will be moved)")
        else:
            print(f"✗ {folder}/ not found")
    
    print("\n" + "="*60)

def fix_config_file():
    """Update config/settings.py to point to parent folder"""
    config_file = current_dir / "config" / "settings.py"
    
    if not config_file.exists():
        print("❌ config/settings.py not found!")
        return False
    
    print("\n⚙️  Fixing config/settings.py...")
    
    try:
        # Read current content
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Find and replace ROOT_DIR
        old_line = "ROOT_DIR = Path(__file__).parent.parent"
        new_line = "ROOT_DIR = Path(__file__).parent.parent.parent  # Go up to parent folder"
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            print(f"  ✓ Updated ROOT_DIR to point to parent folder")
        else:
            print(f"  ⚠ Could not find ROOT_DIR line")
            # Add it manually
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "from pathlib import Path" in line:
                    lines.insert(i + 1, new_line)
                    content = '\n'.join(lines)
                    print(f"  ✓ Added ROOT_DIR line")
                    break
        
        # Write back
        with open(config_file, 'w') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error fixing config: {e}")
        return False

def move_files_to_parent():
    """Move files from MediaOrganizer to parent folder"""
    print("\n📦 Moving files to parent folder...")
    
    folders_to_move = ["_RawData", "Photos", "Videos", "Audio"]
    
    for folder in folders_to_move:
        source = current_dir / folder
        destination = parent_dir / folder
        
        if source.exists():
            # Check if destination already exists
            if destination.exists():
                print(f"  ⚠ {folder}/ already exists in parent")
                print(f"    Merging files...")
                
                # Merge files
                for item in source.rglob("*"):
                    if item.is_file():
                        rel_path = item.relative_to(source)
                        dest_path = destination / rel_path
                        
                        # Create parent directories
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Handle duplicates
                        if dest_path.exists():
                            counter = 1
                            original_dest = dest_path
                            while dest_path.exists():
                                stem = original_dest.stem
                                suffix = original_dest.suffix
                                dest_path = original_dest.parent / f"{stem}_{counter}{suffix}"
                                counter += 1
                        
                        shutil.move(str(item), str(dest_path))
                        print(f"      Moved: {rel_path}")
                
                # Remove empty source directory
                try:
                    shutil.rmtree(source)
                    print(f"    ✓ Removed empty {folder}/ from MediaOrganizer")
                except:
                    pass
                
            else:
                # Move entire folder
                shutil.move(str(source), str(destination))
                print(f"  ✓ Moved {folder}/ to parent folder")
        else:
            print(f"  ⚠ {folder}/ not found in MediaOrganizer")
    
    return True

def create_missing_folders():
    """Create any missing folders in parent directory"""
    print("\n📁 Creating missing folders in parent...")
    
    folders = ["_RawData", "Photos", "Videos", "Audio"]
    audio_subfolders = ["Music", "Recordings", "Podcasts", "Audiobooks"]
    
    created_count = 0
    
    for folder in folders:
        folder_path = parent_dir / folder
        if not folder_path.exists():
            folder_path.mkdir(exist_ok=True)
            print(f"  ✓ Created {folder}/ in parent")
            created_count += 1
    
    # Create audio subfolders
    audio_path = parent_dir / "Audio"
    if audio_path.exists():
        for subfolder in audio_subfolders:
            subfolder_path = audio_path / subfolder
            if not subfolder_path.exists():
                subfolder_path.mkdir(exist_ok=True)
                print(f"  ✓ Created Audio/{subfolder}/")
    
    if created_count == 0:
        print("  ✓ All folders already exist")
    
    return True

def create_symlink():
    """Create symbolic link from MediaOrganizer to parent folders (optional)"""
    print("\n🔗 Creating symbolic links (optional)...")
    
    try:
        folders = ["_RawData", "Photos", "Videos", "Audio"]
        
        for folder in folders:
            source = parent_dir / folder
            destination = current_dir / folder
            
            # Remove if exists in MediaOrganizer
            if destination.exists():
                if destination.is_symlink():
                    destination.unlink()
                elif destination.is_dir():
                    shutil.rmtree(destination)
                else:
                    destination.unlink()
            
            # Create symlink
            if source.exists():
                os.symlink(source, destination, target_is_directory=True)
                print(f"  ✓ Created symlink: MediaOrganizer/{folder} -> ../{folder}")
            else:
                print(f"  ⚠ Cannot create symlink: ../{folder} doesn't exist")
        
        return True
    except Exception as e:
        print(f"  ⚠ Could not create symlinks: {e}")
        print("    (This is optional, organizer will still work)")
        return False

def create_run_script():
    """Create a run script that works from MediaOrganizer folder"""
    print("\n📜 Creating run script...")
    
    script_content = '''#!/usr/bin/env python
"""
Run Media Organizer from parent folder context
"""
import os
import sys
from pathlib import Path

# Go to parent directory (where _RawData, Photos, etc. are)
parent_dir = Path(__file__).parent.parent
os.chdir(parent_dir)

# Add MediaOrganizer to Python path
sys.path.insert(0, str(parent_dir / "MediaOrganizer"))

# Import and run
try:
    from MediaOrganizer.main import main
    main()
except ImportError as e:
    print(f"Error: {e}")
    print("Make sure you're in the MediaOrganizer directory")
'''

    script_path = current_dir / "run.py"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"  ✓ Created run.py in MediaOrganizer folder")
    print(f"  💡 Run with: python run.py")
    
    return True

def main():
    """Main fix function"""
    print("🔧 MEDIA ORGANIZER QUICK FIX")
    print("="*60)
    print("\nThis will:")
    print("1. Move _RawData, Photos, Videos, Audio to parent folder")
    print("2. Update config to point to parent folder")
    print("3. Create symbolic links (optional)")
    print("4. Create run script")
    print("\n" + "="*60)
    
    # Show current structure
    check_current_structure()
    
    # Confirm
    confirm = input("\nContinue with fix? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Operation cancelled.")
        return
    
    print("\n" + "="*60)
    print("STARTING FIX...")
    print("="*60)
    
    # Step 1: Fix config
    if not fix_config_file():
        print("⚠ Config fix failed, but continuing...")
    
    # Step 2: Move files
    move_files_to_parent()
    
    # Step 3: Create missing folders
    create_missing_folders()
    
    # Step 4: Create symlinks (optional)
    symlink_choice = input("\nCreate symbolic links? (MediaOrganizer/folder -> ../folder) [Y/n]: ").strip().lower()
    if symlink_choice in ['y', 'yes', '']:
        create_symlink()
    
    # Step 5: Create run script
    create_run_script()
    
    # Step 6: Create test files if _RawData is empty
    rawdata = parent_dir / "_RawData"
    if rawdata.exists():
        files = list(rawdata.rglob("*"))
        files = [f for f in files if f.is_file()]
        if len(files) == 0:
            create_test = input("\n_RawData is empty. Create test files? [Y/n]: ").strip().lower()
            if create_test in ['y', 'yes', '']:
                create_test_files()
    
    print("\n" + "="*60)
    print("✅ FIX COMPLETE!")
    print("="*60)
    print("\n📁 NEW STRUCTURE:")
    print(f"  Parent folder ({parent_dir}):")
    print("    ├── _RawData/     (put your files here)")
    print("    ├── Photos/       (organized photos)")
    print("    ├── Videos/       (organized videos)")
    print("    ├── Audio/        (organized audio)")
    print("    └── MediaOrganizer/  (your code)")
    print("\n🚀 HOW TO RUN:")
    print("  Option 1: python run.py (from MediaOrganizer folder)")
    print("  Option 2: cd .. && python MediaOrganizer/main.py")
    print("\n💡 Put your media files in ../_RawData/ folder")

def create_test_files():
    """Create sample test files"""
    print("\n🧪 Creating test files...")
    
    from datetime import datetime
    import os
    
    rawdata = parent_dir / "_RawData"
    rawdata.mkdir(exist_ok=True)
    
    test_files = [
        ("photo_2023.jpg", "Test photo from 2023\n"),
        ("video_2024.mp4", "Test video from 2024\n"),
        ("audio_recording.mp3", "Test audio recording\n"),
    ]
    
    for filename, content in test_files:
        file_path = rawdata / filename
        with open(file_path, 'w') as f:
            f.write(content)
            f.write("=" * 40 + "\n")
            f.write("Test file for Media Organizer\n")
            f.write("=" * 40 + "\n")
        
        # Set modification time
        if "2023" in filename:
            timestamp = datetime(2023, 6, 15).timestamp()
        elif "2024" in filename:
            timestamp = datetime(2024, 1, 20).timestamp()
        else:
            timestamp = datetime.now().timestamp()
        
        os.utime(file_path, (timestamp, timestamp))
        print(f"  ✓ Created: {filename}")
    
    print(f"✅ Created {len(test_files)} test files in _RawData/")

if __name__ == "__main__":
    main()