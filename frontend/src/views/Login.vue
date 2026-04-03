<template>
  <div class="login">
    <div class="card">
      <h2>警员登录</h2>

      <input v-model="policeNumber" placeholder="警员编号" />
      <input v-model="password" type="password" placeholder="密码" />

      <label>
        <input type="checkbox" v-model="remember" />
        记住我
      </label>

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

    console.log("登录成功返回：", res)

    // ✅ 存 token
    localStorage.setItem("token", res.token)

    // ✅ 存用户信息（建议）
    localStorage.setItem("user", JSON.stringify(res.user))

    alert("登录成功")

    router.push("/")
  } catch (err: any) {
    console.error("完整错误：", err)
    console.log("后端返回：", err?.response)

    const msg =
      err?.response?.data?.detail?.[0]?.msg || "登录失败"

    alert(msg)
  }
}
</script>

<style scoped>
.login {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f0f4ff;
}

.card {
  width: 320px;
  padding: 30px;
  border-radius: 15px;
  background: white;
  box-shadow: 0 10px 30px rgba(0, 0, 255, 0.1);
}
</style>