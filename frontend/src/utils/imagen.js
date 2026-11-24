// Prepara la foto de una mascota antes de subirla.
// Las fotos del celular suelen pesar entre 4 y 12 MB. Se reducen en el navegador a un tamaño
// de sobra para la pantalla (lado mayor de 1600 px, JPG): se ven igual de bien, suben mucho más
// rápido con datos móviles y ocupan poco espacio en el servidor.

export const MAX_FOTO_ORIGINAL = 25 * 1024 * 1024 // lo máximo que se acepta elegir
const MAX_SIN_REDUCIR = 5 * 1024 * 1024 // si no se puede reducir, se sube tal cual solo si pesa menos que esto
const LADO_MAX = 1600
const CALIDAD = 0.85

function cargarImagen(archivo) {
  return new Promise((resolver, rechazar) => {
    const url = URL.createObjectURL(archivo)
    const img = new Image()
    img.onload = () => {
      URL.revokeObjectURL(url)
      resolver(img)
    }
    img.onerror = () => {
      URL.revokeObjectURL(url)
      rechazar(new Error('No se pudo leer la imagen'))
    }
    img.src = url
  })
}

// Devuelve un File listo para subir. Lanza un Error con un mensaje claro si no se puede usar la foto.
export async function prepararFoto(archivo) {
  if (archivo.size > MAX_FOTO_ORIGINAL) {
    throw new Error('La foto pesa más de 25 MB. Elige otra o tómala con menos calidad.')
  }

  try {
    const img = await cargarImagen(archivo) // respeta la orientación con que se tomó la foto
    const escala = Math.min(1, LADO_MAX / Math.max(img.naturalWidth, img.naturalHeight))
    const ancho = Math.max(1, Math.round(img.naturalWidth * escala))
    const alto = Math.max(1, Math.round(img.naturalHeight * escala))

    const lienzo = document.createElement('canvas')
    lienzo.width = ancho
    lienzo.height = alto
    const ctx = lienzo.getContext('2d')
    ctx.fillStyle = '#ffffff' // los PNG con transparencia quedan sobre fondo blanco
    ctx.fillRect(0, 0, ancho, alto)
    ctx.drawImage(img, 0, 0, ancho, alto)

    const blob = await new Promise((resolver) => lienzo.toBlob(resolver, 'image/jpeg', CALIDAD))
    if (!blob) throw new Error('sin resultado')

    // Si la foto ya era pequeña y la original pesa menos, se deja como estaba
    if (escala === 1 && archivo.type === 'image/jpeg' && archivo.size <= blob.size) return archivo
    return new File([blob], 'foto.jpg', { type: 'image/jpeg' })
  } catch {
    // El navegador no pudo procesarla (formato raro): se sube sin tocar si el servidor la va a aceptar
    if (archivo.size <= MAX_SIN_REDUCIR) return archivo
    throw new Error('No pudimos leer esa foto. Prueba con otra en formato JPG o PNG.')
  }
}
