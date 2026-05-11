import json
import uuid
import time
import requests
import re
import os

# --- CONFIGURATION ---
# Replace it with your csv-filename. If you have multiple csv-Files, just add them seperated by , eg "first.csv", "second.cs" etc.
# One db-file for every single CSV will be created.
INPUT_FILES = ["yourFile.csv"]

def get_yt_metadata(video_id):
    """Fetches title and channel name directly from the YouTube page."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        html = response.text
        
        # Extract title
        title_match = re.search(r'<title>(.*?) - YouTube</title>', html)
        title = title_match.group(1) if title_match else f"Video {video_id}"
        
        # Extract author/channel name
        author_match = re.search(r'"author":"(.*?)"', html)
        author = author_match.group(1) if author_match else "Unknown Channel"
        
        return title, author
    except:
        return f"Video {video_id}", "Unknown Channel"

def process_files():
    for input_file in INPUT_FILES:
        if not os.path.exists(input_file):
            print(f"Skipping: '{input_file}' not found.")
            continue

        output_file = input_file + ".db"
        current_time_ms = int(time.time() * 1000)
        videos = []

        print(f"\n--- Processing: {input_file} ---")
        
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
                # Skip header if 'video' string is found in the first line
                start_index = 1 if "video" in lines[0].lower() else 0
                
                for line in lines[start_index:]:
                    video_id = line.strip().split(",")[0].strip()
                    if len(video_id) != 11:
                        continue

                    print(f"Scraping metadata for: {video_id}...")
                    title, author = get_yt_metadata(video_id)
                    
                    video_obj = {
                        "type": "video",
                        "videoId": video_id,
                        "title": title,
                        "author": author,
                        "authorId": "UC" + "0"*22, 
                        "published": current_time_ms,
                        "lengthSeconds": 0,
                        "isUpcoming": False,
                        "timeAdded": current_time_ms,
                        "playlistItemId": str(uuid.uuid4())
                    }
                    videos.append(video_obj)
                    time.sleep(0.5) # Short delay to avoid being blocked

            playlist_data = {
                "playlistName": input_file.replace(".csv", ""),
                "protected": False,
                "description": "Imported from CSV",
                "videos": videos,
                "_id": "ft-playlist--" + str(uuid.uuid4()),
                "createdAt": current_time_ms,
                "lastUpdatedAt": current_time_ms
            }

            # Write as single-line JSONL
            with open(output_file, "w", encoding="utf-8") as out:
                json_line = json.dumps(playlist_data, separators=(',', ':'))
                out.write(json_line + "\n")
            
            print(f"SUCCESS! {len(videos)} videos saved to '{output_file}'.")

        except Exception as e:
            print(f"Error processing {input_file}: {e}")

if __name__ == "__main__":
    process_files()
    print("\nAll tasks finished.")
