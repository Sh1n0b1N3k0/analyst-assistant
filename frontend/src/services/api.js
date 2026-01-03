import axios from 'axios'
import { createClient } from '@supabase/supabase-js'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Supabase клиент для Realtime (опционально, если хотите использовать напрямую)
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = supabaseUrl && supabaseKey 
  ? createClient(supabaseUrl, supabaseKey)
  : null

// Projects API
export const projectsAPI = {
  list: () => api.get('/projects'),
  get: (id) => api.get(`/projects/${id}`),
  create: (data) => api.post('/projects', data),
  update: (id, data) => api.put(`/projects/${id}`, data),
  analyze: (id, options) => api.post(`/projects/${id}/analyze`, options),
}

// Requirements API
export const requirementsAPI = {
  process: (data) => api.post('/requirements/process', data),
  getProcessingStatus: (id) => api.get(`/requirements/process/${id}`),
  list: (params) => api.get('/storage/requirements', { params }),
  get: (id) => api.get(`/storage/requirements/${id}`),
  create: (data) => api.post('/storage/requirements', data),
  update: (id, data) => api.put(`/storage/requirements/${id}`, data),
  delete: (id) => api.delete(`/storage/requirements/${id}`),
}

// Knowledge Base API
export const knowledgeAPI = {
  import: (data) => api.post('/knowledge/import', data),
  checkDuplicates: (id) => api.get(`/knowledge/duplicates/${id}`),
  checkConflicts: (id) => api.get(`/knowledge/conflicts/${id}`),
  getRecommendations: (id) => api.get(`/knowledge/recommendations/${id}`),
  analyzeCompleteness: (projectId) => api.get(`/knowledge/completeness/${projectId}`),
  getGraph: (projectId) => api.get(`/knowledge/graph/${projectId}`),
}

// Specifications API
export const specificationsAPI = {
  generate: (data) => api.post('/specs/generate', data),
  listTemplates: () => api.get('/specs/templates'),
  getTemplate: (type) => api.get(`/specs/templates/${type}`),
  listRequirementSpecs: (requirementId) => api.get(`/specs/requirements/${requirementId}/specs`),
}

export default api

