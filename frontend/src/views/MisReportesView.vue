<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAcciones } from '@/composables/useAcciones'
import { useAutoRefresh } from '@/composables/useAutoRefresh'
import reportesService from '@/services/reportesService'
import PetCard from '@/components/mascotas/PetCard.vue'
import ActionDialog from '@/components/mascotas/ActionDialog.vue'
import PawIcon from '@/components/layout/PawIcon.vue'

// "Mis reportes": solo lo que yo publiqué (mascotas que perdí o que encontré), con cuántos avisos tiene cada uno.
const auth = useAuthStore()

const lista = ref([])
const cargando = ref(true)
const error = ref('')
const filtro = ref('abiertos')

async function cargar(silencioso = false) {
  if (!silencioso) cargando.value = true
  try {
    lista.value = (await reportesService.mios()).data.resultados
    error.value = ''
  } catch (e) {
    if (!silencioso || !lista.value.length) {
      error.value = e.response ? e.response.data?.error || 'No se pudieron cargar tus reportes' : 'No se pudo conectar con el servidor'
    }
  } finally {
    cargando.value = false
  }
}
onMounted(cargar)
useAutoRefresh(() => cargar(true))

const acciones = useAcciones(() => cargar(true))

const abiertos = computed(() => lista.value.filter((r) => r.estado === 'abierto'))
const cerrados = computed(() => lista.value.filter((r) => r.estado !== 'abierto'))
const visibles = computed(() => (filtro.value === 'abiertos' ? abiertos.value : filtro.value === 'cerrados' ? cerrados.value : lista.value))
const porRevisar = computed(() => abiertos.value.reduce((n, r) => n + (Number(r.por_revisar) || 0), 0))

const FILTROS = computed(() => [
  { valor: 'abiertos', texto: `Abiertos (${abiertos.value.length})` },
  { valor: 'cerrados', texto: `Con final feliz (${cerrados.value.length})` },
  { valor: 'todos', texto: `Todos (${lista.value.length})` },
])
</script>

<template>
  <section class="page">
    <header class="page-head">
      <h1>Mis reportes</h1>
      <p class="page-subtitle">Las mascotas que reportaste como perdidas o encontradas. Aquí puedes corregirlas, revisar los avisos o eliminarlas.</p>
    </header>

    <p v-if="porRevisar" class="alert aviso" role="status">
      🔔 Tienes <strong>{{ porRevisar }}</strong> aviso{{ porRevisar === 1 ? '' : 's' }} por revisar. Entra a «Ver historial» de la tarjeta para confirmar si es tu mascota.
    </p>

    <div class="chips" role="group" aria-label="Filtrar mis reportes">
      <button v-for="f in FILTROS" :key="f.valor" type="button" class="chip" :class="{ 'chip--on': filtro === f.valor }" :aria-pressed="filtro === f.valor" @click="filtro = f.valor">
        {{ f.texto }}
      </button>
    </div>

    <div v-if="cargando" class="pet-grid" aria-hidden="true">
      <div v-for="n in 3" :key="n" class="skeleton sk-card"></div>
    </div>

    <p v-else-if="error" class="alert alert-error alert-flex" role="alert">
      {{ error }}
      <button class="btn btn-secondary btn-sm" @click="cargar()">Reintentar</button>
    </p>

    <div v-else-if="visibles.length" class="pet-grid">
      <PetCard
        v-for="r in visibles"
        :key="r.id"
        :reporte="r"
        es-mio
        @resuelto="acciones.resolver"
        @eliminar="acciones.eliminar"
      />
    </div>

    <div v-else class="empty card">
      <PawIcon class="empty-paw" />
      <h3>{{ lista.length ? 'No hay reportes en esta lista' : 'Todavía no has reportado ninguna mascota' }}</h3>
      <p v-if="!lista.length">Si perdiste a tu mascota o encontraste una, publícala para que la comunidad te ayude.</p>
      <RouterLink to="/reportar" class="btn btn-sun">+ Reportar una mascota</RouterLink>
    </div>

    <ActionDialog
      :modo="acciones.modo.value"
      :reporte="acciones.seleccionada.value"
      :enviando="acciones.enviando.value"
      :error="acciones.errorDialogo.value"
      :resultado="acciones.resultado.value"
      @confirmar="acciones.confirmar"
      @cerrar="acciones.cerrar"
    />
  </section>
</template>

<style scoped>
.aviso { background: var(--color-sun-soft); border: 1px solid var(--color-sun); color: var(--color-ink); margin-bottom: 1rem; }
.chips { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.2rem; }
.sk-card { height: 380px; }
.empty-paw { font-size: 3rem; color: var(--color-sun); }
.empty .btn { margin-top: 1rem; }
</style>
