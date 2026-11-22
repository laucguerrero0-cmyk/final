import axios from 'axios'

// El backend son 3 microservicios (cada uno en su puerto), así que hay un cliente Axios por servicio.
// Los 3 comparten el mismo interceptor: agrega el token JWT en cada petición.
function crearCliente(baseURL) {
  const cliente = axios.create({ baseURL })

  cliente.interceptors.request.use((config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })

  // Si el token venció (2 horas) o no es válido, se cierra la sesión y se vuelve al login
  cliente.interceptors.response.use(
    (respuesta) => respuesta,
    (error) => {
      const esLogin = error.config?.url?.includes('/auth/login')
      if (error.response?.status === 401 && !esLogin && localStorage.getItem('token')) {
        localStorage.removeItem('token')
        localStorage.removeItem('usuario')
        window.location.href = '/login'
      }
      return Promise.reject(error)
    },
  )

  return cliente
}

export const apiUsuarios = crearCliente(import.meta.env.VITE_API_USUARIOS_URL)
export const apiMascotas = crearCliente(import.meta.env.VITE_API_MASCOTAS_URL)
export const apiReportes = crearCliente(import.meta.env.VITE_API_REPORTES_URL)
