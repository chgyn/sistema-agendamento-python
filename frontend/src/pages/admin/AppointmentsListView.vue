<script setup lang="ts">
import { ref, onMounted } from 'vue';
import AdminLayout from '@/components/layout/AdminLayout.vue';
import StatusBadge from '@/components/ui/StatusBadge.vue';
import { useAppointmentsStore } from '@/stores/appointments';
import { Clock, Filter, Ban, CheckCircle, AlertTriangle } from 'lucide-vue-next';

const appointmentsStore = useAppointmentsStore();

const startDate = ref(new Date().toISOString().split('T')[0]);
const endDate = ref(new Date(Date.now() + 7 * 86400000).toISOString().split('T')[0]);
const selectedStatus = ref('');

const showCancelModal = ref(false);
const cancellingAppointmentId = ref<string | null>(null);
const cancelReason = ref('');

onMounted(async () => {
  await fetchFiltered();
});

async function fetchFiltered() {
  const start = `${startDate.value}T00:00:00Z`;
  const end = `${endDate.value}T23:59:59Z`;
  await appointmentsStore.fetchAppointments(start, end, undefined, selectedStatus.value || undefined);
}

function openCancel(id: string) {
  cancellingAppointmentId.value = id;
  cancelReason.value = '';
  showCancelModal.value = true;
}

async function confirmCancel() {
  if (!cancellingAppointmentId.value || !cancelReason.value) return;
  await appointmentsStore.cancelAppointment(cancellingAppointmentId.value, cancelReason.value);
  showCancelModal.value = false;
  cancellingAppointmentId.value = null;
}
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-2xl font-extrabold text-white tracking-tight">Gestão de Agendamentos</h1>
          <p class="text-xs text-slate-400 mt-1">Histórico e controle detalhado do ciclo de vida dos atendimentos</p>
        </div>
      </div>

      <!-- Filtros -->
      <div class="glass-panel p-4 rounded-2xl flex flex-wrap items-center gap-3">
        <div class="flex items-center gap-2">
          <label class="text-xs text-slate-400 font-semibold">De:</label>
          <input
            type="date"
            v-model="startDate"
            class="bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none"
          />
        </div>

        <div class="flex items-center gap-2">
          <label class="text-xs text-slate-400 font-semibold">Até:</label>
          <input
            type="date"
            v-model="endDate"
            class="bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none"
          />
        </div>

        <div class="flex items-center gap-2">
          <label class="text-xs text-slate-400 font-semibold">Status:</label>
          <select
            v-model="selectedStatus"
            class="bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none"
          >
            <option value="">Todos</option>
            <option value="SCHEDULED">Agendado</option>
            <option value="CONFIRMED">Confirmado</option>
            <option value="COMPLETED">Concluído</option>
            <option value="CANCELLED">Cancelado</option>
            <option value="NO_SHOW">Não Compareceu</option>
          </select>
        </div>

        <button
          @click="fetchFiltered"
          class="px-4 py-1.5 bg-amber-500 text-slate-950 text-xs font-bold rounded-xl hover:bg-amber-400 transition cursor-pointer flex items-center gap-1 ml-auto"
        >
          <Filter class="w-3.5 h-3.5" />
          Filtrar
        </button>
      </div>

      <!-- Tabela -->
      <div class="glass-panel rounded-2xl overflow-hidden border border-slate-800">
        <div v-if="appointmentsStore.isLoading" class="p-8 text-center text-slate-400 text-xs">
          Buscando registros...
        </div>

        <div v-else-if="appointmentsStore.appointments.length === 0" class="p-12 text-center text-slate-500 text-sm">
          Nenhum agendamento encontrado no período informado.
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-sm text-slate-300">
            <thead class="text-xs uppercase bg-slate-900/60 text-slate-400 border-b border-slate-800">
              <tr>
                <th class="px-5 py-3">Data & Hora</th>
                <th class="px-5 py-3">Cliente</th>
                <th class="px-5 py-3">Profissional</th>
                <th class="px-5 py-3">Serviço</th>
                <th class="px-5 py-3">Status</th>
                <th class="px-5 py-3 text-right">Ações</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60">
              <tr v-for="appt in appointmentsStore.appointments" :key="appt.id" class="hover:bg-slate-900/40 transition">
                <td class="px-5 py-3.5 font-medium text-white whitespace-nowrap">
                  {{ new Date(appt.start_datetime).toLocaleDateString('pt-BR') }} às
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
                    v-if="appt.status !== 'CANCELLED' && appt.status !== 'COMPLETED'"
                    @click="openCancel(appt.id)"
                    class="px-2 py-1 text-xs rounded-lg text-rose-400 hover:bg-rose-500/10 border border-rose-500/20 font-medium transition cursor-pointer"
                  >
                    Cancelar
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Modal de Cancelamento -->
      <div
        v-if="showCancelModal"
        class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      >
        <div class="glass-panel w-full max-w-md p-6 rounded-3xl space-y-4">
          <div class="flex items-center gap-3 text-rose-400">
            <AlertTriangle class="w-6 h-6 shrink-0" />
            <h3 class="text-lg font-bold text-white">Confirmar Cancelamento</h3>
          </div>
          <p class="text-xs text-slate-400">
            Informe o motivo do cancelamento. O horário será liberado na agenda e o histórico mantido.
          </p>
          <textarea
            v-model="cancelReason"
            rows="3"
            placeholder="Ex: Imprevisto informado pelo cliente via WhatsApp"
            class="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-amber-500 resize-none"
          ></textarea>
          <div class="flex justify-end gap-2 pt-2">
            <button
              @click="showCancelModal = false"
              class="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white rounded-xl"
            >
              Voltar
            </button>
            <button
              @click="confirmCancel"
              :disabled="!cancelReason"
              class="px-4 py-2 text-xs font-bold text-white bg-rose-600 hover:bg-rose-500 rounded-xl disabled:opacity-50 transition cursor-pointer"
            >
              Confirmar Cancelamento
            </button>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>
