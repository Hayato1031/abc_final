import requests

import constatns
import logging
import sys

url ='https://api.webempath.net/v2/analyzeWav'

payload = {'apikey': constatns.EMPATH_API_KEY}

async def get_emotion_from_wav(wav_file):
	logger = logging.getLogger(__name__)
	handler = logging.StreamHandler(sys.stdout)    
	logger.addHandler(handler)
	logger.setLevel(logging.DEBUG)

	try:
		file_bytes = await wav_file.read()
		file = {'wav': file_bytes}
		res = requests.post(url, params=payload, files=file).json()
	except Exception as e:
		logger.info(e)
		raise Exception("Reading File Failed...")
		
	return res


# PCM WAVE形式　16bit
# データサイズが1.9MB以下
# PCM_FLOAT、PCM_SIGNED、PCM_UNSIGNEDのいずれかのフォーマット
# 録音時間が5.0秒未満
# サンプリング周波数が11025Hz
# チャンネル数が1（モノラル）
