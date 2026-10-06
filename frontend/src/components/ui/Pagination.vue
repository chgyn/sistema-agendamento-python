<script setup lang="ts">
import { computed } from 'vue';
import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from 'lucide-vue-next';

interface Props {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
  isLoading?: boolean;
  pageSizeOptions?: number[];
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  pageSizeOptions: () => [10, 20, 50],
});

const emit = defineEmits<{
  (e: 'update:page', page: number): void;
  (e: 'update:pageSize', pageSize: number): void;
  (e: 'change', payload: { page: number; pageSize: number }): void;
}>();

const startItem = computed(() => {
  if (props.total === 0) return 0;
  return (props.page - 1) * props.pageSize + 1;
});

const endItem = computed(() => {
  if (props.total === 0) return 0;
  return Math.min(props.page * props.pageSize, props.total);
});

const visiblePages = computed<(number | string)[]>(() => {
  const total = props.totalPages;
  const current = props.page;
  const delta = 1;

  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  const range: number[] = [];
  for (
    let i = Math.max(2, current - delta);
    i <= Math.min(total - 1, current + delta);
    i++
  ) {
    range.push(i);
  }

  const pages: (number | string)[] = [1];

  if (range[0] > 2) {
    pages.push('...');
  }

  pages.push(...range);

  if (range[range.length - 1] < total - 1) {
    pages.push('...');
  }

  pages.push(total);
  return pages;
});

function goToPage(p: number) {
  if (p < 1 || p > props.totalPages || p === props.page || props.isLoading) return;
  emit('update:page', p);
  emit('change', { page: p, pageSize: props.pageSize });
}

function onPageSizeChange(event: Event) {
  const target = event.target as HTMLSelectElement;
  const newSize = Number(target.value);
  emit('update:pageSize', newSize);
  emit('update:page', 1);
  emit('change', { page: 1, pageSize: newSize });
}
</script>

<template>
  <div
    class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 px-4 py-3 bg-slate-900/60 border-t border-slate-800 text-xs text-slate-400"
  >
    <!-- Informações de Registros e Tamanho por Página -->
    <div class="flex items-center gap-4 flex-wrap">
      <div>
        <span v-if="total > 0">
          Mostrando <span class="font-bold text-white">{{ startItem }}</span> a
          <span class="font-bold text-white">{{ endItem }}</span> de
          <span class="font-bold text-amber-400">{{ total }}</span> registros
        </span>
        <span v-else class="text-slate-500">
          Nenhum registro encontrado
        </span>
      </div>

      <div class="flex items-center gap-2">
        <label for="page-size-select" class="text-[11px] text-slate-400">Exibir:</label>
        <select
          id="page-size-select"
          :value="pageSize"
          @change="onPageSizeChange"
          :disabled="isLoading"
          class="bg-slate-950 border border-slate-800 rounded-lg px-2 py-1 text-xs text-white focus:outline-none focus:border-amber-500 cursor-pointer disabled:opacity-50"
        >
          <option v-for="opt in pageSizeOptions" :key="opt" :value="opt">
            {{ opt }} por pág.
          </option>
        </select>
      </div>
    </div>

    <!-- Navegação de Páginas -->
    <nav aria-label="Navegação da paginação" class="flex items-center gap-1.5 self-center sm:self-auto">
      <!-- Primeira Página -->
      <button
        type="button"
        title="Primeira página"
        @click="goToPage(1)"
        :disabled="totalPages <= 0 || page <= 1 || isLoading"
        class="p-1.5 rounded-lg border border-slate-800 hover:bg-slate-800/80 text-slate-300 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
      >
        <ChevronsLeft class="w-3.5 h-3.5" />
      </button>

      <!-- Página Anterior -->
      <button
        type="button"
        title="Página anterior"
        @click="goToPage(page - 1)"
        :disabled="totalPages <= 0 || page <= 1 || isLoading"
        class="p-1.5 rounded-lg border border-slate-800 hover:bg-slate-800/80 text-slate-300 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
      >
        <ChevronLeft class="w-3.5 h-3.5" />
      </button>

      <!-- Números das Páginas -->
      <template v-for="(p, idx) in visiblePages" :key="idx">
        <span
          v-if="p === '...'"
          class="px-2 py-1 text-slate-500 select-none"
        >
          ...
        </span>
        <button
          v-else
          type="button"
          @click="goToPage(Number(p))"
          :disabled="isLoading"
          :class="[
            'min-w-7 h-7 px-2 rounded-lg text-xs font-semibold transition cursor-pointer',
            Number(p) === page
              ? 'bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-500/20'
              : 'border border-slate-800 hover:bg-slate-800/80 text-slate-300'
          ]"
        >
          {{ p }}
        </button>
      </template>

      <!-- Próxima Página -->
      <button
        type="button"
        title="Próxima página"
        @click="goToPage(page + 1)"
        :disabled="totalPages <= 0 || page >= totalPages || isLoading"
        class="p-1.5 rounded-lg border border-slate-800 hover:bg-slate-800/80 text-slate-300 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
      >
        <ChevronRight class="w-3.5 h-3.5" />
      </button>

      <!-- Última Página -->
      <button
        type="button"
        title="Última página"
        @click="goToPage(totalPages)"
        :disabled="totalPages <= 0 || page >= totalPages || isLoading"
        class="p-1.5 rounded-lg border border-slate-800 hover:bg-slate-800/80 text-slate-300 disabled:opacity-30 disabled:pointer-events-none transition cursor-pointer"
      >
        <ChevronsRight class="w-3.5 h-3.5" />
      </button>
    </nav>
  </div>
</template>
