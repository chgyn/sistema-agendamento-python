<script setup lang="ts">
import { Scissors } from 'lucide-vue-next';
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 flex flex-col antialiased">
    <!-- Header público sutil -->
    <header class="border-b border-slate-800/80 glass-panel sticky top-0 z-30">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-500 to-amber-400 flex items-center justify-center text-slate-950 shadow-md shadow-amber-500/20">
            <Scissors class="w-5 h-5 stroke-[2.5]" />
          </div>
          <span class="font-bold text-lg tracking-tight text-white">Agendamento Online</span>
        </div>
        <router-link
          to="/login"
          class="text-xs font-medium text-slate-400 hover:text-amber-400 transition"
        >
          Acesso Lojista &rarr;
        </router-link>
      </div>
    </header>

    <!-- Conteúdo principal -->
    <main class="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 py-8">
      <slot />
    </main>

    <!-- Footer sutil -->
    <footer class="border-t border-slate-800/60 py-6 text-center text-xs text-slate-500">
      <p>&copy; 2026 Plataforma de Agendamentos. Todos os direitos reservados.</p>
    </footer>
  </div>
</template>
