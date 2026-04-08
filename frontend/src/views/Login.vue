<template>
  <div class="login">

    <!-- 背景 -->
    <div class="bg"></div>

    <!-- 居中卡片 -->
    <div class="card">
      <h2 class="title">警员登录</h2>

      <input v-model="policeNumber" placeholder="警员编号" />
      <input v-model="password" type="password" placeholder="密码" />

      <div class="options">
        <label>
          <input type="checkbox" v-model="remember" />
          记住我
        </label>
      </div>

      <button @click="handleLogin">登录</button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { login } from "@/api/auth"
import { useRouter } from "vue-router"

const router = useRouter()

const policeNumber = ref("")
const password = ref("")
const remember = ref(false)

const handleLogin = async () => {
  try {
    const res = await login({
      police_number: policeNumber.value,
      password: password.value,
      remember_me: remember.value,
    })

    localStorage.setItem("token", res.token)
    localStorage.setItem("user", JSON.stringify(res.user))

    router.push("/")
  } catch (err: any) {
    const msg =
      err?.response?.data?.detail?.[0]?.msg || "登录失败"
    alert(msg)
  }
}
</script>

<style scoped>
.login {
  width: 100vw;
  height: 100vh;
  position: relative;

  display: flex;
  justify-content: center;
  align-items: center;
}

/* 背景（柔和一点） */
.bg {
  position: absolute;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #e6f0ff, #f8fbff);
}

/* 卡片 */
.card {
  position: relative;
  z-index: 1;

  width: 360px;
  padding: 40px;

  background: white;
  border-radius: 16px;

  box-shadow: 0 20px 50px rgba(0, 80, 255, 0.15);

  display: flex;
  flex-direction: column;
}

/* 标题 */
.title {
  text-align: center;
  font-size: 24px;
  color: #2f6bff;
  margin-bottom: 25px;
}

/* 输入框 */
.card input {
  width: 100%;
  padding: 12px;
  margin-bottom: 15px;

  border-radius: 8px;
  border: 1px solid #ddd;

  transition: 0.2s;
}

.card input:focus {
  border-color: #2f6bff;
  outline: none;
  box-shadow: 0 0 0 2px rgba(47,107,255,0.1);
}

/* 选项 */
.options {
  margin-bottom: 20px;
  font-size: 14px;
  color: #555;
}

/* 按钮 */
.card button {
  padding: 12px;

  border: none;
  border-radius: 8px;

  background: #2f6bff;
  color: white;
  font-size: 16px;

  cursor: pointer;
  transition: 0.2s;
}

.card button:hover {
  background: #1d4ed8;
}
</style>