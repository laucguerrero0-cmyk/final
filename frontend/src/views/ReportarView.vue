<script setup>
import { ref, computed, reactive, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { ESPECIES, COLORES, unirSugerencias } from '@/utils/format'
import mascotasService from '@/services/mascotasService'
import reportesService from '@/services/reportesService'
import PetCard from '@/components/mascotas/PetCard.vue'

const router = useRouter()
const auth = useAuthStore()
const { mostrar } = useToast()

const CIUDADES = ['Popayán', 'Cali', 'Bogotá', 'Medellín', 'Pasto', 'Neiva', 'Barranquilla', 'Cartagena', 'Bucaramanga']
const MAX_FOTO = 4 * 1024 * 1024

// tipo: 'perdida' (perdí a mi mascota) | 'encontrada' (encontré una mascota)
const tipo = ref('perdida')
const f = reactive({
  nombre: '', especie: 'Perro', raza: '', color: '', caracteristicas: '',
  ciudad: '', lugar: '', nota: '',
})
const archivo = ref(null)
const vistaFoto = ref(null)
const error = ref('')
const enviando = ref(false)

// Especie, raza y color son de escritura libre; estas listas solo ayudan a completar
const opciones = ref({ especies: [], razas: [], colores: [] })
const sugEspecies = computed(() => unirSugerencias(ESPECIES, opciones.value.especies))
const sugRazas = computed(() => unirSugerencias(opciones.value.razas))
const sugColores = computed(() => unirSugerencias(COLORES, opciones.value.colores))

// Para que quien vea el reporte pueda llamar o escribir por WhatsApp, la cuenta necesita un teléfono
const telefono = ref('')
const pideTelefono = computed(() => !auth.usuario?.telefono)

onMounted(async () => {
  try {
    opciones.value = (await reportesService.filtros()).data
  } catch {
    /* sin sugerencias: igual se puede escribir */
  }
  try {
    await auth.refrescarPerfil() // la sesión puede ser anterior al campo de teléfono
  } catch {
    /* si falla, se pide el teléfono igual */
  }
})

function elegirFoto(e) {
  error.value = ''
  const a = e.target.files[0]
  if (!a) return
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(a.type)) {
    error.value = 'La foto debe ser JPG, PNG o WEBP'
    e.target.value = ''
    return
  }
  if (a.size > MAX_FOTO) {
    error.value = 'La foto pesa más de 4 MB'
    e.target.value = ''
    return
  }
  if (vistaFoto.value) URL.revokeObjectURL(vistaFoto.value)
  archivo.value = a
  vistaFoto.value = URL.createObjectURL(a)
}
onBeforeUnmount(() => vistaFoto.value && URL.revokeObjectURL(vistaFoto.value))

const lugarCompleto = computed(() => [f.ciudad.trim(), f.lugar.trim()].filter(Boolean).join(' - '))

// Tarjeta de vista previa: se arma con lo que se va escribiendo
const previa = computed(() => ({
  id: 0,
  tipo: tipo.value,
  estado: 'abierto',
  fecha: new Date().toISOString().slice(0, 19).replace('T', ' '),
  mascota: f.nombre.trim() || (tipo.value === 'perdida' ? 'Nombre de tu mascota' : 'Sin nombre'),
  especie: f.especie,
  raza: f.raza.trim(),
  color: f.color,
  descripcion_mascota: f.caracteristicas.trim(),
  lugar: lugarCompleto.value || 'Ciudad - Barrio o lugar',
  descripcion: f.nota.trim(),
  foto_url: vistaFoto.value,
  reportado_por: auth.usuario?.nombre,
}))

