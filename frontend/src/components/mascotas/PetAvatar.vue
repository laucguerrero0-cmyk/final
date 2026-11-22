<script setup>
import { computed } from 'vue'
import PawIcon from '@/components/layout/PawIcon.vue'
import { paleta } from '@/utils/format'

// Ilustración de la mascota para cuando todavía no tiene foto.
// Se dibuja según la especie y el color que se registró.
const props = defineProps({
  especie: { type: String, default: '' },
  color: { type: String, default: '' },
})

const esPerro = computed(() => props.especie.toLowerCase() === 'perro')
const esGato = computed(() => props.especie.toLowerCase() === 'gato')
const p = computed(() => paleta(props.color))
const fondo = computed(() => (esGato.value ? '#dcebe8' : '#fdf0cf'))
const rayado = computed(() => ['naranja', 'gris'].includes((props.color || '').toLowerCase()))
</script>

<template>
  <div class="avatar" :style="{ background: fondo }" role="img" :aria-label="`Ilustración de ${especie || 'mascota'} ${color || ''}`">
    <svg v-if="esPerro || esGato" viewBox="0 0 200 200" class="avatar-svg">
      <g fill="#fff" opacity=".55">
        <circle cx="26" cy="34" r="7" /><circle cx="42" cy="24" r="5" /><circle cx="170" cy="168" r="7" /><circle cx="158" cy="180" r="5" />
      </g>

      <!-- PERRO -->
      <g v-if="esPerro" :stroke="p.oscuro" stroke-width="2.5" stroke-linejoin="round">
        <ellipse cx="50" cy="104" rx="21" ry="42" transform="rotate(14 50 104)" :fill="p.oscuro" />
        <ellipse cx="150" cy="104" rx="21" ry="42" transform="rotate(-14 150 104)" :fill="p.oscuro" />
        <ellipse cx="100" cy="106" rx="58" ry="54" :fill="p.base" />
        <ellipse cx="100" cy="128" rx="30" ry="24" :fill="p.claro" />
        <ellipse cx="100" cy="114" rx="12" ry="8.5" fill="#2a2d31" stroke="none" />
        <ellipse cx="96" cy="111.5" rx="3.5" ry="2" fill="#fff" opacity=".6" stroke="none" />
        <path d="M100 122 v9 M100 131 q-9 9 -18 2 M100 131 q9 9 18 2" fill="none" stroke="#2a2d31" stroke-width="2.8" stroke-linecap="round" />
        <path d="M92 138 q8 18 16 0 z" fill="#ef8a95" stroke="none" />
        <circle cx="77" cy="94" r="7" fill="#fff" stroke="none" /><circle cx="123" cy="94" r="7" fill="#fff" stroke="none" />
        <circle cx="78" cy="95" r="4.6" fill="#23262a" stroke="none" /><circle cx="122" cy="95" r="4.6" fill="#23262a" stroke="none" />
        <circle cx="79.5" cy="93" r="1.5" fill="#fff" stroke="none" /><circle cx="123.5" cy="93" r="1.5" fill="#fff" stroke="none" />
        <path d="M66 78 q11 -8 22 -2 M112 76 q11 -6 22 2" fill="none" :stroke="p.oscuro" stroke-width="3" stroke-linecap="round" />
      </g>

      <!-- GATO -->
      <g v-else :stroke="p.oscuro" stroke-width="2.5" stroke-linejoin="round">
        <polygon points="46,84 52,28 96,60" :fill="p.base" />
        <polygon points="154,84 148,28 104,60" :fill="p.base" />
        <polygon points="57,70 58,43 80,60" fill="#f4b6bd" stroke="none" />
        <polygon points="143,70 142,43 120,60" fill="#f4b6bd" stroke="none" />
        <ellipse cx="100" cy="112" rx="60" ry="52" :fill="p.base" />
        <g v-if="rayado" fill="none" :stroke="p.oscuro" stroke-width="4" stroke-linecap="round" opacity=".7">
          <path d="M100 62 v16 M86 66 l3 13 M114 66 l-3 13" />
          <path d="M44 108 h14 M46 122 h13 M156 108 h-14 M154 122 h-13" />
        </g>
        <ellipse cx="100" cy="128" rx="24" ry="17" :fill="p.claro" stroke="none" />
        <ellipse cx="76" cy="100" rx="10" ry="12" fill="#e6f0a4" /><ellipse cx="124" cy="100" rx="10" ry="12" fill="#e6f0a4" />
        <ellipse cx="76" cy="100" rx="3.2" ry="9" fill="#23262a" stroke="none" /><ellipse cx="124" cy="100" rx="3.2" ry="9" fill="#23262a" stroke="none" />
        <circle cx="79" cy="95" r="2" fill="#fff" stroke="none" /><circle cx="127" cy="95" r="2" fill="#fff" stroke="none" />
        <path d="M93 118 h14 l-7 8 z" fill="#ef8a95" stroke="none" />
        <path d="M100 126 q-6 9 -15 4 M100 126 q6 9 15 4" fill="none" stroke="#2a2d31" stroke-width="2.4" stroke-linecap="round" />
        <path d="M60 124 l-26 -5 M60 132 l-26 5 M140 124 l26 -5 M140 132 l26 5" fill="none" stroke="#2a2d31" stroke-width="1.8" stroke-linecap="round" opacity=".55" />
      </g>
    </svg>
    <PawIcon v-else class="avatar-paw" />
  </div>
</template>

<style scoped>
.avatar {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
}

.avatar-svg {
  width: 78%;
  height: 92%;
}

.avatar-paw {
  font-size: 4rem;
  color: var(--color-sun);
}
</style>
