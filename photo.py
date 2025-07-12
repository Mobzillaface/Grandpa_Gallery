import os
import json
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS

# Configuration - no changes needed
PHOTOS_DIRECTORY = "Grandpa\Photos"  # Since we're running from Grandpa folder
OUTPUT_FILE = "photos.json"

def get_image_metadata(image_path):
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                return {
                    TAGS[k]: v for k, v in exif_data.items()
                    if k in TAGS and isinstance(v, (str, int, float, bytes))
                }
    except Exception:
        return {}

def generate_photo_index():
    supported_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff')
    photos = []
    
    print(f"Scanning: {PHOTOS_DIRECTORY}")
    
    for filename in os.listdir(PHOTOS_DIRECTORY):
        if filename.lower().endswith(supported_extensions):
            filepath = os.path.join(PHOTOS_DIRECTORY, filename)
            
            # Get file info
            stat = os.stat(filepath)
            date_taken = get_date_taken(get_image_metadata(filepath)) or \
                        datetime.fromtimestamp(stat.st_mtime).date().isoformat()
            
            photos.append({
                "filename": filename,
                "path": f"Photos/{filename}",  # Simple relative path
                "dateTaken": date_taken,
                "sizeKB": round(stat.st_size / 1024, 2)
            })
            print(f"Added: {filename}")
    
    # Sort by date (newest first)
    photos.sort(key=lambda x: x['dateTaken'], reverse=True)
    
    # Write JSON file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({"photos": photos}, f, indent=2)
    
    print(f"\nGenerated {OUTPUT_FILE} with {len(photos)} photos")

def get_date_taken(exif_data):
    date_keys = ['DateTimeOriginal', 'DateTimeDigitized', 'DateTime']
    for key in date_keys:
        if key in exif_data:
            try:
                date_str = exif_data[key]
                if isinstance(date_str, bytes):
                    date_str = date_str.decode('utf-8', errors='ignore')
                return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S').date().isoformat()
            except (ValueError, TypeError):
                continue
    return None

if __name__ == "__main__":
    if not os.path.exists(PHOTOS_DIRECTORY):
        print(f"Error: Photos folder not found in {os.getcwd()}")
    else:
        generate_photo_index()