<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAcciones } from '@/composables/useAcciones'
import { useAutoRefresh } from '@/composables/useAutoRefresh'
import { useToast } from '@/composables/useToast'
import reportesService from '@/services/reportesService'
import { haceTiempo, parseFecha, urlFoto, partesConEnlaces } from '@/utils/format'
import PetAvatar from '@/components/mascotas/PetAvatar.vue'
import ContactoCard from '@/components/mascotas/ContactoCard.vue'
import ActionDialog from '@/components/mascotas/ActionDialog.vue'

// Historial de una mascota: el reporte y todo lo que ha pasado con él (avistamientos, avisos de hallazgo,
// reclamos y el final feliz). Quien publicó el reporte ve aquí los avisos de los demás, puede llamar o escribir
// a quien los dejó y confirmar si de verdad era su mascota.
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const { mostrar } = useToast()

const reporte = ref(null)
const esDueno = ref(false)
const eventos = ref([])
const cargando = ref(true)
const error = ref('')
const revisando = ref(null) // id del aviso que se está confirmando o descartando

const id = computed(() => route.params.id)

async function cargar(silencioso = false) {
  if (!id.value) return
  if (!silencioso) cargando.value = true
  error.value = ''
  try {
    const { data } = await reportesService.historial(id.value)
    reporte.value = data.reporte
    esDueno.value = data.es_dueno
    eventos.value = data.eventos
  } catch (e) {
    if (silencioso && reporte.value && e.response?.status !== 404) return // fallo pasajero: se conserva lo que ya se ve
    reporte.value = null
    error.value = e.response ? e.response.data?.error || 'No se pudo cargar el historial' : 'No se pudo conectar con el servidor'
  } finally {
    cargando.value = false
  }
}
onMounted(() => cargar())
useAutoRefresh(() => cargar(true)) // se actualiza solo: avisos nuevos, confirmaciones, final feliz
watch(id, () => {
  contactoPublicador.value = null
  cargar()
})

const acciones = useAcciones((eliminado) => {
  if (eliminado) router.replace('/mis-reportes') // el reporte ya no existe
  else cargar(true)
})
const fotoAmpliada = ref('')

const r = computed(() => reporte.value)
const perdida = computed(() => r.value?.tipo === 'perdida')
const abierto = computed(() => r.value?.estado === 'abierto')
const titulo = computed(() => (r.value?.mascota === 'Sin nombre' ? `${r.value.especie} sin nombre` : r.value?.mascota))
const detalles = computed(() => [r.value?.especie, r.value?.raza, r.value?.color].filter(Boolean))
const foto = computed(() => urlFoto(r.value?.foto_url))
const fotoRota = ref(false)
const volverA = computed(() => (perdida.value ? '/' : '/encontradas'))
const porRevisar = computed(() => eventos.value.filter((e) => e.puede_revisar).length)
const yo = computed(() => auth.usuario?.id)

// ---- Cómo se muestra cada evento de la línea de tiempo
function presentar(e) {
  if (e.clase === 'reporte') {
    return e.tipo === 'perdida'
      ? { icono: '📢', titulo: 'Reporte de pérdida', tono: 'perdida' }
      : { icono: '🏠', titulo: 'Reporte de mascota encontrada', tono: 'encontrada' }
  }
  const tipos = {
    avistamiento: { icono: '👀', titulo: 'La vieron por aquí', tono: 'avistamiento' },
    hallazgo: { icono: '💚', titulo: 'Dicen que la encontraron', tono: 'encontrada' },
    reclamo: { icono: '🙋', titulo: 'Alguien cree que es su mascota', tono: 'reclamo' },
    resuelto: { icono: '🎉', titulo: 'Final feliz: ya está con su familia', tono: 'ok' },
  }
  return tipos[e.tipo] || { icono: '📌', titulo: 'Novedad', tono: 'avistamiento' }
}

const ESTADOS_AVISO = {
  abierta: { texto: 'Por confirmar', clase: 'st-wait' },
  confirmada: { texto: 'Confirmado', clase: 'st-ok' },
  descartada: { texto: 'Descartado', clase: 'st-no' },
}

