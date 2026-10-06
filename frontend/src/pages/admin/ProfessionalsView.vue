<script setup lang="ts">
import { ref, onMounted } from 'vue';
import AdminLayout from '@/components/layout/AdminLayout.vue';
import Pagination from '@/components/ui/Pagination.vue';
import api from '@/services/api';
import { Users, Plus, Phone, Mail, X } from 'lucide-vue-next';

interface ProfessionalItem {
  id: string;
  name: string;
  email?: string | null;
  phone?: string | null;
  bio?: string | null;
  is_active: boolean;
  service_ids: string[];
}

const professionals = ref<ProfessionalItem[]>([]);
const services = ref<any[]>([]);
const isLoading = ref(false);
const showAddModal = ref(false);

const pagination = ref({
  page: 1,
  pageSize: 10,
  total: 0,
  totalPages: 1,
});

const newProf = ref({
  name: '',
  email: '',
  phone: '',
  bio: '',
  service_ids: [] as string[],
});

onMounted(async () => {
  await Promise.all([fetchProfessionals(1, pagination.value.pageSize), fetchServices()]);
});

async function fetchProfessionals(page: number = 1, pageSize: number = pagination.value.pageSize) {
  isLoading.value = true;
  try {
    const params = {
      page,
      page_size: pageSize,
    };
    const res = await api.get('/professionals', { params });
    if (res.data && Array.isArray(res.data.items)) {
      professionals.value = res.data.items;
      pagination.value = {
        page: res.data.page ?? page,
        pageSize: res.data.page_size ?? pageSize,
        total: res.data.total ?? 0,
        totalPages: res.data.total_pages ?? 1,
      };
    } else if (Array.isArray(res.data)) {
      professionals.value = res.data;
      pagination.value = {
        page: 1,
        pageSize: res.data.length,
        total: res.data.length,
        totalPages: 1,
      };
    }
  } catch (err) {
    console.error('Erro ao buscar profissionais:', err);
  } finally {
    isLoading.value = false;
  }
}

async function fetchServices() {
  try {
    const res = await api.get('/services', { params: { all_records: true } });
    services.value = res.data.items || res.data;
  } catch (err) {
    console.error('Erro ao buscar serviços:', err);
  }
}

function handlePageChange({ page, pageSize }: { page: number; pageSize: number }) {
  fetchProfessionals(page, pageSize);
}

async function handleCreateProfessional() {
  try {
    await api.post('/professionals', newProf.value);
    showAddModal.value = false;
    newProf.value = { name: '', email: '', phone: '', bio: '', service_ids: [] };
    await fetchProfessionals(1, pagination.value.pageSize);
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

      <div v-if="isLoading && professionals.length === 0" class="p-12 text-center text-slate-400 text-xs">
        Carregando profissionais...
      </div>

      <div v-else-if="!isLoading && professionals.length === 0" class="p-12 text-center text-slate-500 text-sm">
        Nenhum profissional cadastrado até o momento.
      </div>

      <!-- Grid de Profissionais -->
      <div v-else class="space-y-4">
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

        <!-- Painel de Paginação -->
        <div class="glass-panel rounded-2xl overflow-hidden border border-slate-800">
          <Pagination
            :page="pagination.page"
            :page-size="pagination.pageSize"
            :total="pagination.total"
            :total-pages="pagination.totalPages"
            :is-loading="isLoading"
            @change="handlePageChange"
          />
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
