<template>
  <router-view />
</template>

<!-- <script setup>
import { useRouter } from "vue-router"
import { onMounted } from "vue"

const router = useRouter()

onMounted(() => {
  const token = localStorage.getItem("token")

  if (!token) {
    router.replace("/login")
  } else {
    router.replace("/")
  }
})
</script> -->