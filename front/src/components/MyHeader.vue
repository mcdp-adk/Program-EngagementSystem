<template>
  <el-header>
    <el-menu
        :default-active="activeIndex2"
        class="el-menu-demo"
        mode="horizontal"
        background-color="#545c64"
        text-color="#fff"
        active-text-color="#ffd04b"
        @select="handleSelect"
    >
      <el-sub-menu>
        <template #title>上课</template>
        <el-menu-item>开始上课</el-menu-item>
        <el-menu-item>结束上课</el-menu-item>
      </el-sub-menu>
      <el-menu-item>详细</el-menu-item>
    </el-menu>
  </el-header>
</template>

<script>
export default {
  name: "MyHeader"
}
</script>

<style scoped>

</style>