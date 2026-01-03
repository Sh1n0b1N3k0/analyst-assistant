/**Supabase Realtime для обновлений в реальном времени на фронтенде.*/
import { supabase } from './api'

export class RealtimeService {
  constructor() {
    this.channels = new Map()
  }

  /**
   * Подписаться на изменения требований проекта
   * @param {string} projectId - ID проекта
   * @param {Function} callback - Функция обратного вызова при изменении
   * @returns {Function} Функция для отписки
   */
  subscribeToRequirements(projectId, callback) {
    if (!supabase) {
      console.warn('Supabase not configured')
      return () => {}
    }

    const channel = supabase
      .channel(`requirements:${projectId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'requirements',
          filter: `project_id=eq.${projectId}`,
        },
        (payload) => {
          callback(payload)
        }
      )
      .subscribe()

    this.channels.set(`requirements:${projectId}`, channel)

    // Возвращаем функцию для отписки
    return () => {
      supabase.removeChannel(channel)
      this.channels.delete(`requirements:${projectId}`)
    }
  }

  /**
   * Подписаться на изменения проектов
   * @param {Function} callback - Функция обратного вызова
   * @returns {Function} Функция для отписки
   */
  subscribeToProjects(callback) {
    if (!supabase) {
      console.warn('Supabase not configured')
      return () => {}
    }

    const channel = supabase
      .channel('projects')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'projects',
        },
        (payload) => {
          callback(payload)
        }
      )
      .subscribe()

    this.channels.set('projects', channel)

    return () => {
      supabase.removeChannel(channel)
      this.channels.delete('projects')
    }
  }

  /**
   * Отписаться от всех каналов
   */
  unsubscribeAll() {
    this.channels.forEach((channel) => {
      supabase.removeChannel(channel)
    })
    this.channels.clear()
  }
}

export const realtimeService = new RealtimeService()

