<script setup>
import { computed, ref } from 'vue'
import PetAvatar from '@/components/mascotas/PetAvatar.vue'
import { urlFoto, diasDesde } from '@/utils/format'

const props = defineProps({
  reporte: { type: Object, required: true },
  esMio: { type: Boolean, default: false }, // el reporte lo creó el usuario en sesión
  vistaPrevia: { type: Boolean, default: false }, // sin botones (formulario de reportar)
})
const emit = defineEmits(['encontrada', 'avistamiento', 'reclamar', 'resuelto'])

const r = computed(() => props.reporte)
const perdida = computed(() => r.value.tipo === 'perdida')
const resuelto = computed(() => r.value.estado === 'resuelto')

const fotoRota = ref(false)
const foto = computed(() => (fotoRota.value ? null : urlFoto(r.value.foto_url)))

const insignia = computed(() => {
  if (resuelto.value) return { texto: 'Final feliz', clase: 'is-ok' }
  return perdida.value ? { texto: 'Perdida', clase: 'is-lost' } : { texto: 'Encontrada', clase: 'is-found' }
})

const hace = computed(() => {
  if (!r.value.fecha) return ''
  const d = diasDesde(r.value.fecha)
  const verbo = perdida.value ? 'Perdida' : 'Encontrada'
  if (d <= 0) return `${verbo} hoy`
  if (d === 1) return `${verbo} ayer`
  return `${verbo} hace ${d} días`
})

const detalles = computed(() => [r.value.especie, r.value.raza, r.value.color].filter(Boolean))
const titulo = computed(() => (r.value.mascota === 'Sin nombre' ? `${r.value.especie} sin nombre` : r.value.mascota))

// Compartir por WhatsApp: cada persona que comparte es un posible hallazgo
const urlWhatsapp = computed(() => {
  const x = r.value
  const texto = perdida.value
    ? `🐾 Se busca a ${titulo.value} (${detalles.value.join(', ')}). Última vez vista: ${x.lugar}. ¿La has visto? ${window.location.origin}`
    : `🐾 Encontramos a ${titulo.value} (${detalles.value.join(', ')}) en ${x.lugar}. ¿Es tu mascota? ${window.location.origin}`
  return `https://wa.me/?text=${encodeURIComponent(texto)}`
})
</script>

<template>
  <article class="pet" :class="{ 'pet--ok': resuelto }">
    <div class="pet-photo">
      <img v-if="foto" :src="foto" :alt="`Foto de ${titulo}, ${r.especie}`" loading="lazy" @error="fotoRota = true" />
      <PetAvatar v-else :especie="r.especie" :color="r.color" />
      <span class="pet-badge" :class="insignia.clase">{{ insignia.texto }}</span>
      <span v-if="hace" class="pet-when">{{ hace }}</span>
    </div>

    <div class="pet-body">
      <h3 class="pet-name">{{ titulo }}</h3>

      <ul class="pet-tags" aria-label="Características">
        <li v-for="d in detalles" :key="d">{{ d }}</li>
      </ul>

      <p v-if="r.descripcion_mascota" class="pet-desc">{{ r.descripcion_mascota }}</p>

      <p class="pet-where">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
          <path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z" />
        </svg>
        <span><strong>{{ perdida ? 'Vista por última vez:' : 'Encontrada en:' }}</strong> {{ r.lugar }}</span>
      </p>
      <p v-if="r.descripcion" class="pet-note">“{{ r.descripcion }}”</p>
      <p class="pet-by">Reportó {{ esMio ? 'tú' : r.reportado_por }}</p>

      <!-- CTA -->
      <div v-if="!vistaPrevia" class="pet-actions">
        <p v-if="resuelto" class="pet-happy">💚 Esta mascota ya está con su familia</p>

        <template v-else>
          <button v-if="perdida && !esMio" class="btn btn-cta" @click="emit('encontrada', r)">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5" /></svg>
            ¡La encontré!
          </button>
          <button v-else-if="perdida" class="btn btn-cta" @click="emit('resuelto', r)">Ya apareció</button>
          <button v-else-if="!esMio" class="btn btn-cta" @click="emit('reclamar', r)">¡Es mi mascota!</button>
          <button v-else class="btn btn-cta" @click="emit('resuelto', r)">Ya la entregué</button>

          <button v-if="perdida && !esMio" class="btn btn-secondary btn-sm-action" @click="emit('avistamiento', r)">
            La vi por aquí
          </button>
          <a
            class="btn btn-secondary btn-share"
            :href="urlWhatsapp"
            target="_blank"
            rel="noopener"
            :aria-label="`Compartir a ${titulo} por WhatsApp`"
            title="Compartir por WhatsApp"
          >
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <circle cx="18" cy="5" r="3" /><circle cx="6" cy="12" r="3" /><circle cx="18" cy="19" r="3" /><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4" />
            </svg>
          </a>
        </template>
      </div>
    </div>
  </article>
