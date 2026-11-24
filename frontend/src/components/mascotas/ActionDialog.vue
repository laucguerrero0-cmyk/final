<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import ContactoCard from '@/components/mascotas/ContactoCard.vue'

// Ventana emergente para los botones de una tarjeta. Según `modo` cambia el contenido:
//   encontrada   -> "¡La encontré!"     (dónde, en qué estado está, detalles)
//   avistamiento -> "La vi por aquí"    (dónde, hace cuánto, cómo estaba, detalles)
//   reclamar     -> "¡Es mi mascota!"   (cómo la reconoce)
//   resuelto     -> "Ya apareció"       (confirmación de quien publicó el reporte)
// Cuando el aviso se envía (`resultado`), muestra cómo contactar a quien publicó el reporte.
const props = defineProps({
  modo: { type: String, default: '' }, // '' = cerrado
  reporte: { type: Object, default: null },
  enviando: { type: Boolean, default: false },
  error: { type: String, default: '' },
  resultado: { type: Object, default: null },
})
const emit = defineEmits(['confirmar', 'cerrar'])

const auth = useAuthStore()

// Opciones de "¿hace cuánto la viste?" (en minutos)
const CUANDO = [
  { min: 0, texto: 'Ahora mismo' },
  { min: 15, texto: 'Hace 15 minutos' },
  { min: 30, texto: 'Hace 30 minutos' },
  { min: 60, texto: 'Hace 1 hora' },
  { min: 180, texto: 'Hace 3 horas' },
  { min: 360, texto: 'Hace 6 horas' },
  { min: 1440, texto: 'Ayer' },
  { min: 2880, texto: 'Hace 2 días' },
]

// Atajos para describir cómo estaba (igual se puede escribir lo que sea)
const ESTADOS = {
  avistamiento: ['Se veía bien', 'Asustada', 'Herida', 'Con collar', 'Con otra persona'],
  encontrada: ['La tengo conmigo', 'En un lugar seguro', 'Está herida', 'Tiene collar'],
}

const nombre = computed(() => (props.reporte?.mascota === 'Sin nombre' ? 'esta mascota' : props.reporte?.mascota))

const t = computed(() => {
  const encontradaPorMi = props.reporte?.tipo === 'encontrada'
  const textos = {
    encontrada: {
      titulo: `¿Encontraste a ${nombre.value}?`,
      intro: 'Cuéntanos dónde está. Le avisamos de inmediato a quien la busca y te damos su contacto.',
      lugar: '¿Dónde la encontraste? *',
      placeholderLugar: 'Ej: Parque Caldas, frente a la iglesia',
      estado: '¿Cómo está?',
      nota: 'Detalles (opcional)',
      placeholderNota: 'Ej: está en la veterinaria de la 5ta',
      boton: 'Avisar que la encontré',
    },
    avistamiento: {
      titulo: `¿Viste a ${nombre.value}?`,
      intro: 'Aunque no la tengas contigo, tu pista puede ser clave. Se la enviamos a su familia.',
      lugar: '¿Dónde la viste? *',
      placeholderLugar: 'Ej: Calle 5 con carrera 6',
      estado: '¿Cómo se veía?',
      nota: 'Detalles (opcional)',
      placeholderNota: 'Ej: iba hacia el norte, parecía asustada',
      boton: 'Avisar a su familia',
    },
    reclamar: {
      titulo: '¿Es tu mascota?',
      intro: 'Le avisamos a quien la encontró para que se ponga en contacto contigo.',
      nota: '¿Cómo la reconoces? (opcional)',
      placeholderNota: 'Ej: se llama Miel y tiene una mancha en la pata',
      boton: 'Avisar a quien la encontró',
    },
    resuelto: {
      titulo: encontradaPorMi ? '¿Ya la entregaste a su familia?' : `¿Ya apareció ${nombre.value}?`,
      intro: encontradaPorMi
        ? 'Confirma solo si ya está con su familia. Cerraremos el reporte.'
        : 'Confirma solo si ya está contigo. Cerraremos el reporte y avisaremos a la comunidad y a quienes ayudaron.',
      boton: encontradaPorMi ? 'Sí, ya la entregué' : 'Sí, ya apareció',
    },
  }
  return textos[props.modo] || textos.encontrada
})

const conLugar = computed(() => ['encontrada', 'avistamiento'].includes(props.modo))
const conUbicacion = conLugar
const pideTelefono = computed(() => !!props.modo && props.modo !== 'resuelto' && !auth.usuario?.telefono)

