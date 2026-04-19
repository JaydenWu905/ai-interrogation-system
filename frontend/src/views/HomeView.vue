<template>
  <div class="dashboard">
    <header class="topbar">
      <div>
        <span class="kicker">案件协同工作台</span>
        <h1>执法业务协同平台</h1>
        <p>围绕接待、案件、笔录与智能分析组织核心工作流，帮助值班人员快速进入任务。</p>
      </div>

      <div class="topbar-actions">
        <div class="clock-card">
          <span>当前时间</span>
          <strong>{{ time }}</strong>
        </div>
        <div class="user-card">
          <div>
            <span class="user-label">当前用户</span>
            <strong>{{ user?.name || "未登录" }}</strong>
          </div>
          <div class="avatar">{{ user?.name?.[0] || "?" }}</div>
          <button v-if="!user" class="ghost-btn" @click="goLogin">登录</button>
          <button v-else class="ghost-btn" @click="logout">退出</button>
        </div>
      </div>
    </header>

    <main class="workspace">
      <section class="feature-panel">
        <div class="section-head">
          <div>
            <span class="section-kicker">快速入口</span>
            <h2>今天要处理什么</h2>
          </div>
          <button class="primary-btn" @click="openModal">新建笔录</button>
        </div>

        <div class="feature-grid">
          <article
            v-for="feature in features"
            :key="feature.title"
            class="feature-card"
            @click="openModal"
          >
            <div class="feature-icon">{{ feature.icon }}</div>
            <div class="feature-copy">
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.description }}</p>
            </div>
            <span class="feature-tag">{{ feature.tag }}</span>
          </article>
        </div>
      </section>

      <aside class="sidebar">
        <section class="panel summary-panel">
          <div class="section-head compact">
            <div>
              <span class="section-kicker">值班概览</span>
              <h2>任务状态</h2>
            </div>
          </div>

          <div class="stat-grid">
            <div v-for="stat in stats" :key="stat.label" class="stat-card">
              <strong>{{ stat.value }}</strong>
              <span>{{ stat.label }}</span>
            </div>
          </div>
        </section>

        <section class="panel queue-panel">
          <div class="section-head compact">
            <div>
              <span class="section-kicker">待办队列</span>
              <h2>优先处理</h2>
            </div>
          </div>

          <div class="queue-list">
            <article v-for="item in pendingList" :key="item.title" class="queue-item">
              <div class="queue-main">
                <span class="queue-badge" :class="item.theme">{{ item.type }}</span>
                <h3>{{ item.title }}</h3>
                <p>{{ item.detail }}</p>
              </div>
              <button class="mini-btn" @click="openModal">进入</button>
            </article>
          </div>
        </section>
      </aside>
    </main>

    <section class="insight-strip">
      <article class="insight-card dark">
        <span>流程提示</span>
        <strong>首次接待可直接发起“快速询问”，系统将自动带入人员基础信息。</strong>
      </article>
      <article class="insight-card">
        <span>设计方向</span>
        <strong>界面已切到更完整的产品态布局，后续更适合继续补图标、色板和真实数据。</strong>
      </article>
    </section>
  </div>

  <RecordModal v-if="showModal" @close="closeModal" />
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue"
import { useRouter } from "vue-router"
import RecordModal from "@/components/RecordModal.vue"

const router = useRouter()
const time = ref("")
const user = ref<any>(null)
const showModal = ref(false)

const features = [
  { icon: "询", title: "快速询问", description: "面向初始接待和基础情况采集，适合快速启动流程。", tag: "常用" },
  { icon: "讯", title: "快速讯问", description: "进入重点案件场景，保持对话记录与笔录同步。", tag: "高优先" },
  { icon: "录", title: "常规笔录", description: "用于规范化笔录整理，便于打印、复核与归档。", tag: "标准化" },
  { icon: "案", title: "案件管理", description: "聚合案件名称、涉案人员与流程节点，适合后续扩展。", tag: "协同" },
]

const stats = [
  { value: "08", label: "待处理笔录" },
  { value: "03", label: "高优先案件" },
  { value: "12", label: "今日已归档" },
  { value: "99%", label: "信息完整率" },
]

const pendingList = [
  {
    type: "询问",
    theme: "blue",
    title: "关于某涉案人员情况补充询问",
    detail: "需要补录身份信息与到场时间，建议优先完成。",
  },
  {
    type: "讯问",
    theme: "green",
    title: "证人背景核查记录复核",
    detail: "当前笔录已生成，待进入页面继续完善对话整理。",
  },
  {
    type: "案件",
    theme: "orange",
    title: "案件 A 材料归档检查",
    detail: "涉及 2 份附件与 1 条 AI 分析摘要，待最终确认。",
  },
]

const openModal = () => {
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const updateTime = () => {
  const now = new Date()
  time.value = now.toLocaleString()
}

let timer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  const storedUser = localStorage.getItem("user")
  if (storedUser) {
    user.value = JSON.parse(storedUser)
  }

  updateTime()
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
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
.dashboard {
  min-height: 100vh;
  padding: 28px;
}

.topbar,
.panel,
.feature-panel,
.insight-card {
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-xl);
  background: var(--bg-panel);
  backdrop-filter: blur(24px);
  box-shadow: var(--shadow-md);
}

