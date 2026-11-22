import { apiReportes } from './api'

export default {
  listar: () => apiReportes.get('/notificaciones'),
  resumen: () => apiReportes.get('/notificaciones/resumen'),
  marcarLeidas: () => apiReportes.put('/notificaciones/leer'),
}
