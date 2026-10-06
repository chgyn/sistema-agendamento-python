<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import AdminLayout from '@/components/layout/AdminLayout.vue';
import StatusBadge from '@/components/ui/StatusBadge.vue';
import { useAppointmentsStore } from '@/stores/appointments';
import {
  Calendar,
  CheckCircle2,
  Clock,
  XCircle,
  Sparkles,
  User,
  ArrowRight,
} from 'lucide-vue-next';

const appointmentsStore = useAppointmentsStore();

const todayStr = new Date().toISOString().split('T')[0];

onMounted(async () => {
  const start = `${todayStr}T00:00:00Z`;
  const end = `${todayStr}T23:59:59Z`;
  await appointmentsStore.fetchAppointments(start, end);
});

const todayAppointments = computed(() => appointmentsStore.appointments);

const totalToday = computed(() => todayAppointments.value.length);
const totalConfirmed = computed(() => todayAppointments.value.filter((a) => a.status === 'CONFIRMED').length);
const totalCompleted = computed(() => todayAppointments.value.filter((a) => a.status === 'COMPLETED').length);
const totalCancelled = computed(() => todayAppointments.value.filter((a) => a.status === 'CANCELLED').length);

async function handleStatusChange(id: string, status: string) {
  await appointmentsStore.updateStatus(id, status);
}
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <!-- Título -->
      <div>
        <h1 class="text-2xl font-extrabold text-white tracking-tight">Painel de Controle</h1>
        <p class="text-xs text-slate-400 mt-1">Resumo operacional e atendimentos previstos para hoje</p>
      </div>

      <!-- Cards de Métricas -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="glass-panel p-5 rounded-2xl flex items-center justify-between">
          <div>
            <span class="text-xs font-semibold text-slate-400">Total Hoje</span>
            <p class="text-2xl font-black text-white mt-1">{{ totalToday }}</p>
          </div>
          <div class="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center">
            <Calendar class="w-5 h-5" />
          </div>
        </div>

        <div class="glass-panel p-5 rounded-2xl flex items-center justify-between">
          <div>
            <span class="text-xs font-semibold text-slate-400">Confirmados</span>
            <p class="text-2xl font-black text-emerald-400 mt-1">{{ totalConfirmed }}</p>
          </div>
          <div class="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
            <CheckCircle2 class="w-5 h-5" />
          </div>
        </div>

        <div class="glass-panel p-5 rounded-2xl flex items-center justify-between">
          <div>
            <span class="text-xs font-semibold text-slate-400">Concluídos</span>
            <p class="text-2xl font-black text-blue-400 mt-1">{{ totalCompleted }}</p>
          </div>
          <div class="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center">
            <Clock class="w-5 h-5" />
          </div>
        </div>

        <div class="glass-panel p-5 rounded-2xl flex items-center justify-between">
          <div>
            <span class="text-xs font-semibold text-slate-400">Cancelados</span>
            <p class="text-2xl font-black text-rose-400 mt-1">{{ totalCancelled }}</p>
          </div>
          <div class="w-10 h-10 rounded-xl bg-rose-500/10 text-rose-400 flex items-center justify-center">
            <XCircle class="w-5 h-5" />
          </div>
        </div>
      </div>

      <!-- Tabela de Atendimentos de Hoje -->
      <div class="glass-panel rounded-2xl overflow-hidden border border-slate-800">
        <div class="p-5 border-b border-slate-800 flex items-center justify-between">
          <h2 class="text-base font-bold text-white flex items-center gap-2">
            <Clock class="w-4 h-4 text-amber-500" />
            Atendimentos de Hoje
          </h2>
          <router-link
            to="/admin/appointments"
            class="text-xs text-amber-400 hover:text-amber-300 font-semibold flex items-center gap-1"
          >
            Ver todos &rarr;
          </router-link>
        </div>

        <div v-if="appointmentsStore.isLoading" class="p-8 text-center text-slate-400 text-xs">
          Carregando atendimentos...
        </div>

        <div v-else-if="todayAppointments.length === 0" class="p-12 text-center text-slate-500 text-sm">
          Nenhum agendamento programado para hoje.
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-sm text-slate-300">
            <thead class="text-xs uppercase bg-slate-900/60 text-slate-400 border-b border-slate-800">
              <tr>
                <th class="px-5 py-3">Horário</th>
                <th class="px-5 py-3">Cliente</th>
                <th class="px-5 py-3">Profissional</th>
                <th class="px-5 py-3">Serviço</th>
                <th class="px-5 py-3">Status</th>
                <th class="px-5 py-3 text-right">Ações Rápidas</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60">
              <tr v-for="appt in todayAppointments" :key="appt.id" class="hover:bg-slate-900/40 transition">
                <td class="px-5 py-3.5 font-bold text-white whitespace-nowrap">
                  {{ new Date(appt.start_datetime).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) }}
                </td>
                <td class="px-5 py-3.5">
                  <div class="font-medium text-white">{{ appt.customer_name }}</div>
                  <div class="text-xs text-slate-500">{{ appt.customer_phone }}</div>
                </td>
                <td class="px-5 py-3.5 text-slate-300">{{ appt.professional_name }}</td>
                <td class="px-5 py-3.5 text-slate-300">{{ appt.service_name }}</td>
                <td class="px-5 py-3.5">
                  <StatusBadge :status="appt.status" />
                </td>
                <td class="px-5 py-3.5 text-right whitespace-nowrap space-x-1">
                  <button
                    v-if="appt.status === 'SCHEDULED'"
                    @click="handleStatusChange(appt.id, 'CONFIRMED')"
                    class="px-2.5 py-1 text-xs rounded-lg bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 font-medium transition cursor-pointer"
                  >
                    Confirmar
                  </button>
                  <button
                    v-if="appt.status === 'CONFIRMED'"
                    @click="handleStatusChange(appt.id, 'COMPLETED')"
                    class="px-2.5 py-1 text-xs rounded-lg bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 font-medium transition cursor-pointer"
                  >
                    Concluir
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>
