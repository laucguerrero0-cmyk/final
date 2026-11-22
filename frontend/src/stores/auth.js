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
    logout() {
      this.token = null
      this.usuario = null
      localStorage.removeItem('token')
      localStorage.removeItem('usuario')
    },
  },
})
