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
        role: '',
        token: '',
        timestamp: '',
        value: ''
      }
    }
  },
  methods: {
    saveData() {
      this.user.role = parseInt(this.user.role);
      let thisUser = this.user;
      let xhr = new XMLHttpRequest();
      // xhr.open('post', host + '/insert', false);
      // xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
      // xhr.send("uname=" + this.user.uname + "&channel=" + this.user.channel + "&role=" + this.user.role);

      xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
          thisUser.token = xhr.responseText;
        }
      }
      xhr.open('post', host + '/token', false);
      xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
      xhr.send("channel=" + this.user.channel);
      this.$emit("receiveData", this.user);
      alert("保存成功！");
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