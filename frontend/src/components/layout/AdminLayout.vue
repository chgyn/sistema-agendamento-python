<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import {
  LayoutDashboard,
  Calendar,
  Clock,
  Sparkles,
  Users,
  Contact,
  Settings,
  LogOut,
  Scissors,
  Menu,
  X,
} from 'lucide-vue-next';

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();

const isMobileMenuOpen = ref(false);

const navigation = [
  { name: 'Dashboard', to: '/admin/dashboard', icon: LayoutDashboard },
  { name: 'Agenda Visual', to: '/admin/calendar', icon: Calendar },
  { name: 'Agendamentos', to: '/admin/appointments', icon: Clock },
  { name: 'Serviços', to: '/admin/services', icon: Sparkles },
  { name: 'Profissionais', to: '/admin/professionals', icon: Users },
  { name: 'Clientes', to: '/admin/customers', icon: Contact },
  { name: 'Configurações', to: '/admin/settings', icon: Settings },
];

function handleLogout() {
  authStore.logout();
  router.push('/login');
}
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 flex">
    <!-- Sidebar Desktop -->
    <aside class="hidden lg:flex lg:flex-col w-64 border-r border-slate-800 glass-panel p-5">
      <!-- Marca do Estabelecimento -->
      <div class="flex items-center space-x-3 mb-8">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-amber-400 flex items-center justify-center text-slate-950 shadow-md shadow-amber-500/20">
          <Scissors class="w-5 h-5 stroke-[2.5]" />
        </div>
        <div class="overflow-hidden">
          <h2 class="font-bold text-sm tracking-tight text-white truncate">
            {{ authStore.establishment?.name || 'Meu Estabelecimento' }}
          </h2>
          <span class="text-xs text-amber-400 font-medium capitalize">
            {{ authStore.user?.role.toLowerCase() || 'Painel' }}
          </span>
        </div>
      </div>

      <!-- Links de Navegação -->
      <nav class="flex-1 space-y-1">
        <router-link
          v-for="item in navigation"
          :key="item.name"
          :to="item.to"
          :class="[
            'flex items-center space-x-3 px-3 py-2.5 rounded-xl text-sm font-medium transition duration-150',
            route.path === item.to
              ? 'bg-amber-500 text-slate-950 font-semibold shadow-md shadow-amber-500/10'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
          ]"
        >
          <component :is="item.icon" class="w-4 h-4" />
          <span>{{ item.name }}</span>
        </router-link>
      </nav>

      <!-- Rodapé do Usuário -->
      <div class="pt-4 border-t border-slate-800">
        <div class="flex items-center justify-between mb-3">
          <div class="overflow-hidden pr-2">
            <p class="text-xs font-semibold text-white truncate">{{ authStore.user?.name }}</p>
            <p class="text-[11px] text-slate-500 truncate">{{ authStore.user?.email }}</p>
          </div>
        </div>
        <button
          @click="handleLogout"
          class="w-full flex items-center justify-center space-x-2 py-2 px-3 rounded-xl text-xs font-medium text-rose-400 hover:bg-rose-500/10 border border-rose-500/20 transition"
        >
          <LogOut class="w-3.5 h-3.5" />
          <span>Encerrar Sessão</span>
        </button>
      </div>
    </aside>

    <!-- Estrutura Principal -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Barra Superior Mobile -->
      <header class="lg:hidden h-16 border-b border-slate-800 glass-panel px-4 flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <div class="w-8 h-8 rounded-lg bg-amber-500 flex items-center justify-center text-slate-950">
            <Scissors class="w-4 h-4" />
          </div>
          <span class="font-bold text-sm text-white truncate">
            {{ authStore.establishment?.name || 'Painel' }}
          </span>
        </div>
        <button
          @click="isMobileMenuOpen = !isMobileMenuOpen"
          class="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
        >
          <Menu v-if="!isMobileMenuOpen" class="w-5 h-5" />
          <X v-else class="w-5 h-5" />
        </button>
      </header>

      <!-- Drawer Mobile -->
      <div
        v-if="isMobileMenuOpen"
        class="lg:hidden border-b border-slate-800 bg-slate-900/95 backdrop-blur-xl px-4 py-3 space-y-1"
      >
        <router-link
          v-for="item in navigation"
          :key="item.name"
          :to="item.to"
          @click="isMobileMenuOpen = false"
          :class="[
            'flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium',
            route.path === item.to
              ? 'bg-amber-500 text-slate-950 font-semibold'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          ]"
        >
          <component :is="item.icon" class="w-4 h-4" />
          <span>{{ item.name }}</span>
        </router-link>
        <button
          @click="handleLogout"
          class="w-full mt-2 flex items-center justify-center space-x-2 py-2 rounded-lg text-sm font-medium text-rose-400 bg-rose-500/10"
        >
          <LogOut class="w-4 h-4" />
          <span>Sair</span>
        </button>
      </div>

      <!-- Conteúdo da Página -->
      <main class="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto">
        <slot />
      </main>
    </div>
  </div>
</template>