function quien(e) {
  return e.usuario_id === yo.value ? 'Tú' : e.usuario
}

const fechaLarga = (texto) => parseFecha(texto).toLocaleString('es-CO', { dateStyle: 'medium', timeStyle: 'short' })

// "Vista hace 20 min" solo cuando la persona dijo que la vio antes de avisar
function vistaHace(e) {
  return e.tipo === 'avistamiento' && e.visto_en && e.visto_en !== e.fecha ? haceTiempo(e.visto_en) : ''
}

function mensajeWhatsapp(e) {
  const nombre = e.contacto?.nombre?.split(' ')[0]
  const mascota = r.value?.mascota === 'Sin nombre' ? 'la mascota' : r.value?.mascota
  return `Hola${nombre ? ' ' + nombre : ''}, te escribo por ${mascota} (la vi en Mascotas). Gracias por avisar.`
}

// ---- Quien publicó el reporte confirma o descarta un aviso
async function revisar(evento, confirmar) {
  revisando.value = evento.id
  try {
    const llamada = confirmar ? reportesService.confirmarNovedad : reportesService.descartarNovedad
    const { data } = await llamada(evento.reporte_id, evento.id)
    mostrar(data.mensaje)
    await cargar(true)
  } catch (e) {
    mostrar(e.response?.data?.error || 'No se pudo guardar tu respuesta', 'error')
  } finally {
    revisando.value = null
  }
}

// ---- Contacto de quien publicó el reporte (para quien no es el dueño)
const contactoPublicador = ref(null)
const verContacto = ref(false)
const cargandoContacto = ref(false)

async function mostrarContacto() {
  if (verContacto.value) {
    verContacto.value = false
    return
  }
  if (!contactoPublicador.value) {
    cargandoContacto.value = true
    try {
      const { data } = await reportesService.contacto(r.value.id)
      contactoPublicador.value = data.contacto || {}
    } catch (e) {
      mostrar(e.response?.data?.error || 'No se pudo obtener el contacto', 'error')
      cargandoContacto.value = false
      return
    }
    cargandoContacto.value = false
  }
  verContacto.value = true
}

const mensajeAlPublicador = computed(() => {
  const nombre = contactoPublicador.value?.nombre?.split(' ')[0]
  const mascota = r.value?.mascota === 'Sin nombre' ? 'la mascota' : r.value?.mascota
  return `Hola${nombre ? ' ' + nombre : ''}, vi tu reporte de ${mascota} en Mascotas y quiero ayudarte.`
})
</script>

