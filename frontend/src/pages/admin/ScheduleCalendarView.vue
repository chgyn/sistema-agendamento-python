<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import AdminLayout from '@/components/layout/AdminLayout.vue';
import StatusBadge from '@/components/ui/StatusBadge.vue';
import { useAppointmentsStore } from '@/stores/appointments';
import api from '@/services/api';
import { Calendar as CalendarIcon, Clock, User, ChevronLeft, ChevronRight } from 'lucide-vue-next';

const appointmentsStore = useAppointmentsStore();

const selectedDate = ref(new Date().toISOString().split('T')[0]);
const professionals = ref<any[]>([]);

onMounted(async () => {
  try {
    const res = await api.get('/professionals');
    professionals.value = res.data;
  } catch (err) {
    console.error(err);
  }
  await loadCalendar();
});

watch(selectedDate, async () => {
  await loadCalendar();
});

async function loadCalendar() {
  const start = `${selectedDate.value}T00:00:00Z`;
  const end = `${selectedDate.value}T23:59:59Z`;
  await appointmentsStore.fetchAppointments(start, end);
}

function nextDay() {
  const d = new Date(selectedDate.value);
  d.setDate(d.getDate() + 1);
  selectedDate.value = d.toISOString().split('T')[0];
}

function prevDay() {
  const d = new Date(selectedDate.value);
  d.setDate(d.getDate() - 1);
  selectedDate.value = d.toISOString().split('T')[0];
}
</script>

<template>
  <AdminLayout>
    <div class="space-y-6">
      <!-- Topo com Navegação de Data -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-2xl font-extrabold text-white tracking-tight">Agenda Visual</h1>
          <p class="text-xs text-slate-400 mt-1">Visão cronológica dos atendimentos por profissional</p>
        </div>

        <div class="flex items-center gap-2 glass-panel px-3 py-1.5 rounded-2xl">
          <button @click="prevDay" class="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800">
            <ChevronLeft class="w-4 h-4" />
          </button>
          <input
            type="date"
            v-model="selectedDate"
            class="bg-transparent text-sm text-white font-semibold focus:outline-none cursor-pointer"
          />
          <button @click="nextDay" class="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800">
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- Colunas de Profissionais -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        <div
          v-for="prof in professionals"
          :key="prof.id"
          class="glass-panel rounded-2xl flex flex-col h-[650px] overflow-hidden"
        >
          <!-- Cabeçalho do Profissional -->
          <div class="p-4 border-b border-slate-800 bg-slate-900/50 flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 font-bold flex items-center justify-center">
              {{ prof.name.charAt(0) }}
            </div>
            <div>
              <h3 class="font-bold text-sm text-white">{{ prof.name }}</h3>
              <p class="text-xs text-slate-500">{{ prof.phone || 'Sem telefone' }}</p>
            </div>
          </div>

          <!-- Lista de Agendamentos do Profissional no Dia -->
          <div class="flex-1 p-4 overflow-y-auto space-y-3">
            <div
              v-for="appt in appointmentsStore.appointments.filter((a) => a.professional_id === prof.id)"
              :key="appt.id"
              class="glass-card p-3.5 rounded-xl border border-slate-800/80 hover:border-slate-700 transition space-y-2"
            >
              <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-amber-400 flex items-center gap-1">
                  <Clock class="w-3.5 h-3.5" />
                  {{ new Date(appt.start_datetime).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) }}
                  -
                  {{ new Date(appt.end_datetime).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) }}
                </span>
                <StatusBadge :status="appt.status" />
              </div>

              <div>
                <p class="font-semibold text-xs text-white">{{ appt.customer_name }}</p>
                <p class="text-[11px] text-slate-400 mt-0.5">{{ appt.service_name }}</p>
              </div>

              <div v-if="appt.notes" class="text-[11px] text-slate-500 italic">
                "{{ appt.notes }}"
              </div>
            </div>

            <div
              v-if="appointmentsStore.appointments.filter((a) => a.professional_id === prof.id).length === 0"
              class="h-full flex items-center justify-center text-xs text-slate-500 text-center"
            >
              Nenhum agendamento para este profissional nesta data.
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>
