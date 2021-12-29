import youtube_dl
import subprocess as sp
#
# sp.call(["mkdir", "-p", pieq_tmp])

prefix = ''

playlist_id = [
    "OLAK5uy_m33d-iqwXjPK2lcUZy1_Jy8cj6Sa7dizc",
    "OLAK5uy_lGZXAEcoxRuRbOYS65uBZ7EyCN1BctcoI",
    "OLAK5uy_k6sXMGx9EHlf2rCpoctp0azMSECiHDDgk"

]

video_list = []




import googleapiclient.discovery
# API information
api_service_name = "youtube"
api_version = "v3"
# API key
DEVELOPER_KEY = "AIzaSyDQAXQ8qOtLZ5FM8GVByo-0gTqm1oYrE-s"
#playlist_id = "OLAK5uy_mZUxifKouQ2-X-0-Q2Nmz4_Zw7fj44Qxk"

# API client
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey=DEVELOPER_KEY)
# 'request' variable is the only thing you must change
# depending on the resource and method you need to use
# in your query
for playlist in playlist_id:
    playlink = playlist
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        maxResults=50,
        playlistId=playlist
    )
    # Query execution
    response = request.execute()
    # Print the results
    vlink = [(item.get('snippet').get('title'), item.get('snippet').get('resourceId').get('videoId') ) for item in response.get('items')]
    for item in vlink:
        albumtitle = item[0]
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '{}/%(title)s.%(ext)s'.format(playlink.split('_')[-1]),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download(['https://www.youtube.com/watch?v={}'.format(item[1])])
        except:
            sp.call(['youtube-dl', '--rm-cache-dir'])
            print('error: ', albumtitle)
            continue
