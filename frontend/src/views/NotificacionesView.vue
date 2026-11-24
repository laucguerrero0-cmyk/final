<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAutoRefresh } from '@/composables/useAutoRefresh'
import notificacionesService from '@/services/notificacionesService'
import { useNotificacionesStore } from '@/stores/notificaciones'
import { useToast } from '@/composables/useToast'
import { haceTiempo, urlFoto } from '@/utils/format'
import PetAvatar from '@/components/mascotas/PetAvatar.vue'
import PawIcon from '@/components/layout/PawIcon.vue'

const router = useRouter()
const store = useNotificacionesStore()
const { mostrar } = useToast()

const lista = ref([])
const cargando = ref(true)
const error = ref('')
const filtro = ref('todas')

const TIPOS = {
  nuevo_reporte: { etiqueta: 'Nuevo reporte', icono: '📢', clase: 't-new' },
  avistamiento: { etiqueta: 'Avistamiento', icono: '👀', clase: 't-sight' },
  encontrada: { etiqueta: 'Encontrada', icono: '💚', clase: 't-found' },
  reclamo: { etiqueta: 'Reclamo', icono: '🙋', clase: 't-claim' },
}
const FILTROS = [
  { valor: 'todas', texto: 'Todas' },
  { valor: 'mias', texto: 'Sobre mis reportes' },
  { valor: 'nuevo_reporte', texto: 'Nuevos reportes' },
  { valor: 'avistamiento', texto: 'Avistamientos' },
  { valor: 'encontrada', texto: 'Encontradas' },
]

const visibles = computed(() =>
  lista.value.filter((n) =>
    filtro.value === 'todas' ? true : filtro.value === 'mias' ? n.sobre_mi_reporte : n.tipo === filtro.value,
  ),
)
const sinLeer = computed(() => lista.value.filter((n) => !n.leida).length)

async function cargar() {
  try {
    error.value = ''
    lista.value = (await notificacionesService.listar()).data.notificaciones
  } catch (e) {
    error.value = e.response?.data?.error || 'No se pudieron cargar las notificaciones'
  } finally {
    cargando.value = false
  }
}
onMounted(cargar)
useAutoRefresh(cargar)

async function marcarLeidas() {
  try {
    await store.marcarLeidas()
    lista.value.forEach((n) => (n.leida = true))
  } catch {
    mostrar('No se pudo marcar como leídas', 'error')
  }
}

// Al abrir una notificación se va al historial de esa mascota, donde está el detalle de la novedad
// (y, si es tu reporte, los botones para confirmar el aviso y contactar a quien lo dejó).
function abrir(n) {
  if (n.reporte_id) {
    router.push({ name: 'historial', params: { id: n.reporte_id } })
    return
  }
  const destino = n.tipo === 'nuevo_reporte' || n.tipo === 'avistamiento' ? '/' : '/encontradas'
  router.push({ path: destino, query: n.mascota && n.mascota !== 'Sin nombre' ? { q: n.mascota } : {} })
}
</script>

