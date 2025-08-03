import requests
# Copy the request URL of your interested video by open network section of your browser developer tool console then split it in to base_url and end_url
base_url = "https://cfvod.kaltura.com/scf/hls/p/2910381/sp/291038100/serveFlavor/entryId/1_kljmj6lr/v/11/ev/5/flavorId/1_vtsmxsr7/name/a.mp4/seg-"
end_url = "-v1-a1.ts?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jZnZvZC5rYWx0dXJhLmNvbS9zY2YvaGxzL3AvMjkxMDM4MS9zcC8yOTEwMzgxMDAvc2VydmVGbGF2b3IvZW50cnlJZC8xX2tsam1qNmxyL3YvMTEvZXYvNS9mbGF2b3JJZC8xX3Z0c214c3I3L25hbWUvYS5tcDQvKiIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc0MDgyMzAzNH19fV19&Signature=C4R4HXYOAaE9nor-vYDYwzdj~OW4vB-WS7VZZoYuxrPNjaFH29bUV7hReAS87y1q6zgKbEIFNhMyPYvmwtjN-N0MZCqEtWy-lcmUZK20w30TiRPQZkbhaTy3txM-yj8Nzq2WvGqVWLaz9XX1d1t6hIMuM~R83TWWRtPmS3A3Bt19pYEyPah-bazDeVvxrIsW7Q4HYjzpqharjKYViXcb6pIVIy7lJGQU1hS2dDGFVGF1t0yMMoIhs33m15bZMRg9bEpHwHe1yKP7DHB7RXk5GtkDHR9zJfFlReR6AWjtJq5Z3V9ZdFfADa39UiAJ-LxFIVzCqhqXLd5uKCgNW0QKcA__&Key-Pair-Id=APKAJT6QIWSKVYK3V34A"

start_segment = 1  # Change as needed
end_segment = 902  # Adjust this value based on the total number of segments

for i in range(start_segment, end_segment + 1):
    url = f"{base_url}{i}{end_url}"
    filename = f"segment_{i}.ts"
    
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            print(f"Downloaded {filename}")
        else:
            print(f"Skipping segment {i}: Not found")
    except Exception as e:
        print(f"Error downloading segment {i}: {e}")

