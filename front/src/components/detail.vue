<template>
  <div id="detail">
    <div>
      <el-card class="box-card">
        <template #header>
          <span>🎉课堂情况分析</span>
        </template>
        <p>频道➡️{{ user.channel }}</p>
        <!--<p>授课教师➡️{{ user.uname }}</p>-->
        <p>上课时间➡️{{ startTime }}</p>
        <p>下课时间➡️{{ endTime }}</p>
      </el-card>
    </div>

    <div id="main" style="width: 600px;height:400px;"></div>

    <el-card class="box-card" v-if="!user.role">
      <template #header>
        <span>✅以下同学表现较好</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="4" v-for="user in allUserData" :key="user.uname">
          <el-avatar :size="70" shape="square" v-if="user.value>=60" @mouseenter="showUserData($event)"
                     @mouseleave="deleteUserData"
                     :id="user.uname">
            {{ user.uname }}
          </el-avatar>
        </el-col>
      </el-row>
    </el-card>
    <el-card class="box-card" v-if="!user.role">
      <template #header>
        <span>⚠️以下同学还需努力</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="4" v-for="user in allUserData" :key="user.uname">
          <el-avatar :size="70" shape="square" v-if="user.value<60">{{ user.uname }}</el-avatar>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script>
import * as echarts from "echarts";
import {host} from "@/properties";

export default {
  name: "detail",
  props: ["appUser"],
  components: [],
  data() {
    return {
      user: this.appUser,
      allData: [],
      allUserData: [],
      userData: [],
      startTime: '',
      endTime: ''
    }
  },
  methods: {
    createChart(dataX, dataY, headText, ElementId) {
      let myChart = echarts.init(document.getElementById(ElementId));

      // 指定图表的配置项和数据
      let option = {
        title: {
          text: headText
        },
        xAxis: {
          type: 'category',
          data: dataX
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            data: dataY,
            type: 'line',
            smooth: true
          }
        ]
      };

      // 使用刚指定的配置项和数据显示图表。
      myChart.setOption(option);
    },
    async getData() {
      await fetch(host + '/getAllUserData', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          channel: this.user.channel
        })
      }).then(res => res.json())
          .then(data => {
            this.allData = data;
            let time = new Date(this.allData[0].startTime);
            let Y = time.getFullYear() + '-';
            let M = time.getMonth() + 1 + '-';
            let D = time.getDate() + ' ';
            let h = time.getHours() + ':';
            let m = time.getMinutes() + ':';
            let s = time.getSeconds();
            this.startTime = Y + M + D + h + m + s;
            time = new Date(this.allData[0].endTime);
            Y = time.getFullYear() + '-';
            M = time.getMonth() + 1 + '-';
            D = time.getDate() + ' ';
            h = time.getHours() + ':';
            m = time.getMinutes() + ':';
            s = time.getSeconds();
            this.endTime = Y + M + D + h + m + s;
          })

      if (this.user.role) {
        fetch(host + '/getUserData', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            channel: this.user.channel,
            uname: this.user.uname
          })
        }).then(res => res.text()).then(data => {
          this.userData = data.split(',');
          let dataX = [];
          let dataY = [];
          for (let i = 0; i < this.userData.length; i++) {
            dataX.push(i);
            dataY.push(this.userData[i]);
          }
          this.createChart(dataX, dataY, '个人课堂曲线图', 'main');
        })
      } else {
        let dataX = [];
        let dataY = this.allData[0].value.split(',');
        dataY.shift();
        dataY.shift();
        for (let i = 0; i < this.userData.length; i++) {
          dataX.push(i);
        }
        this.createChart(dataX, dataY, '课堂整体曲线图', 'main');
        for (let i = 1; i < this.allData.length; i++) {
          let user = {
            uname: this.allData[i].uname,
            value: 0
          }
          let values = this.allData[i].value.split(',');
          let sum = 0;
          let count = 0;
          for (let i = 0; i < values.length; i++) {
            if (parseInt(values[i]) > 0) {
              sum += parseInt(values[i]);
              count++;
            }
          }
          user.value = sum / count;
          this.allUserData.push(user);
        }
      }
    },
    showUserData(data) {
      let userId = data.currentTarget.id
      let div = document.createElement('div');
      div.id = 'table';
      div.style.width = '600px';
      div.style.height = '400px';
      div.style.position = 'absolute';
      div.style.top = '100px';
      div.style.left = '50px';
      document.getElementById('detail').appendChild(div);

      fetch(host + '/getUserData', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          channel: this.user.channel,
          uname: userId
        })
      }).then(res => res.text()).then(data => {
        this.userData = data.split(',');
        let dataX = [];
        let dataY = [];
        for (let i = 0; i < this.userData.length; i++) {
          dataX.push(i);
          dataY.push(this.userData[i]);
        }
        this.createChart(dataX, dataY, '   ' + userId, 'table');
      })
    },
    deleteUserData() {
      const table = document.getElementById('table');
      table.remove();
    }
  },
  created() {
    this.getData();
  },
  mounted() {
  },
  watch: {
    appUser: function (val) {
      this.user = val;
    }
  }
}
</script>

<style scoped>
#detail {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
}

#detail > div {
  margin: 30px;
}

.text {
  font-size: 14px;
}

.item {
  padding: 18px 0;
}

.el-card {
  width: 600px;
}

.el-card span {
  font-size: x-large;
  margin: 0px;
}

.el-card p {
  font-size: larger;
}
</style>