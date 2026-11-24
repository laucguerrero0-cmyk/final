import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import reportesService from '@/services/reportesService'
import { prepararFoto } from '@/utils/imagen'

// Maneja los botones de las tarjetas (¡La encontré!, La vi por aquí, ¡Es mi mascota!, Ya apareció)
// y la ventana emergente que piden. `alTerminar` recarga la lista de la pantalla.
export function useAcciones(alTerminar) {
  const auth = useAuthStore()
  const { mostrar } = useToast()

  const modo = ref('') // '' | 'encontrada' | 'avistamiento' | 'reclamar' | 'resuelto' | 'eliminar'
  const seleccionada = ref(null)
  const enviando = ref(false)
  const errorDialogo = ref('')
  // Cuando el aviso se envía, la ventana muestra { mensaje, contacto } de quien publicó el reporte
  const resultado = ref(null)

  const textoError = (e, defecto) =>
    e.response ? e.response.data?.error || defecto : e.message?.startsWith('La foto') || e.message?.startsWith('No pudimos') ? e.message : 'No se pudo conectar con el servidor. Intenta de nuevo.'

  function abrir(nuevoModo, reporte) {
    errorDialogo.value = ''
    resultado.value = null
    seleccionada.value = reporte
    modo.value = nuevoModo
  }

  function cerrar() {
    const habiaResultado = !!resultado.value
    modo.value = ''
    seleccionada.value = null
    resultado.value = null
    if (habiaResultado) alTerminar() // el aviso ya se envió: se actualiza la pantalla
  }

  async function confirmar(datos) {
    const reporte = seleccionada.value
    if (!reporte) return
    enviando.value = true
    errorDialogo.value = ''
    try {
      const { telefono, foto, ...cuerpo } = datos
      if (telefono) await auth.guardarTelefono(telefono) // para que puedan contactarla

      if (modo.value === 'resuelto') {
        await reportesService.cambiarEstado(reporte.id, 'resuelto')
        const nombre = reporte.mascota === 'Sin nombre' ? 'La mascota' : reporte.mascota
        mostrar(reporte.tipo === 'perdida' ? `¡Qué alegría! ${nombre} volvió a casa.` : 'Gracias por devolverla a su familia.')
        cerrar()
        alTerminar()
        return
      }

      if (modo.value === 'eliminar') {
        await reportesService.eliminar(reporte.id)
        mostrar('Tu reporte fue eliminado.')
        cerrar()
        alTerminar(true)
        return
      }

      // Foto opcional del aviso: se sube primero y luego se adjunta
      if (foto) {
        const { data: subida } = await reportesService.subirFotoAviso(await prepararFoto(foto))
        cuerpo.foto_url = subida.foto_url
      }

      const enviar = {
        encontrada: reportesService.marcarEncontrada,
        avistamiento: reportesService.avistamiento,
        reclamar: reportesService.reclamar,
      }[modo.value]
      const { data } = await enviar(reporte.id, cuerpo)
      resultado.value = { mensaje: data.mensaje, contacto: data.contacto || null }
    } catch (e) {
      errorDialogo.value = textoError(e, 'No se pudo completar la acción')
    } finally {
      enviando.value = false
    }
  }

  // "Ya apareció" / "Ya la entregué": solo quien creó el reporte lo ve. Pide confirmación
  // antes de cerrar el reporte, porque es esa persona quien confirma que la mascota sí fue encontrada.
  function resolver(reporte) {
    abrir('resuelto', reporte)
  }

  // Eliminar un reporte propio (pide confirmación en la ventana)
  function eliminar(reporte) {
    abrir('eliminar', reporte)
  }

  return { eliminar, modo, seleccionada, enviando, errorDialogo, resultado, abrir, cerrar, confirmar, resolver }
}
