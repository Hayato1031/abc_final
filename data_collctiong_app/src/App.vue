<script setup>
import { ref, reactive, watch, onMounted } from "vue"


const record = reactive({state: false});
const audioPlayer = ref(); //<audio>タグを取得
let recorder = null; //MediaRecorderに使う変数を宣言
let chunks = []; //録音のblobを挿入する配列
let recordingTimer;
let dataTimer;

let dataTImer_running = ref(false)
let label = ref("danceability")
let power = ref("10")

navigator.mediaDevices.getUserMedia({ audio: true })
  .then(function (stream) {
    recorder = new MediaRecorder(stream);          
    recorder.ondataavailable = (e) => {
      chunks.push(e.data);
    }

    recorder.onstart = () => {
        console.log('started');
    }

    recorder.onstop = () => {
      const blob = new Blob(chunks, { 'type': "audio/wav" });
      convertToWav(blob)
      chunks = [];
    }
  })
  .catch(function (err) {
    console.log('The following getUserMedia error occured: ' + err);
  });

const convertToWav = (blob) => {
            const reader = new FileReader();

            reader.onload = () => {
                const arrayBuffer = reader.result;
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                audioContext.decodeAudioData(arrayBuffer, async (buffer) => {
                  const wavBlob = await audioBufferToWav(buffer, 11025);
                  const audioURL = window.URL.createObjectURL(wavBlob);
                  // ここで audioURL を使って何かしらの処理を行う

                  audioPlayer.value.src = audioURL;

                  //aタグを生成
                  const downloadLink = document.createElement('a');
                  downloadLink.href = audioURL;
                  const uuid = Math.floor(new Date() / 1000);
                  downloadLink.download = label.value + power.value + "_" + String(uuid) + '.wav'; 
                  downloadLink.style.display = 'none';
                  document.body.appendChild(downloadLink);
                  
                  // リンクをクリックしてダウンロードを開始
                  downloadLink.click();

                  // リンクを削除
                  document.body.removeChild(downloadLink);
                  console.log(audioURL);
                });
            };

            reader.readAsArrayBuffer(blob);
      };

const startRecording = () => {
  record.state = true;
  recorder.start();
  recordingTimer = setTimeout(() => {
        console.log("stop")
        stopRecording();
      }, 5000);
}

const stopRecording = () => {
  record.state = false;
  recorder.stop();
  clearTimeout(recordingTimer);
}

async function audioBufferToWav(buffer, targetSampleRate) {
  const numChannels = buffer.numberOfChannels;
  const originalSampleRate = buffer.sampleRate;
  const length = buffer.length * (targetSampleRate / originalSampleRate);

  // OfflineAudioContextを作成してリサンプリングを行う
  const offlineContext = new OfflineAudioContext(numChannels, length, targetSampleRate);
  const source = offlineContext.createBufferSource();
  source.buffer = buffer;

  source.connect(offlineContext.destination);
  source.start();

  return new Promise((resolve) => {
    offlineContext.oncomplete = (e) => {
      const resampledBuffer = e.renderedBuffer;
      const wavBlob = bufferToWavBlob(resampledBuffer, targetSampleRate);
      resolve(wavBlob);
    };

    offlineContext.startRendering();
  });
}

function bufferToWavBlob(buffer, sampleRate) {
  const numChannels = buffer.numberOfChannels;
  const bitDepth = 16;

  const length = buffer.length * numChannels * bitDepth / 8;
  const data = new DataView(new ArrayBuffer(length));

  let offset = 0;

  for (let channel = 0; channel < numChannels; channel++) {
    const channelData = buffer.getChannelData(channel);
    for (let i = 0; i < channelData.length; i++, offset += 2) {
      const sample = Math.max(-1, Math.min(1, channelData[i]));
      data.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
    }
  }

  const wavBuffer = new ArrayBuffer(44 + length);
  const wavData = new DataView(wavBuffer);

  // WAV ヘッダ
  wavData.setUint8(0, 'R'.charCodeAt(0));
  wavData.setUint8(1, 'I'.charCodeAt(0));
  wavData.setUint8(2, 'F'.charCodeAt(0));
  wavData.setUint8(3, 'F'.charCodeAt(0));
  wavData.setUint32(4, 36 + length, true);
  wavData.setUint8(8, 'W'.charCodeAt(0));
  wavData.setUint8(9, 'A'.charCodeAt(0));
  wavData.setUint8(10, 'V'.charCodeAt(0));
  wavData.setUint8(11, 'E'.charCodeAt(0));
  wavData.setUint8(12, 'f'.charCodeAt(0));
  wavData.setUint8(13, 'm'.charCodeAt(0));
  wavData.setUint8(14, 't'.charCodeAt(0));
  wavData.setUint8(15, ' '.charCodeAt(0));
  wavData.setUint32(16, 16, true);
  wavData.setUint16(20, 1, true);  // PCMフォーマット
  wavData.setUint16(22, numChannels, true);
  wavData.setUint32(24, sampleRate, true);
  wavData.setUint32(28, sampleRate * numChannels * bitDepth / 8, true);
  wavData.setUint16(32, numChannels * bitDepth / 8, true);
  wavData.setUint16(34, bitDepth, true);
  wavData.setUint8(36, 'd'.charCodeAt(0));
  wavData.setUint8(37, 'a'.charCodeAt(0));
  wavData.setUint8(38, 't'.charCodeAt(0));
  wavData.setUint8(39, 'a'.charCodeAt(0));
  wavData.setUint32(40, length, true);

  // 音声データ
  new Uint8Array(wavBuffer, 44).set(new Uint8Array(data.buffer));

  return new Blob([wavBuffer], { type: 'audio/wav' });
}

