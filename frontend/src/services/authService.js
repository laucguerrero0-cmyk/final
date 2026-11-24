import { apiUsuarios } from './api'

// Refleja los endpoints reales del microservicio de usuarios (puerto 5003)
export default {
  login(usuario, password) {
    return apiUsuarios.post('/auth/login', { usuario, password })
  },
  registrar({ nombre, usuario, correo, telefono, password }) {
    return apiUsuarios.post('/auth/registro', { nombre, usuario, correo, telefono, password })
  },
  perfil(id) {
    return apiUsuarios.get(`/usuarios/${id}`)
  },
  // Solo cambia el teléfono: el servidor conserva el resto de los datos si no se envían
  actualizarTelefono(id, telefono) {
    return apiUsuarios.put(`/usuarios/${id}`, { telefono })
  },
}
