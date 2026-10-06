<script setup lang="ts">
import { ref, onMounted } from 'vue';
import AdminLayout from '@/components/layout/AdminLayout.vue';
import api from '@/services/api';
import { Users, Plus, Phone, Mail, X } from 'lucide-vue-next';

const professionals = ref<any[]>([]);
const services = ref<any[]>([]);
const isLoading = ref(false);
const showAddModal = ref(false);

const newProf = ref({
  name: '',
  email: '',
  phone: '',
  bio: '',
  service_ids: [] as string[],
});

onMounted(async () => {
  await Promise.all([fetchProfessionals(), fetchServices()]);
});

async function fetchProfessionals() {
  isLoading.value = true;
  try {
    const res = await api.get('/professionals');
    professionals.value = res.data;
  } catch (err) {
    console.error(err);
  } finally {
    isLoading.value = false;
  }
}

async function fetchServices() {
  try {
    const res = await api.get('/services');
    services.value = res.data;
  } catch (err) {
    console.error(err);
  }
}

async function handleCreateProfessional() {
  try {
    await api.post('/professionals', newProf.value);
    showAddModal.value = false;
    newProf.value = { name: '', email: '', phone: '', bio: '', service_ids: [] };
    await fetchProfessionals();
  } catch (err: any) {
    alert(err.response?.data?.message || 'Erro ao cadastrar profissional.');
  }
}
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-extrabold text-white tracking-tight">Equipe de Profissionais</h1>
          <p class="text-xs text-slate-400 mt-1">Gerencie os atendentes, serviços habilitados e escalas</p>
        </div>
        <button
          @click="showAddModal = true"
          class="px-4 py-2.5 rounded-xl bg-amber-500 text-slate-950 font-bold text-xs shadow-lg shadow-amber-500/20 hover:bg-amber-400 transition flex items-center gap-2 cursor-pointer"
        >
          <Plus class="w-4 h-4" />
          Novo Profissional
        </button>
      </div>

      <!-- Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="prof in professionals"
          :key="prof.id"
          class="glass-panel p-5 rounded-2xl flex flex-col justify-between space-y-4"
        >
          <div class="flex items-start gap-3">
            <div class="w-12 h-12 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 font-bold text-base">
              {{ prof.name.charAt(0) }}
            </div>
            <div>
              <h3 class="font-bold text-white text-base">{{ prof.name }}</h3>
              <p class="text-xs text-slate-400 mt-0.5 line-clamp-2">
                {{ prof.bio || 'Sem biografia informada.' }}
              </p>
            </div>
          </div>

          <div class="space-y-1 text-xs text-slate-400 pt-2 border-t border-slate-800/60">
            <div v-if="prof.phone" class="flex items-center gap-1.5">
              <Phone class="w-3.5 h-3.5 text-slate-500" />
              <span>{{ prof.phone }}</span>
            </div>
            <div v-if="prof.email" class="flex items-center gap-1.5">
              <Mail class="w-3.5 h-3.5 text-slate-500" />
              <span>{{ prof.email }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Novo Profissional -->
      <div
        v-if="showAddModal"
        class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      >
        <div class="glass-panel w-full max-w-md p-6 rounded-3xl space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-bold text-white">Novo Profissional</h3>
            <button @click="showAddModal = false" class="text-slate-400 hover:text-white">
              <X class="w-5 h-5" />
            </button>
          </div>

          <form @submit.prevent="handleCreateProfessional" class="space-y-3">
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Nome Completo *</label>
              <input
                v-model="newProf.name"
                type="text"
                required
                placeholder="Ex: João Barbeiro"
                class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-amber-500"
              />
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Telefone / WhatsApp</label>
              <input
                v-model="newProf.phone"
                type="tel"
                placeholder="(11) 98765-4321"
                class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-amber-500"
              />
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">E-mail</label>
              <input
                v-model="newProf.email"
                type="email"
                placeholder="profissional@barbearia.com"
                class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-amber-500"
              />
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Biografia Curta</label>
              <textarea
                v-model="newProf.bio"
                rows="2"
                placeholder="Especialidades..."
                class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-amber-500 resize-none"
              ></textarea>
            </div>

            <div class="flex justify-end gap-2 pt-3">
              <button
                type="button"
                @click="showAddModal = false"
                class="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white"
              >
                Cancelar
              </button>
              <button
                type="submit"
                class="px-5 py-2 text-xs font-bold text-slate-950 bg-amber-500 hover:bg-amber-400 rounded-xl transition cursor-pointer"
              >
                Salvar Profissional
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>
