<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { Scissors, AlertCircle, LogIn } from 'lucide-vue-next';

const email = ref('');
const password = ref('');
const authStore = useAuthStore();
const router = useRouter();

async function handleLogin() {
  const success = await authStore.login(email.value, password.value);
  if (success) {
    router.push('/admin/dashboard');
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-950 flex items-center justify-center p-4">
    <div class="w-full max-w-md space-y-6">
      <!-- Logo e Título -->
      <div class="text-center space-y-2">
        <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-amber-500 to-amber-400 flex items-center justify-center text-slate-950 shadow-xl shadow-amber-500/20 mx-auto">
          <Scissors class="w-8 h-8 stroke-[2.5]" />
        </div>
        <h1 class="text-2xl font-extrabold text-white tracking-tight">Acesso ao Painel</h1>
        <p class="text-xs text-slate-400">Entre com seu e-mail e senha corporativa</p>
      </div>

      <!-- Card de Login -->
      <div class="glass-panel p-8 rounded-3xl relative overflow-hidden">
        <div class="absolute -right-10 -bottom-10 w-32 h-32 bg-amber-500/10 rounded-full blur-2xl pointer-events-none"></div>

        <form @submit.prevent="handleLogin" class="space-y-4 relative z-10">
          <div v-if="authStore.errorMessage" class="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle class="w-4 h-4 shrink-0" />
            <span>{{ authStore.errorMessage }}</span>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">E-mail Profissional</label>
            <input
              v-model="email"
              type="email"
              required
              placeholder="seu.email@estabelecimento.com"
              class="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500 transition"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">Senha</label>
            <input
              v-model="password"
              type="password"
              required
              placeholder="••••••••"
              class="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500 transition"
            />
          </div>

          <button
            type="submit"
            :disabled="authStore.isLoading"
            class="w-full mt-2 py-3 px-4 rounded-xl bg-gradient-to-r from-amber-500 to-amber-400 text-slate-950 font-bold text-sm shadow-lg shadow-amber-500/20 hover:opacity-95 transition flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
          >
            <LogIn class="w-4 h-4" />
            <span>{{ authStore.isLoading ? 'Autenticando...' : 'Entrar no Sistema' }}</span>
          </button>
        </form>
      </div>

      <div class="text-center text-xs text-slate-500">
        Plataforma Multi-tenant de Gestão e Agendamentos &bull; v1.0
      </div>
    </div>
  </div>
</template>
