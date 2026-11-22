<script setup>
import { useToast } from '@/composables/useToast'
const { mensaje, tipo } = useToast()
</script>

<template>
  <Transition name="toast">
    <div v-if="mensaje" class="toast" :class="{ 'toast--error': tipo === 'error' }" :role="tipo === 'error' ? 'alert' : 'status'">
      {{ mensaje }}
    </div>
  </Transition>
</template>

<style scoped>
.toast {
  position: fixed;
  left: 50%;
  bottom: 1.5rem;
  transform: translateX(-50%);
  z-index: 50;
  width: max-content;
  max-width: calc(100vw - 2rem);
  padding: 0.9rem 1.4rem;
  border-radius: 999px;
  background: var(--color-ink);
  color: var(--color-white);
  font-weight: 700;
  box-shadow: 0 12px 30px rgba(15, 61, 62, 0.4);
}

.toast--error { background: var(--color-danger); }

.toast-enter-active,
.toast-leave-active { transition: opacity 0.3s, transform 0.3s; }

.toast-enter-from,
.toast-leave-to { opacity: 0; transform: translate(-50%, 12px); }
</style>
