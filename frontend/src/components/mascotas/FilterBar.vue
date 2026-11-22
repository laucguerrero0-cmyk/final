<script setup>
// Barra de filtros: nombre, ciudad, especie, raza y color.
// `filtros` es el objeto reactivo de useBusqueda: al cambiar un campo, la lista se vuelve a pedir al servidor.
defineProps({
  filtros: { type: Object, required: true },
  opciones: { type: Object, required: true },
  hayFiltros: { type: Boolean, default: false },
})
defineEmits(['limpiar'])
</script>

<template>
  <form class="filters card" role="search" aria-label="Filtrar mascotas" @submit.prevent>
    <div class="field f-wide">
      <label for="f-q">Buscar por nombre</label>
      <input id="f-q" v-model="filtros.q" type="search" placeholder="Ej: Max, Luna…" />
    </div>
    <div class="field">
      <label for="f-ciudad">Ciudad</label>
      <select id="f-ciudad" v-model="filtros.ciudad">
        <option value="">Todas</option>
        <option v-for="c in opciones.ciudades" :key="c">{{ c }}</option>
      </select>
    </div>
    <div class="field">
      <label for="f-especie">Especie</label>
      <select id="f-especie" v-model="filtros.especie">
        <option value="">Todas</option>
        <option v-for="e in opciones.especies" :key="e">{{ e }}</option>
      </select>
    </div>
    <div class="field">
      <label for="f-raza">Raza</label>
      <select id="f-raza" v-model="filtros.raza">
        <option value="">Todas</option>
        <option v-for="r in opciones.razas" :key="r">{{ r }}</option>
      </select>
    </div>
    <div class="field">
      <label for="f-color">Color</label>
      <select id="f-color" v-model="filtros.color">
        <option value="">Todos</option>
        <option v-for="c in opciones.colores" :key="c">{{ c }}</option>
      </select>
    </div>
    <button type="button" class="btn btn-secondary btn-sm f-clear" :disabled="!hayFiltros" @click="$emit('limpiar')">
      Limpiar filtros
    </button>
  </form>
</template>

<style scoped>
.filters {
  display: grid;
  grid-template-columns: 1.6fr repeat(4, 1fr) auto;
  align-items: end;
  gap: 0.9rem;
  padding: 1.1rem 1.2rem;
  margin-bottom: 1.4rem;
}

.field select,
.field input[type='search'] {
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 0.6rem 0.7rem;
  font-size: 0.92rem;
  font-family: inherit;
  background: var(--color-mist);
  color: var(--color-ink);
  min-width: 0;
}

.field select:focus,
.field input:focus {
  outline: 2px solid var(--color-teal);
  background: var(--color-white);
}

.f-clear { height: 2.5rem; white-space: nowrap; }

@media (max-width: 960px) {
  .filters { grid-template-columns: repeat(2, 1fr); }
  .f-wide { grid-column: 1 / -1; }
  .f-clear { grid-column: 1 / -1; }
}
</style>
