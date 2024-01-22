import numpy as np
import librosa
import os
import re
import joblib

def get_MFCC(y, sr):
	mfcc_feature = librosa.feature.mfcc(y=y,sr=sr,n_mfcc=13)
	mean_mfccs = np.mean(mfcc_feature, axis=1)
	return mean_mfccs

def get_average_amplitude(y):
	average_amplitude = np.mean(np.abs(y))
	return average_amplitude

def get_zerocross(y):
	zero_crossings = librosa.feature.zero_crossing_rate(y)
	mean_zero_crossings = np.mean(zero_crossings, axis=1)

	return mean_zero_crossings

def get_melspec_db(y, sr):
	melspec = librosa.feature.melspectrogram(y=y, sr=sr)
	mean_melspec = np.mean(melspec, axis=1)

	return mean_melspec

def get_label(wav):
	basefile = os.path.basename(wav)
	label = basefile.split("_")[0]
	match = re.match(r'([a-zA-Z]+)([0-9]+)', label)
	return match.group(1), int(match.group(2))

def predict(wav):
	loaded_random_forest_model = joblib.load('random_forest.joblib')

	X = []
	y, sr = librosa.load(wav)

	average_amplitude = get_average_amplitude(y)
	zerocross = get_zerocross(y)
	melspec_db = get_melspec_db(y, sr)
	mfcc = get_MFCC(y, sr)
	combined_features = np.concatenate((mfcc, zerocross, melspec_db, [average_amplitude]), axis=0)

	X.append(combined_features)
	# 新しいデータに対して予測を行う
	predictions = loaded_random_forest_model.predict(X)
	print(predictions[0])


# プレイリストから曲を取得
def get_playlist(playlist_id, sp):
    try:
        playlist = sp.playlist(playlist_id)
    except Exception as e:
        print(e)
    track_ids = []
    for item in playlist['tracks']['items']:
        track = item['track']
        if not track['id'] in track_ids:
            track_ids.append(track['id'])
        else:
            for item in playlist['tracks']['items']:
                track = item['track']
                if not track['id'] in track_ids:
                    track_ids.append(track['id'])
    return track_ids

# 音楽IDから情報を取得
def get_music_info(music_id, sp):
	result = sp.audio_features(music_id)
	return result

def predict(file):
	loaded_random_forest_model = joblib.load('random_forest.joblib')
	# file_path = f"uploaded_files/{file.filename}"

	# with open(file_path, "wb") as audio_file:
	# 	print(file_path)
	# 	audio_file.write(file.file.read())

	X = []
	y, sr = librosa.load(file.file)

	average_amplitude = get_average_amplitude(y)
	zerocross = get_zerocross(y)
	melspec_db = get_melspec_db(y, sr)
	mfcc = get_MFCC(y, sr)
	combined_features = np.concatenate((mfcc, zerocross, melspec_db, [average_amplitude]), axis=0)
	X.append(combined_features)
	# 新しいデータに対して予測を行う
	predictions = loaded_random_forest_model.predict(X)

	return predictions[0]
