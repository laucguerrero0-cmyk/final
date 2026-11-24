// Funciones de apoyo para mostrar datos (fechas, precios, fotos, colores)

const API_MASCOTAS = import.meta.env.VITE_API_MASCOTAS_URL

// Las fotos subidas viven en el microservicio de mascotas (/uploads/...).
// También se aceptan rutas del frontend (/mascotas/foto.jpg) y URLs completas.
export function urlFoto(url) {
  if (!url) return null
  return url.startsWith('/uploads/') ? API_MASCOTAS + url : url
}

// La base entrega las fechas en UTC ("2026-11-17 08:05:00", ver backend/common/db.py).
// Se marca con "Z" para que el navegador las convierta a la hora del celular; sin la "Z"
// las leía como hora local y en Colombia (UTC-5) todo se veía 5 horas en el futuro.
export function parseFecha(texto) {
  const t = String(texto).replace(' ', 'T')
  return new Date(/(Z|[+-]\d\d:?\d\d)$/i.test(t) ? t : t + 'Z')
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

// Sugerencias para los campos de texto (siempre se puede escribir cualquier otra cosa)
export const ESPECIES = ['Perro', 'Gato', 'Conejo', 'Ave', 'Hámster', 'Tortuga']
export const COLORES = ['Negro', 'Blanco', 'Café', 'Gris', 'Naranja', 'Dorado', 'Crema', 'Tricolor', 'Manchado']

// Une listas de sugerencias sin repetir (sin importar mayúsculas ni tildes)
export function unirSugerencias(...listas) {
  const vistos = new Map()
  for (const lista of listas) {
    for (const valor of lista || []) {
      const clave = String(valor).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
      if (valor && !vistos.has(clave)) vistos.set(clave, valor)
    }
  }
  return [...vistos.values()]
}

// Convierte un texto en partes para mostrarlo con los enlaces clicables (sin usar v-html).
// Los enlaces de mapa se muestran como "Ver en el mapa".
export function partesConEnlaces(texto) {
  const t = String(texto || '')
  const partes = []
  const patron = /https?:\/\/[^\s]+/g
  let desde = 0
  let m
  while ((m = patron.exec(t))) {
    if (m.index > desde) partes.push({ texto: t.slice(desde, m.index) })
    const url = m[0]
    partes.push({ texto: /maps/i.test(url) ? '📍 Ver en el mapa' : url, url })
    desde = m.index + url.length
  }
  if (desde < t.length) partes.push({ texto: t.slice(desde) })
  return partes
}

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
