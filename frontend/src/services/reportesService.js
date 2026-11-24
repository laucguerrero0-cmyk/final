import { apiReportes } from './api'

// Refleja los endpoints del microservicio de reportes (puerto 5002)
export default {
  buscar: (params) => apiReportes.get('/reportes/buscar', { params }),
  filtros: () => apiReportes.get('/reportes/filtros'),
  resumen: () => apiReportes.get('/reportes/resumen'),
  crear: (datos) => apiReportes.post('/reportes', datos),

  // CTA "¡La encontré!": cualquier usuario puede avisar. `lugar` es obligatorio.
  // Datos: { lugar, descripcion, condicion, compartir_contacto }. Responde con el contacto de quien publicó.
  marcarEncontrada: (id, datos) => apiReportes.put(`/reportes/${id}/encontrada`, datos),
  // "La vi por aquí": avisa sin cerrar el reporte.
  // Datos: { lugar, descripcion, condicion, hace_minutos, compartir_contacto }
  avistamiento: (id, datos) => apiReportes.post(`/reportes/${id}/avistamiento`, datos),
  // "¡Es mi mascota!": sobre un reporte de hallazgo. Datos: { descripcion, compartir_contacto }
  reclamar: (id, datos) => apiReportes.post(`/reportes/${id}/reclamar`, datos),
  // Para quien publicó el reporte: "Ya apareció" / "Ya la entregué"
  cambiarEstado: (id, estado) => apiReportes.put(`/reportes/${id}/estado`, { estado }),

  // Historial de la mascota: reportes y novedades (avistamientos, hallazgos, reclamos)
  historial: (id) => apiReportes.get(`/reportes/${id}/historial`),
  // Cómo llamar o escribir a quien publicó el reporte
  contacto: (id) => apiReportes.get(`/reportes/${id}/contacto`),
  // Quien publicó el reporte confirma o descarta un aviso ("¿sí era mi mascota?")
  // Mis reportes (los que yo publiqué), con cuántos avisos tiene cada uno
  mios: () => apiReportes.get('/reportes/mios'),
  // Quien publicó puede corregir el lugar y la descripción, o eliminar el reporte
  actualizar: (id, datos) => apiReportes.put(`/reportes/${id}`, datos),
  eliminar: (id) => apiReportes.delete(`/reportes/${id}`),
  // Foto del aviso (¡La encontré! / La vi por aquí): se sube primero y su foto_url va en el aviso
  subirFotoAviso(archivo) {
    const form = new FormData()
    form.append('foto', archivo)
    return apiReportes.post('/reportes/fotos', form)
  },
  confirmarNovedad: (id, novedadId) => apiReportes.put(`/reportes/${id}/novedades/${novedadId}/confirmar`),
  descartarNovedad: (id, novedadId) => apiReportes.put(`/reportes/${id}/novedades/${novedadId}/descartar`),
}
