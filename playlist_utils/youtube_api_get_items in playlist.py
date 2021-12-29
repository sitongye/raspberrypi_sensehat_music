import googleapiclient.discovery
# API information
api_service_name = "youtube"
api_version = "v3"
# API key
DEVELOPER_KEY = "AIzaSyDQAXQ8qOtLZ5FM8GVByo-0gTqm1oYrE-s"
playlist_id = "OLAK5uy_mZUxifKouQ2-X-0-Q2Nmz4_Zw7fj44Qxk"

# API client
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey=DEVELOPER_KEY)
# 'request' variable is the only thing you must change
# depending on the resource and method you need to use
# in your query
request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        maxResults=100,
        playlistId=playlist_id
    )
# Query execution
response = request.execute()
# Print the results
print(response)

vlink = [(item.get('snippet').get('title'), item.get('snippet').get('resourceId').get('videoId') ) for item in response.get('items')]

