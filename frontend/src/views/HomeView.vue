<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBusqueda } from '@/composables/useBusqueda'
import { useAcciones } from '@/composables/useAcciones'
import { useAutoRefresh } from '@/composables/useAutoRefresh'
import reportesService from '@/services/reportesService'
import PetCard from '@/components/mascotas/PetCard.vue'
import FilterBar from '@/components/mascotas/FilterBar.vue'
import ActionDialog from '@/components/mascotas/ActionDialog.vue'
import PawIcon from '@/components/layout/PawIcon.vue'

const auth = useAuthStore()
const route = useRoute()

// Mascotas perdidas que todavía no aparecen. Si llegamos desde una notificación, ?q= trae el nombre.
const { filtros, opciones, resultados, cargando, error, hayFiltros, buscar, limpiar } = useBusqueda(
  () => ({ tipo: 'perdida', estado: 'abierto' }),
  { q: route.query.q || '' },
)

const resumen = ref({ perdidas: 0, encontradas: 0, reunidas: 0 })
async function cargarResumen() {
  try {
    resumen.value = (await reportesService.resumen()).data
  } catch {
    /* los números quedan en 0; el error de conexión ya se muestra en la lista */
  }
}
onMounted(cargarResumen)
useAutoRefresh(cargarResumen)

const acciones = useAcciones(() => {
  buscar(true)
  cargarResumen()
})
</script>

<template>
  <section class="page home">
    <!-- Hero: mensaje, CTA principal y números -->
    <header class="hero">
      <div class="hero-copy">
        <p class="hero-eyebrow">Hola, {{ auth.usuario?.nombre?.split(' ')[0] }} 👋</p>
        <h1>Ayúdanos a traerlas de vuelta a casa</h1>
        <p class="page-subtitle">
          Estas mascotas siguen perdidas. Si viste a alguna, avísalo con un clic: puede ser el mejor día para su
          familia.
        </p>
        <div class="hero-buttons">
          <a href="#perdidas" class="btn hero-cta">Ver mascotas perdidas ↓</a>
          <RouterLink to="/reportar" class="btn btn-sun">+ Reportar una mascota</RouterLink>
        </div>
      </div>

      <div class="hero-stats" aria-live="polite">
        <div class="stat stat--sun">
          <PawIcon class="stat-paw" />
          <strong>{{ resumen.perdidas }}</strong>
          <span>esperan volver a casa</span>
        </div>
        <RouterLink to="/encontradas" class="stat stat--teal">
          <strong>{{ resumen.encontradas }}</strong>
          <span>fueron encontradas</span>
        </RouterLink>
        <div class="stat stat--ok">
          <strong>{{ resumen.reunidas }}</strong>
          <span>ya volvieron con su familia</span>
        </div>
      </div>
    </header>

    <div class="list-head" id="perdidas">
      <h2>Mascotas perdidas</h2>
      <p v-if="!cargando" class="list-count">{{ resultados.length }} resultado{{ resultados.length === 1 ? '' : 's' }}</p>
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
        @encontrada="acciones.abrir('encontrada', $event)"
        @avistamiento="acciones.abrir('avistamiento', $event)"
        @resuelto="acciones.resolver"
        @eliminar="acciones.eliminar"
      />
    </div>

    <div v-else-if="!error" class="empty card">
      <PawIcon class="empty-paw" />
      <template v-if="hayFiltros">
        <h3>Ninguna mascota coincide con tu búsqueda</h3>
        <p>Prueba con otra ciudad, raza o color.</p>
        <button class="btn btn-secondary" @click="limpiar">Limpiar filtros</button>
      </template>
      <template v-else>
        <h3>¡Todas las mascotas están a salvo!</h3>
        <p>No hay reportes de mascotas perdidas por ahora.</p>
      </template>
    </div>

    <!-- Banner de planes -->
    <aside class="plans-banner">
      <div>
        <h2>¿Eres una fundación o una veterinaria?</h2>
        <p>Con nuestros planes publicas más reportes, destacas tus casos y recibes alertas prioritarias.</p>
      </div>
      <RouterLink to="/planes" class="btn btn-sun">Ver planes y precios</RouterLink>
    </aside>

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
.hero {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 2.5rem;
  padding: 1.4rem 0 2.2rem;
}

.hero-eyebrow { font-weight: 800; color: var(--color-teal); margin-bottom: 0.3rem; }
.hero h1 { font-size: 2.6rem; max-width: 18ch; }
.hero .page-subtitle { max-width: 48ch; font-size: 1.05rem; margin-top: 0.7rem; }

.hero-buttons { display: flex; flex-wrap: wrap; gap: 0.7rem; margin-top: 1.3rem; }

.hero-cta {
  background: var(--color-teal);
  color: var(--color-white);
  padding: 0.8rem 1.6rem;
  font-size: 1rem;
}
.hero-cta:hover { background: var(--color-teal-dark); }
.hero-buttons .btn-sun { padding: 0.8rem 1.6rem; font-size: 1rem; }

.hero-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.8rem;
  width: 340px;
}

.stat {
  display: flex;
  flex-direction: column;
  padding: 1rem 1.1rem;
  border-radius: 22px;
  font-weight: 700;
  text-decoration: none;
  box-shadow: 0 10px 22px var(--color-shadow);
  line-height: 1.25;
}
.stat strong { font-family: var(--font-title); font-size: 2.6rem; line-height: 1.1; }
.stat span { font-size: 0.85rem; }
.stat--sun { grid-column: 1 / -1; background: var(--color-sun); align-items: center; text-align: center; border-radius: 28px; padding: 1.3rem; }
.stat--sun strong { font-size: 3.6rem; }
.stat-paw { font-size: 1.6rem; opacity: 0.8; }
.stat--teal { background: var(--color-teal); color: var(--color-white); }
.stat--teal:hover { background: var(--color-teal-dark); }
.stat--ok { background: var(--color-success-soft); color: var(--color-success); }

.list-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
  scroll-margin-top: 5rem;
}
.list-head h2 { font-size: 1.6rem; }
.list-count { color: var(--color-ink-soft); font-weight: 700; font-size: 0.9rem; }

.empty-paw { font-size: 3rem; color: var(--color-sun); }
.empty .btn { margin-top: 1rem; }

.plans-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1.2rem;
  margin-top: 3rem;
  padding: 1.8rem 2rem;
  border-radius: 24px;
  background: var(--color-ink);
  color: var(--color-white);
}
.plans-banner h2 { font-size: 1.4rem; }
.plans-banner p { color: #cfe3e0; margin-top: 0.3rem; max-width: 52ch; }

@media (max-width: 860px) {
  .hero { grid-template-columns: 1fr; gap: 1.5rem; padding: 0.6rem 0 1.4rem; }
  .hero h1 { font-size: 1.9rem; }
  .hero-stats { width: 100%; }
}

@media (max-width: 560px) {
  .hero h1 { font-size: 1.65rem; }
  .hero .page-subtitle { font-size: 0.98rem; }
  .hero-buttons .btn { flex: 1 1 100%; min-height: 48px; }
  .stat { padding: 0.8rem 0.9rem; }
  .stat strong { font-size: 2.1rem; }
  .stat--sun { padding: 1rem; }
  .stat--sun strong { font-size: 3rem; }
  .plans-banner { padding: 1.3rem 1.2rem; margin-top: 2rem; }
  .plans-banner .btn { width: 100%; }
}
</style>
