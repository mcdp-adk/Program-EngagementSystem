<template>
  <div id="agora">
    <div id="video"/>
    <div id="controller">
      <el-row justify="center">
        <el-col :span="2">
          <el-button id="join">加入频道</el-button>
        </el-col>
        <el-col :span="2">
          <el-button id="share">共享屏幕</el-button>
        </el-col>
        <el-col :span="2">
          <el-button id="leave">离开频道</el-button>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import AgoraRTC from "agora-rtc-sdk-ng"

let rtc = {
  // For the local audio and video tracks.
  localAudioTrack: null,
  localVideoTrack: null,
  localMicrophoneTrack: null,
  client: null
};

let options = {
  // Pass your app ID here.
  appId: "8aaf87961df2495d97f7497e553e8817",
  // Set the channel name.
  channel: "test",
  // Set the user role in the channel.
  role: "audience",
  // Use a temp token
  token: "0068aaf87961df2495d97f7497e553e8817IADaN/s1imbL3N8CZ1cGWqZv+K2SwTR4zZyxczuWfTm18Qx+f9gAAAAAEAAn2yw6rJgYYgEAAQCmmBhi",
};

let clientRoleOptions = {
  // Set latency level to low latency
  level: 1
}

async function startBasicLiveStreaming() {

  rtc.client = AgoraRTC.createClient({mode: "live", codec: "vp8"});

  window.onload = function () {

    document.getElementById("join").onclick = async function () {
      rtc.client.setClientRole(options.role, clientRoleOptions);
      await rtc.client.join(options.appId, options.channel, options.token);
    }

    document.getElementById("leave").onclick = async function () {
      // Traverse all remote users.
      rtc.client.remoteUsers.forEach(user => {
        // Destroy the dynamically created DIV containers.
        const playerContainer = document.getElementById(user.uid);
        playerContainer && playerContainer.remove();
      });

      // Leave the channel.
      await rtc.client.unpublish();
      await rtc.client.leave();
    }
  }

  document.getElementById("share").onclick = async function () {
    await rtc.client.setClientRole("host");
    await rtc.client.join(options.appId, options.channel, options.token);
    AgoraRTC.createScreenVideoTrack({
      withAudio: "enable"
    }).then((ILocalVideoTrack, ILocalAudioTrack) => {
      rtc.localVideoTrack = ILocalVideoTrack;
      rtc.localAudioTrack = ILocalAudioTrack;
      rtc.client.publish(rtc.localVideoTrack, rtc.localAudioTrack);

      const PlayerContainer = document.getElementById("video");
      rtc.localVideoTrack.play(PlayerContainer);
    });
  }

  rtc.client.on("user-published", async (user, mediaType) => {
    // Subscribe to a remote user.
    await rtc.client.subscribe(user, mediaType);
    console.log("subscribe success");

    // If the subscribed track is video.
    if (mediaType === "video") {
      // Get `RemoteVideoTrack` in the `user` object.
      const remoteVideoTrack = user.videoTrack;
      // Dynamically create a container in the form of a DIV element for playing the remote video track.
      const remotePlayerContainer = document.getElementById("video");
      // Specify the ID of the DIV container. You can use the `uid` of the remote user.
      // remotePlayerContainer.id = user.uid.toString();
      // remotePlayerContainer.textContent = "Remote user " + user.uid.toString();
      // remotePlayerContainer.style.width = "640px";
      // remotePlayerContainer.style.height = "480px";
      // document.body.append(remotePlayerContainer);

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

  rtc.client.on("user-unpublished", () => {
    // Get the dynamically created DIV container.
    const remotePlayerContainer = document.getElementById("video");
    // Destroy the container.
    remotePlayerContainer.remove();
  });
}

export default {
  name: "agora",
  mounted() {
    startBasicLiveStreaming()
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
  background-color: #42b983;
  height: 100%;
  width: 100%;
}

#controller {
  background-color: #2c3e50;
  margin-top: auto;
  height: 75px;
}
</style>