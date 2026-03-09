// frontend/src/api.js
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
})

export const chatAPI = {
  ask: (question) => api.post('/chat', { question }),
}

export const pipelineAPI = {
  upload: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/pipeline/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  status: (jobId) => api.get(`/pipeline/status/${jobId}`),
  reportUrl: (jobId) => `${API_BASE_URL}/pipeline/report/${jobId}`,
}

export default api