const dialogo = ref(null)
const lugar = ref('')
const nota = ref('')
const estado = ref('')
const hace = ref(0)
const compartir = ref(true)
const telefono = ref('')
const ubicacion = ref('') // enlace de mapa con la ubicación actual (opcional)
const ubicando = ref(false)
const errorUbicacion = ref('')

const valido = computed(() => !conLugar.value || lugar.value.trim().length > 0)

// Mensaje que ya sale escrito en WhatsApp cuando se contacta a quien publicó
const mensajeWhatsapp = computed(() => {
  const quien = props.resultado?.contacto?.nombre?.split(' ')[0] || ''
  const base = quien ? `Hola ${quien}, ` : 'Hola, '
  const mascota = nombre.value
  if (props.modo === 'reclamar') return `${base}creo que ${mascota} es mi mascota. ¿Podemos hablar?`
  if (props.modo === 'encontrada') return `${base}vi tu reporte en Mascotas: creo que encontré a ${mascota} en ${lugar.value.trim()}.`
  return `${base}vi tu reporte en Mascotas: vi a ${mascota} en ${lugar.value.trim()}.`
})

watch(
  () => [props.modo, props.reporte],
  async ([modo, reporte]) => {
    if (modo && reporte) {
      lugar.value = ''
      nota.value = ''
      estado.value = ''
      hace.value = 0
      compartir.value = true
      telefono.value = ''
      ubicacion.value = ''
      errorUbicacion.value = ''
      if (!dialogo.value.open) dialogo.value.showModal()
      await nextTick()
      // En el celular no se enfoca solo: el teclado taparía la ventana
      if (window.matchMedia('(pointer: fine)').matches) dialogo.value?.querySelector('input')?.focus()
    } else if (dialogo.value?.open) {
      dialogo.value.close()
    }
  },
)

function usarUbicacion() {
  errorUbicacion.value = ''
  if (!navigator.geolocation) {
    errorUbicacion.value = 'Tu navegador no permite compartir la ubicación'
    return
  }
  ubicando.value = true
  navigator.geolocation.getCurrentPosition(
    ({ coords }) => {
      ubicacion.value = `https://www.google.com/maps?q=${coords.latitude.toFixed(5)},${coords.longitude.toFixed(5)}`
      if (!lugar.value.trim()) lugar.value = 'Mi ubicación actual'
      ubicando.value = false
    },
    () => {
      errorUbicacion.value = 'No pudimos obtener tu ubicación. Escribe el lugar a mano.'
      ubicando.value = false
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 },
  )
}

function elegirEstado(texto) {
  estado.value = estado.value === texto ? '' : texto
}

function enviar() {
  // La descripción admite 255 caracteres: el enlace del mapa va al final y se recorta la nota si hace falta
  const extra = ubicacion.value
  const maximo = 255 - (extra ? extra.length + 1 : 0)
  const descripcion = [nota.value.trim().slice(0, maximo), extra].filter(Boolean).join(' ')
  emit('confirmar', {
    lugar: lugar.value.trim(),
    descripcion,
    condicion: estado.value.trim(),
    hace_minutos: Number(hace.value),
    compartir_contacto: compartir.value,
    telefono: pideTelefono.value && compartir.value ? telefono.value.trim() : '',
  })
}
</script>