<template>
  <section class="page historial">
    <RouterLink :to="volverA" class="volver">← Volver a {{ perdida || cargando ? 'mascotas perdidas' : 'mascotas encontradas' }}</RouterLink>

    <div v-if="cargando" aria-hidden="true">
      <div class="skeleton sk-head"></div>
      <div class="skeleton sk-line" v-for="n in 3" :key="n"></div>
    </div>

    <p v-else-if="error" class="alert alert-error alert-flex" role="alert">
      {{ error }}
      <button class="btn btn-secondary btn-sm" @click="cargar()">Reintentar</button>
    </p>

    <template v-else-if="r">
      <!-- Ficha de la mascota -->
      <header class="ficha card">
        <div class="ficha-foto">
          <img v-if="foto && !fotoRota" :src="foto" :alt="`Foto de ${titulo}`" @error="fotoRota = true" />
          <PetAvatar v-else :especie="r.especie" :color="r.color" />
        </div>
        <div class="ficha-info">
          <div class="ficha-titulo">
            <h1>{{ titulo }}</h1>
            <span class="badge" :class="!abierto ? 'is-ok' : perdida ? 'is-lost' : 'is-found'">
              {{ !abierto ? 'Final feliz' : perdida ? 'Perdida' : 'Encontrada' }}
            </span>
          </div>
          <ul class="tags" aria-label="Características">
            <li v-for="d in detalles" :key="d">{{ d }}</li>
          </ul>
          <p v-if="r.descripcion_mascota" class="ficha-desc">{{ r.descripcion_mascota }}</p>
          <p class="ficha-meta">
            {{ perdida ? 'Vista por última vez en' : 'Encontrada en' }} <strong>{{ r.lugar }}</strong> ·
            reportó {{ r.usuario_id === yo ? 'tú' : r.reportado_por }}
          </p>
        </div>
      </header>

      <!-- Acciones: cambian según quién mira -->
      <div v-if="abierto" class="acciones">
        <template v-if="esDueno">
          <p v-if="porRevisar" class="aviso-revisar">
            🔔 Tienes <strong>{{ porRevisar }}</strong> aviso{{ porRevisar === 1 ? '' : 's' }} por revisar. Confirma abajo si
            es tu mascota.
          </p>
          <button class="btn btn-cta" @click="acciones.resolver(r)">
            {{ perdida ? 'Ya apareció' : 'Ya la entregué' }}
          </button>
          <RouterLink :to="{ name: 'editar', params: { id: r.id } }" class="btn btn-secondary">✏️ Editar</RouterLink>
          <button class="btn btn-secondary btn-borrar" @click="acciones.eliminar(r)">🗑️ Eliminar</button>
        </template>
        <template v-else>
          <button v-if="perdida" class="btn btn-cta" @click="acciones.abrir('encontrada', r)">¡La encontré!</button>
          <button v-else class="btn btn-cta" @click="acciones.abrir('reclamar', r)">¡Es mi mascota!</button>
          <button v-if="perdida" class="btn btn-secondary" @click="acciones.abrir('avistamiento', r)">La vi por aquí</button>
          <button class="btn btn-secondary" :disabled="cargandoContacto" :aria-expanded="verContacto" @click="mostrarContacto">
            {{ verContacto ? 'Ocultar contacto' : cargandoContacto ? 'Buscando…' : 'Contactar a quien publicó' }}
          </button>
        </template>
      </div>
      <ContactoCard v-if="verContacto" class="contacto-publicador" :contacto="contactoPublicador" :mensaje="mensajeAlPublicador" />

      <!-- Línea de tiempo -->
      <h2 class="lt-titulo">Historial</h2>
      <ol class="lt">
        <li v-for="e in eventos" :key="e.clave" class="lt-item" :class="`tono-${presentar(e).tono}`">
          <span class="lt-icono" aria-hidden="true">{{ presentar(e).icono }}</span>
          <div class="lt-cuerpo">
            <div class="lt-cabecera">
              <h3>{{ presentar(e).titulo }}</h3>
              <span v-if="ESTADOS_AVISO[e.estado] && ['hallazgo', 'reclamo'].includes(e.tipo)" class="estado" :class="ESTADOS_AVISO[e.estado].clase">
                {{ ESTADOS_AVISO[e.estado].texto }}
              </span>
            </div>
            <p class="lt-quien">
              <template v-if="e.tipo !== 'resuelto'">Por {{ quien(e) }} · </template>
              <time :datetime="e.fecha" :title="fechaLarga(e.fecha)">{{ haceTiempo(e.fecha) }}</time>
            </p>

            <p v-if="e.lugar" class="lt-lugar">
              <span aria-hidden="true">📍</span> {{ e.lugar }}
              <span v-if="vistaHace(e)" class="pill">Vista {{ vistaHace(e) }}</span>
            </p>
            <p v-if="e.condicion" class="lt-estado"><span class="pill pill--soft">{{ e.condicion }}</span></p>
            <p v-if="e.descripcion" class="lt-nota">
              <template v-for="(p, i) in partesConEnlaces(e.descripcion)" :key="i">
                <a v-if="p.url" :href="p.url" target="_blank" rel="noopener noreferrer">{{ p.texto }}</a>
                <template v-else>{{ p.texto }}</template>
              </template>
            </p>

            <!-- Foto que mandó quien avisó: su dueño la compara con la de su mascota -->
            <div v-if="e.foto_url" class="lt-foto">
              <button type="button" class="lt-foto-btn" :aria-label="`Ver más grande la foto de ${quien(e)}`" @click="fotoAmpliada = urlFoto(e.foto_url)">
                <img :src="urlFoto(e.foto_url)" :alt="`Foto enviada por ${quien(e)}`" loading="lazy" />
              </button>
              <p v-if="esDueno && e.puede_revisar" class="lt-foto-pista">Compárala con la foto de tu mascota (arriba) antes de confirmar.</p>
            </div>

            <!-- Solo quien publicó el reporte ve el contacto, y solo si la otra persona decidió compartirlo -->
            <ContactoCard v-if="e.contacto" compacto :contacto="e.contacto" :mensaje="mensajeWhatsapp(e)" />

            <div v-if="e.puede_revisar" class="revisar">
              <p>{{ e.tipo === 'hallazgo' ? '¿Es tu mascota la que encontraron?' : '¿Esta persona tiene a tu mascota?' }}</p>
              <div class="revisar-botones">
                <button class="btn btn-primary btn-sm" :disabled="revisando === e.id" @click="revisar(e, true)">
                  Sí, es mi mascota
                </button>
                <button class="btn btn-secondary btn-sm" :disabled="revisando === e.id" @click="revisar(e, false)">
                  No es mi mascota
                </button>
              </div>
            </div>
          </div>
        </li>
      </ol>
    </template>

    <dialog v-if="fotoAmpliada" :ref="(el) => el && !el.open && el.showModal()" class="zoom" @close="fotoAmpliada = ''" @click="fotoAmpliada = ''">
      <img :src="fotoAmpliada" alt="Foto ampliada" />
    </dialog>

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
.volver {
  display: inline-block;
  margin-bottom: 1rem;
  font-weight: 800;
  color: var(--color-teal);
  text-decoration: none;
}
.volver:hover { text-decoration: underline; }

