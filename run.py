#!/usr/bin/env python
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
