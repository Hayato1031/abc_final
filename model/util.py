import numpy as np
import librosa
import scipy
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

