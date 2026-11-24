<script setup>
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificacionesStore } from '@/stores/notificaciones'

// Barra de navegación inferior: solo se ve en el celular, al alcance del pulgar.
const auth = useAuthStore()
const notif = useNotificacionesStore()
</script>

<template>
  <nav v-if="auth.estaAutenticado" class="bottom-nav" aria-label="Navegación principal">
    <RouterLink to="/" class="bn-item">
      <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <circle cx="11" cy="11" r="7" /><path d="M20 20l-3.5-3.5" />
      </svg>
      <span>Perdidas</span>
    </RouterLink>

    <RouterLink to="/encontradas" class="bn-item">
      <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z" />
      </svg>
      <span>Encontradas</span>
    </RouterLink>

    <RouterLink to="/reportar" class="bn-item bn-main">
      <span class="bn-plus" aria-hidden="true">+</span>
      <span>Reportar</span>
    </RouterLink>

    <RouterLink to="/mis-reportes" class="bn-item">
      <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01" />
      </svg>
      <span>Mis reportes</span>
    </RouterLink>

    <RouterLink to="/notificaciones" class="bn-item">
      <span class="bn-icon">
        <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9M13.7 21a2 2 0 0 1-3.4 0" />
        </svg>
        <span v-if="notif.noLeidas" class="bn-count">{{ notif.noLeidas > 9 ? '9+' : notif.noLeidas }}</span>
      </span>
      <span>Avisos</span>
    </RouterLink>
  </nav>
</template>

<style scoped>
.bottom-nav { display: none; }

@media (max-width: 860px) {
  .bottom-nav {
    position: fixed;
    inset: auto 0 0 0;
    z-index: 40;
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    align-items: end;
    padding: 0.35rem 0.4rem calc(0.35rem + env(safe-area-inset-bottom));
    background: var(--color-ink);
    color: #cfe3e0;
    box-shadow: 0 -6px 18px rgba(15, 61, 62, 0.25);
  }

  .bn-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.15rem;
    min-height: 3.2rem;
    border-radius: 12px;
    color: inherit;
    text-decoration: none;
    font-size: 0.72rem;
    font-weight: 800;
  }

  .bn-item.router-link-exact-active { color: var(--color-sun); }

  .bn-icon { position: relative; display: grid; }
  .bn-count {
    position: absolute;
    top: -0.3rem;
    right: -0.7rem;
    min-width: 1.1rem;
    height: 1.1rem;
    padding: 0 0.25rem;
    border-radius: 999px;
    background: var(--color-danger);
    color: var(--color-white);
    font-size: 0.68rem;
    line-height: 1.1rem;
    text-align: center;
  }

  /* El botón central de "Reportar" sobresale para que sea lo más fácil de tocar */
  .bn-main { color: var(--color-white); }
  .bn-plus {
    display: grid;
    place-items: center;
    width: 2.6rem;
    height: 2.6rem;
    margin-top: -1.1rem;
    border-radius: 50%;
    background: var(--color-sun);
    color: var(--color-ink);
    font-size: 1.7rem;
    font-weight: 800;
    line-height: 1;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
  }
}
</style>
