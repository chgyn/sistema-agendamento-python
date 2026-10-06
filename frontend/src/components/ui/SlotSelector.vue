<script setup lang="ts">
export interface Slot {
  start_time: string;
  end_time: string;
  is_available: boolean;
}

defineProps<{
  slots: Slot[];
  selectedSlot: Slot | null;
}>();

const emit = defineEmits<{
  (e: 'select', slot: Slot): void;
}>();
</script>

<template>
  <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2.5">
    <button
      v-for="slot in slots"
      :key="slot.start_time"
      type="button"
      :disabled="!slot.is_available"
      @click="slot.is_available && emit('select', slot)"
      :class="[
        'py-2 px-3 text-sm font-medium rounded-xl border transition-all duration-150 text-center',
        !slot.is_available
          ? 'opacity-35 cursor-not-allowed bg-slate-900/40 text-slate-500 border-slate-800 line-through'
          : selectedSlot?.start_time === slot.start_time
          ? 'bg-amber-500 text-slate-950 font-semibold border-amber-400 shadow-lg shadow-amber-500/20 scale-102'
          : 'bg-slate-900/80 text-slate-200 border-slate-700/80 hover:border-amber-500/50 hover:bg-slate-800'
      ]"
    >
      {{ slot.start_time }}
    </button>
  </div>
</template>
