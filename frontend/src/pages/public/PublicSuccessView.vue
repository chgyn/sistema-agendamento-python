<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { usePublicBookingStore } from '@/stores/publicBooking';
import PublicLayout from '@/components/layout/PublicLayout.vue';
import { CheckCircle2, Calendar, User, Sparkles, Home } from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();
const bookingStore = usePublicBookingStore();

const slug = computed(() => route.params.slug as string);
const booking = computed(() => bookingStore.lastBooking);

function handleNewBooking() {
  bookingStore.resetFlow();
  router.push({ name: 'PublicBooking', params: { slug: slug.value } });
}
</script>

<template>
  <PublicLayout>
    <div class="max-w-md mx-auto text-center space-y-6 py-10">
      <!-- Ícone de Sucesso -->
      <div class="w-20 h-20 bg-emerald-500/10 border border-emerald-500/20 rounded-full flex items-center justify-center mx-auto text-emerald-400">
        <CheckCircle2 class="w-10 h-10" />
      </div>

      <div class="space-y-2">
        <h1 class="text-2xl font-extrabold text-white">Agendamento Realizado!</h1>
        <p class="text-sm text-slate-400">
          Seu horário foi reservado com sucesso no estabelecimento.
        </p>
      </div>

      <!-- Card com Dados do Agendamento -->
      <div v-if="booking" class="glass-panel p-6 rounded-2xl text-left space-y-3 text-sm">
        <div class="flex items-center gap-3 text-slate-300">
          <Sparkles class="w-4 h-4 text-amber-500 shrink-0" />
          <span><strong>Serviço:</strong> {{ booking.service_name }}</span>
        </div>
        <div class="flex items-center gap-3 text-slate-300">
          <User class="w-4 h-4 text-amber-500 shrink-0" />
          <span><strong>Profissional:</strong> {{ booking.professional_name }}</span>
        </div>
        <div class="flex items-center gap-3 text-slate-300">
          <Calendar class="w-4 h-4 text-amber-500 shrink-0" />
          <span><strong>Início:</strong> {{ new Date(booking.start_datetime).toLocaleString('pt-BR') }}</span>
        </div>
        <div class="pt-3 border-t border-slate-800 text-xs text-slate-500 text-center">
          Identificador da Reserva: <span class="font-mono text-slate-400">{{ booking.id }}</span>
        </div>
      </div>

      <div class="pt-4">
        <button
          @click="handleNewBooking"
          class="w-full py-3 px-4 rounded-xl bg-slate-900 border border-slate-700 text-slate-200 hover:text-white hover:bg-slate-800 font-semibold text-sm transition flex items-center justify-center gap-2 cursor-pointer"
        >
          <Home class="w-4 h-4" />
          Fazer Outro Agendamento
        </button>
      </div>
    </div>
  </PublicLayout>
</template>
