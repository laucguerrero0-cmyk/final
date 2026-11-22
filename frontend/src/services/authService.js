import { apiUsuarios } from './api'

// Refleja los endpoints reales del microservicio de usuarios (puerto 5003)
export default {
  login(usuario, password) {
    return apiUsuarios.post('/auth/login', { usuario, password })
  },
  registrar({ nombre, usuario, correo, password }) {
    return apiUsuarios.post('/auth/registro', { nombre, usuario, correo, password })
  },
  perfil(id) {
    return apiUsuarios.get(`/usuarios/${id}`)
  },
}