<template>
  <section class="page">
    <header class="page-head head-row">
      <div>
        <h1>Notificaciones</h1>
        <p class="page-subtitle">Lo último que pasa en la comunidad: reportes nuevos, avistamientos y mascotas encontradas.</p>
      </div>
      <button class="btn btn-secondary" :disabled="!sinLeer" @click="marcarLeidas">
        Marcar todo como leído <span v-if="sinLeer" class="count">{{ sinLeer }}</span>
      </button>
    </header>

    <div class="chips filters" role="group" aria-label="Filtrar notificaciones">
      <button v-for="f in FILTROS" :key="f.valor" class="chip" :class="{ 'chip--on': filtro === f.valor }" :aria-pressed="filtro === f.valor" @click="filtro = f.valor">
        {{ f.texto }}
      </button>
    </div>

    <p v-if="error" class="alert alert-error" role="alert">{{ error }}</p>

    <div v-if="cargando" aria-hidden="true"><div v-for="n in 4" :key="n" class="skeleton row-skeleton"></div></div>

    <ul v-else-if="visibles.length" class="feed">
      <li v-for="n in visibles" :key="n.id">
        <button class="item" :class="{ unread: !n.leida, mine: n.sobre_mi_reporte }" @click="abrir(n)">
          <span class="thumb">
            <img v-if="n.foto_url" :src="urlFoto(n.foto_url)" alt="" />
            <PetAvatar v-else :especie="n.especie" :color="n.color" />
            <span class="icon" :class="TIPOS[n.tipo].clase" aria-hidden="true">{{ TIPOS[n.tipo].icono }}</span>
          </span>
          <span class="text">
            <span class="meta">
              <span class="tag" :class="TIPOS[n.tipo].clase">{{ TIPOS[n.tipo].etiqueta }}</span>
              <span v-if="n.sobre_mi_reporte" class="tag t-mine">Sobre tu reporte</span>
              <span class="time">{{ haceTiempo(n.creado_en) }}</span>
            </span>
            <span class="msg">{{ n.mensaje }}</span>
            <span class="go">{{ n.reporte_id ? 'Ver historial →' : 'Ver mascota →' }}</span>
          </span>
          <span v-if="!n.leida" class="dot" aria-label="Sin leer"></span>
        </button>
      </li>
    </ul>

    <div v-else-if="!error" class="empty card">
      <PawIcon class="empty-paw" />
      <h3>Aquí no hay nada todavía</h3>
      <p>Cuando alguien reporte, vea o encuentre una mascota, te lo contamos aquí.</p>
    </div>
  </section>
</template>

<style scoped>
.head-row { display: flex; align-items: flex-end; justify-content: space-between; flex-wrap: wrap; gap: 1rem; }
.count { background: var(--color-danger); color: #fff; border-radius: 999px; padding: 0 0.5rem; font-size: 0.78rem; }
.filters { margin-bottom: 1.2rem; }
.row-skeleton { height: 92px; margin-bottom: 0.8rem; }

.feed { list-style: none; padding: 0; display: grid; gap: 0.8rem; }

.item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 1rem;
  text-align: left;
  padding: 0.9rem 1.1rem;
  background: var(--color-white);
  color: var(--color-ink);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  box-shadow: 0 4px 12px var(--color-shadow);
  transition: transform 0.15s, box-shadow 0.15s;
}
.item:hover { transform: translateY(-2px); box-shadow: 0 10px 22px var(--color-shadow); }
.item.unread { border-left: 5px solid var(--color-teal); background: #f7fcfb; }
.item.mine { border-left-color: var(--color-sun); background: #fffaf0; }

.thumb { position: relative; flex: none; width: 64px; height: 64px; border-radius: 50%; }
.thumb > img, .thumb > :deep(.avatar) { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; overflow: hidden; }
.icon {
  position: absolute;
  right: -6px;
  bottom: -4px;
  width: 26px;
  height: 26px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  font-size: 0.85rem;
  border: 2px solid #fff;
}

.text { display: flex; flex-direction: column; gap: 0.25rem; flex: 1; min-width: 0; }
.meta { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem; }
.tag { padding: 0.1rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 800; }
.time { font-size: 0.8rem; color: var(--color-ink-soft); font-weight: 700; }
.msg { font-weight: 700; }
.go { font-size: 0.82rem; font-weight: 800; color: var(--color-teal); }

.t-new { background: #e1ecfb; color: #1f56a5; }
.t-sight { background: #ede4fb; color: #5b34a5; }
.t-found { background: var(--color-success-soft); color: var(--color-success); }
.t-claim { background: var(--color-sun-soft); color: #8a5a00; }
.t-mine { background: var(--color-sun); color: var(--color-ink); }
.icon.t-new { background: #e1ecfb; } .icon.t-sight { background: #ede4fb; }
.icon.t-found { background: var(--color-success-soft); } .icon.t-claim { background: var(--color-sun-soft); }

.dot { flex: none; width: 12px; height: 12px; border-radius: 50%; background: var(--color-teal); }
.empty-paw { font-size: 3rem; color: var(--color-sun); }

@media (max-width: 560px) {
  .item { gap: 0.75rem; padding: 0.8rem; }
  .thumb { width: 52px; height: 52px; }
  .msg { font-size: 0.95rem; overflow-wrap: anywhere; }
  .head-row .btn { width: 100%; }
}
</style>
