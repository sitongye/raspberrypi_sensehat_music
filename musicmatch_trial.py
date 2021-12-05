import requests

custom_headers = {'authority': "apic-desktop.musixmatch.com",
        'cookie': "x-mxm-token-guid=",}
response = requests.get('https://apic-desktop.musixmatch.com/ws/1.1/macro.subtitles.get?format=json&namespace=lyrics_richsynched&subtitle_format=mxm&app_id=web-desktop-app-v1.0&usertoken=211203f344808859cc1d6246456be4ea846813450d9592fc6bcdc9&q_album=parcels',headers=custom_headers )
print(response.json())
