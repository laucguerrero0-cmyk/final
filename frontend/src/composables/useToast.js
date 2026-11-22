import { ref } from 'vue'

// Mensaje flotante global (se muestra en <ToastHost /> dentro de App.vue)
const mensaje = ref('')
const tipo = ref('ok') // 'ok' | 'error'
let temporizador

export function useToast() {
  function mostrar(texto, nuevoTipo = 'ok') {
    mensaje.value = texto
    tipo.value = nuevoTipo
    clearTimeout(temporizador)
    temporizador = setTimeout(() => (mensaje.value = ''), 6000)
  }
  return { mensaje, tipo, mostrar }
}
