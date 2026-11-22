// Funciones de apoyo para mostrar datos (fechas, precios, fotos, colores)

const API_MASCOTAS = import.meta.env.VITE_API_MASCOTAS_URL

// Las fotos subidas viven en el microservicio de mascotas (/uploads/...).
// También se aceptan rutas del frontend (/mascotas/foto.jpg) y URLs completas.
export function urlFoto(url) {
  if (!url) return null
  return url.startsWith('/uploads/') ? API_MASCOTAS + url : url
}

// MySQL entrega "2026-11-17 08:05:00"; se convierte a Date
export function parseFecha(texto) {
  return new Date(String(texto).replace(' ', 'T'))
}

export function diasDesde(texto) {
  return Math.floor((Date.now() - parseFecha(texto).getTime()) / 86400000)
}

// "hace 5 min", "hace 3 h", "ayer", "hace 4 días"
export function haceTiempo(texto) {
  const seg = (Date.now() - parseFecha(texto).getTime()) / 1000
  if (seg < 60) return 'hace un momento'
  const min = Math.floor(seg / 60)
  if (min < 60) return `hace ${min} min`
  const horas = Math.floor(min / 60)
  if (horas < 24) return `hace ${horas} h`
  const dias = Math.floor(horas / 24)
  if (dias === 1) return 'ayer'
  if (dias < 30) return `hace ${dias} días`
  return `hace ${Math.floor(dias / 30)} mes(es)`
}

const formatoPesos = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  maximumFractionDigits: 0,
})
export const pesos = (valor) => formatoPesos.format(valor)

// Colores de pelaje que usa el formulario y los filtros
export const COLORES = ['Negro', 'Blanco', 'Café', 'Gris', 'Naranja', 'Dorado', 'Crema']

const PELAJE = {
  negro: '#3a3f45',
  blanco: '#f8f5ef',
  café: '#9a6a43',
  cafe: '#9a6a43',
  gris: '#9ba4ac',
  naranja: '#e8923a',
  dorado: '#e3b04a',
  crema: '#ecd9b0',
}

function mezclar(hex, con, t) {
  const a = hex.match(/\w\w/g).map((h) => parseInt(h, 16))
  const b = con.match(/\w\w/g).map((h) => parseInt(h, 16))
  return '#' + a.map((v, i) => Math.round(v + (b[i] - v) * t).toString(16).padStart(2, '0')).join('')
}

// Paleta (base, oscuro, claro) para dibujar la ilustración de la mascota
export function paleta(color) {
  const base = PELAJE[(color || '').toLowerCase()] || '#c9a679'
  return { base, oscuro: mezclar(base, '000000', 0.28), claro: mezclar(base, 'ffffff', 0.55) }
}
