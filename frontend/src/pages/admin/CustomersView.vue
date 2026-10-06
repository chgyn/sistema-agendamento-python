<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import AdminLayout from '@/components/layout/AdminLayout.vue';
import api from '@/services/api';
import { Contact, Search, Phone, Mail, Calendar } from 'lucide-vue-next';

const customers = ref<any[]>([]);
const searchQuery = ref('');
const isLoading = ref(false);

onMounted(async () => {
  isLoading.value = true;
  try {
    const res = await api.get('/customers');
    customers.value = res.data;
  } catch (err) {
    console.error(err);
  } finally {
    isLoading.value = false;
  }
});

const filteredCustomers = computed(() => {
  if (!searchQuery.value) return customers.value;
  const q = searchQuery.value.toLowerCase();
  return customers.value.filter(
    (c) => c.name.toLowerCase().includes(q) || c.phone.includes(q)
  );
});
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-2xl font-extrabold text-white tracking-tight">Base de Clientes</h1>
          <p class="text-xs text-slate-400 mt-1">Clientes cadastrados e histórico de contatos do estabelecimento</p>
        </div>

        <div class="relative w-full sm:w-72">
          <Search class="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar por nome ou celular..."
            class="w-full bg-slate-900 border border-slate-700/80 rounded-xl pl-10 pr-4 py-2 text-xs text-white focus:outline-none focus:border-amber-500"
          />
        </div>
      </div>

      <!-- Tabela -->
      <div class="glass-panel rounded-2xl overflow-hidden border border-slate-800">
        <div v-if="isLoading" class="p-8 text-center text-slate-400 text-xs">
          Carregando clientes...
        </div>

        <div v-else-if="filteredCustomers.length === 0" class="p-12 text-center text-slate-500 text-sm">
          Nenhum cliente encontrado.
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-sm text-slate-300">
            <thead class="text-xs uppercase bg-slate-900/60 text-slate-400 border-b border-slate-800">
              <tr>
                <th class="px-5 py-3">Nome</th>
                <th class="px-5 py-3">Celular / WhatsApp</th>
                <th class="px-5 py-3">E-mail</th>
                <th class="px-5 py-3">Cadastrado em</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60">
              <tr v-for="c in filteredCustomers" :key="c.id" class="hover:bg-slate-900/40 transition">
                <td class="px-5 py-3.5 font-bold text-white flex items-center gap-2.5">
                  <div class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-xs text-amber-400 font-bold">
                    {{ c.name.charAt(0) }}
                  </div>
                  <span>{{ c.name }}</span>
                </td>
                <td class="px-5 py-3.5 whitespace-nowrap text-slate-300">
                  {{ c.phone }}
                </td>
                <td class="px-5 py-3.5 text-slate-400">
                  {{ c.email || 'Não informado' }}
                </td>
                <td class="px-5 py-3.5 text-xs text-slate-500 whitespace-nowrap">
                  {{ new Date(c.created_at).toLocaleDateString('pt-BR') }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>
