<template>
  <div class="container">

    <!-- 顶部信息 -->
    <div class="header">
      <div>案件：张某某案件</div>
      <div>被询问人：王三</div>
    </div>

    <!-- 主体 -->
    <div class="main">

      <!-- 左侧：笔录 -->
      <div class="left">
        <h3>询问笔录</h3>

        <textarea v-model="recordText"></textarea>
      </div>

      <!-- 右侧：对话 -->
      <div class="right">
        <h3>对话记录</h3>

        <div class="chat">
          <div v-for="(item, index) in chatList" :key="index" class="msg">
            <div class="q">问：{{ item.q }}</div>
            <div class="a">答：{{ item.a }}</div>
          </div>
        </div>
      </div>

    </div>

    <!-- 下部：要素分析 -->
    <div class="analysis">
      <h3>要素分析（AI）</h3>
      <div class="content">
        {{ analysis }}
      </div>
    </div>

    <!-- 底部按钮 -->
    <div class="footer">
      <button @click="pause">暂停</button>
      <button @click="resume">继续</button>
      <button @click="print">打印笔录</button>
      <button class="end" @click="finish">结束</button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { useRoute } from "vue-router"

const route = useRoute()

let formData: any = {}

if (route.query.form) {
  formData = JSON.parse(route.query.form as string)
}

console.log("接收到的数据:", formData)
console.log(formData)

// 笔录内容
const recordText = ref("这里是固定模板内容...\n\n（后续接AI自动生成）")

// 对话记录（模拟）
const chatList = ref([
  { q: "介绍一下你的基本情况", a: "我今年30岁，在某单位工作" },
  { q: "案发当时你在哪里？", a: "我在家中" }
])

// AI分析（预留）
const analysis = ref("（AI将根据对话自动分析案件要素）")

// 按钮逻辑
const pause = () => console.log("暂停")
const resume = () => console.log("继续")
const print = () => console.log("打印")
const finish = () => console.log("结束")
</script>

<style scoped>
.container {
  width: 90vw;
  height: 90vh;

  display: flex;
  flex-direction: column;

  background: #f5f7fb;
}

/* 顶部 */
.header {
  padding: 15px 20px;
  background: white;
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid #eee;
}

/* 主体 */
.main {
  flex: 1;

  display: flex;
  gap: 20px;

  padding: 20px;
  box-sizing: border-box;
}
/* 左侧 */
.left {
  flex: 3;
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.left textarea {
  flex: 1;
  resize: none;
  border: none;
  outline: none;
}

/* 右侧 */
.right {
  flex: 1;
  background: white;
  border-radius: 12px;
  padding: 20px;
}

.chat {
  overflow-y: auto;
  max-height: 100%;
}

.msg {
  margin-bottom: 10px;
}

.q {
  color: #2f6bff;
}

.a {
  margin-left: 10px;
}

/* 分析 */
.analysis {
  height: 120px;
  background: white;
  margin: 10px;
  border-radius: 10px;
  padding: 10px;
}

/* 底部 */
.footer {
  padding: 10px;
  display: flex;
  justify-content: center;
  gap: 20px;
  background: white;
}

.footer button {
  padding: 8px 16px;
}

.end {
  background: red;
  color: white;
}
</style>