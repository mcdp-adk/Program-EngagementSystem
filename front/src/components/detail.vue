<template>
  <div id="detail">
    <div>
      <el-card class="box-card">
        <template #header>
          <span>🎉课堂情况分析</span>
        </template>
        <p>课程名称➡️2022 级大物</p>
        <p>授课教师➡️李洋</p>
        <p>上课时间➡️17:49:12</p>
      </el-card>
    </div>
    <div id="main" style="width: 600px;height:400px;"></div>
    <el-card class="box-card">
      <template #header>
        <span>✅以下同学表现较好</span>
      </template>
      <p>👦张三</p>
      <p>👧李四</p>
    </el-card>
    <el-card class="box-card">
      <template #header>
        <span>⚠️以下同学还需努力</span>
      </template>
      <p>👦李华</p>
    </el-card>
  </div>
</template>

<script>
import * as echarts from "echarts";

export default {
  name: "detail",
  components: {},
  mounted() {
    var myChart = echarts.init(document.getElementById('main'));

    // 指定图表的配置项和数据
    var option = {
      title: {
        text: '课堂整体专注度曲线'
      },
      xAxis: {
        type: 'category',
        data: ['0', '5', '10', '15', '20', '25', '30', '35', '40']
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          data: [40, 50, 80, 95, 75, 60, 90, 85, 80],
          type: 'line',
          smooth: true
        }
      ]
    };

    // 使用刚指定的配置项和数据显示图表。
    myChart.setOption(option);
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