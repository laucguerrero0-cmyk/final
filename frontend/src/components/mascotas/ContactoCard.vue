<script setup>
import { computed } from 'vue'
import { enlaceLlamar, enlaceWhatsapp, enlaceCorreo } from '@/utils/contacto'

// Muestra cómo comunicarse con una persona: llamar, WhatsApp o correo.
//   contacto: { nombre, telefono, correo } (o null si no dejó datos)
//   mensaje:  texto que ya viene escrito en WhatsApp
const props = defineProps({
  contacto: { type: Object, default: null },
  mensaje: { type: String, default: '' },
  compacto: { type: Boolean, default: false },
})

const llamar = computed(() => enlaceLlamar(props.contacto?.telefono))
const whatsapp = computed(() => enlaceWhatsapp(props.contacto?.telefono, props.mensaje))
const correo = computed(() => enlaceCorreo(props.contacto?.correo, 'Sobre una mascota en Mascotas'))
const hayDatos = computed(() => !!(llamar.value || correo.value))
</script>

<template>
  <div class="contacto" :class="{ 'contacto--compacto': compacto }">
    <template v-if="contacto && hayDatos">
      <p class="c-quien">
        <strong>{{ contacto.nombre }}</strong>
        <span v-if="contacto.telefono"> · {{ contacto.telefono }}</span>
      </p>
      <div class="c-botones">
        <a v-if="llamar" :href="llamar" class="btn btn-primary btn-sm">📞 Llamar</a>
        <a v-if="whatsapp" :href="whatsapp" target="_blank" rel="noopener" class="btn btn-wa btn-sm">💬 WhatsApp</a>
        <a v-if="correo" :href="correo" class="btn btn-secondary btn-sm">✉️ Correo</a>
      </div>
      <p v-if="contacto.correo && !compacto" class="c-correo">{{ contacto.correo }}</p>
    </template>
    <p v-else class="c-vacio">
      Esta persona no dejó datos de contacto, pero ya le enviamos una notificación para que te responda por aquí.
    </p>
  </div>
</template>

<style scoped>
.contacto {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  padding: 0.9rem 1rem;
  border-radius: 14px;
  background: var(--color-mist);
  border: 1px solid var(--color-border);
}

.contacto--compacto { padding: 0.65rem 0.8rem; gap: 0.45rem; }

.c-quien { overflow-wrap: anywhere; }
.c-botones { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.c-botones .btn { flex: 1 1 7.5rem; }
.c-correo { font-size: 0.85rem; color: var(--color-ink-soft); overflow-wrap: anywhere; }
.c-vacio { font-size: 0.9rem; color: var(--color-ink-soft); }

.btn-wa { background: #128c4a; color: var(--color-white); }
.btn-wa:hover { background: #0e6f3b; }
</style>
