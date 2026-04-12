<template>
  <div class="overlay" @click.self="close">
    <div class="modal">

      <h2>被询问人信息</h2>
      <p class="desc">
        您可以在“案件名称”的选择框中直接创建新案件：
        <br />
        如果是第一次询问对方，可以在选择框中直接创建“被询问人”。
      </p>

      <div class="form">

        <div class="row">
          <label>案件类型：</label>
          <select v-model="form.caseType">
            <option value="故意伤人案">故意伤人案</option>
            <option value="盗窃案">盗窃案</option>
            <option value="诈骗案">诈骗案</option>
          </select>
        </div>

        <div class="row">
          <label>案件名称：</label>
          <select v-model="form.caseName">
            <option value="未立案">未立案</option>
            <option value="案件A">案件A</option>
            <option value="案件B">案件B</option>
          </select>
        </div>

        <div class="row">
          <label>被询问人：</label>
          <select v-model="form.personType">
            <option value="受害人">受害人</option>
            <option value="证人">证人</option>
            <option value="嫌疑人">嫌疑人</option>
          </select>
          <input 
          v-model="form.personName"
          placeholder="请输入或选择被询问人" />
        </div>

        <div class="row">
          <label>有效证件：</label>
          <select v-model="form.idType">
            <option value="身份证">身份证</option>
            <option value="护照">护照</option>
            <option value="驾照">驾照</option>
          </select>
          <input 
          v-model="form.idNumber"
          placeholder="请输入证件号码" />
        </div>

      </div>

      <button class="start" @click="submit">开始</button>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { createRecord } from "@/api/record"
import { useRouter } from "vue-router"

const router = useRouter()



const form = ref({
  caseType: "",
  caseName: "",
  personType: "",
  personName: "",
  idType: "",
  idNumber: ""
})
const emit = defineEmits(["close"])

const close = () => {
  emit("close")
}

const submit = async () => {
  try {
    // 1. 打印数据（调试用）
    console.log("表单数据:", form.value)

    // 2. 调用后端（可选：现在可以先不接）
    // const res = await createRecord(form.value)
    // console.log("后端返回:", res)

    // 3. 跳转页面（核心）
    router.push({
      path: "/record",
      query: {
        form: JSON.stringify(form.value)
      }
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
  background: rgba(0,0,0,0.3);

  display: flex;
  justify-content: center;
  align-items: center;

  z-index: 999;
}

.modal {
  width: 500px;
  background: white;
  border-radius: 16px;
  padding: 30px;
}

.desc {
  font-size: 14px;
  color: #666;
  margin-bottom: 20px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.row label {
  width: 90px;
  color: #555;
}

.row input,
.row select {
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #ddd;
}

.start {
  margin-top: 20px;
  width: 100%;
  padding: 10px;
  background: #2f6bff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
</style>