.topbar {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 28px;
}

.kicker,
.section-kicker,
.user-label {
  display: inline-block;
  font-size: 12px;
  color: var(--text-faint);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.topbar h1,
.section-head h2,
.queue-item h3,
.feature-copy h3 {
  margin: 8px 0 0;
}

.topbar p,
.feature-copy p,
.queue-item p {
  margin: 10px 0 0;
  color: var(--text-soft);
}

.topbar-actions {
  display: flex;
  gap: 16px;
  align-items: stretch;
}

.clock-card,
.user-card {
  min-width: 220px;
  padding: 18px 20px;
  border-radius: var(--radius-lg);
  background: var(--bg-panel-strong);
  border: 1px solid rgba(114, 136, 177, 0.18);
}

.clock-card span,
.user-card span {
  color: var(--text-faint);
  font-size: 13px;
}

.clock-card strong,
.user-card strong {
  display: block;
  margin-top: 10px;
  font-size: 20px;
}

.user-card {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 12px;
  align-items: center;
}

.avatar {
  width: 46px;
  height: 46px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  color: #fff;
  background: linear-gradient(135deg, var(--brand), var(--brand-deep));
  font-weight: 700;
}

.ghost-btn,
.mini-btn,
.primary-btn {
  border-radius: 14px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.ghost-btn {
  grid-column: 1 / -1;
  height: 44px;
  background: rgba(29, 111, 216, 0.08);
  color: var(--brand);
}

.primary-btn,
.mini-btn {
  background: linear-gradient(135deg, var(--brand), var(--brand-deep));
  color: #fff;
}

.primary-btn {
  height: 48px;
  padding: 0 18px;
  box-shadow: 0 16px 28px rgba(18, 79, 154, 0.24);
}

.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) 380px;
  gap: 20px;
  margin-top: 20px;
}

.feature-panel,
.panel {
  padding: 24px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-bottom: 22px;
}

.section-head.compact {
  margin-bottom: 18px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.feature-card {
  position: relative;
  min-height: 180px;
  padding: 22px;
  border-radius: var(--radius-lg);
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.92), rgba(233, 241, 252, 0.9));
  border: 1px solid rgba(114, 136, 177, 0.16);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  cursor: pointer;
}

.feature-card:hover,
.primary-btn:hover,
.mini-btn:hover,
.ghost-btn:hover {
  transform: translateY(-2px);
}

.feature-icon {
  width: 58px;
  height: 58px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, rgba(29, 111, 216, 0.14), rgba(17, 166, 161, 0.18));
  color: var(--brand-deep);
  font-size: 24px;
  font-weight: 700;
}

.feature-tag {
  align-self: flex-start;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(17, 166, 161, 0.12);
  color: var(--accent);
  font-size: 12px;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.summary-panel,
.queue-panel {
  flex: 1;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.stat-card {
  padding: 18px;
  border-radius: 18px;
  background: var(--bg-panel-strong);
  border: 1px solid rgba(114, 136, 177, 0.16);
}

.stat-card strong {
  display: block;
  font-size: 28px;
}

.stat-card span {
  color: var(--text-soft);
}

.queue-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.queue-item {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  padding: 18px;
  border-radius: 18px;
  background: var(--bg-panel-strong);
  border: 1px solid rgba(114, 136, 177, 0.16);
}

.queue-main {
  min-width: 0;
}

.queue-badge {
  display: inline-flex;
  padding: 5px 10px;
  border-radius: 999px;
  font-size: 12px;
}

.queue-badge.blue {
  background: rgba(29, 111, 216, 0.12);
  color: var(--brand);
}

.queue-badge.green {
  background: rgba(17, 166, 161, 0.12);
  color: var(--accent);
}

.queue-badge.orange {
  background: rgba(255, 138, 61, 0.14);
  color: var(--warning);
}

.mini-btn {
  min-width: 72px;
  height: 42px;
  align-self: center;
}

.insight-strip {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.insight-card {
  padding: 22px 24px;
}

.insight-card.dark {
  background: linear-gradient(140deg, var(--bg-dark), #23446b);
  color: #fff;
}

.insight-card span {
  display: block;
  margin-bottom: 12px;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  opacity: 0.75;
}

.insight-card strong {
  font-size: 18px;
  line-height: 1.5;
}

@media (max-width: 1180px) {
  .workspace {
    grid-template-columns: 1fr;
  }

  .topbar {
    flex-direction: column;
  }
}

@media (max-width: 760px) {
  .dashboard {
    padding: 16px;
  }

  .topbar-actions,
  .feature-grid,
  .stat-grid,
  .insight-strip {
    grid-template-columns: 1fr;
    display: grid;
  }

  .queue-item {
    flex-direction: column;
  }
}
</style>