import { defineStore } from 'pinia'
import authService from '@/services/authService'

function leerUsuario() {
  try {
    return JSON.parse(localStorage.getItem('usuario')) || null
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    usuario: leerUsuario(), // { id, nombre, rol } que devuelve /auth/login
  }),
  getters: {
    estaAutenticado: (state) => !!state.token,
    esAdmin: (state) => state.usuario?.rol === 'admin',
  },
  actions: {
    async login(usuario, password) {
      const { data } = await authService.login(usuario, password)
      this.token = data.token
      this.usuario = data.usuario
      localStorage.setItem('token', data.token)
      localStorage.setItem('usuario', JSON.stringify(data.usuario))
    },
    // Trae el teléfono guardado en el servidor (la sesión puede venir de antes de que existiera)
    async refrescarPerfil() {
      if (!this.usuario?.id) return
      const { data } = await authService.perfil(this.usuario.id)
      this.usuario = { ...this.usuario, telefono: data.telefono || null }
      localStorage.setItem('usuario', JSON.stringify(this.usuario))
    },
    // Guarda el teléfono para que otras personas puedan llamar o escribir por WhatsApp
    async guardarTelefono(telefono) {
      await authService.actualizarTelefono(this.usuario.id, telefono)
      await this.refrescarPerfil()
    },
    logout() {
      this.token = null
      this.usuario = null
      localStorage.removeItem('token')
      localStorage.removeItem('usuario')
    },
  },
})
