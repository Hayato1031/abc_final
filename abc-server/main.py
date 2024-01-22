from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import util
import empath
import constatns

ccm = SpotifyClientCredentials(client_id = constatns.SPOTIFY_CLIENT_ID, client_secret = constatns.SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager = ccm)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 許可するオリジン（本番環境では適切なオリジンを指定）
    allow_credentials=True,
    allow_methods=["*"],  # 許可するHTTPメソッド
    allow_headers=["*"],  # 許可するヘッダー
)


@app.post("/get_music/")
async def create_upload_file(playlist_url: str, file: UploadFile = File(...)):
    try: 
        playlist_id = playlist_url.replace("https://open.spotify.com/playlist/", "").split("?")[0]
        playlist = util.get_playlist(playlist_id, sp=sp)
        # Wavファイルから推定されたユーザーのコンテクスト
        #emotion = await empath.get_emotion_from_wav(file)
        danceability_x = util.predict(file)
        # print(emotion)
    except Exception as e:
        return {"error": 1, "msg": e}
        
    distance = []
    minfos = util.get_music_info(playlist, sp=sp)
    for info in minfos:
        danceability = info["danceability"]*10  # 0-10 -> calm

        distance.append(abs(danceability - danceability_x))

    sorted_list = sorted(distance)[:3]
    index = [distance.index(x) for x in sorted_list]
    musics = [playlist[i] for i in index]
    music_infos = util.get_music_info(musics, sp=sp)
    music_uris = [infos["id"] for infos in music_infos]
    music_urls = [f"https://open.spotify.com/embed/track/{uri}" for uri in music_uris]
    
    return {
        "error": 0,
        "music": music_urls,
        "danceability": danceability_x
        }

@app.get("/danceability")
def getdance(music_ids):
    music_ids = music_ids.split(",")
    minfos = util.get_music_info(music_ids, sp=sp)
    
    return {
        "minfo": minfos
    }

if __name__ == "__main__":
    uvicorn.run("main:app",host="0.0.0.0", port=8000, reload=True)