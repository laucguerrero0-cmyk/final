import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import reportesService from '@/services/reportesService'

// Maneja los CTA de las tarjetas (¡La encontré!, La vi por aquí, ¡Es mi mascota!, Ya apareció)
// y la ventana emergente que piden. `alTerminar` recarga la lista de la pantalla.
export function useAcciones(alTerminar) {
  const auth = useAuthStore()
  const { mostrar } = useToast()

  const modo = ref('') // '' | 'encontrada' | 'avistamiento' | 'reclamar'
  const seleccionada = ref(null)
  const enviando = ref(false)
  const errorDialogo = ref('')

  const primerNombre = () => auth.usuario?.nombre?.split(' ')[0] || ''
  const textoError = (e, defecto) =>
    e.response ? e.response.data?.error || defecto : 'No se pudo conectar con el servicio de reportes'

  function abrir(nuevoModo, reporte) {
    errorDialogo.value = ''
    seleccionada.value = reporte
    modo.value = nuevoModo
  }

  function cerrar() {
    modo.value = ''
    seleccionada.value = null
  }

  async function confirmar(datos) {
    const reporte = seleccionada.value
    enviando.value = true
    errorDialogo.value = ''
    try {
      if (modo.value === 'encontrada') {
        await reportesService.marcarEncontrada(reporte.id, datos)
        mostrar(`¡Gracias, ${primerNombre()}! Avisamos que ${reporte.mascota} fue encontrada.`)
      } else if (modo.value === 'avistamiento') {
        await reportesService.avistamiento(reporte.id, datos)
        mostrar(`¡Gracias, ${primerNombre()}! Le avisamos a quien busca a ${reporte.mascota}.`)
      } else {
        const { data } = await reportesService.reclamar(reporte.id, datos)
        mostrar(data.mensaje)
      }
      cerrar()
      alTerminar()
    } catch (e) {
      errorDialogo.value = textoError(e, 'No se pudo completar la acción')
    } finally {
      enviando.value = false
    }
  }

  // "Ya apareció" / "Ya la entregué": solo lo ve quien creó el reporte
  async function resolver(reporte) {
    try {
      await reportesService.cambiarEstado(reporte.id, 'resuelto')
      mostrar(reporte.tipo === 'perdida' ? `¡Qué alegría! ${reporte.mascota} volvió a casa.` : 'Gracias por devolverla a su familia.')
      alTerminar()
    } catch (e) {
      mostrar(textoError(e, 'No se pudo actualizar el reporte'), 'error')
    }
  }

  return { modo, seleccionada, enviando, errorDialogo, abrir, cerrar, confirmar, resolver }
}
