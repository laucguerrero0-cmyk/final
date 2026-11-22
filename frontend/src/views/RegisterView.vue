<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import authService from '@/services/authService'
import PawIcon from '@/components/layout/PawIcon.vue'
import AuthShell from '@/components/layout/AuthShell.vue'

const router = useRouter()

const nombre = ref('')
const usuario = ref('')
const correo = ref('')
const password = ref('')
const confirmar = ref('')
const error = ref('')
const exito = ref('')
const cargando = ref(false)

async function onSubmit() {
  error.value = ''
  exito.value = ''

  if (password.value !== confirmar.value) {
    error.value = 'Las contraseñas no coinciden'
    return
  }

  cargando.value = true
  try {
    await authService.registrar({
      nombre: nombre.value,
      usuario: usuario.value,
      correo: correo.value || null, // el correo es opcional en la API
      password: password.value,
    })
    exito.value = 'Cuenta creada. Ya puedes iniciar sesión.'
    setTimeout(() => router.push('/login'), 1200)
  } catch (e) {
    error.value = e.response
      ? e.response.data?.error || 'No se pudo registrar el usuario'
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
      <h1>Crear cuenta</h1>
      <p class="page-subtitle">Regístrate para reportar y buscar mascotas</p>

      <form @submit.prevent="onSubmit">
        <p v-if="error" class="alert alert-error" role="alert">{{ error }}</p>
        <p v-if="exito" class="alert alert-success" role="status">{{ exito }}</p>

        <div class="field">
          <label for="nombre">Nombre completo</label>
          <input id="nombre" v-model.trim="nombre" placeholder="Tu nombre" required autocomplete="name" />
        </div>
        <div class="field">
          <label for="usuario">Usuario</label>
          <input id="usuario" v-model.trim="usuario" placeholder="Elige un usuario" required autocomplete="username" />
        </div>
        <div class="field">
          <label for="correo">Correo (opcional)</label>
          <input id="correo" v-model.trim="correo" type="email" placeholder="tucorreo@ejemplo.com" autocomplete="email" />
        </div>
        <div class="field">
          <label for="password">Contraseña</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Mínimo 6 caracteres"
            required
            minlength="6"
            autocomplete="new-password"
          />
        </div>
        <div class="field">
          <label for="confirmar">Repite la contraseña</label>
          <input
            id="confirmar"
            v-model="confirmar"
            type="password"
            placeholder="Escríbela otra vez"
            required
            minlength="6"
            autocomplete="new-password"
          />
        </div>
        <button class="btn btn-primary" type="submit" :disabled="cargando || !!exito">
          {{ cargando ? 'Creando...' : 'Crear cuenta' }}
        </button>
      </form>

      <p class="auth-switch">
        ¿Ya tienes cuenta?
        <RouterLink to="/login">Inicia sesión</RouterLink>
      </p>
    </div>
  </AuthShell>
</template>