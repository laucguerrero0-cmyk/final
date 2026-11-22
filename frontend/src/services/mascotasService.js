import { apiMascotas } from './api'

export default {
  crear: (datos) => apiMascotas.post('/mascotas', datos),
  // La foto se envía como multipart/form-data (campo "foto")
  subirFoto(id, archivo) {
    const form = new FormData()
    form.append('foto', archivo)
    return apiMascotas.post(`/mascotas/${id}/foto`, form)
  },
}
