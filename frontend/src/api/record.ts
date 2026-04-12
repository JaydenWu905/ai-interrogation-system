import request from "@/utils/request"

export const createRecord = (data: any) => {
  return request({
    url: "/v1/record/create", // 后端接口
    method: "POST",
    data
  })
}