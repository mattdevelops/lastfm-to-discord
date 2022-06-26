import requests
import time
from datetime import datetime
import json
with open('config.json') as f:
    data = json.loads(f.read())
    api_key = data['api_key']
    spotify_token = data['spotify_token']
    discord_webhook = data['discord_webhook']
    experimental = data['experimental']
    refresh = int(data['refresh'])

details = [0, "Song"]

while True:
    try:
        do_post = True
        r = requests.get(f'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=matttmlive&api_key={api_key}&format=json')
        data = r.json()

        if experimental:
            song = data['recenttracks']['track'][0]
            if '@attr' in song: # now playing
                if song['name'] == details[1]:
                    do_post = False
                else:
                    details = [str(time.time()).split('.')[0], song['name']]
            else:
                if song['date']['uts'] == details[0]:
                    do_post = False
                else:
                    details = [song['date']['uts'], song['name']]
        else:
            song = data['recenttracks']['track'][0]
            if '@attr' in song: # now playing
                song = data['recenttracks']['track'][1]
                if song['date']['uts'] == details[0]:
                    do_post = False
                else:
                    details = [song['date']['uts'], song['name']]
        artist_name = song['artist']['#text']
        song_name = song['name']
        album_name = song['album']['#text']
        if do_post:
            try:
                access_token = requests.post("https://accounts.spotify.com/api/token", data={'grant_type': 'client_credentials'}, headers={'Authorization': f'Basic {spotify_token}'}).json()['access_token']
                r = requests.get(f"https://api.spotify.com/v1/search?type=artist&include_external=audio&q={artist_name}", headers={'Authorization': f'Bearer {access_token}'})
                artist_picture = r.json()['artists']['items'][0]['images'][0]['url']
            except:
                artist_picture = None

            if song['album']['mbid'] != '':
                r = requests.get(f"http://ws.audioscrobbler.com/2.0/?method=album.getinfo&mbid={song['album']['mbid']}&api_key={api_key}&format=json")
                try:
                    album_picture = r.json()['album']['image'][-1]['#text']
                except:
                    album_picture = song['image'][-1]['#text']
            else:
                album_picture = None

            print("Posting")
            status_code = requests.post(discord_webhook,
            json={
              "content": None,
              "embeds": [
                {
                  "description": song_name,
                  "color": 12787270,
                  "author": {
                    "name": artist_name,
                  },
                  "footer": {
                    "text": album_name,
                    "icon_url": artist_picture if album_picture != None else None
                  },
                  "timestamp": datetime.utcfromtimestamp(int(details[0])).isoformat(),
                  "thumbnail": {
                    "url": album_picture if album_picture != None else artist_picture
                  }
                }
              ],
              "username": "Last.fm - Matt",
              "avatar_url": "https://www.last.fm/static/images/lastfm_avatar_twitter.52a5d69a85ac.png",
              "attachments": []
            }).status_code
            print(status_code)
    except:
        pass

    time.sleep(refresh)
