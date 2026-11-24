// Enlaces para llamar, escribir por WhatsApp o enviar un correo a una persona.
// El backend guarda el teléfono limpio ("+573001234567" o "3001234567").

const CODIGO_PAIS = '57' // Colombia: se agrega si el celular viene sin indicativo

const limpio = (texto) => String(texto || '').trim()
const digitos = (texto) => limpio(texto).replace(/\D/g, '')

// Número en el formato que pide WhatsApp: solo dígitos y con indicativo de país
export function numeroWhatsapp(telefono) {
  const d = digitos(telefono)
  if (!d) return ''
  if (limpio(telefono).startsWith('+')) return d
  return d.length === 10 ? CODIGO_PAIS + d : d
}

export function enlaceLlamar(telefono) {
  const d = digitos(telefono)
  if (!d) return ''
  return 'tel:' + (limpio(telefono).startsWith('+') ? '+' : '') + d
}

export function enlaceWhatsapp(telefono, texto = '') {
  const numero = numeroWhatsapp(telefono)
  if (!numero) return ''
  return `https://wa.me/${numero}` + (texto ? `?text=${encodeURIComponent(texto)}` : '')
}

export function enlaceCorreo(correo, asunto = '') {
  const c = limpio(correo)
  if (!c) return ''
  return `mailto:${c}` + (asunto ? `?subject=${encodeURIComponent(asunto)}` : '')
}
