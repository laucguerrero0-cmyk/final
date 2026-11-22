<script setup>
import { ref, computed, watch, nextTick } from 'vue'

// Ventana emergente para los CTA de una tarjeta. Según `modo` cambia el texto:
//   encontrada   -> "¡La encontré!"       (pide dónde la encontró)
//   avistamiento -> "La vi por aquí"      (pide dónde la vio)
//   reclamar     -> "¡Es mi mascota!"     (mensaje opcional para quien la encontró)
const props = defineProps({
  modo: { type: String, default: '' }, // '' = cerrado
  reporte: { type: Object, default: null },
  enviando: { type: Boolean, default: false },
  error: { type: String, default: '' },
})
const emit = defineEmits(['confirmar', 'cerrar'])

const TEXTOS = {
  encontrada: {
    titulo: (m) => `¿Encontraste a ${m}?`,
    intro: 'Cuéntanos dónde la encontraste. Le avisamos de inmediato a quien la está buscando.',
    lugar: '¿Dónde la encontraste? *',
    placeholderLugar: 'Ej: Parque Caldas, frente a la iglesia',
    nota: 'Detalles (opcional)',
    placeholderNota: 'Ej: está en la veterinaria de la 5ta',
    boton: 'Confirmar que la encontré',
  },
  avistamiento: {
    titulo: (m) => `¿Viste a ${m}?`,
    intro: 'Aunque no la tengas contigo, tu pista puede ser clave. Se la enviamos a su familia.',
    lugar: '¿Dónde la viste? *',
    placeholderLugar: 'Ej: Calle 5 con carrera 6',
    nota: 'Detalles (opcional)',
    placeholderNota: 'Ej: iba hacia el norte, parecía asustada',
    boton: 'Avisar a su familia',
  },
  reclamar: {
    titulo: () => '¿Es tu mascota?',
    intro: 'Le avisamos a quien la encontró para que se ponga en contacto contigo.',
    lugar: null,
    nota: '¿Cómo la reconoces? (opcional)',
    placeholderNota: 'Ej: se llama Miel y tiene una mancha en la pata',
    boton: 'Avisar a quien la encontró',
  },
}

const t = computed(() => TEXTOS[props.modo] || TEXTOS.encontrada)
const nombre = computed(() => (props.reporte?.mascota === 'Sin nombre' ? 'esta mascota' : props.reporte?.mascota))

const dialogo = ref(null)
const lugar = ref('')
const nota = ref('')
const valido = computed(() => props.modo === 'reclamar' || lugar.value.trim().length > 0)

watch(
  () => [props.modo, props.reporte],
  async ([modo, reporte]) => {
    if (modo && reporte) {
      lugar.value = ''
      nota.value = ''
      if (!dialogo.value.open) dialogo.value.showModal()
      await nextTick()
      dialogo.value?.querySelector('input')?.focus()
    } else if (dialogo.value?.open) {
      dialogo.value.close()
    }
  },
)

function enviar() {
  emit('confirmar', { lugar: lugar.value.trim(), descripcion: nota.value.trim() })
}
</script>

<template>
  <!-- <dialog> nativo: cierra con Esc, atrapa el foco y bloquea el fondo -->
  <dialog ref="dialogo" class="action" @cancel.prevent="emit('cerrar')" @click.self="emit('cerrar')">
    <form v-if="reporte && modo" @submit.prevent="enviar">
      <h2>{{ t.titulo(nombre) }}</h2>
      <p class="action-intro">{{ t.intro }}</p>

      <p v-if="error" class="alert alert-error" role="alert">{{ error }}</p>

      <div v-if="t.lugar" class="field">
        <label for="act-lugar">{{ t.lugar }}</label>
        <input id="act-lugar" v-model="lugar" required maxlength="120" :placeholder="t.placeholderLugar" />
      </div>
      <div class="field">
        <label for="act-nota">{{ t.nota }}</label>
        <input id="act-nota" v-model="nota" maxlength="200" :placeholder="t.placeholderNota" />
      </div>

      <div class="action-buttons">
        <button type="button" class="btn btn-secondary" :disabled="enviando" @click="emit('cerrar')">Cancelar</button>
        <button type="submit" class="btn btn-primary" :disabled="enviando || !valido">
          {{ enviando ? 'Enviando…' : t.boton }}
        </button>
      </div>
    </form>
  </dialog>
</template>

<style scoped>
.action {
  width: min(440px, calc(100vw - 2rem));
  margin: auto;
  padding: 1.6rem;
  border: none;
  border-radius: var(--radius);
  background: var(--color-white);
  color: var(--color-ink);
  box-shadow: 0 24px 60px rgba(15, 61, 62, 0.35);
}

.action::backdrop { background: rgba(15, 61, 62, 0.55); }

form { display: flex; flex-direction: column; gap: 1rem; }
h2 { font-size: 1.5rem; }
.action-intro { color: var(--color-ink-soft); margin-top: -0.5rem; }

.action-buttons {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 0.6rem;
}
</style>
