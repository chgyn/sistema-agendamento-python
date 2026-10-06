<script setup lang="ts">
import { ref, onMounted } from 'vue';
import AdminLayout from '@/components/layout/AdminLayout.vue';
import { useAuthStore } from '@/stores/auth';
import api from '@/services/api';
import { Settings, ExternalLink, Save, CheckCircle2 } from 'lucide-vue-next';

const authStore = useAuthStore();

const formData = ref({
  name: '',
  phone: '',
  email: '',
  address: '',
});

const isSaving = ref(false);
const saveSuccess = ref(false);

onMounted(async () => {
  await authStore.fetchEstablishment();
  if (authStore.establishment) {
    formData.value = {
      name: authStore.establishment.name,
      phone: authStore.establishment.phone,
      email: authStore.establishment.email,
      address: authStore.establishment.address || '',
    };
  }
});

async function handleSave() {
  isSaving.value = true;
  saveSuccess.value = false;
  try {
    const res = await api.patch('/establishment/me', formData.value);
    authStore.establishment = res.data;
    saveSuccess.value = true;
    setTimeout(() => {
      saveSuccess.value = false;
    }, 3000);
  } catch (err: any) {
    alert(err.response?.data?.message || 'Falha ao salvar configurações.');
  } finally {
    isSaving.value = false;
  }
}
</script>

<template>
  <AdminLayout>
    <div class="max-w-2xl space-y-6">
      <div>
        <h1 class="text-2xl font-extrabold text-white tracking-tight">Configurações da Unidade</h1>
        <p class="text-xs text-slate-400 mt-1">Dados cadastrais e link público de agendamento</p>
      </div>

      <!-- Link Público -->
      <div v-if="authStore.establishment" class="glass-panel p-5 rounded-2xl flex items-center justify-between">
        <div>
          <span class="text-xs font-semibold text-slate-400">Página Pública de Agendamento</span>
          <p class="font-mono text-xs text-amber-400 mt-1">
            /p/{{ authStore.establishment.slug }}
          </p>
        </div>
        <a
          :href="`/p/${authStore.establishment.slug}`"
          target="_blank"
          class="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 hover:border-amber-500/50 text-xs font-semibold text-white transition flex items-center gap-1.5"
        >
          <span>Abrir</span>
          <ExternalLink class="w-3.5 h-3.5" />
        </a>
      </div>

      <!-- Formulário -->
      <form @submit.prevent="handleSave" class="glass-panel p-6 rounded-3xl space-y-4">
        <div v-if="saveSuccess" class="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs rounded-xl flex items-center gap-2">
          <CheckCircle2 class="w-4 h-4 shrink-0" />
          <span>Configurações salvas com sucesso!</span>
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Nome do Estabelecimento *</label>
          <input
            v-model="formData.name"
            type="text"
            required
            class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-amber-500"
          />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Telefone Principal *</label>
            <input
              v-model="formData.phone"
              type="text"
              required
              class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-amber-500"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">E-mail de Contato *</label>
            <input
              v-model="formData.email"
              type="email"
              required
              class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-amber-500"
            />
          </div>
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Endereço Completo</label>
          <input
            v-model="formData.address"
            type="text"
            placeholder="Rua, número, bairro, cidade - UF"
            class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-amber-500"
          />
        </div>

        <div class="pt-2 flex justify-end">
          <button
            type="submit"
            :disabled="isSaving"
            class="px-6 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs shadow-lg shadow-amber-500/20 transition flex items-center gap-2 cursor-pointer disabled:opacity-50"
          >
            <Save class="w-4 h-4" />
            <span>{{ isSaving ? 'Salvando...' : 'Salvar Alterações' }}</span>
          </button>
        </div>
      </form>
    </div>
  </AdminLayout>
</template>
