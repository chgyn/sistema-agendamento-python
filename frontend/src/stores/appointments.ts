import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '@/services/api';

export interface AppointmentItem {
  id: string;
  establishment_id: string;
  customer_id: string;
  customer_name: string;
  customer_phone: string;
  professional_id: string;
  professional_name: string;
  service_id: string;
  service_name: string;
  start_datetime: string;
  end_datetime: string;
  status: 'SCHEDULED' | 'CONFIRMED' | 'CANCELLED' | 'COMPLETED' | 'NO_SHOW';
  cancellation_reason?: string;
  notes?: string;
  created_at: string;
}

export const useAppointmentsStore = defineStore('appointments', () => {
  const appointments = ref<AppointmentItem[]>([]);
  const isLoading = ref(false);
  const errorMessage = ref<string | null>(null);

  async function fetchAppointments(
    startDate: string,
    endDate: string,
    professionalId?: string,
    status?: string
  ) {
    isLoading.value = true;
    errorMessage.value = null;
    try {
      const params: Record<string, string> = {
        start_date: startDate,
        end_date: endDate,
      };
      if (professionalId) params.professional_id = professionalId;
      if (status) params.status = status;

      const res = await api.get('/appointments', { params });
      appointments.value = res.data;
    } catch (err: any) {
      errorMessage.value = err.response?.data?.message || 'Erro ao carregar agendamentos.';
    } finally {
      isLoading.value = false;
    }
  }

  async function updateStatus(appointmentId: string, newStatus: string): Promise<boolean> {
    try {
      const res = await api.patch(`/appointments/${appointmentId}/status`, {
        status: newStatus,
      });
      const idx = appointments.value.findIndex((a) => a.id === appointmentId);
      if (idx !== -1) {
        appointments.value[idx] = res.data;
      }
      return true;
    } catch (err: any) {
      errorMessage.value = err.response?.data?.message || 'Erro ao atualizar status.';
      return false;
    }
  }

  async function cancelAppointment(appointmentId: string, reason: string): Promise<boolean> {
    try {
      const res = await api.post(`/appointments/${appointmentId}/cancel`, { reason });
      const idx = appointments.value.findIndex((a) => a.id === appointmentId);
      if (idx !== -1) {
        appointments.value[idx] = res.data;
      }
      return true;
    } catch (err: any) {
      errorMessage.value = err.response?.data?.message || 'Erro ao cancelar agendamento.';
      return false;
    }
  }

  return {
    appointments,
    isLoading,
    errorMessage,
    fetchAppointments,
    updateStatus,
    cancelAppointment,
  };
});
