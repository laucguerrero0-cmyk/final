import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '@/views/HomeView.vue'
import EncontradasView from '@/views/EncontradasView.vue'
import ReportarView from '@/views/ReportarView.vue'
import NotificacionesView from '@/views/NotificacionesView.vue'
import HistorialView from '@/views/HistorialView.vue'
import PlanesView from '@/views/PlanesView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'inicio', component: HomeView, meta: { requiereAuth: true } },
    { path: '/encontradas', name: 'encontradas', component: EncontradasView, meta: { requiereAuth: true } },
    { path: '/reportar', name: 'reportar', component: ReportarView, meta: { requiereAuth: true } },
    { path: '/notificaciones', name: 'notificaciones', component: NotificacionesView, meta: { requiereAuth: true } },
    { path: '/reporte/:id(\\d+)/historial', name: 'historial', component: HistorialView, meta: { requiereAuth: true } },
    { path: '/planes', name: 'planes', component: PlanesView }, // pública: es la vitrina de planes
    { path: '/login', name: 'login', component: LoginView, meta: { soloInvitados: true } },
    { path: '/register', name: 'register', component: RegisterView, meta: { soloInvitados: true } },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior: (to) => (to.hash ? { el: to.hash, behavior: 'smooth' } : { top: 0 }),
})

// Guardia de navegación: protege rutas privadas y evita volver al login ya autenticado
router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiereAuth && !auth.estaAutenticado) {
    return { name: 'login' }
  }
  if (to.meta.soloInvitados && auth.estaAutenticado) {
    return { name: 'inicio' }
  }
})

export default router
