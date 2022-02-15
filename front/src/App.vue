<template>
  <!--  <img alt="Vue logo" src="./assets/logo.png">-->
  <!--  <HelloWorld msg="Welcome to Your Vue.js App"/>-->

  <study/>
</template>

<script>
import study from "@/components/study";

export default {
  name: 'App',
  components: {
    study
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
}
</style>