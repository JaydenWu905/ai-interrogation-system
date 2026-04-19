<template>
  <div class="login-page">
    <div class="login-shell">
      <section class="hero-panel">
        <span class="eyebrow">智能执法记录平台</span>
        <h1>把笔录、案件和现场协同放进同一个工作台</h1>
        <p class="hero-copy">
          为询问、讯问、案件管理与 AI 要素分析提供统一入口，帮助前端和业务团队快速推进产品落地。
        </p>

        <div class="hero-grid">
          <article v-for="item in heroItems" :key="item.title" class="hero-card">
            <div class="hero-icon">{{ item.icon }}</div>
            <div>
              <h3>{{ item.title }}</h3>
              <p>{{ item.description }}</p>
            </div>
          </article>
        </div>

        <div class="hero-metrics">
          <div v-for="metric in metrics" :key="metric.label" class="metric">
            <strong>{{ metric.value }}</strong>
            <span>{{ metric.label }}</span>
          </div>
        </div>
      </section>

      <section class="auth-panel">
        <div class="auth-head">
          <span class="badge">安全登录</span>
          <h2>警员登录</h2>
          <p>请输入警员编号和密码，进入案件工作台。</p>
        </div>

        <div class="auth-form">
          <label class="field">
            <span>警员编号</span>
            <input v-model="policeNumber" placeholder="例如 4401-0186" />
          </label>

          <label class="field">
            <span>登录密码</span>
            <input v-model="password" type="password" placeholder="请输入密码" />
          </label>

          <label class="remember-row">
            <input v-model="remember" type="checkbox" />
            <span>记住当前设备</span>
          </label>

          <button class="submit-btn" @click="handleLogin">进入系统</button>
        </div>

        <div class="auth-foot">
          <div>
            <strong>值班提醒</strong>
            <span>登录后可继续上次未完成的笔录任务</span>
          </div>
          <div class="status-pill">在线协同</div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"
import { login } from "@/api/auth"

const router = useRouter()

const policeNumber = ref("")
const password = ref("")
const remember = ref(false)

const heroItems = [
  { icon: "01", title: "流程集中", description: "从接待录入到笔录归档，关键动作统一在一屏完成。" },
  { icon: "02", title: "信息整洁", description: "更清晰的结构和层级，让业务页面更适合继续深化设计。" },
  { icon: "03", title: "AI 辅助", description: "预留分析与摘要区域，方便后续接入智能能力。" },
]

const metrics = [
  { value: "24h", label: "值班在线" },
  { value: "4类", label: "核心业务入口" },
  { value: "1屏", label: "统一工作台" },
]

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
    const msg = err?.response?.data?.detail?.[0]?.msg || "登录失败，请检查账号或密码"
    alert(msg)
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  padding: 32px;
  display: grid;
  place-items: center;
}

.login-shell {
  width: min(1200px, 100%);
  display: grid;
  grid-template-columns: 1.3fr 0.9fr;
  gap: 24px;
}

.hero-panel,
.auth-panel {
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-xl);
  backdrop-filter: blur(22px);
  box-shadow: var(--shadow-lg);
}

.hero-panel {
  padding: 40px;
  background:
    linear-gradient(145deg, rgba(18, 35, 60, 0.95), rgba(20, 79, 154, 0.88)),
    linear-gradient(145deg, #12233c, #1d6fd8);
  color: #f8fbff;
  position: relative;
  overflow: hidden;
}

.hero-panel::after {
  content: "";
  position: absolute;
  inset: auto -10% -25% auto;
  width: 320px;
  height: 320px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.16), transparent 70%);
}

.eyebrow,
.badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  letter-spacing: 0.08em;
}

.eyebrow {
  background: rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.9);
}

.hero-panel h1 {
  margin: 18px 0 16px;
  max-width: 9em;
  font-size: clamp(36px, 4vw, 58px);
  line-height: 1.05;
}

.hero-copy {
  max-width: 38rem;
  margin: 0 0 28px;
  color: rgba(240, 246, 255, 0.8);
  font-size: 16px;
}

.hero-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.hero-card {
  display: grid;
  grid-template-columns: 48px 1fr;
  gap: 14px;
  padding: 18px;
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.hero-icon {
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.14);
  font-weight: 700;
}

.hero-card h3,
.metric strong,
.auth-head h2 {
  margin: 0;
}

.hero-card p,
.auth-head p,
.auth-foot span {
  margin: 6px 0 0;
  color: rgba(240, 246, 255, 0.72);
}

.hero-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 22px;
}

.metric {
  padding: 18px;
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.08);
}

.metric strong {
  display: block;
  font-size: 30px;
}

.metric span {
  font-size: 13px;
  color: rgba(240, 246, 255, 0.72);
}

.auth-panel {
  padding: 34px;
  background: rgba(255, 255, 255, 0.78);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.badge {
  background: rgba(17, 166, 161, 0.12);
  color: var(--accent);
}

.auth-head p {
  color: var(--text-soft);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
  margin-top: 24px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: var(--text-soft);
  font-size: 14px;
}

.field input {
  height: 52px;
  padding: 0 16px;
  border-radius: 16px;
  border: 1px solid var(--line-soft);
  background: rgba(255, 255, 255, 0.92);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.field input:focus {
  outline: none;
  border-color: rgba(29, 111, 216, 0.6);
  box-shadow: 0 0 0 4px rgba(29, 111, 216, 0.12);
  transform: translateY(-1px);
}

.remember-row {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-soft);
  font-size: 14px;
}

.submit-btn {
  height: 54px;
  border-radius: 18px;
  background: linear-gradient(135deg, var(--brand), var(--brand-deep));
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 18px 30px rgba(18, 79, 154, 0.24);
}

.auth-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-top: 28px;
  padding-top: 22px;
  border-top: 1px solid var(--line-soft);
  color: var(--text-soft);
}

.auth-foot strong {
  display: block;
  color: var(--text-main);
}

.status-pill {
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(17, 166, 161, 0.12);
  color: var(--accent);
  white-space: nowrap;
}

@media (max-width: 980px) {
  .login-shell {
    grid-template-columns: 1fr;
  }

  .hero-grid,
  .hero-metrics {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .login-page {
    padding: 16px;
  }

  .hero-panel,
  .auth-panel {
    padding: 24px;
  }
}
</style>