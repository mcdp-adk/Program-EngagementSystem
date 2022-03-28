<template>
  <!--  <img alt="Vue logo" src="./assets/logo.png">-->
  <!--  <HelloWorld msg="Welcome to Your Vue.js App"/>-->

  <!-- 导航栏 -->
  <el-header>
    <el-menu
        :default-active="activeIndex2"
        class="el-menu-demo"
        mode="horizontal"
        background-color="#545c64"
        text-color="#fff"
        active-text-color="#fff"
        @select="handleSelect"
    >
      <el-menu-item @click="userShow=true,studyShow=false,detailShow=false">设置</el-menu-item>
      <el-menu-item @click="studyShow=true,userShow=false,detailShow=false">学习</el-menu-item>
      <el-menu-item @click="detailShow=true,userShow=false,studyShow=false">详细</el-menu-item>
      <el-menu-item @click="test01">测试</el-menu-item>
    </el-menu>
  </el-header>

  <user @receiveData="setData" v-if="userShow"/>
  <study :app-user="user" v-if="studyShow"/>
  <detail :app-user="user" v-if="detailShow"/>
</template>

<script>
import user from "@/components/user";
import study from "@/components/study";
import detail from "@/components/detail";

export default {
  name: 'App',
  components: {
    user,
    study,
    detail
  },
  data() {
    return {
      userShow: true,
      studyShow: false,
      detailShow: false,
      user: {}
    }
  },
  methods: {
    setData(data) {
      this.user = data;
    },
    test01() {
      window.eel.getNowAttention()().then(result => {
        console.log(result);
      })
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;

  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;

  display: flex;
  flex-direction: column;
}

.el-header {
  background-color: #b3c0d1;
  text-align: center;
  padding: 0px;
  border: 0px;
}
</style>