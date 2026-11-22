<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBusqueda } from '@/composables/useBusqueda'
import { useAcciones } from '@/composables/useAcciones'
import PetCard from '@/components/mascotas/PetCard.vue'
import FilterBar from '@/components/mascotas/FilterBar.vue'
import ActionDialog from '@/components/mascotas/ActionDialog.vue'
import PawIcon from '@/components/layout/PawIcon.vue'

const auth = useAuthStore()
const route = useRoute()

// '' = todas | 'abierto' = buscan a su dueño | 'resuelto' = ya reunidas
const estado = ref('')
const ESTADOS = [
  { valor: '', texto: 'Todas' },
  { valor: 'abierto', texto: 'Buscan a su dueño' },
  { valor: 'resuelto', texto: 'Ya reunidas' },
]

const { filtros, opciones, resultados, cargando, error, hayFiltros, buscar, limpiar } = useBusqueda(
  () => ({ tipo: 'encontrada', ...(estado.value ? { estado: estado.value } : {}) }),
  { q: route.query.q || '' },
)

const acciones = useAcciones(() => buscar(true))
const titulo = computed(() => ESTADOS.find((e) => e.valor === estado.value).texto)
</script>

<template>
  <section class="page">
    <header class="page-head">
      <h1>Mascotas encontradas</h1>
      <p class="page-subtitle">
        Personas como tú las encontraron. Si reconoces a alguna, avísale a quien la tiene con un clic.
      </p>
    </header>

    <div class="chips head-chips" role="group" aria-label="Estado">
      <button
        v-for="e in ESTADOS"
        :key="e.valor"
        class="chip"
        :class="{ 'chip--on': estado === e.valor }"
        :aria-pressed="estado === e.valor"
        @click="estado = e.valor"
      >
        {{ e.texto }}
      </button>
    </div>

    <FilterBar :filtros="filtros" :opciones="opciones" :hay-filtros="hayFiltros" @limpiar="limpiar" />

    <p v-if="error" class="alert alert-error alert-flex" role="alert">
      {{ error }}
      <button class="btn btn-secondary btn-sm" @click="buscar()">Reintentar</button>
    </p>

    <div v-if="cargando" class="pet-grid" aria-hidden="true">
      <div v-for="n in 3" :key="n" class="skeleton"></div>
    </div>

    <div v-else-if="resultados.length" class="pet-grid">
      <PetCard
        v-for="r in resultados"
        :key="r.id"
        :reporte="r"
        :es-mio="r.usuario_id === auth.usuario?.id"
        @reclamar="acciones.abrir('reclamar', $event)"
        @resuelto="acciones.resolver"
      />
    </div>

    <div v-else-if="!error" class="empty card">
      <PawIcon class="empty-paw" />
      <h3>No hay resultados en «{{ titulo }}»</h3>
      <p>{{ hayFiltros ? 'Prueba con otros filtros.' : 'Cuando alguien reporte un hallazgo aparecerá aquí.' }}</p>
    </div>

    <ActionDialog
      :modo="acciones.modo.value"
      :reporte="acciones.seleccionada.value"
      :enviando="acciones.enviando.value"
      :error="acciones.errorDialogo.value"
      @confirmar="acciones.confirmar"
      @cerrar="acciones.cerrar"
    />
  </section>
</template>

<style scoped>
.head-chips { margin-bottom: 1.2rem; }
.empty-paw { font-size: 3rem; color: var(--color-sun); }
</style>
