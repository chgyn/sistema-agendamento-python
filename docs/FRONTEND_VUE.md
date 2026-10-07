# 🎨 Arquitetura do Frontend (Vue 3 + Vite + Tailwind CSS v4)

## 1. Stack e Tecnologias
- **Framework:** Vue.js 3 (`<script setup>`, Composition API)
- **Linguagem:** TypeScript estrito
- **Build Tool:** Vite 5
- **Estado Global:** Pinia
- **Roteamento:** Vue Router 4 (com guards de autenticação)
- **Estilização:** Tailwind CSS v4 com paleta Dark Glassmorphism
- **Ícones:** Lucide Icons (`lucide-vue-next`)
- **HTTP Client:** Axios centralizado com interceptors de JWT

---

## 2. Estrutura de Pastas
```text
frontend/src/
├── components/
│   ├── layout/
│   │   ├── AdminLayout.vue         # Sidebar retrátil, drawer mobile e perfil
│   │   └── PublicLayout.vue        # Cabeçalho e rodapé para clientes
│   └── ui/
│       ├── Pagination.vue          # Componente reutilizável de paginação e seletor
│       ├── SlotSelector.vue        # Seletor interativo de horários livres
│       └── StatusBadge.vue         # Badges coloridos de ciclo de vida
├── pages/
│   ├── public/
│   │   ├── PublicBookingView.vue   # Wizard passo a passo para o cliente
│   │   └── PublicSuccessView.vue   # Comprovante de agendamento confirmado
│   ├── auth/
│   │   └── LoginView.vue           # Login dos administradores e operadores
│   └── admin/
│       ├── DashboardView.vue       # Resumo operacional e atendimentos do dia
│       ├── ScheduleCalendarView.vue# Agenda visual em colunas por profissional
│       ├── AppointmentsListView.vue# Tabela de agendamentos com filtros e cancelamento
│       ├── ServicesView.vue        # Cadastro e gestão de serviços e preços
│       ├── ProfessionalsView.vue   # Cadastro e gestão de profissionais
│       ├── CustomersView.vue       # Consulta de clientes do estabelecimento
│       └── SettingsView.vue        # Dados cadastrais e link público
├── router/
│   └── index.ts                    # Definição de rotas e beforeEach de autenticação
├── services/
│   └── api.ts                      # Instância Axios com injeção automática de token
└── stores/
    ├── auth.ts                     # Estado do usuário logado e tenant
    ├── appointments.ts             # Estado da lista de atendimentos e filtros
    └── publicBooking.ts            # Estado reativo do wizard de agendamento
```

---

## 3. Fluxo de Autenticação e Interceptors
O cliente Axios (`src/services/api.ts`) é configurado para:
1. Injetar automaticamente o header `Authorization: Bearer <token>` em todas as requisições quando houver token no `localStorage`.
2. Interceptar respostas com status **401 Unauthorized**: limpa os dados da sessão e redireciona automaticamente para a tela de login (`/login`) caso o usuário esteja em uma rota administrativa.

---

## 4. Wizard Público em 4 Etapas (`PublicBookingView.vue`)
O fluxo do cliente para realizar agendamento sem necessidade de login funciona através da store reativa `usePublicBookingStore`:
1. **Etapa 1 (Serviço):** Cliente seleciona o serviço desejado (exibe preço e duração).
2. **Etapa 2 (Profissional):** Filtra e exibe profissionais habilitados para aquele serviço.
3. **Etapa 3 (Data & Slot):** Escolha da data com requisição dinâmica para `/public/{slug}/availability`, exibindo apenas os horários livres calculados pelo motor de disponibilidade.
4. **Etapa 4 (Dados & Confirmação):** Informa nome, WhatsApp e e-mail. Ao submeter, envia a requisição de reserva com lock e redireciona para a tela de sucesso (`/p/{slug}/sucesso`).