.sk-head { height: 180px; margin-bottom: 1rem; }
.sk-line { height: 90px; margin-bottom: 0.8rem; }

/* Ficha */
.ficha { display: grid; grid-template-columns: 150px 1fr; gap: 1.4rem; align-items: center; }
.ficha-foto { aspect-ratio: 1; border-radius: 16px; overflow: hidden; background: var(--color-sun-soft); }
.ficha-foto img { width: 100%; height: 100%; object-fit: cover; display: block; }
.ficha-info { display: flex; flex-direction: column; gap: 0.5rem; min-width: 0; }
.ficha-titulo { display: flex; flex-wrap: wrap; align-items: center; gap: 0.6rem; }
.ficha-titulo h1 { font-size: 2rem; overflow-wrap: anywhere; }
.ficha-desc { color: var(--color-ink-soft); }
.ficha-meta { font-size: 0.9rem; color: var(--color-ink-soft); overflow-wrap: anywhere; }

.badge { padding: 0.2rem 0.75rem; border-radius: 999px; font-size: 0.78rem; font-weight: 800; color: var(--color-white); }
.is-lost { background: var(--color-danger); }
.is-found { background: var(--color-teal); }
.is-ok { background: var(--color-success); }

.tags { display: flex; flex-wrap: wrap; gap: 0.4rem; list-style: none; padding: 0; }
.tags li {
  padding: 0.15rem 0.7rem;
  border-radius: 999px;
  background: var(--color-mist);
  border: 1px solid var(--color-border);
  font-size: 0.82rem;
  font-weight: 700;
}

