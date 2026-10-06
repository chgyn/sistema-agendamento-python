import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '@/services/api';

export interface PublicEstablishment {
  id: string;
  name: string;
  slug: string;
  phone: string;
  email: string;
  address?: string;
  settings: Record<string, any>;
}

export interface PublicService {
  id: string;
  name: string;
  description?: string;
  duration_minutes: number;
  price: number;
}

export interface PublicProfessional {
  id: string;
  name: string;
  bio?: string;
}

export interface TimeSlot {
  start_time: string;
  end_time: string;
  is_available: boolean;
}

export interface BookingConfirmation {
  id: string;
  start_datetime: string;
  end_datetime: string;
  status: string;
  service_name: string;
  professional_name: string;
  message: string;
}

export const usePublicBookingStore = defineStore('publicBooking', () => {
  const establishment = ref<PublicEstablishment | null>(null);
  const services = ref<PublicService[]>([]);
  const professionals = ref<PublicProfessional[]>([]);
  const availableSlots = ref<TimeSlot[]>([]);

  // Estado da reserva em progresso
  const selectedService = ref<PublicService | null>(null);
  const selectedProfessional = ref<PublicProfessional | null>(null);
  const selectedDate = ref<string>(new Date().toISOString().split('T')[0]);
  const selectedSlot = ref<TimeSlot | null>(null);

  const customerName = ref('');
  const customerPhone = ref('');
  const customerEmail = ref('');
  const customerNotes = ref('');

  const lastBooking = ref<BookingConfirmation | null>(null);
  const isLoading = ref(false);
  const errorMessage = ref<string | null>(null);

  async function loadEstablishment(slug: string) {
    isLoading.value = true;
    errorMessage.value = null;
    try {
      const res = await api.get(`/public/${slug}`);
      establishment.value = res.data;
    } catch (err: any) {
      errorMessage.value = err.response?.data?.message || 'Estabelecimento não encontrado.';
    } finally {
      isLoading.value = false;
    }
  }

  async function loadServices(slug: string) {
    try {
      const res = await api.get(`/public/${slug}/services`);
      services.value = res.data;
    } catch (err) {
      console.error(err);
    }
  }

  async function loadProfessionals(slug: string, serviceId?: string) {
    try {
      const url = serviceId
        ? `/public/${slug}/professionals?service_id=${serviceId}`
        : `/public/${slug}/professionals`;
      const res = await api.get(url);
      professionals.value = res.data;
    } catch (err) {
      console.error(err);
    }
  }

  async function fetchAvailability(slug: string) {
    if (!selectedProfessional.value || !selectedService.value || !selectedDate.value) return;

    isLoading.value = true;
    try {
      const res = await api.get(`/public/${slug}/availability`, {
        params: {
          professional_id: selectedProfessional.value.id,
          service_id: selectedService.value.id,
          date: selectedDate.value,
        },
      });
      availableSlots.value = res.data.slots;
    } catch (err: any) {
      errorMessage.value = err.response?.data?.message || 'Erro ao consultar horários disponíveis.';
      availableSlots.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  async function submitBooking(slug: string): Promise<boolean> {
    if (!selectedService.value || !selectedProfessional.value || !selectedSlot.value) {
      errorMessage.value = 'Selecione serviço, profissional e horário antes de continuar.';
      return false;
    }

    isLoading.value = true;
    errorMessage.value = null;
    try {
      const startDateTime = `${selectedDate.value}T${selectedSlot.value.start_time}:00Z`;
      const payload = {
        service_id: selectedService.value.id,
        professional_id: selectedProfessional.value.id,
        start_datetime: startDateTime,
        customer_name: customerName.value,
        customer_phone: customerPhone.value,
        customer_email: customerEmail.value || null,
        notes: customerNotes.value || null,
      };

      const res = await api.post(`/public/${slug}/appointments`, payload);
      lastBooking.value = res.data;
      return true;
    } catch (err: any) {
      errorMessage.value = err.response?.data?.message || 'Falha ao concluir agendamento.';
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  function resetFlow() {
    selectedService.value = null;
    selectedProfessional.value = null;
    selectedSlot.value = null;
    customerName.value = '';
    customerPhone.value = '';
    customerEmail.value = '';
    customerNotes.value = '';
    errorMessage.value = null;
  }

  return {
    establishment,
    services,
    professionals,
    availableSlots,
    selectedService,
    selectedProfessional,
    selectedDate,
    selectedSlot,
    customerName,
    customerPhone,
    customerEmail,
    customerNotes,
    lastBooking,
    isLoading,
    errorMessage,
    loadEstablishment,
    loadServices,
    loadProfessionals,
    fetchAvailability,
    submitBooking,
    resetFlow,
  };
});
