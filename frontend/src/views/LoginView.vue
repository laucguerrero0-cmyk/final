<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import PawIcon from '@/components/layout/PawIcon.vue'
import AuthShell from '@/components/layout/AuthShell.vue'

const router = useRouter()
const auth = useAuthStore()

const usuario = ref('')
const password = ref('')
const error = ref('')
const cargando = ref(false)

async function onSubmit() {
  error.value = ''
  cargando.value = true
  try {
    await auth.login(usuario.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response
      ? e.response.data?.error || 'Usuario o contraseña incorrectos'
      : 'No se pudo conectar con el servidor. Revisa que el servicio de usuarios esté encendido.'
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <AuthShell>
    <div class="card auth-card">
      <div class="auth-logo"><PawIcon style="font-size: 1.8rem" /></div>
      <h1>Bienvenido de nuevo</h1>
      <p class="page-subtitle">Inicia sesión para ayudar a mascotas a volver a casa</p>

      <form @submit.prevent="onSubmit">
        <p v-if="error" class="alert alert-error" role="alert">{{ error }}</p>

        <div class="field">
          <label for="usuario">Usuario</label>
          <input id="usuario" v-model.trim="usuario" placeholder="Tu usuario" required autocomplete="username" />
        </div>
        <div class="field">
          <label for="password">Contraseña</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Tu contraseña"
            required
            autocomplete="current-password"
          />
        </div>
        <button class="btn btn-primary" type="submit" :disabled="cargando">
          {{ cargando ? 'Ingresando...' : 'Iniciar sesión' }}
        </button>
      </form>

      <p class="auth-switch">
        ¿No tienes cuenta?
        <RouterLink to="/register">Regístrate aquí</RouterLink>
      </p>
    </div>
  </AuthShell>
</template>