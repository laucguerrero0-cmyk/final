import { apiUsuarios } from './api'

// Planes y suscripciones (microservicio de usuarios, puerto 5003)
export default {
  listar: () => apiUsuarios.get('/planes'),
  miPlan: () => apiUsuarios.get('/suscripciones/mia'),
  contratar: (datos) => apiUsuarios.post('/suscripciones', datos),
  cancelar: () => apiUsuarios.delete('/suscripciones/mia'),
}
