import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '@/pages/auth/LoginView.vue';
import PublicBookingView from '@/pages/public/PublicBookingView.vue';
import PublicSuccessView from '@/pages/public/PublicSuccessView.vue';
import DashboardView from '@/pages/admin/DashboardView.vue';
import ScheduleCalendarView from '@/pages/admin/ScheduleCalendarView.vue';
import AppointmentsListView from '@/pages/admin/AppointmentsListView.vue';
import ServicesView from '@/pages/admin/ServicesView.vue';
import ProfessionalsView from '@/pages/admin/ProfessionalsView.vue';
import CustomersView from '@/pages/admin/CustomersView.vue';
import SettingsView from '@/pages/admin/SettingsView.vue';

const routes = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { public: true },
  },
  {
    path: '/p/:slug',
    name: 'PublicBooking',
    component: PublicBookingView,
    meta: { public: true },
  },
  {
    path: '/p/:slug/sucesso',
    name: 'PublicSuccess',
    component: PublicSuccessView,
    meta: { public: true },
  },
  // Rotas Administrativas
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: DashboardView,
    meta: { requiresAuth: true },
  },
  {
    path: '/admin/calendar',
    name: 'AdminCalendar',
    component: ScheduleCalendarView,
    meta: { requiresAuth: true },
  },
  {
    path: '/admin/appointments',
    name: 'AdminAppointments',
    component: AppointmentsListView,
    meta: { requiresAuth: true },
  },
  {
    path: '/admin/services',
    name: 'AdminServices',
    component: ServicesView,
    meta: { requiresAuth: true },
  },
  {
    path: '/admin/professionals',
    name: 'AdminProfessionals',
    component: ProfessionalsView,
    meta: { requiresAuth: true },
  },
  {
    path: '/admin/customers',
    name: 'AdminCustomers',
    component: CustomersView,
    meta: { requiresAuth: true },
  },
  {
    path: '/admin/settings',
    name: 'AdminSettings',
    component: SettingsView,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token');
  if (to.meta.requiresAuth && !token) {
    next('/login');
  } else {
    next();
  }
});

export default router;
