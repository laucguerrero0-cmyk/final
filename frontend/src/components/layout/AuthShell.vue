<script setup>
import PetAvatar from '@/components/mascotas/PetAvatar.vue'
</script>

<template>
  <div class="auth-split">
    <aside class="auth-aside" aria-hidden="false">
      <h2>Cada mascota merece volver a casa</h2>
      <p>Reporta una mascota perdida, avisa cuando encuentres una y ayuda a que más familias se reúnan.</p>
      <div class="auth-pets" aria-hidden="true">
        <div class="auth-pet"><PetAvatar especie="Perro" color="Dorado" /></div>
        <div class="auth-pet"><PetAvatar especie="Gato" color="Naranja" /></div>
        <div class="auth-pet"><PetAvatar especie="Perro" color="Café" /></div>
      </div>
      <ul>
        <li>Mascotas perdidas y encontradas en tu ciudad</li>
        <li>Filtros por ciudad, raza, color y especie</li>
        <li>Notificaciones cuando alguien la ve</li>
      </ul>
    </aside>
    <div class="auth-slot"><slot /></div>
  </div>
</template>

<style scoped>
.auth-split {
  min-height: calc(100vh - 130px);
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: 3rem;
  padding: 1.5rem 0;
}

.auth-aside h2 { font-size: 2.2rem; max-width: 20ch; }
.auth-aside p { margin: 0.8rem 0 1.4rem; color: var(--color-ink-soft); font-size: 1.05rem; max-width: 42ch; }

.auth-pets { display: flex; gap: 0.9rem; margin-bottom: 1.5rem; }
.auth-pet {
  width: 104px;
  height: 104px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid var(--color-white);
  box-shadow: 0 8px 20px var(--color-shadow);
}
.auth-pet:nth-child(2) { transform: translateY(14px); }

.auth-aside ul { list-style: none; padding: 0; display: grid; gap: 0.5rem; font-weight: 700; margin-top: 2rem; }
.auth-aside li::before { content: '✓'; color: var(--color-teal); margin-right: 0.5rem; font-weight: 800; }

.auth-slot :deep(.auth-card) { margin: 0 auto; }

@media (max-width: 860px) {
  .auth-split { grid-template-columns: 1fr; gap: 1.5rem; }
  .auth-aside { display: none; }
}
</style>
