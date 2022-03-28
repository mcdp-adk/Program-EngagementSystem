<template>
  <div id="agora">
    <div id="video"/>
    <div id="controller">
      <el-row justify="center">
        <el-col :span="2">
          <el-button @click="joinButton" v-if="user.role" id="join">加入频道</el-button>
        </el-col>
        <el-col :span="2">
          <el-button @click="shareButton" v-if="!user.role" id="share">共享屏幕</el-button>
        </el-col>
        <el-col :span="2">
          <el-button @click="stopButton" v-if="!user.role" id="stop">停止共享</el-button>
        </el-col>
        <el-col :span="2">
          <el-button @click="leaveButton" id="leave">离开频道</el-button>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import AgoraRTC from "agora-rtc-sdk-ng"
import {host} from "@/properties";

let rtc = {
  // For the local audio and video tracks.
  localAudioTrack: null,
  localVideoTrack: null,
  client: null
};

let options = {
  // Pass your app ID here.
  appId: "8aaf87961df2495d97f7497e553e8817",
  // Set the channel name.
  channel: "",
  // Set the user role in the channel.
  role: "audience",
  // Use a temp token
  token: "",
  // Uid
  uid: 123456
};

let clientRoleOptions = {
  // Set latency level to low latency
  level: 1
}

async function startBasicLiveStreaming() {
  rtc.client = AgoraRTC.createClient({mode: "live", codec: "vp8"});

  rtc.client.on("user-published", async (user, mediaType) => {
    // Subscribe to a remote user.
    await rtc.client.subscribe(user, mediaType);
    console.log("subscribe success");

    // If the subscribed track is video.
    if (mediaType === "video") {
      // Get `RemoteVideoTrack` in the `user` object.
      const remoteVideoTrack = user.videoTrack;
      // Dynamically create a container in the form of a DIV element for playing the remote video track.
      const remotePlayerContainer = document.createElement("div");
      // Specify the ID of the DIV container. You can use the `uid` of the remote user.
      remotePlayerContainer.id = user.uid.toString();
      remotePlayerContainer.style.width = "100%";
      remotePlayerContainer.style.height = "100%";
      document.getElementById("video").append(remotePlayerContainer);

      // Play the remote video track.
      // Pass the DIV container and the SDK dynamically creates a player in the container for playing the remote video track.
      remoteVideoTrack.play(remotePlayerContainer);

      // Or just pass the ID of the DIV container.
      // remoteVideoTrack.play(playerContainer.id);
    }

    // If the subscribed track is audio.
    if (mediaType === "audio") {
      // Get `RemoteAudioTrack` in the `user` object.
      const remoteAudioTrack = user.audioTrack;
      // Play the audio track. No need to pass any DOM element.
      remoteAudioTrack.play();
    }
  });

  rtc.client.on("user-unpublished", user => {
    // Get the dynamically created DIV container.
    const remotePlayerContainer = document.getElementById(user.uid);
    // Destroy the container.
    remotePlayerContainer.remove();
  });
}

export default {
  name: "agora",
  props: ["studyUser"],
  data() {
    return {
      user: this.studyUser,
      sendingValue: null
    }
  },
  methods: {
    async joinButton() {
      rtc.client.setClientRole(options.role, clientRoleOptions);
      rtc.client.join(options.appId, options.channel, options.token);
      this.sendingValue = setInterval(() => {
        let valueANDtime = this.user;
        window.eel.getNowAttention()().then(result => {
          valueANDtime.value = result;
        })
        valueANDtime.time = new Date().getTime();

        console.log(valueANDtime);

        let xhr = new XMLHttpRequest();
        xhr.open('post', host + '/users/insert');
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.send("uname=" + this.user.uname + "&channel=" + this.user.channel + "&role=" + this.user.role + "&timestamp=" + valueANDtime.time + "&value=" + valueANDtime.value);
      }, 5000);
    },
    async shareButton() {
      await rtc.client.setClientRole("host");
      await rtc.client.join(options.appId, options.channel, options.token);
      AgoraRTC.createScreenVideoTrack({
        withAudio: "enable"
      }).then((ILocalVideoTrack, ILocalAudioTrack) => {
        rtc.localVideoTrack = ILocalVideoTrack;
        rtc.localAudioTrack = ILocalAudioTrack;
        rtc.client.publish(rtc.localVideoTrack, rtc.localAudioTrack);

        const playerContainer = document.createElement("div");
        playerContainer.id = options.uid.toString();
        playerContainer.style.width = "100%";
        playerContainer.style.height = "100%";
        document.getElementById("video").append(playerContainer);
        rtc.localVideoTrack.play(playerContainer);
      });
    },
    async stopButton() {
      this.stopShare();
    },
    async leaveButton() {
      clearInterval(this.sendingValue);
      this.stopShare();

      // Traverse all remote users.
      rtc.client.remoteUsers.forEach(user => {
        // Destroy the dynamically created DIV containers.
        const remoteContainer = document.getElementById(user.uid);
        remoteContainer.remove();
      });

      // Leave the channel.
      await rtc.client.leave();
    },
    stopShare() {
      if (document.getElementById(options.uid)) {
        if (rtc.localVideoTrack) rtc.localVideoTrack.close();
        if (rtc.localAudioTrack) rtc.localAudioTrack.close();
        const playerContainer = document.getElementById(options.uid);
        playerContainer.remove();
      }
    }
  },
  mounted() {
    startBasicLiveStreaming();
    options.channel = this.user.channel;
    options.token = this.user.token;
  },
  watch: {
    studyUser: function (val) {
      this.user = val;
      options.channel = this.user.channel;
      options.token = this.user.token;
    }
  }
}
</script>

<style scoped>
#agora {
  height: 100%;
  display: flex;
  flex-direction: column;
}

#video {
  background-color: #ffffff;
  height: 100%;
  width: 100%;
}

#controller {
  background-color: #2c3e50;
  margin-top: auto;
  height: 75px;
}
</style>