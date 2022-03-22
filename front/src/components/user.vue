<template>
  <el-row justify="center">
    <el-col :span="8">
      <el-card class="box-card">
        <span>Name：</span>
        <el-input v-model="user.uname" placeholder="Your name"/>
        <br>
        <span>Channel：</span>
        <el-input v-model="user.channel" placeholder="Your channel"/>
        <div>
          <el-radio v-model="user.role" label="0" size="larger">Teacher</el-radio>
          <el-radio v-model="user.role" label="1" size="larger">Student</el-radio>
        </div>
        <br>
        <el-button @click="saveData">Save</el-button>
      </el-card>
    </el-col>
  </el-row>
</template>

<script>
import {host} from "@/properties";

export default {
  name: "user",
  data() {
    return {
      user: {
        uname: '',
        channel: '',
        role: ''
      }
    }
  },
  methods: {
    saveData() {
      this.$emit("receiveData", this.user);

      let xhr = new XMLHttpRequest();
      xhr.open('post', host + '/users/insert');
      xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
      xhr.send("uname=" + this.user.uname + "&channel=" + this.user.channel + "&role=" + this.user.role);
    }
  }
}
</script>

<style scoped>
.el-card {
  margin: 30px;
}

.el-input {
  margin: 10px;
  width: 200px;
}
</style>