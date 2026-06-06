<template>
  <div class="overlay" @click.self="close">
    <div class="modal">
      <div class="modal-head">
        <div>
          <span class="eyebrow">创建记录</span>
          <h2>新建笔录任务</h2>
          <p>先确定案件与人员身份，进入笔录页面后再继续补充细节。</p>
        </div>
        <button class="close-btn" @click="close">关闭</button>
      </div>

      <div class="form-grid">
        <label class="field">
          <span>案件类型</span>
          <select v-model="form.caseType">
            <option value="故意伤害案">故意伤害案</option>
            <option value="盗窃案">盗窃案</option>
            <option value="诈骗案">诈骗案</option>
          </select>
        </label>

        <label class="field">
          <span>案件名称</span>
          <select v-model="form.caseName">
            <option value="未立案">未立案</option>
            <option value="案件 A">案件 A</option>
            <option value="案件 B">案件 B</option>
          </select>
        </label>

        <label class="field">
          <span>人员身份</span>
          <select v-model="form.personType">
            <option value="受害人">受害人</option>
            <option value="证人">证人</option>
            <option value="嫌疑人">嫌疑人</option>
          </select>
        </label>

        <label class="field wide">
          <span>被询问人</span>
          <input 
            v-model="form.personName" 
            type="text"
            placeholder="请输入姓名（支持中文）" 
            autocomplete="off"
            inputmode="text"
          />
        </label>

        <label class="field">
          <span>证件类型</span>
          <select v-model="form.idType">
            <option value="身份证">身份证</option>
            <option value="护照">护照</option>
            <option value="驾驶证">驾驶证</option>
          </select>
        </label>

        <label class="field wide">
          <span>证件号码</span>
          <input v-model="form.idNumber" placeholder="请输入证件号码" />
        </label>
      </div>

      <div class="tips">
        <div class="tip-card">
          <strong>使用建议</strong>
          <span>如果是首次接待，先选“未立案”，后续可在案件管理中继续补全。</span>
        </div>
        <div class="tip-card">
          <strong>下一步</strong>
          <span>进入笔录页后将自动带入当前信息，方便继续编辑和打印。</span>
        </div>
      </div>

      <button class="start-btn" @click="submit">开始笔录</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()

const props = withDefaults(defineProps<{ mode?: string }>(), {
  mode: "inquiry",
})

const form = ref({
  caseType: "故意伤害案",
  caseName: "未立案",
  personType: "证人",
  personName: "",
  idType: "身份证",
  idNumber: "",
})

const emit = defineEmits(["close"])

const close = () => {
  emit("close")
}

const submit = async () => {
  try {
    router.push({
      path: "/record",
      query: {
        form: JSON.stringify(form.value),
        mode: props.mode,
      },
    })
  } catch (err) {
    console.error("提交失败", err)
  }
}
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(12, 20, 36, 0.45);
  backdrop-filter: blur(12px);
  display: grid;
  place-items: center;
  z-index: 999;
  padding: 18px;
}

.modal {
  width: min(760px, 100%);
  padding: 28px;
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid var(--line-soft);
  box-shadow: var(--shadow-lg);
}

.modal-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 22px;
}

.eyebrow {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(29, 111, 216, 0.08);
  color: var(--brand);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.modal-head h2 {
  margin: 10px 0 8px;
}

.modal-head p,
.tip-card span {
  margin: 0;
  color: var(--text-soft);
}

.close-btn {
  min-width: 72px;
  height: 42px;
  border-radius: 14px;
  background: rgba(114, 136, 177, 0.12);
  color: var(--text-soft);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field.wide {
  grid-column: span 2;
}

.field span {
  font-size: 14px;
  color: var(--text-soft);
}

.field input,
.field select {
  height: 50px;
  padding: 0 14px;
  border-radius: 14px;
  border: 1px solid var(--line-soft);
  background: #fff;
}

.field input:focus,
.field select:focus {
  outline: none;
  border-color: rgba(29, 111, 216, 0.6);
  box-shadow: 0 0 0 4px rgba(29, 111, 216, 0.12);
}

.tips {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 18px;
}

.tip-card {
  padding: 18px;
  border-radius: 18px;
  background: rgba(238, 243, 251, 0.9);
}

.tip-card strong {
  display: block;
  margin-bottom: 8px;
}

.start-btn {
  width: 100%;
  height: 54px;
  margin-top: 22px;
  border-radius: 18px;
  color: #fff;
  background: linear-gradient(135deg, var(--brand), var(--brand-deep));
  box-shadow: 0 18px 30px rgba(18, 79, 154, 0.24);
}

@media (max-width: 720px) {
  .modal-head,
  .form-grid,
  .tips {
    display: flex;
    flex-direction: column;
  }

  .field.wide {
    grid-column: auto;
  }
}
</style>
