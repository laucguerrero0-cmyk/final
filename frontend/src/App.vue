<script setup>
import { RouterView } from 'vue-router'
import NavBar from '@/components/layout/NavBar.vue'
import BottomNav from '@/components/layout/BottomNav.vue'
import ToastHost from '@/components/ToastHost.vue'
import PawIcon from '@/components/layout/PawIcon.vue'
</script>

<template>
  <NavBar />
  <main class="container">
    <RouterView />
  </main>
  <footer class="footer">
    <PawIcon /> Mascotas Perdidas y Encontradas · Proyecto académico · Unicomfacauca
  </footer>
  <BottomNav />
  <ToastHost />
</template>

<style scoped>
.footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem;
  font-size: 0.85rem;
  color: var(--color-ink-soft);
  border-top: 1px solid var(--color-border);
  text-align: center;
}

/* Deja espacio para que la barra inferior no tape el final de la página */
@media (max-width: 860px) {
  .footer { padding-bottom: calc(5.5rem + env(safe-area-inset-bottom)); }
}
</style>