const collect_data = () => {
  const click_button = () => {
    var button = document.getElementById('record_button');
    button.click();
  }
  
  dataTimer = setInterval(click_button, 6000);
  dataTImer_running.value = true
}

const stop_collect_data = () => {
  clearInterval(dataTimer);
  dataTImer_running.value = false
}

</script>
  
<template>
  <div class="buttons">
    <a class="btn record" v-if="!dataTImer_running" @click="collect_data">データ連続取得開始</a>
    <a class="btn recording" v-if="dataTImer_running" @click="stop_collect_data">データ連続取得終了</a>
    <a class="btn record" id="record_button" @click="startRecording()" v-if="!record.state"><font-awesome-icon :icon="['fas', 'microphone-lines']" style="font-size: 5rem;"/></a>
    <a class="btn recording" v-if="record.state">録音中...</a>
    <article class="clip">
      <audio ref="audioPlayer" controls></audio>
    </article>
  </div>
  <div class="selects">
    <div class="select">
      <select v-model="label">
        <option value="danceability">danceability</option>
        <option value="energy">energy</option>
        <option value="valence">valence</option>
      </select>
    </div>
    <div class="select">
      <select v-model="power">
        <option value="10">High</option>
        <option value="5">Middle</option>
        <option value="1">Low</option>
      </select>
    </div>
  </div>
</template>

<style scoped>
  .buttons{
    display: flex;
    align-items: center;
    justify-content:center;
    flex-flow: column;
    gap: 10px;
  }

  .btn{
    flex-grow: 1;
    width: 400px;
    background-color: #20D760;
    border-bottom: 5px solid #016d27;
    font-size: 1.6rem;
    display: flex;
    justify-content: center; /*左右中央揃え*/
    align-items: center; 
    padding: 1rem 4rem;
    cursor: pointer;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
    -webkit-transition: all 0.3s;
    transition: all 0.3s;
    text-align: center;
    vertical-align: middle;
    text-decoration: none;
    letter-spacing: 0.1em;
    color: #212529;
    border-radius: 0.5rem;
  }
  .btn:hover{
    margin-top: 3px;
    border-bottom: 2px solid #20D760;
  }

  .recording{
    margin-top: 3px;
    border-bottom: 2px solid #20D760;
  }
  .selects{
    display: flex;
    gap: 10px;
    width: 400px;
  }
  .select {
	overflow: hidden;
	width: 90%;
	margin: 10px auto;
	text-align: center;
  flex-grow: 1;
}
.select select {
	width: 100%;
	padding-right: 1em;
	cursor: pointer;
	text-indent: 0.01px;
	text-overflow: ellipsis;
	border: none;
	outline: none;
	background: transparent;
	background-image: none;
	box-shadow: none;
	-webkit-appearance: none;
	appearance: none;
}
.select select::-ms-expand {
    display: none;
}
.select {
	position: relative;
	border: 1px solid #bbbbbb;
	border-radius: 2px;
	background: #ffffff;
}
.select::before {
	position: absolute;
	top: 0.8em;
	right: 0.9em;
	width: 0;
	height: 0;
	padding: 0;
	content: '';
	border-left: 6px solid transparent;
	border-right: 6px solid transparent;
	border-top: 6px solid #666666;
	pointer-events: none;
}
.select select {
	padding: 8px 38px 8px 8px;
	color: #666666;
}

</style>
