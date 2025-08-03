import os
import shutil
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
import threading

def get_date_taken(path):
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
    folder_path = r"D:\fotosgsmvtviadploods\iphone13vt"
    destination_folder = r"D:\loodsgeorteerdefotos\2025\5"  # year=2024, month=1

    # Extract year and month from destination_folder path
    month = int(os.path.basename(destination_folder))  # '1' -> 1
    year = int(os.path.basename(os.path.dirname(destination_folder)))  # parent folder name '2024' -> 2024

    print(f"Year detected: {year}, Month detected: {month}")

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
            date_taken_str = get_date_taken(file_path)
            if date_taken_str:
                try:
                    date_taken = datetime.strptime(date_taken_str, '%Y:%m:%d %H:%M:%S')
                    if date_taken.year == year and date_taken.month == month:
                        dest_path = os.path.join(destination_folder, file)
                        print(f"Moving: {file_path} -> {dest_path}")
                        shutil.move(file_path, dest_path)
                except ValueError:
                    continue

if __name__ == "__main__":
    main()
