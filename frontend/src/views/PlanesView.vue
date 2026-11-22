<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { pesos, parseFecha } from '@/utils/format'
import planesService from '@/services/planesService'

const auth = useAuthStore()
const router = useRouter()
const { mostrar } = useToast()

const planes = ref([])
const miPlan = ref(null)
const periodo = ref('mensual') // 'mensual' | 'anual'
const cargando = ref(true)
const error = ref('')

async function cargar() {
  try {
    planes.value = (await planesService.listar()).data
    if (auth.estaAutenticado) miPlan.value = (await planesService.miPlan()).data.suscripcion
  } catch (e) {
    error.value = e.response?.data?.error || 'No se pudieron cargar los planes. Revisa que el servicio de usuarios esté encendido.'
  } finally {
    cargando.value = false
  }
}
onMounted(cargar)

const codigoActual = computed(() => miPlan.value?.codigo || (auth.estaAutenticado ? 'comunidad' : null))
const precio = (p) => (periodo.value === 'anual' ? p.precio_anio : p.precio_mes)
const porMes = (p) => Math.round(p.precio_anio / 12)
const vence = computed(() =>
  miPlan.value?.vence_en
    ? parseFecha(miPlan.value.vence_en).toLocaleDateString('es-CO', { day: 'numeric', month: 'long', year: 'numeric' })
    : '',
)

// ---- Contratar (el pago es simulado: no se piden datos de tarjeta) ----
const dialogo = ref(null)
const elegido = ref(null)
const organizacion = ref('')
const errorPlan = ref('')
const enviando = ref(false)
const pideOrganizacion = computed(() => ['fundacion', 'institucional'].includes(elegido.value?.codigo))

async function elegir(plan) {
  if (!auth.estaAutenticado) return router.push('/register')
  if (plan.precio_mes === 0) return cancelarPlan()
  elegido.value = plan
  organizacion.value = ''
  errorPlan.value = ''
  dialogo.value.showModal()
  await nextTick()
  dialogo.value.querySelector('input')?.focus()
}

async function confirmar() {
  enviando.value = true
  errorPlan.value = ''
  try {
    const { data } = await planesService.contratar({
      plan_id: elegido.value.id,
      periodo: periodo.value,
      organizacion: organizacion.value.trim() || null,
    })
    dialogo.value.close()
    mostrar(data.mensaje + '. ¡Gracias por apoyar a las mascotas!')
    miPlan.value = (await planesService.miPlan()).data.suscripcion
  } catch (e) {
    errorPlan.value = e.response?.data?.error || 'No se pudo contratar el plan'
  } finally {
    enviando.value = false
  }
}

async function cancelarPlan() {
  if (!miPlan.value) return
  try {
    await planesService.cancelar()
    miPlan.value = null
    mostrar('Tu suscripción fue cancelada. Volviste al plan Comunidad.')
  } catch {
    mostrar('No se pudo cancelar la suscripción', 'error')
  }
}

function textoBoton(p) {
  if (!auth.estaAutenticado) return p.precio_mes === 0 ? 'Crear cuenta gratis' : `Empezar con ${p.nombre}`
  if (p.codigo === codigoActual.value) return 'Tu plan actual'
  return p.precio_mes === 0 ? 'Volver a Comunidad' : `Elegir ${p.nombre}`
}

const BENEFICIOS = [
  { icono: '📣', titulo: 'Más alcance', texto: 'Tus reportes se muestran primero y se pueden compartir con carteles listos para redes.' },
  { icono: '🔔', titulo: 'Alertas prioritarias', texto: 'Te avisamos al instante cuando alguien ve o encuentra una de tus mascotas.' },
  { icono: '📊', titulo: 'Impacto medible', texto: 'Mira cuántas mascotas lograron volver a casa gracias a tu trabajo.' },
]
const PREGUNTAS = [
  { p: '¿Puedo cambiar de plan cuando quiera?', r: 'Sí. Al elegir otro plan, el anterior se cancela y el nuevo empieza de inmediato.' },
  { p: '¿Qué pasa si cancelo?', r: 'Vuelves al plan Comunidad, que es gratis. No pierdes tus reportes ni tus mascotas.' },
  { p: '¿Cuánto ahorro con el plan anual?', r: 'Pagas 10 meses y recibes 12: son dos meses gratis en cualquier plan.' },
  { p: '¿Cómo se paga?', r: 'En esta versión del proyecto el pago es simulado: no se cobra nada ni se piden datos de tarjeta.' },
]
</script>