async function enviar() {
  error.value = ''
  if (tipo.value === 'perdida' && !f.nombre.trim()) {
    error.value = 'Escribe el nombre de tu mascota'
    return
  }
  if (!f.especie.trim()) {
    error.value = 'Escribe la especie (perro, gato, conejo…)'
    return
  }
  enviando.value = true
  try {
    if (pideTelefono.value && telefono.value.trim()) await auth.guardarTelefono(telefono.value.trim())
    const { data: mascota } = await mascotasService.crear({
      nombre: f.nombre.trim() || 'Sin nombre',
      especie: f.especie.trim(),
      raza: f.raza.trim() || null,
      color: f.color.trim() || null,
      descripcion: f.caracteristicas.trim() || null,
    })
    if (archivo.value) await mascotasService.subirFoto(mascota.id, archivo.value)
    await reportesService.crear({
      mascota_id: mascota.id,
      tipo: tipo.value,
      lugar: lugarCompleto.value,
      descripcion: f.nota.trim() || null,
    })
    mostrar(
      tipo.value === 'perdida'
        ? 'Reporte publicado. Avisamos a la comunidad para que te ayude a buscarla.'
        : 'Gracias por ayudar. Publicamos tu hallazgo para que su familia la encuentre.',
    )
    router.push(tipo.value === 'perdida' ? '/' : '/encontradas')
  } catch (e) {
    error.value = e.response
      ? e.response.data?.error || 'No se pudo publicar el reporte'
      : 'No se pudo conectar con el servidor. Revisa que los servicios estén encendidos.'
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <section class="page">
    <header class="page-head">
      <h1>Reportar una mascota</h1>
      <p class="page-subtitle">Cuéntanos qué pasó. Mientras más datos des, más fácil será encontrarla.</p>
    </header>

    <div class="rep-layout">
      <form class="card rep-form" @submit.prevent="enviar">
        <div class="rep-tipo" role="radiogroup" aria-label="Tipo de reporte">
          <button type="button" role="radio" :aria-checked="tipo === 'perdida'" class="rep-op" :class="{ on: tipo === 'perdida' }" @click="tipo = 'perdida'">
            <strong>Perdí a mi mascota</strong><span>Publica una búsqueda</span>
          </button>
          <button type="button" role="radio" :aria-checked="tipo === 'encontrada'" class="rep-op" :class="{ on: tipo === 'encontrada' }" @click="tipo = 'encontrada'">
            <strong>Encontré una mascota</strong><span>Ayuda a que vuelva a casa</span>
          </button>
        </div>

        <p v-if="error" class="alert alert-error" role="alert">{{ error }}</p>

        <fieldset>
          <legend>La mascota</legend>
          <div class="grid2">
            <div class="field">
              <label for="r-nombre">Nombre {{ tipo === 'perdida' ? '*' : '(si lo sabes)' }}</label>
              <input id="r-nombre" v-model="f.nombre" maxlength="80" :required="tipo === 'perdida'" placeholder="Ej: Luna" />
            </div>
            <div class="field">
              <label for="r-especie">Especie *</label>
              <input id="r-especie" v-model="f.especie" list="dl-especie" required maxlength="40" autocomplete="off" placeholder="Ej: Perro, gato, conejo…" />
              <datalist id="dl-especie"><option v-for="e in sugEspecies" :key="e" :value="e" /></datalist>
            </div>
            <div class="field">
              <label for="r-raza">Raza</label>
              <input id="r-raza" v-model="f.raza" list="dl-raza" maxlength="60" autocomplete="off" placeholder="Ej: Labrador, criollo, mestizo" />
              <datalist id="dl-raza"><option v-for="r in sugRazas" :key="r" :value="r" /></datalist>
            </div>
            <div class="field">
              <label for="r-color">Color</label>
              <input id="r-color" v-model="f.color" list="dl-color" maxlength="40" autocomplete="off" placeholder="Ej: Negro, tricolor, café con blanco" />
              <datalist id="dl-color"><option v-for="c in sugColores" :key="c" :value="c" /></datalist>
            </div>
          </div>
          <div class="field">
            <label for="r-car">Señas particulares</label>
            <input id="r-car" v-model="f.caracteristicas" maxlength="255" placeholder="Ej: collar rojo, mancha en la oreja" />
          </div>
          <div class="field">
            <label for="r-foto">Foto (JPG, PNG o WEBP, máx. 4 MB)</label>
            <input id="r-foto" type="file" accept="image/jpeg,image/png,image/webp" @change="elegirFoto" />
          </div>
        </fieldset>

        <fieldset>
          <legend>{{ tipo === 'perdida' ? '¿Dónde la viste por última vez?' : '¿Dónde la encontraste?' }}</legend>
          <div class="grid2">
            <div class="field">
              <label for="r-ciudad">Ciudad *</label>
              <input id="r-ciudad" v-model="f.ciudad" list="ciudades" required maxlength="40" placeholder="Ej: Popayán" />
              <datalist id="ciudades"><option v-for="c in CIUDADES" :key="c" :value="c" /></datalist>
            </div>
            <div class="field">
              <label for="r-lugar">Barrio o lugar *</label>
              <input id="r-lugar" v-model="f.lugar" required maxlength="70" placeholder="Ej: Parque Caldas" />
            </div>
          </div>
          <div class="field">
            <label for="r-nota">Cuéntanos qué pasó</label>
            <input id="r-nota" v-model="f.nota" maxlength="255" placeholder="Ej: se soltó de la correa en la tarde" />
          </div>
        </fieldset>

        <fieldset v-if="pideTelefono">
          <legend>¿Cómo te contactan?</legend>
          <div class="field">
            <label for="r-tel">Tu WhatsApp o teléfono *</label>
            <input
              id="r-tel"
              v-model="telefono"
              type="tel"
              inputmode="tel"
              autocomplete="tel"
              required
              maxlength="20"
              placeholder="Ej: 300 123 4567"
            />
            <span class="field-hint">
              Cuando alguien avise que la vio o la encontró, podrá llamarte o escribirte. Lo guardamos en tu cuenta y solo se
              muestra a quien responde a tu reporte.
            </span>
          </div>
        </fieldset>

        <button class="btn btn-sun rep-submit" type="submit" :disabled="enviando">
          {{ enviando ? 'Publicando…' : tipo === 'perdida' ? 'Publicar búsqueda' : 'Publicar hallazgo' }}
        </button>
      </form>

      <aside class="rep-preview" aria-label="Vista previa">
        <p class="rep-preview-title">Así se verá tu reporte</p>
        <PetCard :reporte="previa" es-mio vista-previa />
      </aside>
    </div>
  </section>
</template>

<style scoped>
.rep-layout {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 2rem;
  align-items: start;
}

.rep-form { display: flex; flex-direction: column; gap: 1.4rem; }

.rep-tipo { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; }

.rep-op {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  text-align: left;
  padding: 0.9rem 1rem;
  border-radius: 14px;
  border: 2px solid var(--color-border);
  background: var(--color-white);
  color: var(--color-ink);
}
.rep-op span { font-size: 0.85rem; color: var(--color-ink-soft); }
.rep-op:hover { border-color: var(--color-teal); }
.rep-op.on { border-color: var(--color-teal); background: var(--color-mist); box-shadow: inset 0 0 0 1px var(--color-teal); }

fieldset { border: none; padding: 0; display: flex; flex-direction: column; gap: 1rem; }
legend { font-family: var(--font-title); font-weight: 600; font-size: 1.15rem; margin-bottom: 0.7rem; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }

input[type='file'] { padding: 0.5rem; background: var(--color-mist); border: 1px dashed var(--color-teal); border-radius: 10px; font-size: 0.9rem; }

.rep-submit { padding: 0.9rem; font-size: 1.05rem; box-shadow: 0 4px 0 #d79a1d; }

.rep-preview { position: sticky; top: 5.5rem; }
.rep-preview-title { font-weight: 800; color: var(--color-ink-soft); margin-bottom: 0.6rem; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; }

@media (max-width: 900px) {
  .rep-layout { grid-template-columns: 1fr; }
  .rep-preview { position: static; max-width: 340px; } /* la vista previa va después del formulario */
  .rep-tipo, .grid2 { grid-template-columns: 1fr; }
}

@media (max-width: 560px) {
  .rep-form { gap: 1.2rem; }
  .rep-submit { min-height: 52px; }
  .rep-preview { max-width: none; }
}
</style>
