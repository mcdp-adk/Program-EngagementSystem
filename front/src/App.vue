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
      <el-sub-menu>
        <template #title>上课</template>
        <el-menu-item>开始上课</el-menu-item>
        <el-menu-item>结束上课</el-menu-item>
      </el-sub-menu>
      <el-menu-item @click="studyShow=true">学习</el-menu-item>
      <el-menu-item @click="studyShow=false">详细</el-menu-item>
    </el-menu>
  </el-header>

  <study v-if="studyShow"/>
  <detail v-if="!studyShow"/>
</template>

<script>
import study from "@/components/study";
import detail from "@/components/detail";

export default {
  name: 'App',
  components: {
    study,
    detail
  },
  data() {
    return {
      studyShow: true
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