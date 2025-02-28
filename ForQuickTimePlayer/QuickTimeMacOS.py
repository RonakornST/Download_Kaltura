import os
import subprocess
import requests

# Base URL up to 'seg-'
base_url = "https://cfvod.kaltura.com/scf/hls/p/2910381/sp/291038100/serveFlavor/entryId/1_72on1pk9/v/11/ev/5/flavorId/1_kr8v8cxz/name/a.mp4/seg-"

# Full authentication parameters (replace with your actual values)
auth_params = "?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jZnZvZC5rYWx0dXJhLmNvbS9zY2YvaGxzL3AvMjkxMDM4MS9zcC8yOTEwMzgxMDAvc2VydmVGbGF2b3IvZW50cnlJZC8xXzcyb24xcGs5L3YvMTEvZXYvNS9mbGF2b3JJZC8xX2tyOHY4Y3h6L25hbWUvYS5tcDQvKiIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc0MDgzMjE3M319fV19&Signature=D2H~a5zMCnAB47sbLCTUsVxduNXKqEUU6Pxj5SMgSPGAQNaCo5zd4e1LqDHss6v5eQxzVr5V2Mbqfc2oCBJ6mrhH8xgm~c7DrL9Cjbi~Bt2Jz2H4JCqGDkfq30S2xV043L7fhUdrUuh9rElNdCFVUBeDIeRl2acAjkBgzW7MDB5BiKtvoNTBj48Hj0GWX9p~qFe8twpWHRjbhbce4Mb1EWPLmEaj76A8gHN3PlYU761hHpSelhnCno4W0FKhOaQNKbGS-yvsNKKqBgCo5mcetdcHzjYaFBddSiLmPGNrnbAbmxZL8mreglfJpBQIa0QUXGbTQ0k7QxEM8LfbDnootA__&Key-Pair-Id=APKAJT6QIWSKVYK3V34A"

# Directory to store .ts files
output_dir = "video_segments"
os.makedirs(output_dir, exist_ok=True)

# Automatically detect the number of .ts segments
ts_files = []
i = 1
print("Starting download...")

while True:
    ts_filename = f"{output_dir}/seg-{i}.ts"
    url = f"{base_url}{i}-v1-a1.ts{auth_params}"  # Append authentication parameters

    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(ts_filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        ts_files.append(ts_filename)
        print(f"Downloaded: seg-{i}.ts")
    else:
        print(f"No more segments found at seg-{i}. Stopping download.")
        break  # Stop when a segment is missing

    i += 1

# Check if any files were downloaded
if not ts_files:
    print("No .ts files downloaded. Exiting.")
    exit(1)

# Create a file list for ffmpeg
file_list_path = "file_list.txt"
with open(file_list_path, "w") as f:
    for ts in ts_files:
        f.write(f"file '{ts}'\n")

print("Merging .ts files into output.mp4...")
subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", file_list_path, "-c", "copy", "output.mp4"], check=True)

# Convert to QuickTime-compatible format
print("Converting to QuickTime-compatible format...")
subprocess.run(["ffmpeg", "-i", "output.mp4", "-movflags", "faststart", "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", "final_output.mp4"], check=True)

print("Done! Your video is saved as 'final_output.mp4'")
