<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { usePublicBookingStore } from '@/stores/publicBooking';
import PublicLayout from '@/components/layout/PublicLayout.vue';
import SlotSelector from '@/components/ui/SlotSelector.vue';
import {
  Sparkles,
  User,
  Calendar as CalendarIcon,
  Clock,
  CheckCircle2,
  AlertCircle,
  ChevronRight,
  ArrowLeft,
  MapPin,
  Phone,
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();
const bookingStore = usePublicBookingStore();

const slug = computed(() => route.params.slug as string);
const step = ref<number>(1);

onMounted(async () => {
  if (slug.value) {
    await bookingStore.loadEstablishment(slug.value);
    await bookingStore.loadServices(slug.value);
  }
});

async function selectService(service: any) {
  bookingStore.selectedService = service;
  await bookingStore.loadProfessionals(slug.value, service.id);
  step.value = 2;
}

async function selectProfessional(prof: any) {
  bookingStore.selectedProfessional = prof;
  await bookingStore.fetchAvailability(slug.value);
  step.value = 3;
}

watch(
  () => bookingStore.selectedDate,
  async () => {
    if (step.value === 3) {
      await bookingStore.fetchAvailability(slug.value);
    }
  }
);

function selectSlot(slot: any) {
  bookingStore.selectedSlot = slot;
  step.value = 4;
}

async function handleConfirmBooking() {
  const success = await bookingStore.submitBooking(slug.value);
  if (success) {
    router.push({ name: 'PublicSuccess', params: { slug: slug.value } });
  }
}
</script>

<template>
  <PublicLayout>
    <div v-if="bookingStore.isLoading && !bookingStore.establishment" class="text-center py-20">
      <div class="inline-block animate-spin w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full mb-3"></div>
      <p class="text-slate-400 text-sm">Carregando informações do estabelecimento...</p>
    </div>

    <div v-else-if="bookingStore.establishment" class="space-y-6">
      <!-- Cabeçalho do Estabelecimento -->
      <div class="glass-panel rounded-2xl p-6 relative overflow-hidden">
        <div class="absolute -right-10 -bottom-10 w-40 h-40 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div class="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 class="text-2xl font-extrabold text-white tracking-tight">
              {{ bookingStore.establishment.name }}
            </h1>
            <div class="flex flex-wrap items-center gap-3 text-xs text-slate-400 mt-2">
              <span v-if="bookingStore.establishment.address" class="flex items-center gap-1">
                <MapPin class="w-3.5 h-3.5 text-amber-500" />
                {{ bookingStore.establishment.address }}
              </span>
              <span class="flex items-center gap-1">
                <Phone class="w-3.5 h-3.5 text-amber-500" />
                {{ bookingStore.establishment.phone }}
              </span>
            </div>
          </div>
          <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 w-fit">
            Agendamento Disponível
          </span>
        </div>
      </div>

      <!-- Barra de Progresso em Passos -->
      <div class="flex items-center justify-between px-2">
        <div
          v-for="i in 4"
          :key="i"
          class="flex items-center flex-1 last:flex-none"
        >
          <div
            :class="[
              'w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-200',
              step === i
                ? 'bg-amber-500 text-slate-950 ring-4 ring-amber-500/20'
                : step > i
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                : 'bg-slate-900 text-slate-500 border border-slate-800'
            ]"
          >
            <CheckCircle2 v-if="step > i" class="w-4 h-4" />
            <span v-else>{{ i }}</span>
          </div>
          <div
            v-if="i < 4"
            :class="[
              'h-0.5 flex-1 mx-2 transition-all duration-200',
              step > i ? 'bg-emerald-500/40' : 'bg-slate-800'
            ]"
          ></div>
        </div>
      </div>

      <!-- Alerta de Erro -->
      <div
        v-if="bookingStore.errorMessage"
        class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm flex items-center gap-3"
      >
        <AlertCircle class="w-5 h-5 shrink-0" />
        <span>{{ bookingStore.errorMessage }}</span>
      </div>

      <!-- ETAPA 1: SELEÇÃO DE SERVIÇO -->
      <div v-if="step === 1" class="space-y-4">
        <h2 class="text-lg font-bold text-white flex items-center gap-2">
          <Sparkles class="w-5 h-5 text-amber-500" />
          1. Escolha o Serviço
        </h2>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div
            v-for="service in bookingStore.services"
            :key="service.id"
            @click="selectService(service)"
            class="glass-panel p-5 rounded-2xl cursor-pointer hover:border-amber-500/50 hover:bg-slate-900/90 transition group flex flex-col justify-between"
          >
            <div>
              <div class="flex items-start justify-between gap-2">
                <h3 class="font-bold text-white group-hover:text-amber-400 transition">
                  {{ service.name }}
                </h3>
                <span class="text-sm font-extrabold text-amber-400 whitespace-nowrap">
                  R$ {{ Number(service.price).toFixed(2) }}
                </span>
              </div>
              <p class="text-xs text-slate-400 mt-2 line-clamp-2">
                {{ service.description || 'Atendimento profissional personalizado.' }}
              </p>
            </div>
            <div class="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-500">
              <span class="flex items-center gap-1">
                <Clock class="w-3.5 h-3.5 text-slate-400" />
                {{ service.duration_minutes }} min
              </span>
              <span class="text-amber-400 font-medium group-hover:translate-x-0.5 transition flex items-center">
                Selecionar &rarr;
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- ETAPA 2: SELEÇÃO DE PROFISSIONAL -->
      <div v-else-if="step === 2" class="space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-bold text-white flex items-center gap-2">
            <User class="w-5 h-5 text-amber-500" />
            2. Escolha o Profissional
          </h2>
          <button
            @click="step = 1"
            class="text-xs text-slate-400 hover:text-white flex items-center gap-1"
          >
            <ArrowLeft class="w-3.5 h-3.5" /> Voltar
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div
            v-for="prof in bookingStore.professionals"
            :key="prof.id"
            @click="selectProfessional(prof)"
            class="glass-panel p-5 rounded-2xl cursor-pointer hover:border-amber-500/50 hover:bg-slate-900/90 transition group flex items-center justify-between"
          >
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-amber-400 font-bold text-lg">
                {{ prof.name.charAt(0) }}
              </div>
              <div>
                <h3 class="font-bold text-white group-hover:text-amber-400 transition">
                  {{ prof.name }}
                </h3>
                <p class="text-xs text-slate-400 mt-0.5">
                  {{ prof.bio || 'Especialista em atendimento' }}
                </p>
              </div>
            </div>
            <ChevronRight class="w-5 h-5 text-slate-600 group-hover:text-amber-400 transition" />
          </div>
        </div>
      </div>

      <!-- ETAPA 3: DATA E HORÁRIO -->
      <div v-else-if="step === 3" class="space-y-5">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-bold text-white flex items-center gap-2">
            <CalendarIcon class="w-5 h-5 text-amber-500" />
            3. Selecione o Dia e Horário
          </h2>
          <button
            @click="step = 2"
            class="text-xs text-slate-400 hover:text-white flex items-center gap-1"
          >
            <ArrowLeft class="w-3.5 h-3.5" /> Voltar
          </button>
        </div>

        <!-- Seletor de Data -->
        <div class="glass-panel p-4 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <label class="text-sm font-medium text-slate-300">Data do Atendimento:</label>
          <input
            type="date"
            v-model="bookingStore.selectedDate"
            :min="new Date().toISOString().split('T')[0]"
            class="bg-slate-900 border border-slate-700 rounded-xl px-4 py-2 text-white text-sm focus:outline-none focus:border-amber-500"
          />
        </div>

        <!-- Grade de Horários -->
        <div class="glass-panel p-6 rounded-2xl space-y-4">
          <h3 class="text-sm font-semibold text-slate-300">Horários Disponíveis</h3>
          <div v-if="bookingStore.isLoading" class="text-center py-8">
            <div class="inline-block animate-spin w-6 h-6 border-2 border-amber-500 border-t-transparent rounded-full"></div>
            <p class="text-xs text-slate-400 mt-2">Buscando horários livres...</p>
          </div>
          <div v-else-if="bookingStore.availableSlots.length === 0" class="text-center py-8 text-slate-500 text-sm">
            Nenhum horário disponível para a data selecionada. Tente outro dia.
          </div>
          <SlotSelector
            v-else
            :slots="bookingStore.availableSlots"
            :selectedSlot="bookingStore.selectedSlot"
            @select="selectSlot"
          />
        </div>
      </div>

      <!-- ETAPA 4: DADOS DO CLIENTE E CONFIRMAÇÃO -->
      <div v-else-if="step === 4" class="space-y-5">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-bold text-white flex items-center gap-2">
            <CheckCircle2 class="w-5 h-5 text-amber-500" />
            4. Seus Dados e Confirmação
          </h2>
          <button
            @click="step = 3"
            class="text-xs text-slate-400 hover:text-white flex items-center gap-1"
          >
            <ArrowLeft class="w-3.5 h-3.5" /> Voltar
          </button>
        </div>

        <!-- Resumo da Reserva -->
        <div class="glass-card rounded-2xl p-5 border-amber-500/20 bg-amber-500/5 space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-slate-400">Serviço:</span>
            <span class="font-bold text-white">{{ bookingStore.selectedService?.name }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">Profissional:</span>
            <span class="font-bold text-white">{{ bookingStore.selectedProfessional?.name }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-400">Data e Hora:</span>
            <span class="font-bold text-amber-400">
              {{ bookingStore.selectedDate }} às {{ bookingStore.selectedSlot?.start_time }}
            </span>
          </div>
          <div class="flex justify-between pt-2 border-t border-slate-800">
            <span class="text-slate-400">Valor Total:</span>
            <span class="font-extrabold text-white text-base">
              R$ {{ Number(bookingStore.selectedService?.price).toFixed(2) }}
            </span>
          </div>
        </div>

        <!-- Formulário do Cliente -->
        <form @submit.prevent="handleConfirmBooking" class="glass-panel p-6 rounded-2xl space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Seu Nome Completo *</label>
            <input
              v-model="bookingStore.customerName"
              type="text"
              required
              placeholder="Ex: Carlos Silva"
              class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Celular / WhatsApp *</label>
            <input
              v-model="bookingStore.customerPhone"
              type="tel"
              required
              placeholder="Ex: (11) 98765-4321"
              class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">E-mail (opcional para confirmação)</label>
            <input
              v-model="bookingStore.customerEmail"
              type="email"
              placeholder="Ex: seuemail@exemplo.com"
              class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Observações (opcional)</label>
            <textarea
              v-model="bookingStore.customerNotes"
              rows="2"
              placeholder="Alguma preferência ou informação relevante..."
              class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500 resize-none"
            ></textarea>
          </div>

          <button
            type="submit"
            :disabled="bookingStore.isLoading"
            class="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-amber-500 to-amber-400 text-slate-950 font-bold text-sm shadow-lg shadow-amber-500/20 hover:opacity-95 transition disabled:opacity-50 cursor-pointer"
          >
            <span v-if="bookingStore.isLoading">Finalizando agendamento...</span>
            <span v-else>Confirmar Agendamento</span>
          </button>
        </form>
      </div>
    </div>
  </PublicLayout>
</template>
