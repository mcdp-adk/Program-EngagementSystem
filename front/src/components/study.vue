<template>
  <div id="study">
    <el-container>
      <el-main>
        <agora @receiveAttention="setAttention" :study-user="user"/>
      </el-main>
      <el-aside>
        <video id="v"></video>

        <!--        <el-card v-if="!user.role" class="box-card">-->
        <!--          <template #header>-->
        <!--            <span>✅班级表现评分</span>-->
        <!--          </template>-->
        <!--          <p>80</p>-->
        <!--        </el-card>-->
        <!--        <el-card v-if="!user.role" class="box-card">-->
        <!--          <template #header>-->
        <!--            <span>⚠️表现较差的学生</span>-->
        <!--          </template>-->
        <!--          <p>李华</p>-->
        <!--        </el-card>-->

        <el-card v-if="!user.role" class="box-card">
          <div id="allAttention" style="height:400px;"/>
        </el-card>
        <el-card v-if="user.role" class="box-card">
          <div id="studentAttention" style="height:400px;"/>
        </el-card>
      </el-aside>
    </el-container>
  </div>
</template>

<script>
import agora from "@/components/agora";
import * as echarts from 'echarts';
import {host} from "@/properties";

export default {
  name: "study",
  props: ["appUser"],
  components: {
    agora
  },
  data() {
    return {
      user: this.appUser,
      attention: [],
      AttentionChart: null,
      option: {}
    }
  },
  methods: {
    startCamera() {
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
    },
    setAttention(data) {
      if (this.attention.length >= 5) {
        this.attention.shift();
      }
      this.attention.push(data);
      this.option = {
        tooltip: {
          formatter: '{a} <br/>{b} : {c}%'
        },
        series: [
          {
            name: 'Pressure',
            type: 'gauge',
            progress: {
              show: true
            },
            detail: {
              valueAnimation: true,
              formatter: '{value}'
            },
            data: [
              {
                value: (this.getAvgAttention() + 1) * 25,
                name: '即时专注度'
              }
            ]
          }
        ]
      };
      this.AttentionChart.setOption(this.option);
    },
    createStudentAttention() {
      this.AttentionChart = echarts.init(document.getElementById('studentAttention'));
      this.option = {
        tooltip: {
          formatter: '{a} <br/>{b} : {c}%'
        },
        series: [
          {
            name: 'Pressure',
            type: 'gauge',
            progress: {
              show: true
            },
            detail: {
              valueAnimation: true,
              formatter: '{value}'
            },
            data: [
              {
                value: (this.getAvgAttention() + 1) * 25,
                name: '即时专注度'
              }
            ]
          }
        ]
      };
      this.AttentionChart.setOption(this.option);
    },
    createAllAttention() {
      this.AttentionChart = echarts.init(document.getElementById('allAttention'));
      let xhr = new XMLHttpRequest();
      let thisOption = this.option;
      let thisAttentionChart = this.AttentionChart;
      xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
          thisOption = {
            tooltip: {
              formatter: '{a} <br/>{b} : {c}%'
            },
            series: [
              {
                name: 'Pressure',
                type: 'gauge',
                progress: {
                  show: true
                },
                detail: {
                  valueAnimation: true,
                  formatter: '{value}'
                },
                data: [
                  {
                    value: parseInt(xhr.responseText),
                    name: '即时专注度'
                  }
                ]
              }
            ]
          };
          thisAttentionChart.setOption(thisOption);
        }
      }
      xhr.open('post', host + '/getNow', true);
      xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
      xhr.send('channel=' + this.user.channel);
      console.log(thisOption);
      console.log(thisAttentionChart);
    },
    getAvgAttention() {
      let sum = 0;
      for (let i = 0; i < this.attention.length; i++) {
        sum += this.attention[i];
      }
      return sum / this.attention.length;
    }
  },
  mounted() {
    // 调用摄像头
    this.startCamera();
    if (this.user.role) {
      // 创建学生表现图
      this.createStudentAttention();
    } else {
      // 创建学生表现图
      setInterval(this.createAllAttention, 5000);
    }
  },
  watch: {
    appUser(val) {
      this.user = val;
    }
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

.el-card {
  margin: 20px;
}

.el-card span {
  font-size: x-large;
  margin: 0px;
}

.el-card p {
  font-size: xx-large;
}
</style>