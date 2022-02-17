<template>
  <div id="study">
    <el-container>
      <el-main>Main</el-main>
      <el-aside>
        <video id="v"></video>
      </el-aside>
    </el-container>
  </div>
</template>

<script>

export default {
  name: "study",
  components: {},
  mounted() {
    // 调用摄像头
    // 老的浏览器可能根本没有实现 mediaDevices，所以我们可以先设置一个空的对象
    if (navigator.mediaDevices === undefined) {
      navigator.mediaDevices = {};
    }
    if (navigator.mediaDevices.getUserMedia === undefined) {
      navigator.mediaDevices.getUserMedia = function (constraints) {
        // 首先，如果有getUserMedia的话，就获得它
        var getUserMedia = navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;

        // 一些浏览器根本没实现它 - 那么就返回一个error到promise的reject来保持一个统一的接口
        if (!getUserMedia) {
          return Promise.reject(new Error('getUserMedia is not implemented in this browser'));
        }

        // 否则，为老的navigator.getUserMedia方法包裹一个Promise
        return new Promise(function (resolve, reject) {
          getUserMedia.call(navigator, constraints, resolve, reject);
        });
      }
    }
    const constraints = {
      video: true,
      audio: false
    };
    let promise = navigator.mediaDevices.getUserMedia(constraints);
    promise.then(stream => {
      let v = document.getElementById('v');
      // 旧的浏览器可能没有srcObject
      if ("srcObject" in v) {
        v.srcObject = stream;
      } else {
        // 防止再新的浏览器里使用它，因为它已经不再支持了
        v.src = window.URL.createObjectURL(stream);
      }
      v.onloadedmetadata = function () {
        v.play();
      };
    }).catch(err => {
      console.error(err.name + ": " + err.message);
    })
  }
}
</script>

<style scoped>
#study {
  flex: 1;
}

.el-container {
  height: 100%;
}

.el-aside {
  background-color: #d3dce6;
  text-align: center;
  line-height: 60px;
  width: 20%;
  height: 100%;
}

.el-main {
  background-color: #e9eef3;
  text-align: center;
  line-height: 60px;
  padding: 0px;
}

video {
  width: 100%;
}
</style>