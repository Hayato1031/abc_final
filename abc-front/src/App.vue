<script setup>
import { ref, reactive, watch } from "vue"


const record = reactive({state: false});
const audioPlayer = ref(); //<audio>タグを取得
let recorder = null; //MediaRecorderに使う変数を宣言
let chunks = []; //録音のblobを挿入する配列
let recordingTimer;

let host = "http://localhost:8000/"
let playlist_input = ref(true)
let playlist_url = ref("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
let playlist_embed = ref("")
let music_urls = ref("")
let url_error = ref(false)
let danceability = ref("")
let music_danceabilities = ref([])


watch(music_urls, async() => {
  let ids = music_urls.value.map((x) => x.replace("https://open.spotify.com/embed/track/", ""))
  const response = await fetch(host + "danceability?music_ids=" + ids, {
      method: 'GET',
  });

  if (response.ok) {
    const responseData = await response.json(); 
    let minfo = responseData["minfo"]
    console.log(minfo)
    parseFloat((minfo[0]["danceability"]*10).toFixed(1));
    music_danceabilities.value = [parseFloat((minfo[0]["danceability"]*10).toFixed(1)), parseFloat((minfo[1]["danceability"]*10).toFixed(1)), parseFloat((minfo[2]["danceability"]*10).toFixed(1))]
  } else {
    console.log("failed")
  } 
})

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
      const convertToWav = (blob) => {
            const reader = new FileReader();

            reader.onload = () => {
                const arrayBuffer = reader.result;
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                audioContext.decodeAudioData(arrayBuffer, async (buffer) => {
                  const wavBlob = await audioBufferToWav(buffer, 11025);
                  const audioURL = window.URL.createObjectURL(wavBlob);

                  // ここで audioURL を使って何かしらの処理を行う
                  await uploadWavFile(wavBlob)
                  audioPlayer.value.src = audioURL;
                  console.log(audioURL);
                });
            };

            reader.readAsArrayBuffer(blob);
      };
      

      convertToWav(blob)
      chunks = [];
    }
  })
  .catch(function (err) {
    console.log('The following getUserMedia error occured: ' + err);
  });

const uploadWavFile = async (wavBlob) => {
  try {
    const fd = new FormData();
    fd.append('file', wavBlob);
    const response = await fetch(host + "get_music?playlist_url=" + playlist_url.value, {
      method: 'POST',
      body: fd,
    });

    if (response.ok) {
      const responseData = await response.json(); // もしくは response.text()
      console.log('WAV file uploaded successfully!', responseData);
      music_urls.value = responseData["music"]
      danceability.value = parseFloat(responseData["danceability"].toFixed(1));
    } else {
      console.error('Failed to upload WAV file.');
    }
  } catch (error) {
    console.error('Error uploading WAV file:', error);
  }
}

const change_playlist_input = () => {
  if (playlist_input.value) {
    if (playlist_url.value.startsWith("https://open.spotify.com/playlist/")) {
      url_error.value = false
      playlist_embed = playlist_url.value.replace("playlist", "embed/playlist")
      playlist_input.value = !playlist_input.value
    } else {
      url_error.value = true
    }
  } else {
    playlist_input.value = !playlist_input.value
  }
}

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


</script>
  
<template>
  <header v-if="!playlist_input">
    <a class="logo-text" @click="change_playlist_input">Spotify Music Search</a>
  </header>
  <div class="container" :class="{'min': !playlist_input}">
    <div class="playlist_input_container" v-if="playlist_input">
      <div class="logo">
        <p class="logo-text">Spotify Music Search</p>
      </div>
      <div class="input_form">
        <input class="playlist_input" type="text" v-model="playlist_url" placeholder="Spotifyプレイリストのurlを貼り付けてね">
        <p class="error" v-if="url_error">https://open.spotify.com/playlist から始まる正しいURLを入力してください</p>
      </div>
      <a  class="btn" @click="change_playlist_input">送信</a>
    </div>
    <div class="menu" v-if="!playlist_input">
      <div class="record-container" v-if="playlist_embed">
        <iframe style="border-radius:12px" :src="playlist_embed" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
        <div class="buttons">
          <a class="reset_playlist btn" @click="change_playlist_input">プレイリストを変更</a>
          <a class="btn record" @click="startRecording()" v-if="!record.state"><span style="font-size: 5rem;">{{ danceability }}</span><font-awesome-icon :icon="['fas', 'microphone-lines']" style="font-size: 5rem;"/></a>
          <a class="btn recording" v-if="record.state">録音中...</a>
        </div>
      </div>
      <div class="recommended_music" v-if="music_urls">
        <p class="text">Recommended Musics</p>
        <div class="musics" v-for="(music_url, i) in music_urls">
          <!-- <p style="font-size: 5rem;">{{ music_danceabilities[i] }}</p> -->
          <iframe :src="music_url" width="100%" height="400px" frameborder="0" allowfullscreen></iframe>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
header{
  text-align: center;
}
.container{
  width: 100vw;
  min-height: 100vh;
  max-width: 1024px;
  margin: 0 auto;
  text-align: center;
}

.min{
  min-height: 50vh;
}

@media (min-width: 1024px) {
  .container {
    display: flex;
    place-items: center;
  }
}

.logo-text{
  font-size: 5rem;
  padding-bottom: 20px;
  font-family: futura;
  cursor: pointer;
}

.text{
  font-size: 4rem;
  margin: 40px 0 10px 0;
  border-bottom: #212529 solid 2px;
}
.record-container{
  display: flex;
  gap: 10px;
}

.playlist_input_container{
  width: 100%;
  display: flex;
  flex-flow: column;
  align-items: center;

}
.input_form{
  margin-bottom: 100px;
}
.playlist_input{
    font-size: 2rem;
    display: block;
    width: 1000px;
    margin: 0 auto;
    border: none;
    border-bottom: rgba(200,200,200,50) solid 1px;
    background-color: rgba(0,0,0,0);
    margin-bottom: 10px;
  }

.error{
  color: red;
}
  .menu{
    display: block;
    flex-grow: 1;
  }

  .buttons{
    display: flex;
    flex-flow: column;
    gap: 10px;
  }

  .btn{
    flex-grow: 1;
    width: 300px;
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

</style>
