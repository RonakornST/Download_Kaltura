import urllib.request
import os
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

download_folder = "video_segments_ep11"
output_file = "MotorDrive_EP11.mp4"
max_threads = 50
max_consecutive_failures = 5
max_retries_per_segment = 3


def parse_url(full_url):
    """
    Given a full segment URL, split it into base_url and end_url
    base_url + segment_number + end_url reconstructs full URL
    """
    parsed = urlparse(full_url)
    path = parsed.path  # e.g. /scf/hls/p/2910381/sp/291038100/serveFlavor/entryId/1_gc18nbqv/v/11/ev/4/flavorId/1_vlzfmqey/name/a.mp4/seg-797-v1-a1.ts
    # Find 'seg-' in path, then split before and after segment number
    seg_index = path.find('seg-')
    if seg_index == -1:
        raise ValueError("URL does not contain 'seg-' pattern.")

    # Find the number part after 'seg-'
    after_seg = path[seg_index+4:]
    # segment number is digits before next '-'
    num_end = after_seg.find('-')
    if num_end == -1:
        raise ValueError("URL segment number format incorrect.")

    segment_num = after_seg[:num_end]

    base_path = path[:seg_index+4]  # up to and including 'seg-'
    end_path = path[seg_index+4+len(segment_num):]  # after segment number

    # Rebuild base_url and end_url with scheme and netloc
    base_url = f"{parsed.scheme}://{parsed.netloc}{base_path}"
    end_url = f"{end_path}?{parsed.query}"

    return base_url, end_url, int(segment_num)


def download_segment(base_url, end_url, segment, attempt=1):
    segment_url = f"{base_url}{segment}{end_url}"
    segment_file = os.path.join(download_folder, f"segment-{segment}.ts")

    try:
        with urllib.request.urlopen(segment_url, timeout=10) as response:
            with open(segment_file, "wb") as out_file:
                shutil.copyfileobj(response, out_file)
        print(f"Downloaded: segment-{segment}.ts (Attempt {attempt})")
        return True, segment
    except:
        if os.path.exists(segment_file):
            os.remove(segment_file)
        if attempt < max_retries_per_segment:
            print(f"Retrying segment-{segment}.ts (Attempt {attempt + 1})...")
            time.sleep(1)
            return download_segment(base_url, end_url, segment, attempt + 1)
        else:
            print(f"Failed segment-{segment}.ts after {max_retries_per_segment} attempts.")
            return False, segment


def download_all(base_url, end_url):
    segment = 1
    failures = 0
    downloaded_segments = []

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {}

        while failures < max_consecutive_failures:
            future = executor.submit(download_segment, base_url, end_url, segment)
            futures[future] = segment
            segment += 1

            done = [f for f in list(futures) if f.done()]
            for f in done:
                success, seg_num = f.result()
                if success:
                    downloaded_segments.append(seg_num)
                    failures = 0
                else:
                    failures += 1
                    if failures >= max_consecutive_failures:
                        print(f"\nReached {failures} consecutive failures. Stopping...")
                        for pending in futures:
                            if not pending.done():
                                pending.cancel()
                        return sorted(downloaded_segments)

                del futures[f]

    return sorted(downloaded_segments)


def merge_segments(segments):
    with open(output_file, "wb") as merged:
        for i in segments:
            segment_path = os.path.join(download_folder, f"segment-{i}.ts")
            if os.path.exists(segment_path):
                with open(segment_path, "rb") as ts_file:
                    shutil.copyfileobj(ts_file, merged)

    print(f"Merged video saved as {output_file}")


if __name__ == "__main__":
    full_url = input("Enter a full segment URL (e.g. for segment 1 or 872): ").strip()
    try:
        base_url, end_url, sample_segment = parse_url(full_url)
        print(f"Parsed base_url: {base_url}")
        print(f"Parsed end_url: {end_url}")
        print(f"Starting download from segment 1...")
        segments = download_all(base_url, end_url)
        print(f"\nDownloaded {len(segments)} segments successfully.")
        merge_segments(segments)
    except Exception as e:
        print(f"Error parsing URL or downloading: {e}")
