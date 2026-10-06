<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  status: 'SCHEDULED' | 'CONFIRMED' | 'CANCELLED' | 'COMPLETED' | 'NO_SHOW' | string;
}>();

const config = computed(() => {
  switch (props.status) {
    case 'SCHEDULED':
      return { label: 'Agendado', class: 'bg-amber-500/10 text-amber-400 border-amber-500/20' };
    case 'CONFIRMED':
      return { label: 'Confirmado', class: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' };
    case 'COMPLETED':
      return { label: 'Concluído', class: 'bg-blue-500/10 text-blue-400 border-blue-500/20' };
    case 'CANCELLED':
      return { label: 'Cancelado', class: 'bg-rose-500/10 text-rose-400 border-rose-500/20' };
    case 'NO_SHOW':
      return { label: 'Não compareceu', class: 'bg-purple-500/10 text-purple-400 border-purple-500/20' };
    default:
      return { label: props.status, class: 'bg-slate-700/50 text-slate-300 border-slate-600' };
  }
});
</script>

<template>
  <span
    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border"
    :class="config.class"
  >
    {{ config.label }}
  </span>
</template>
