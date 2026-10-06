<script setup lang="ts">
import { ref, onMounted } from 'vue';
import AdminLayout from '@/components/layout/AdminLayout.vue';
import api from '@/services/api';
import { Sparkles, Plus, Clock, DollarSign, X } from 'lucide-vue-next';

const services = ref<any[]>([]);
const isLoading = ref(false);
const showAddModal = ref(false);

const newService = ref({
  name: '',
  description: '',
  duration_minutes: 30,
  price: 50.0,
});

onMounted(async () => {
  await fetchServices();
});

async function fetchServices() {
  isLoading.value = true;
  try {
    const res = await api.get('/services');
    services.value = res.data;
  } catch (err) {
    console.error(err);
  } finally {
    isLoading.value = false;
  }
}

async function handleCreateService() {
  try {
    await api.post('/services', newService.value);
    showAddModal.value = false;
    newService.value = { name: '', description: '', duration_minutes: 30, price: 50.0 };
    await fetchServices();
  } catch (err: any) {
    alert(err.response?.data?.message || 'Erro ao cadastrar serviço.');
  }
}
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-extrabold text-white tracking-tight">Catálogo de Serviços</h1>
          <p class="text-xs text-slate-400 mt-1">Gerencie os procedimentos, durações e preços oferecidos</p>
        </div>
        <button
          @click="showAddModal = true"
          class="px-4 py-2.5 rounded-xl bg-amber-500 text-slate-950 font-bold text-xs shadow-lg shadow-amber-500/20 hover:bg-amber-400 transition flex items-center gap-2 cursor-pointer"
        >
          <Plus class="w-4 h-4" />
          Novo Serviço
        </button>
      </div>

      <!-- Grid de Serviços -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="service in services"
          :key="service.id"
          class="glass-panel p-5 rounded-2xl flex flex-col justify-between space-y-4"
        >
          <div>
            <div class="flex items-start justify-between gap-2">
              <h3 class="font-bold text-white text-base">{{ service.name }}</h3>
              <span class="text-sm font-extrabold text-amber-400">
                R$ {{ Number(service.price).toFixed(2) }}
              </span>
            </div>
            <p class="text-xs text-slate-400 mt-2 line-clamp-2">
              {{ service.description || 'Sem descrição informada.' }}
            </p>
          </div>

          <div class="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span class="flex items-center gap-1.5">
              <Clock class="w-3.5 h-3.5 text-amber-500" />
              {{ service.duration_minutes }} minutos
            </span>
            <span
              :class="[
                'px-2 py-0.5 rounded-full text-[10px] font-semibold border',
                service.is_active ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-slate-800 text-slate-500 border-slate-700'
              ]"
            >
              {{ service.is_active ? 'Ativo' : 'Inativo' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Modal de Adicionar Serviço -->
      <div
        v-if="showAddModal"
        class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      >
        <div class="glass-panel w-full max-w-md p-6 rounded-3xl space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-bold text-white">Novo Serviço</h3>
            <button @click="showAddModal = false" class="text-slate-400 hover:text-white">
              <X class="w-5 h-5" />
            </button>
          </div>

          <form @submit.prevent="handleCreateService" class="space-y-3">
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Nome do Serviço *</label>
              <input
                v-model="newService.name"
                type="text"
                required
                placeholder="Ex: Corte Degrade + Barba"
                class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-amber-500"
              />
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1">Descrição</label>
              <textarea
                v-model="newService.description"
                rows="2"
                placeholder="Detalhes sobre o procedimento..."
                class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-amber-500 resize-none"
              ></textarea>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-semibold text-slate-300 mb-1">Duração (min) *</label>
                <input
                  v-model.number="newService.duration_minutes"
                  type="number"
                  min="5"
                  step="5"
                  required
                  class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label class="block text-xs font-semibold text-slate-300 mb-1">Preço (R$) *</label>
                <input
                  v-model.number="newService.price"
                  type="number"
                  min="0"
                  step="0.5"
                  required
                  class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-amber-500"
                />
              </div>
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
                Salvar Serviço
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>
