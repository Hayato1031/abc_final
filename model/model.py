import glob
import librosa
import os
import numpy as np
import pandas as pd
import sqlite3
import random
import joblib

import util


if __name__ == "__main__":
	datasets = glob.glob("dataset/*.wav")
	print(datasets, "\n")

	X = []
	label = []

	for data in datasets:
		y, sr = librosa.load(data)

		average_amplitude = util.get_average_amplitude(y)
		zerocross = util.get_zerocross(y)
		melspec_db = util.get_melspec_db(y, sr)
		mfcc = util.get_MFCC(y, sr)
		combined_features = np.concatenate((mfcc, zerocross, melspec_db, [average_amplitude]), axis=0)

		X.append(combined_features)
		label.append(util.get_label(data)[1] + random.uniform(-1, 1))


	from sklearn.ensemble import RandomForestRegressor

	from sklearn.model_selection import train_test_split
	from sklearn.metrics import mean_squared_error, r2_score

	best = 5

	X_train, X_test, y_train, y_test = train_test_split(X, label, test_size=0.1, random_state=9)

	# randonforest
	model = RandomForestRegressor(n_estimators=100)
	model.fit(X_train, y_train)

	y_pred = model.predict(X_test)
	mse = mean_squared_error(y_test, y_pred)
	r2 = r2_score(y_test, y_pred)
	print(f"GB Accuracy: {mse}, {r2}")


	joblib.dump(model, 'random_forest.joblib')



	import matplotlib.pyplot as plt

	# テストデータのインデックスを使って可視化
	plt.scatter(range(len(y_test)), y_test, color='blue', label='Actual')
	plt.scatter(range(len(y_test)), y_pred, color='red', label='Predicted')

	plt.title('Actual vs Predicted')
	plt.xlabel('Data Point')
	plt.ylabel('Target Value')
	plt.legend()
	plt.show()