</template>

<style scoped>
.pet {
  display: flex;
  flex-direction: column;
  background: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  box-shadow: 0 6px 18px var(--color-shadow);
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

@media (prefers-reduced-motion: no-preference) {
  .pet:hover {
    transform: translateY(-4px);
    box-shadow: 0 14px 28px var(--color-shadow);
  }
}

.pet-photo {
  position: relative;
  aspect-ratio: 4 / 3;
  background: var(--color-sun-soft);
}

.pet-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.pet-badge,
.pet-when {
  position: absolute;
  top: 0.75rem;
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 800;
}

.pet-badge {
  left: 0.75rem;
  color: var(--color-white);
}
.is-lost { background: var(--color-danger); }
.is-found { background: var(--color-teal); }
.is-ok { background: var(--color-success); }

.pet-when {
  right: 0.75rem;
  background: rgba(255, 255, 255, 0.94);
  color: var(--color-ink);
}

.pet-body {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  padding: 1.1rem 1.2rem 1.2rem;
  flex: 1;
}

.pet-name { font-size: 1.5rem; }

.pet-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  list-style: none;
  padding: 0;
}

.pet-tags li {
  padding: 0.15rem 0.7rem;
  border-radius: 999px;
  background: var(--color-mist);
  border: 1px solid var(--color-border);
  font-size: 0.82rem;
  font-weight: 700;
}

.pet-desc { color: var(--color-ink-soft); }

.pet-where {
  display: flex;
  gap: 0.4rem;
  align-items: flex-start;
  font-size: 0.9rem;
}

.pet-where svg {
  flex: none;
  margin-top: 0.15rem;
  color: var(--color-teal);
}

.pet-note {
  font-size: 0.88rem;
  font-style: italic;
  color: var(--color-ink-soft);
}

.pet-by {
  font-size: 0.8rem;
  color: var(--color-ink-soft);
}

.pet-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-top: auto;
  padding-top: 0.6rem;
}

.pet-happy {
  width: 100%;
  padding: 0.7rem 1rem;
  border-radius: 12px;
  background: var(--color-success-soft);
  color: var(--color-success);
  font-weight: 800;
  text-align: center;
}

.btn-cta {
  flex: 1 1 100%;
  background: var(--color-sun);
  color: var(--color-ink);
  font-size: 1rem;
  padding: 0.8rem 1.2rem;
  white-space: nowrap;
  box-shadow: 0 4px 0 #d79a1d;
  transition: transform 0.1s, box-shadow 0.1s, background 0.15s;
}

.btn-cta:hover { background: #ffc95e; }

.btn-cta:active {
  transform: translateY(3px);
  box-shadow: 0 1px 0 #d79a1d;
}

.btn-sm-action {
  flex: 1;
  white-space: nowrap;
}

.btn-share {
  flex: none;
  width: 3rem;
  padding-inline: 0;
  margin-left: auto;
}
</style>
