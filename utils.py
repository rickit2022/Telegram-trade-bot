import subprocess, os, requests, random, json, html, re, logging
from yt_dlp import YoutubeDL
from googleapiclient.discovery import build
from googleapiclient import errors
from credsManager import get_key

def encode():
    """ 
    Encode the audio files into .ogg format (telegram recommended format for sending voice messages). It uses ffmpeg to convert .mp4 into .ogg.
    """
    input_videos = []
    
    for file_name in os.listdir(os.getcwd() + r"\bot\resources\songs"):
        if file_name.endswith(".mp4"):
            input_videos.append(file_name)

    for i in range(0,len(input_videos)):
        vid_path = f'bot\songs\{input_videos[i]}'
        output_path = f'bot\songs\{input_videos[i][:-4]}.ogg'
        result = subprocess.run(f'ffmpeg -i "{vid_path}" -vn -c:a libopus -map_metadata -1 -y "{output_path}"',shell=True, cwd = os.getcwd())
        os.remove(vid_path)

def sanitize_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_. ]+', '', filename)

def search_song(query):
    query_words = query.lower().split()
    voice_list = [file for file in os.listdir(os.getcwd() + r"\bot\resources\songs") if file.endswith(".opus")]
    best_match = None
    max_match_count = 0

    for voice in voice_list:
        title = voice.lower().split(".ogg")[0]
        match_count = sum(1 for word in query_words if word in title)
        if match_count > max_match_count:
            best_match = voice
            max_match_count = match_count
    #if there's a "best match" and match rate > 60% of the query
    if best_match and max_match_count > len(query)*0.6:
        return best_match

    return None

def getGIF(keyword: str) -> str:
    """
    Get a random GIF from Tenor API based on a keyword.
    """
    tenorAPI = get_key("tenor_key")
    client_key = "telegram_bot" # to differentiate between different integration (which i have no other lol)
    limit = 20 # limit of search results
    search_term = keyword

    r = requests.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s&random=true" %(search_term, tenorAPI, client_key, limit), timeout = None)

    if r.status_code == 200:
        response = json.loads(r.content) 
        return response['results'][random.randint(0,20)]['media_formats']['gif']['url']
    else:
        return "Couldn't retrieve GIFs, error response code: %s" %(r.status_code)

def search_youtube(keyword:str):
    youtube = build('youtube', 'v3', developerKey= get_key("youtube_key")) # 10000 units/day -> 100 calls

    request = youtube.search().list(
        part='snippet',
        q=keyword,
        type='video',
        videoCategoryId='10',
        maxResults=1
    )
    try:
        response = request.execute()
    except errors.HttpError:
        return "Exceeded limit..."

    if 'items' in response and len(response['items']) > 0:
        video_id = response['items'][0]['id']['videoId']
        video_link = f'https://www.youtube.com/watch?v={video_id}'
        video_title = response['items'][0]['snippet']['title']

        with open(os.getcwd() + "resources/requests/youtube.txt", "w") as file:
            json.dump(response, file)
        
        #' in JSON needs to be unescaped
        return video_link, html.unescape(video_title)

    return None

def custom_format_selector(ctx):
    # formats are already sorted worst to best
    formats = ctx.get('formats')[::-1]
    best_audio = next(f for f in formats if (
        f['acodec'] != 'none' and f['vcodec'] == 'none')) #and f['ext'] in audio_ext

    # These are the minimum required fields for a merged format
    yield {
        'format_id': f'{best_audio["format_id"]}',
        # 'ext': best_video['ext'],
        'ext': best_audio['ext'],
        'requested_formats': [best_audio],
        # Must be + separated list of protocols
        'protocol': f'{best_audio["protocol"]}'
    }

def download_youtube(url) -> bool:
    ydl_opts = {'format': 'bestaudio/best',
            'outtmpl': os.getcwd() + "bot/resources/songs/%(title)s.%(ext)s",
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'opus',
                'preferredquality': '192',
            }],
            # 'logger': 'bot.yt_dlp_logger
            }
    with YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download([url])

        if error_code:
            return False
    return True

def write_data(data, filename ,dir = None):
        path = filename
        if dir:
            path = f"{dir}/{filename}"

        try:
            with open(path, "w") as f:
                if ".json" in path:
                    f.write(json.dumps(data))
                elif ".csv" in path:
                    f.write(data.to_csv())
                elif ".txt" in path:
                    try:
                        f.write(data)
                    except TypeError:
                        f.write(str(data))
        except Exception as e:
            logging.error(f"Export-error: \n {e}")