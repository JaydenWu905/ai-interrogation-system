<template>
  <div class="home">
    <div class="card">
      <h1 class="title">笔录系统</h1>

      <div class="time">{{ time }}</div>

      <button class="btn" @click="goLogin">
        进入登录
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const time = ref("")

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

const goLogin = () => {
  router.push("/login")
}
</script>

<style scoped>
.home {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;

  background: linear-gradient(135deg, #e6f0ff, #ffffff);
}

.card {
  width: 400px;
  padding: 40px;
  border-radius: 20px;
  text-align: center;

  background: white;
  box-shadow: 0 10px 30px rgba(0, 100, 255, 0.1);
}

.title {
  font-size: 32px;
  color: #2f6bff;
  margin-bottom: 20px;
}

.time {
  font-size: 18px;
  margin-bottom: 30px;
  color: #555;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 10px;

  background: #2f6bff;
  color: white;
  font-size: 16px;
  cursor: pointer;

  transition: 0.2s;
}

.btn:hover {
  background: #1d4ed8;
}
</style>