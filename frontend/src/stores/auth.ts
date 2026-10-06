import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/services/api';

export interface User {
  id: string;
  establishment_id: string;
  name: string;
  email: string;
  role: 'ADMIN' | 'OPERATOR';
  is_active: boolean;
}

export interface Establishment {
  id: string;
  name: string;
  slug: string;
  email: string;
  phone: string;
  address?: string;
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'));
  const user = ref<User | null>(
    localStorage.getItem('user_data') ? JSON.parse(localStorage.getItem('user_data')!) : null
  );
  const establishment = ref<Establishment | null>(null);
  const isLoading = ref(false);
  const errorMessage = ref<string | null>(null);

  const isAuthenticated = computed(() => !!token.value);
  const isAdmin = computed(() => user.value?.role === 'ADMIN');

  async function login(email: string, password: string): Promise<boolean> {
    isLoading.value = true;
    errorMessage.value = null;
    try {
      const response = await api.post('/auth/login', { email, password });
      token.value = response.data.access_token;
      localStorage.setItem('access_token', token.value!);

      await fetchProfile();
      await fetchEstablishment();
      return true;
    } catch (err: any) {
      errorMessage.value = err.response?.data?.message || 'Falha ao autenticar. Verifique e-mail e senha.';
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchProfile() {
    try {
      const response = await api.get('/auth/me');
      user.value = response.data;
      localStorage.setItem('user_data', JSON.stringify(user.value));
    } catch {
      logout();
    }
  }

  async function fetchEstablishment() {
    try {
      const response = await api.get('/establishment/me');
      establishment.value = response.data;
    } catch (err) {
      console.error('Erro ao buscar dados do estabelecimento:', err);
    }
  }

  function logout() {
    token.value = null;
    user.value = null;
    establishment.value = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
  }

  return {
    token,
    user,
    establishment,
    isLoading,
    errorMessage,
    isAuthenticated,
    isAdmin,
    login,
    fetchProfile,
    fetchEstablishment,
    logout,
  };
});
