<script setup>
import { computed, ref } from 'vue'
import { ESPECIES, COLORES, unirSugerencias } from '@/utils/format'

// Barra de filtros: búsqueda general, ciudad, especie, raza y color.
// TODOS son de escritura libre: las listas son solo sugerencias y se puede escribir cualquier cosa
// (por ejemplo una especie o una raza que nadie ha registrado todavía).
// `filtros` es el objeto reactivo de useBusqueda: al cambiar un campo, la lista se vuelve a pedir al servidor.
const props = defineProps({
  filtros: { type: Object, required: true },
  opciones: { type: Object, required: true },
  hayFiltros: { type: Boolean, default: false },
})
defineEmits(['limpiar'])

const sugerencias = computed(() => ({
  ciudades: unirSugerencias(props.opciones.ciudades),
  especies: unirSugerencias(ESPECIES, props.opciones.especies),
  razas: unirSugerencias(props.opciones.razas),
  colores: unirSugerencias(COLORES, props.opciones.colores),
}))

// En el celular los filtros avanzados se esconden detrás de un botón para no ocupar toda la pantalla
const abierto = ref(false)
const activos = computed(() => ['ciudad', 'especie', 'raza', 'color'].filter((c) => props.filtros[c]).length)
</script>

<template>
  <form class="filters card" role="search" aria-label="Filtrar mascotas" @submit.prevent>
    <div class="field f-wide">
      <label for="f-q">Buscar</label>
      <input
        id="f-q"
        v-model="filtros.q"
        type="search"
        enterkeyhint="search"
        autocomplete="off"
        placeholder="Nombre, raza, color, barrio…"
      />
    </div>

    <button
      type="button"
      class="btn btn-secondary btn-sm f-toggle"
      :aria-expanded="abierto"
      aria-controls="f-extra"
      @click="abierto = !abierto"
    >
      {{ abierto ? 'Ocultar filtros' : 'Más filtros' }}<span v-if="activos && !abierto"> ({{ activos }})</span>
    </button>

    <div id="f-extra" class="f-extra" :class="{ 'f-extra--open': abierto }">
      <div class="field">
        <label for="f-ciudad">Ciudad</label>
        <input id="f-ciudad" v-model="filtros.ciudad" type="text" list="dl-ciudad" autocomplete="off" placeholder="Ej: Popayán" />
        <datalist id="dl-ciudad"><option v-for="c in sugerencias.ciudades" :key="c" :value="c" /></datalist>
      </div>
      <div class="field">
        <label for="f-especie">Especie</label>
        <input id="f-especie" v-model="filtros.especie" type="text" list="dl-especie" autocomplete="off" placeholder="Perro, gato, conejo…" />
        <datalist id="dl-especie"><option v-for="e in sugerencias.especies" :key="e" :value="e" /></datalist>
      </div>
      <div class="field">
        <label for="f-raza">Raza</label>
        <input id="f-raza" v-model="filtros.raza" type="text" list="dl-raza" autocomplete="off" placeholder="Ej: Labrador, criollo" />
        <datalist id="dl-raza"><option v-for="r in sugerencias.razas" :key="r" :value="r" /></datalist>
      </div>
      <div class="field">
        <label for="f-color">Color</label>
        <input id="f-color" v-model="filtros.color" type="text" list="dl-color" autocomplete="off" placeholder="Ej: negro, tricolor" />
        <datalist id="dl-color"><option v-for="c in sugerencias.colores" :key="c" :value="c" /></datalist>
      </div>
    </div>

    <button type="button" class="btn btn-secondary btn-sm f-clear" :disabled="!hayFiltros" @click="$emit('limpiar')">
      Limpiar filtros
    </button>
  </form>
</template>

<style scoped>
.filters {
  display: grid;
  grid-template-columns: 1.6fr 4fr auto;
  align-items: end;
  gap: 0.9rem;
  padding: 1.1rem 1.2rem;
  margin-bottom: 1.4rem;
}

/* En pantallas grandes las 4 casillas van en una sola fila junto al buscador */
.f-extra {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.9rem;
}

.f-toggle { display: none; }

.field input[type='search'],
.field input[type='text'] {
  min-width: 0;
  font-size: 0.92rem;
}

.field input:focus {
  outline: 2px solid var(--color-teal);
  background: var(--color-white);
}

.f-clear { height: 2.5rem; white-space: nowrap; }

@media (max-width: 960px) {
  .filters { grid-template-columns: 1fr auto; padding: 1rem; }
  .f-wide { grid-column: 1 / -1; }
  .f-toggle { display: inline-flex; grid-column: 1; height: 2.75rem; }
  .f-clear { grid-column: 2; height: 2.75rem; }
  .f-extra { display: none; grid-column: 1 / -1; grid-template-columns: 1fr 1fr; }
  .f-extra--open { display: grid; }
}

@media (max-width: 480px) {
  .f-extra { grid-template-columns: 1fr; }
}
</style>
