import request from "@/utils/request"

export function login(data: {
  police_number: string
  password: string
  remember_me: boolean
}) {
  return request({
    url: "/v1/auth/login",
    method: "POST",
    data,
  })
}

export function logout() {
  return request({
    url: "/v1/auth/logout",
    method: "POST",
  })
}