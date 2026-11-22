import { defineStore } from 'pinia'
import notificacionesService from '@/services/notificacionesService'

// Guarda el número de notificaciones sin leer (la campana de la barra superior)
export const useNotificacionesStore = defineStore('notificaciones', {
  state: () => ({ noLeidas: 0, temporizador: null }),
  actions: {
    async actualizar() {
      try {
        const { data } = await notificacionesService.resumen()
        this.noLeidas = data.no_leidas
      } catch {
        /* sin conexión: se conserva el último número */
      }
    },
    // Consulta cada 30 s mientras haya sesión
    iniciar() {
      this.detener()
      this.actualizar()
      this.temporizador = setInterval(() => this.actualizar(), 30000)
    },
    detener() {
      clearInterval(this.temporizador)
      this.temporizador = null
      this.noLeidas = 0
    },
    async marcarLeidas() {
      await notificacionesService.marcarLeidas()
      this.noLeidas = 0
    },
  },
})
