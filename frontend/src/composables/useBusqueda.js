import { ref, reactive, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import reportesService from '@/services/reportesService'

// Lógica compartida por Inicio (perdidas) y Encontradas: trae los reportes del servidor
// aplicando los filtros (ciudad, especie, raza, color, nombre) y los desplegables.
//   base: función que devuelve los filtros fijos de la pantalla, ej. () => ({ tipo: 'perdida', estado: 'abierto' })
export function useBusqueda(base, filtrosIniciales = {}) {
  const filtros = reactive({ q: '', ciudad: '', especie: '', raza: '', color: '', ...filtrosIniciales })
  const opciones = ref({ ciudades: [], especies: [], razas: [], colores: [] })
  const resultados = ref([])
  const cargando = ref(true)
  const error = ref('')

  const hayFiltros = computed(() => Object.values(filtros).some((v) => v))

  function mensajeError(e) {
    return e.response?.data?.error || 'No se pudo conectar con el servicio de reportes'
  }

  let ultimaPeticion = 0
  async function buscar(silencioso = false) {
    const numero = ++ultimaPeticion
    if (!silencioso) cargando.value = true
    error.value = ''
    const params = { ...base() }
    for (const [clave, valor] of Object.entries(filtros)) if (valor) params[clave] = valor
    try {
      const { data } = await reportesService.buscar(params)
      if (numero === ultimaPeticion) resultados.value = data.resultados // ignora respuestas viejas
    } catch (e) {
      if (numero === ultimaPeticion) error.value = mensajeError(e)
    } finally {
      if (numero === ultimaPeticion) cargando.value = false
    }
  }

  // Espera un momento al escribir para no llamar al servidor con cada letra
  let espera
  watch([filtros, () => JSON.stringify(base())], () => {
    clearTimeout(espera)
    espera = setTimeout(() => buscar(), 250)
  })
  onBeforeUnmount(() => clearTimeout(espera))

  onMounted(async () => {
    buscar()
    try {
      opciones.value = (await reportesService.filtros()).data
    } catch {
      /* los desplegables quedan vacíos; el error ya se muestra al buscar */
    }
  })

  function limpiar() {
    Object.keys(filtros).forEach((k) => (filtros[k] = ''))
  }

  function quitar(id) {
    resultados.value = resultados.value.filter((r) => r.id !== id)
  }

  return { filtros, opciones, resultados, cargando, error, hayFiltros, buscar, limpiar, quitar }
}
