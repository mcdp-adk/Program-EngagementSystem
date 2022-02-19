<template>
  <div id="detail">
    <div>
      <el-card class="box-card">
        <div v-for="o in 4" :key="o" class="text item">{{ 'List item ' + o }}</div>
      </el-card>
    </div>
    <div id="main" style="width: 600px;height:400px;"></div>
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
        text: 'ECharts 入门示例'
      },
      tooltip: {},
      legend: {
        data: ['销量']
      },
      xAxis: {
        data: ['衬衫', '羊毛衫', '雪纺衫', '裤子', '高跟鞋', '袜子']
      },
      yAxis: {},
      series: [
        {
          name: '销量',
          type: 'bar',
          data: [5, 20, 36, 10, 10, 20]
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

.box-card {
  width: 480px;
}
</style>