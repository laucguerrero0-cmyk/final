import { apiReportes } from './api'

// Refleja los endpoints del microservicio de reportes (puerto 5002)
export default {
  buscar: (params) => apiReportes.get('/reportes/buscar', { params }),
  filtros: () => apiReportes.get('/reportes/filtros'),
  resumen: () => apiReportes.get('/reportes/resumen'),
  crear: (datos) => apiReportes.post('/reportes', datos),

  // CTA "¡La encontré!": cualquier usuario puede avisar. `lugar` es obligatorio.
  marcarEncontrada: (id, { lugar, descripcion }) =>
    apiReportes.put(`/reportes/${id}/encontrada`, { lugar, descripcion }),
  // "La vi por aquí": avisa a la comunidad sin cerrar el reporte
  avistamiento: (id, { lugar, descripcion }) =>
    apiReportes.post(`/reportes/${id}/avistamiento`, { lugar, descripcion }),
  // "¡Es mi mascota!": sobre un reporte de hallazgo
  reclamar: (id, { descripcion }) => apiReportes.post(`/reportes/${id}/reclamar`, { descripcion }),
  // Para el dueño del reporte: "Ya apareció" / "Ya la entregué"
  cambiarEstado: (id, estado) => apiReportes.put(`/reportes/${id}/estado`, { estado }),
}
