<template>
  <div class="container">

    <!-- 顶部栏 -->
    <div class="header">
      <div class="logo">
        🛡️ 执法业务协同平台
        <span class="sub">Law Enforcement Case Management System</span>
      </div>

      <div class="user">
        当前用户：{{ user?.name || "未登录" }}

        <div class="avatar">{{ user?.name?.[0] || "?" }}</div>

  <!-- 未登录 -->
        <button v-if="!user" class="login-btn" @click="goLogin">
        登录</button>

  <!-- 已登录 -->
        <button v-else class="logout" @click="logout">
        退出</button>
      </div>
    </div>

    <!-- 主体 -->
    <div class="main">

      <!-- 左侧功能 -->
      <div class="left">
        <div class="grid">
          <div class="box" @click="openModal">讯</div>
        </div>
        <div class="labels">
          <span>快速讯问</span>
        </div>

        <div class="grid">
          <div class="box" @click="openModal">询</div>
        </div>
        <div class="labels">
          <span>快速询问</span>
        </div>

        <div class="grid">
          <div class="box" @click="openModal">录</div>
        </div>
        <div class="labels">
          <span>常规笔录</span>
        </div>

        <div class="grid">
          <div class="box" @click="openModal">案</div>
        </div>
        <div class="labels">
          <span>案件管理</span>
        </div>
      </div>

      <!-- 右侧面板 -->
      <div class="right">
        <div class="panel">

          <div class="time">{{ time }}</div>

          <div class="list">
            <div class="item">
              <div>
                <span class="tag blue">讯问</span>
                关于某涉嫌某案件调查
              </div>
              <button class="enter" @click="openModal">进入笔录</button>
            </div>

            <div class="item">
              <div>
                <span class="tag green">询问</span>
                证人李某背景核查询问
              </div>
              <button class="enter" @click="openModal">进入笔录</button>
            </div>

          </div>

        </div>
      </div>

    </div>

  </div>
  <RecordModal v-if="showModal" @close="closeModal" />
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue"
import { useRouter } from "vue-router"
import RecordModal from "@/components/RecordModal.vue"

const router = useRouter()
const time = ref("")
const user = ref<any>(null)
const showModal = ref(false)

const openModal = () => {
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

onMounted(() => {
  const u = localStorage.getItem("user")
  if (u) {
    user.value = JSON.parse(u)
  }
})

let timer: any = null

const updateTime = () => {
  const now = new Date()
  time.value = now.toLocaleString()
}

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  clearInterval(timer)
})

const logout = () => {
  localStorage.removeItem("token")
  localStorage.removeItem("user")
  user.value = null
}

const goLogin = () => {
  router.push("/login")
}
</script>



<style scoped>
.container {
  height: 100vh;
  width: 100vw;

  background: #f5f7fb;

  display: flex;
  flex-direction: column;

  padding: 20px;
  box-sizing: border-box;
}

/* 顶部 */
.header {
  flex-shrink: 0;

  display: flex;
  justify-content: space-between;
  align-items: center;

  background: white;
  padding: 20px 30px;
  border-radius: 16px;

  box-shadow: 0 5px 20px rgba(0,0,0,0.05);
}

.logo {
  font-size: 20px;
  font-weight: bold;
}

.sub {
  display: block;
  font-size: 12px;
  color: #888;
}

.user {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-right: 30px;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #2f6bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logout {
  padding: 6px 12px;
  border: none;
  background: #eee;
  border-radius: 6px;
  cursor: pointer;
}

.list {
  flex: 1;
  overflow-y: auto;
}

/* 主体 */
.main {
  flex: 1;

  display: flex;
  gap: 20px;

  margin-top: 20px;

  min-height: 0; /* 关键防止溢出 */
}

/* 左侧 */
.left {
  width: 320px;
  flex-shrink:0;
  padding:15px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.box {
  height: 120px;
  border: 2px solid #2f6bff;
  border-radius: 16px;

  display: flex;
  align-items: center;
  justify-content: center;

  font-size: 40px;
  color: #2f6bff;
}

.labels {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  margin-top: 10px;
  text-align: center;
  color: #555;
}

/* 右侧 */
.right {
  flex: 1;
  min-width:0;
  padding-right: 30px;
}

.panel {
  height: 100%;

  background: white;
  border-radius: 16px;
  padding: 20px;

  display: flex;
  flex-direction: column;
}

.time {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 20px;
}

.item {
  display: flex;
  justify-content: space-between;
  align-items: center;

  padding: 15px;
  border-radius: 10px;
  background: #f7f9fc;
  margin-bottom: 10px;
}

.tag {
  padding: 2px 6px;
  border-radius: 6px;
  margin-right: 10px;
}

.blue {
  background: #dbeafe;
  color: #2563eb;
}

.green {
  background: #dcfce7;
  color: #16a34a;
}

.enter {
  background: #2f6bff;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}

.login-btn {
  padding: 6px 12px;
  border: none;
  background: #2f6bff;
  color: white;
  border-radius: 6px;
  cursor: pointer;
}

.logout {
  padding: 6px 12px;
  border: none;
  background: #eee;
  border-radius: 6px;
  cursor: pointer;
}
</style>