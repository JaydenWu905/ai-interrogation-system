import { createRouter, createWebHashHistory } from 'vue-router'

const HomeView = () => import('@/views/HomeView.vue')
const LoginView = () => import('@/views/Login.vue')
const RecordView =() => import('@/views/RecordView.vue')

const routes = [
  {
    path: '/',
    component: HomeView,
  },
  {
    path: '/login',
    component: LoginView,
  },
  {
    path: '/record',
    component: RecordView,
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((_, __, next) => {
  next()
})

// router.beforeEach((to, from, next) => {
//   const token = localStorage.getItem("token")

//   //  未登录
//   if (!token) {
//     if (to.path !== "/login") {
//       next("/login")
//     } else {
//       next()
//     }
//   }
//   //  已登录
//   else {
//     if (to.path === "/login") {
//       next("/") // 已登录不能进登录页
//     } else {
//       next()
//     }
//   }
// })


export default router