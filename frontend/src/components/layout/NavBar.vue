<script setup>
import { ref, watch, onMounted } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificacionesStore } from '@/stores/notificaciones'
import PawIcon from '@/components/layout/PawIcon.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const notif = useNotificacionesStore()

const menuAbierto = ref(false)
watch(() => route.fullPath, () => (menuAbierto.value = false))

// La campana consulta las notificaciones nuevas mientras haya sesión
watch(() => auth.estaAutenticado, (activo) => (activo ? notif.iniciar() : notif.detener()))
onMounted(() => auth.estaAutenticado && notif.iniciar())

function cerrarSesion() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <header class="topbar">
    <div class="topbar-inner">
      <RouterLink to="/" class="brand">
        <PawIcon class="brand-icon" />
        Mascotas
      </RouterLink>

      <div class="topbar-actions">
        <RouterLink
          v-if="auth.estaAutenticado"
          to="/notificaciones"
          class="bell"
          :aria-label="notif.noLeidas ? `Notificaciones: ${notif.noLeidas} sin leer` : 'Notificaciones'"
        >
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9M13.7 21a2 2 0 0 1-3.4 0" />
          </svg>
          <span v-if="notif.noLeidas" class="bell-count">{{ notif.noLeidas > 9 ? '9+' : notif.noLeidas }}</span>
        </RouterLink>

        <button class="burger" :aria-expanded="menuAbierto" aria-controls="menu" aria-label="Abrir menú" @click="menuAbierto = !menuAbierto">
          <span></span><span></span><span></span>
        </button>
      </div>

      <nav id="menu" class="topbar-menu" :class="{ open: menuAbierto }">
        <div class="topbar-links">
          <template v-if="auth.estaAutenticado">
            <RouterLink to="/">Perdidas</RouterLink>
            <RouterLink to="/encontradas">Encontradas</RouterLink>
          </template>
          <RouterLink to="/planes">Planes</RouterLink>
        </div>

        <div class="topbar-right">
          <template v-if="auth.estaAutenticado">
            <RouterLink to="/reportar" class="btn btn-sm btn-sun">+ Reportar mascota</RouterLink>
            <span class="username">{{ auth.usuario?.nombre }}</span>
            <button class="btn btn-secondary btn-sm" @click="cerrarSesion">Cerrar sesión</button>
          </template>
          <template v-else>
            <RouterLink to="/login" class="topbar-guest">Iniciar sesión</RouterLink>
            <RouterLink to="/register" class="btn btn-sm btn-sun">Registrarme</RouterLink>
          </template>
        </div>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.topbar {
  background: var(--color-ink);
  color: var(--color-white);
  position: sticky;
  top: 0;
  z-index: 30;
}

.topbar-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0.8rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-family: var(--font-title);
  font-weight: 600;
  font-size: 1.25rem;
  text-decoration: none;
}

.brand-icon { color: var(--color-sun); font-size: 1.4rem; }

.topbar-menu {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 1.5rem;
}

.topbar-links { display: flex; gap: 1.1rem; flex: 1; }

.topbar-links a {
  color: #cfe3e0;
  text-decoration: none;
  font-weight: 700;
  padding: 0.3rem 0.1rem;
  border-bottom: 2px solid transparent;
}

.topbar-links a:hover { color: var(--color-white); }

.topbar-links a.router-link-exact-active {
  border-bottom-color: var(--color-sun);
  color: var(--color-white);
}

.topbar-right { display: flex; align-items: center; gap: 0.8rem; }

.username {
  font-size: 0.9rem;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 14ch;
}

.topbar-guest { color: #cfe3e0; font-weight: 700; text-decoration: none; }

.btn-sun { background: var(--color-sun); color: var(--color-ink); }
.btn-sun:hover { background: #ffc95e; }

/* Campana */
.topbar-actions { display: flex; align-items: center; gap: 0.6rem; order: 3; }
.bell {
  position: relative;
  display: grid;
  place-items: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  color: #cfe3e0;
}
.bell:hover, .bell.router-link-exact-active { background: rgba(255, 255, 255, 0.12); color: var(--color-white); }

.bell-count {
  position: absolute;
  top: 0;
  right: 0;
  min-width: 1.2rem;
  height: 1.2rem;
  padding: 0 0.25rem;
  border-radius: 999px;
  background: var(--color-danger);
  color: var(--color-white);
  font-size: 0.72rem;
  font-weight: 800;
  line-height: 1.2rem;
  text-align: center;
  border: 2px solid var(--color-ink);
  box-sizing: content-box;
  transform: translate(25%, -10%);
}

.burger {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  padding: 0.6rem;
}
.burger span { width: 22px; height: 2.5px; background: var(--color-white); border-radius: 2px; }

@media (max-width: 860px) {
  .topbar-inner { flex-wrap: wrap; gap: 0.5rem 1rem; }
  .topbar-actions { margin-left: auto; }
  .burger { display: flex; }
  .topbar-menu {
    order: 4;
    display: none;
    flex-basis: 100%;
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
    padding: 0.5rem 0 0.8rem;
  }
  .topbar-menu.open { display: flex; }
  .topbar-links { flex-direction: column; gap: 0.3rem; flex: none; }
  .topbar-links a { padding: 0.5rem 0; }
  .topbar-right { flex-wrap: wrap; }
  .username { max-width: none; }
}
</style>