<template>
  <!-- <dialog> nativo: cierra con Esc, atrapa el foco y bloquea el fondo -->
  <dialog ref="dialogo" class="action" @cancel.prevent="emit('cerrar')" @click.self="emit('cerrar')">
    <div v-if="reporte && modo" class="sheet">
      <!-- Aviso enviado: se muestra cómo contactar a quien publicó el reporte -->
      <div v-if="resultado" class="done">
        <h2>¡Gracias! 💚</h2>
        <p class="action-intro">{{ resultado.mensaje }}</p>
        <ContactoCard :contacto="resultado.contacto" :mensaje="mensajeWhatsapp" />
        <div class="action-buttons">
          <button type="button" class="btn btn-primary" @click="emit('cerrar')">Listo</button>
        </div>
      </div>

      <form v-else @submit.prevent="enviar">
        <h2>{{ t.titulo }}</h2>
        <p class="action-intro">{{ t.intro }}</p>

        <p v-if="error" class="alert alert-error" role="alert">{{ error }}</p>

        <template v-if="modo !== 'resuelto'">
          <div v-if="conLugar" class="field">
            <label for="act-lugar">{{ t.lugar }}</label>
            <input id="act-lugar" v-model="lugar" required maxlength="120" autocomplete="off" :placeholder="t.placeholderLugar" />
            <button v-if="conUbicacion" type="button" class="loc" :disabled="ubicando" @click="usarUbicacion">
              <span aria-hidden="true">📍</span>
              {{ ubicando ? 'Buscando tu ubicación…' : ubicacion ? 'Ubicación agregada ✓' : 'Usar mi ubicación actual' }}
            </button>
            <span v-if="errorUbicacion" class="field-hint hint-error">{{ errorUbicacion }}</span>
          </div>

          <div v-if="modo === 'avistamiento'" class="field">
            <label for="act-hace">¿Hace cuánto la viste?</label>
            <select id="act-hace" v-model="hace">
              <option v-for="c in CUANDO" :key="c.min" :value="c.min">{{ c.texto }}</option>
            </select>
          </div>

          <div v-if="ESTADOS[modo]" class="field">
            <label for="act-estado">{{ t.estado }}</label>
            <div class="chips" role="group" :aria-label="t.estado">
              <button
                v-for="e in ESTADOS[modo]"
                :key="e"
                type="button"
                class="chip"
                :class="{ 'chip--on': estado === e }"
                :aria-pressed="estado === e"
                @click="elegirEstado(e)"
              >
                {{ e }}
              </button>
            </div>
            <input id="act-estado" v-model="estado" maxlength="60" autocomplete="off" placeholder="O escríbelo con tus palabras" />
          </div>

          <div class="field">
            <label for="act-nota">{{ t.nota }}</label>
            <input id="act-nota" v-model="nota" maxlength="200" autocomplete="off" :placeholder="t.placeholderNota" />
          </div>

          <label class="check">
            <input v-model="compartir" type="checkbox" />
            <span>
              Compartir mi contacto con {{ modo === 'reclamar' ? 'quien la encontró' : 'su familia' }} para que me llamen o
              escriban
            </span>
          </label>

          <div v-if="pideTelefono && compartir" class="field">
            <label for="act-tel">Tu WhatsApp o teléfono</label>
            <input
              id="act-tel"
              v-model="telefono"
              type="tel"
              inputmode="tel"
              autocomplete="tel"
              maxlength="20"
              placeholder="Ej: 300 123 4567"
            />
            <span class="field-hint">Lo guardamos en tu cuenta. Solo se comparte cuando tú lo permites.</span>
          </div>
        </template>

        <div class="action-buttons">
          <button type="button" class="btn btn-secondary" :disabled="enviando" @click="emit('cerrar')">
            {{ modo === 'resuelto' ? 'Todavía no' : 'Cancelar' }}
          </button>
          <button type="submit" class="btn btn-primary" :disabled="enviando || !valido">
            {{ enviando ? 'Enviando…' : t.boton }}
          </button>
        </div>
      </form>
    </div>
  </dialog>
</template>

<style scoped>
.action {
  width: min(460px, calc(100vw - 2rem));
  max-height: 92dvh;
  margin: auto;
  padding: 1.6rem;
  border: none;
  border-radius: var(--radius);
  background: var(--color-white);
  color: var(--color-ink);
  box-shadow: 0 24px 60px rgba(15, 61, 62, 0.35);
  overflow-y: auto;
}

.action::backdrop { background: rgba(15, 61, 62, 0.55); }

form,
.done { display: flex; flex-direction: column; gap: 1rem; }
h2 { font-size: 1.5rem; }
.action-intro { color: var(--color-ink-soft); margin-top: -0.5rem; }

.loc {
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.8rem;
  border-radius: 999px;
  border: 1px dashed var(--color-teal);
  background: var(--color-mist);
  color: var(--color-teal-dark);
  font-size: 0.85rem;
  font-weight: 800;
}
.loc:disabled { opacity: 0.7; cursor: progress; }
.hint-error { color: var(--color-danger); }

.check {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--color-ink-soft);
  cursor: pointer;
}
.check input { flex: none; width: 1.2rem; height: 1.2rem; margin-top: 0.1rem; accent-color: var(--color-teal); }

.action-buttons {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 0.6rem;
}

/* En el celular la ventana sube desde abajo, como una hoja, y se puede desplazar */
@media (max-width: 640px) {
  .action {
    width: 100%;
    max-width: 100%;
    margin: auto 0 0;
    padding: 1.3rem 1.1rem calc(1.3rem + env(safe-area-inset-bottom));
    border-radius: 22px 22px 0 0;
  }
  .action-buttons { flex-direction: column-reverse; }
  .action-buttons .btn { width: 100%; }
}
</style>