/* Acciones */
.acciones { display: flex; flex-wrap: wrap; gap: 0.7rem; margin: 1.1rem 0 0.6rem; }
.acciones .btn { min-height: 46px; }
.btn-cta { background: var(--color-sun); color: var(--color-ink); box-shadow: 0 4px 0 #d79a1d; padding-inline: 1.6rem; }
.btn-cta:hover { background: #ffc95e; }
.aviso-revisar {
  flex: 1 1 100%;
  padding: 0.7rem 1rem;
  border-radius: 12px;
  background: var(--color-sun-soft);
  border: 1px solid var(--color-sun);
}
.contacto-publicador { margin-bottom: 0.6rem; }
.btn-borrar { color: var(--color-danger); }

.lt-foto { display: flex; flex-direction: column; gap: 0.35rem; }
.lt-foto-btn { padding: 0; border: 1px solid var(--color-border); border-radius: 12px; overflow: hidden; background: var(--color-mist); cursor: zoom-in; width: min(100%, 260px); }
.lt-foto-btn img { display: block; width: 100%; max-height: 260px; object-fit: cover; }
.lt-foto-pista { font-size: 0.82rem; font-weight: 700; color: var(--color-ink-soft); }
.zoom { margin: auto; padding: 0; border: none; background: transparent; max-width: 96vw; max-height: 94dvh; }
.zoom::backdrop { background: rgba(15, 30, 30, 0.85); }
.zoom img { display: block; max-width: 96vw; max-height: 92dvh; border-radius: 12px; }

/* Línea de tiempo */
.lt-titulo { font-size: 1.4rem; margin: 1.6rem 0 1rem; }
.lt { list-style: none; padding: 0; position: relative; display: grid; gap: 1rem; }
.lt::before {
  content: '';
  position: absolute;
  left: 1.2rem;
  top: 0.5rem;
  bottom: 0.5rem;
  width: 3px;
  border-radius: 2px;
  background: var(--color-border);
}

.lt-item { position: relative; display: grid; grid-template-columns: 2.5rem 1fr; gap: 0.9rem; align-items: start; }
.lt-icono {
  position: relative;
  z-index: 1;
  display: grid;
  place-items: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  font-size: 1.15rem;
  background: var(--color-white);
  border: 3px solid var(--tono, var(--color-border));
}
.tono-perdida { --tono: var(--color-danger); }
.tono-encontrada { --tono: var(--color-teal); }
.tono-avistamiento { --tono: #8a63d2; }
.tono-reclamo { --tono: var(--color-sun); }
.tono-ok { --tono: var(--color-success); }

.lt-cuerpo {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  min-width: 0;
  padding: 0.9rem 1rem;
  background: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  box-shadow: 0 4px 12px var(--color-shadow);
}
.lt-cabecera { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 0.5rem; }
.lt-cabecera h3 { font-size: 1.1rem; }
.lt-quien { font-size: 0.82rem; font-weight: 700; color: var(--color-ink-soft); }
.lt-lugar { display: flex; flex-wrap: wrap; align-items: center; gap: 0.4rem; font-weight: 700; overflow-wrap: anywhere; }
.lt-nota { color: var(--color-ink-soft); overflow-wrap: anywhere; }
.lt-nota a { color: var(--color-teal); font-weight: 800; }

.pill { padding: 0.1rem 0.6rem; border-radius: 999px; background: #ede4fb; color: #3f2480; font-size: 0.78rem; font-weight: 800; }
.pill--soft { background: var(--color-mist); color: var(--color-ink); border: 1px solid var(--color-border); }

.estado { padding: 0.1rem 0.65rem; border-radius: 999px; font-size: 0.75rem; font-weight: 800; }
.st-wait { background: var(--color-sun-soft); color: #8a5a00; }
.st-ok { background: var(--color-success-soft); color: var(--color-success); }
.st-no { background: var(--color-mist); color: var(--color-ink-soft); }

.revisar { padding: 0.8rem; border-radius: 12px; background: var(--color-sun-soft); }
.revisar p { font-weight: 800; margin-bottom: 0.5rem; }
.revisar-botones { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.revisar-botones .btn { flex: 1 1 9rem; min-height: 44px; }

@media (max-width: 640px) {
  .ficha { grid-template-columns: 96px 1fr; gap: 0.9rem; align-items: start; }
  .ficha-titulo h1 { font-size: 1.5rem; }
  .acciones .btn { flex: 1 1 100%; }
  .lt::before { left: 1rem; }
  .lt-item { grid-template-columns: 2rem 1fr; gap: 0.6rem; }
  .lt-icono { width: 2rem; height: 2rem; font-size: 0.95rem; }
  .lt-cuerpo { padding: 0.75rem 0.8rem; }
}
</style>
