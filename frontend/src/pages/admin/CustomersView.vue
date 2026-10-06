<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import AdminLayout from '@/components/layout/AdminLayout.vue';
import Pagination from '@/components/ui/Pagination.vue';
import api from '@/services/api';
import { Search } from 'lucide-vue-next';

interface CustomerItem {
  id: string;
  name: string;
  phone: string;
  email?: string | null;
  created_at: string;
}

const customers = ref<CustomerItem[]>([]);
const searchQuery = ref('');
const isLoading = ref(false);

const pagination = ref({
  page: 1,
  pageSize: 10,
  total: 0,
  totalPages: 1,
});

let searchTimeout: any = null;

onMounted(async () => {
  await fetchCustomers(1, pagination.value.pageSize);
});

async function fetchCustomers(page: number = 1, pageSize: number = pagination.value.pageSize) {
  isLoading.value = true;
  try {
    const params: Record<string, any> = {
      page,
      page_size: pageSize,
    };
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim();
    }

    const res = await api.get('/customers', { params });
    if (res.data && Array.isArray(res.data.items)) {
      customers.value = res.data.items;
      pagination.value = {
        page: res.data.page ?? page,
        pageSize: res.data.page_size ?? pageSize,
        total: res.data.total ?? 0,
        totalPages: res.data.total_pages ?? 1,
      };
    } else if (Array.isArray(res.data)) {
      customers.value = res.data;
      pagination.value = {
        page: 1,
        pageSize: res.data.length,
        total: res.data.length,
        totalPages: 1,
      };
    }
  } catch (err) {
    console.error('Erro ao carregar clientes:', err);
  } finally {
    isLoading.value = false;
  }
}

watch(searchQuery, () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    fetchCustomers(1, pagination.value.pageSize);
  }, 350);
});

function handlePageChange({ page, pageSize }: { page: number; pageSize: number }) {
  fetchCustomers(page, pageSize);
}
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
        <div v-if="isLoading && customers.length === 0" class="p-8 text-center text-slate-400 text-xs">
          Carregando clientes...
        </div>

        <div v-else-if="!isLoading && customers.length === 0" class="p-12 text-center text-slate-500 text-sm">
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
              <tr v-for="c in customers" :key="c.id" class="hover:bg-slate-900/40 transition">
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

        <!-- Paginação -->
        <Pagination
          :page="pagination.page"
          :page-size="pagination.pageSize"
          :total="pagination.total"
          :totalPages="pagination.totalPages"
          :isLoading="isLoading"
          @change="handlePageChange"
        />
      </div>
    </div>
  </AdminLayout>
</template>