<template>
  <section class="page">
    <header class="plans-head">
      <h1>Planes para cada necesidad</h1>
      <p class="page-subtitle">
        Desde una familia que busca a su mascota hasta fundaciones, veterinarias y alcaldías que cuidan a cientos.
      </p>

      <div class="switch" role="group" aria-label="Periodo de facturación">
        <button :class="{ on: periodo === 'mensual' }" :aria-pressed="periodo === 'mensual'" @click="periodo = 'mensual'">Mensual</button>
        <button :class="{ on: periodo === 'anual' }" :aria-pressed="periodo === 'anual'" @click="periodo = 'anual'">
          Anual <span class="save">2 meses gratis</span>
        </button>
      </div>
    </header>

    <p v-if="error" class="alert alert-error" role="alert">{{ error }}</p>

    <div v-if="miPlan" class="current card" role="status">
      <div>
        <strong>Tu plan: {{ miPlan.plan }}</strong> · {{ miPlan.periodo }}
        <span v-if="miPlan.organizacion"> · {{ miPlan.organizacion }}</span>
        <span v-if="vence"> · vence el {{ vence }}</span>
      </div>
      <button class="btn btn-secondary btn-sm" @click="cancelarPlan">Cancelar suscripción</button>
    </div>

    <div v-if="cargando" class="plans" aria-hidden="true"><div v-for="n in 4" :key="n" class="skeleton"></div></div>

    <div v-else class="plans">
      <article v-for="p in planes" :key="p.id" class="plan card" :class="{ featured: p.destacado, active: p.codigo === codigoActual }">
        <span v-if="p.destacado" class="ribbon">Más elegido</span>
        <h2>{{ p.nombre }}</h2>
        <p class="who">{{ p.publico }}</p>

        <p class="price">
          <template v-if="p.precio_mes === 0"><strong>Gratis</strong></template>
          <template v-else>
            <strong>{{ pesos(precio(p)) }}</strong><span>/{{ periodo === 'anual' ? 'año' : 'mes' }}</span>
          </template>
        </p>
        <p class="sub">
          <template v-if="p.precio_mes === 0">Para siempre</template>
          <template v-else-if="periodo === 'anual'">Equivale a {{ pesos(porMes(p)) }} al mes</template>
          <template v-else>o {{ pesos(p.precio_anio) }} al año</template>
        </p>

        <ul>
          <li v-for="c in p.caracteristicas" :key="c">{{ c }}</li>
        </ul>

        <button
          class="btn plan-btn"
          :class="p.destacado ? 'btn-sun' : 'btn-primary'"
          :disabled="p.codigo === codigoActual && (p.precio_mes > 0 || !miPlan)"
          @click="elegir(p)"
        >
          {{ textoBoton(p) }}
        </button>
      </article>
    </div>

    <h2 class="block-title">¿Por qué suscribirte?</h2>
    <div class="benefits">
      <div v-for="b in BENEFICIOS" :key="b.titulo" class="card benefit">
        <span class="b-icon" aria-hidden="true">{{ b.icono }}</span>
        <h3>{{ b.titulo }}</h3>
        <p>{{ b.texto }}</p>
      </div>
    </div>

    <h2 class="block-title">Preguntas frecuentes</h2>
    <div class="faq">
      <details v-for="q in PREGUNTAS" :key="q.p" class="card">
        <summary>{{ q.p }}</summary>
        <p>{{ q.r }}</p>
      </details>
    </div>

    <dialog ref="dialogo" class="checkout" @click.self="dialogo.close()">
      <form v-if="elegido" @submit.prevent="confirmar">
        <h2>Plan {{ elegido.nombre }}</h2>
        <p class="resumen">
          <strong>{{ pesos(periodo === 'anual' ? elegido.precio_anio : elegido.precio_mes) }}</strong>
          <span>{{ periodo === 'anual' ? 'por año' : 'por mes' }}</span>
        </p>

        <p v-if="errorPlan" class="alert alert-error" role="alert">{{ errorPlan }}</p>

        <div v-if="pideOrganizacion" class="field">
          <label for="org">Nombre de tu fundación u organización *</label>
          <input id="org" v-model="organizacion" maxlength="120" required placeholder="Ej: Fundación Patitas del Cauca" />
        </div>

        <p class="sim">Pago simulado: es un proyecto académico, no se cobra nada ni se piden datos de tarjeta.</p>

        <div class="buttons">
          <button type="button" class="btn btn-secondary" :disabled="enviando" @click="dialogo.close()">Cancelar</button>
          <button type="submit" class="btn btn-primary" :disabled="enviando">{{ enviando ? 'Procesando…' : 'Confirmar suscripción' }}</button>
        </div>
      </form>
    </dialog>
  </section>
