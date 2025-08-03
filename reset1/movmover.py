import os
import shutil
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
import threading

def get_date_taken(path):
    """
    Try to get the EXIF 'DateTimeOriginal' tag (taken date).
    Return None if not found or not an image.
    """
    try:
        image = Image.open(path)
        exif_data = image._getexif()
        if exif_data is not None:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == 'DateTimeOriginal':
                    return value
    except Exception:
        return None
    return None

def main():
    # Hardcoded inputs
    folder_path = r"E:\alle fotos tem 1aug2025\ongesorteerd\2025"
    destination_folder = r"E:\alle fotos tem 1aug2025\2025\5"

    # Extract year and month from destination folder path
    month = int(os.path.basename(destination_folder))
    year = int(os.path.basename(os.path.dirname(destination_folder)))

    print(f"Filtering files with EXIF 'DateTimeOriginal' or file system 'gewijzigd' (modification time) in {year}-{month}")

    stop_flag = {"stop": False}

    def listen_for_q():
        while True:
            if input().strip().lower() == 'q':
                stop_flag["stop"] = True
                print("Stopping file moving process...")
                break

    listener_thread = threading.Thread(target=listen_for_q, daemon=True)
    listener_thread.start()

    for root, _, files in os.walk(folder_path):
        if stop_flag["stop"]:
            break
        for file in files:
            if stop_flag["stop"]:
                break
            file_path = os.path.join(root, file)

            # Try get EXIF DateTimeOriginal (genomen op)
            date_taken_str = get_date_taken(file_path)
            date_taken = None

            if date_taken_str:
                try:
                    # EXIF date format: 'YYYY:MM:DD HH:MM:SS'
                    date_taken = datetime.strptime(date_taken_str, '%Y:%m:%d %H:%M:%S')
                except ValueError:
                    # If EXIF date format parsing fails, ignore EXIF date
                    date_taken = None

            if date_taken is None:
                # Fallback to file modification time ('gewijzigd')
                try:
                    mod_time = os.path.getmtime(file_path)
                    date_taken = datetime.fromtimestamp(mod_time)
                except Exception:
                    # If unable to get modification time, skip this file
                    continue

            # Now check extracted date’s year and month
            if date_taken.year == year and date_taken.month == month:
                dest_path = os.path.join(destination_folder, file)
                print(f"Moving: {file_path} -> {dest_path}")
                shutil.move(file_path, dest_path)

if __name__ == "__main__":
    main()
