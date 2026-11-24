import { onMounted, onBeforeUnmount } from 'vue'

// Vuelve a ejecutar `accion` cada cierto tiempo para que la pantalla se actualice sola, sin recargar la página.
// - Se pausa cuando la pestaña está oculta o el celular bloqueado (no gasta datos ni batería).
// - Al volver a la pestaña, actualiza de inmediato.
// - `accion` debe ser "silenciosa": sin esqueletos de carga ni parpadeos.
export function useAutoRefresh(accion, cadaMs = 15000) {
  let reloj = null

  const visible = () => document.visibilityState !== 'hidden'
  const tic = () => {
    if (visible() && navigator.onLine !== false) accion()
  }
  const alVolver = () => {
    if (visible()) tic()
  }

  onMounted(() => {
    reloj = setInterval(tic, cadaMs)
    document.addEventListener('visibilitychange', alVolver)
    window.addEventListener('online', alVolver)
  })
  onBeforeUnmount(() => {
    clearInterval(reloj)
    document.removeEventListener('visibilitychange', alVolver)
    window.removeEventListener('online', alVolver)
  })
}