</template>

<style scoped>
.plans-head { text-align: center; padding: 1rem 0 1.8rem; }
.plans-head h1 { font-size: 2.4rem; }
.plans-head .page-subtitle { max-width: 56ch; margin: 0.6rem auto 1.4rem; font-size: 1.05rem; }

.switch { display: inline-flex; padding: 0.3rem; border-radius: 999px; background: var(--color-white); border: 1px solid var(--color-border); }
.switch button { border: none; background: none; border-radius: 999px; padding: 0.5rem 1.3rem; font-weight: 800; color: var(--color-ink); }
.switch button.on { background: var(--color-ink); color: var(--color-white); }
.save { margin-left: 0.3rem; padding: 0.1rem 0.5rem; border-radius: 999px; background: var(--color-sun); color: var(--color-ink); font-size: 0.72rem; }

.current { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.4rem; background: var(--color-success-soft); border-color: transparent; color: var(--color-success); padding: 1rem 1.4rem; }

.plans { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 1.2rem; align-items: stretch; }
.skeleton { height: 420px; }

.plan { position: relative; display: flex; flex-direction: column; padding: 1.7rem 1.5rem; }
.plan.featured { border: 2px solid var(--color-sun); box-shadow: 0 18px 36px rgba(244, 185, 66, 0.35); }
.plan.active:not(.featured) { border: 2px solid var(--color-teal); }
.ribbon { position: absolute; top: -0.8rem; left: 50%; transform: translateX(-50%); background: var(--color-sun); color: var(--color-ink); font-weight: 800; font-size: 0.78rem; padding: 0.2rem 0.9rem; border-radius: 999px; white-space: nowrap; }
.plan h2 { font-size: 1.5rem; }
.who { color: var(--color-ink-soft); font-size: 0.9rem; min-height: 2.6em; }
.price { margin-top: 0.8rem; display: flex; align-items: baseline; gap: 0.2rem; min-height: 3.2rem; }
.price strong { font-family: var(--font-title); font-size: 2.2rem; }
.price span { color: var(--color-ink-soft); font-weight: 700; }
.sub { font-size: 0.82rem; color: var(--color-ink-soft); font-weight: 700; margin-bottom: 1rem; }
.plan ul { list-style: none; padding: 0; display: grid; gap: 0.55rem; margin-bottom: 1.5rem; font-size: 0.92rem; }
.plan li { padding-left: 1.5rem; position: relative; }
.plan li::before { content: '✓'; position: absolute; left: 0; color: var(--color-teal); font-weight: 800; }
.plan-btn { margin-top: auto; width: 100%; }

.block-title { font-size: 1.5rem; margin: 3rem 0 1rem; text-align: center; }
.benefits { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.2rem; }
.benefit { text-align: center; }
.b-icon { font-size: 2rem; }
.benefit h3 { margin: 0.4rem 0; }
.benefit p { color: var(--color-ink-soft); }

.faq { display: grid; gap: 0.7rem; max-width: 760px; margin: 0 auto; }
.faq details { padding: 1rem 1.3rem; }
.faq summary { font-weight: 800; cursor: pointer; }
.faq p { margin-top: 0.6rem; color: var(--color-ink-soft); }

.checkout { width: min(440px, calc(100vw - 2rem)); margin: auto; padding: 1.6rem; border: none; border-radius: var(--radius); box-shadow: 0 24px 60px rgba(15, 61, 62, 0.35); color: var(--color-ink); }
.checkout::backdrop { background: rgba(15, 61, 62, 0.55); }
.checkout form { display: flex; flex-direction: column; gap: 1rem; }
.checkout h2 { font-size: 1.5rem; }
.resumen { display: flex; align-items: baseline; gap: 0.4rem; }
.resumen strong { font-family: var(--font-title); font-size: 2rem; }
.sim { font-size: 0.82rem; color: var(--color-ink-soft); background: var(--color-mist); padding: 0.6rem 0.8rem; border-radius: 10px; }
.buttons { display: flex; justify-content: flex-end; flex-wrap: wrap; gap: 0.6rem; }

@media (max-width: 600px) { .plans-head h1 { font-size: 1.9rem; } }
</style>
