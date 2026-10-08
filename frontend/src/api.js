import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || ''
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('insureai_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export function setToken(token) {
  localStorage.setItem('insureai_token', token)
}

export function clearToken() {
  localStorage.removeItem('insureai_token')
}
