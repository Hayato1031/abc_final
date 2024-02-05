import glob
import librosa
import os
import numpy as np
import pandas as pd
import sqlite3
import random
import joblib

import util
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score

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
        label.append(util.get_label(data)[1])

    # データをNumPy配列に変換
    X = np.array(X)
    label = np.array(label)

    # データの分割
    X_train, X_test, y_train, y_test = train_test_split(X, label, test_size=0.25, random_state=9)

    # ハイパーパラメータの範囲を指定
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20]
    }

    # グリッドサーチを使用して最適なハイパーパラメータを見つける
    grid_search = GridSearchCV(RandomForestRegressor(), param_grid, cv=5, scoring='neg_mean_squared_error')
    grid_search.fit(X_train, y_train)

    # 最適なモデルを取得
    best_model = grid_search.best_estimator_

    # テストデータで評価
    y_pred = best_model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"Best Model Accuracy: MES={mse}, R2={r2}")

    # モデルの保存
    joblib.dump(best_model, 'best_random_forest.joblib')

    # 可視化
    import matplotlib.pyplot as plt

    # テストデータのインデックスを使って可視化
    plt.scatter(range(len(y_test)), y_test, color='blue', label='Actual')
    plt.scatter(range(len(y_test)), y_pred, color='red', label='Predicted')

    plt.title('Actual vs Predicted')
    plt.xlabel('Data Point')
    plt.ylabel('Target Value')
    plt.legend()
    plt.show()
