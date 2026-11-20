<script setup>
import { computed, onMounted } from 'vue'
import RoleSwitcher from '../components/RoleSwitcher.vue'
import UnitUsagePanel from '../components/UnitUsagePanel.vue'
import { useNavigation } from '../composables/useNavigation'
import { useRole } from '../composables/useRole'

const { goToLanding } = useNavigation()
const { activeRole, activeRoleMeta, setRole } = useRole()

const workspaceTabs = [
  { role: 'ADMIN_UNIT', label: 'Input Unit', badge: 'ADMIN_UNIT' },
  { role: 'KASIR', label: 'Loket Kasir', badge: 'KASIR' },
  { role: 'KEPALA_DESA', label: 'Dashboard Kepala Desa', badge: 'KEPALA_DESA' },
]

const placeholderModules = computed(() => {
  if (activeRole.value === 'KASIR') {
    return [
      {
        title: 'Daftar Tagihan & Pelunasan',
        tag: 'POST /api/finance/invoices/{code}/pay',
        tone: 'c-lime',
        detail:
          'Filter tagihan UNPAID/PAID dan proses pelunasan aman dengan PostgreSQL SELECT ... FOR UPDATE.',
      },
      {
        title: 'Ringkasan Kas Harian',
        tag: 'GET /api/finance/summary',
        tone: 'c-white',
        detail:
          'Pantau total pendapatan terbayar dan sisa piutang dari db_siudes_finance.',
      },
    ]
  }
  return [
    {
      title: 'Konsolidasi Keuangan Desa',
      tag: 'GET /api/finance/summary',
      tone: 'c-forest',
      detail:
        'Ringkasan total revenue, total unpaid, dan rincian per unit usaha (AIR, SAMPAH, ALSINTAN) secara read-only.',
    },
    {
      title: 'Live Event Stream (SSE)',
      tag: 'GET /api/finance/stream',
      tone: 'c-white',
      detail:
        'Menerima event invoice_updated secara real-time saat tagihan baru terbit atau dilunasi kasir.',
    },
  ]
})

onMounted(() => {
  document.body.style.setProperty('--g1', '#dee7da')
  document.body.style.setProperty('--g2', '#c9d6ee')
})
</script>

<template>
  <div class="frame">
    <!-- NAV -->
    <header class="nav flex-wrap">
      <div class="flex items-center gap-3">
        <button
          type="button"
          class="logo bg-transparent p-0"
          aria-label="Kembali ke Landing Page SIUDES"
          @click="goToLanding"
        >
          <i></i>SIUDES
        </button>
        <span class="tag hidden sm:inline-block">Workspace</span>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <RoleSwitcher />
        <button
          type="button"
          class="btn-white border border-black/10 !py-2.5 !px-4 text-xs font-medium"
          @click="goToLanding"
        >
          ← Kembali ke Landing
        </button>
      </div>
    </header>

    <!-- TAB NAVIGASI WORKSPACE TERSINKRONISASI DENGAN ROLESWITCHER -->
    <nav
      class="mt-1 flex flex-wrap items-center justify-between gap-3 rounded-card bg-white/80 p-2"
      aria-label="Navigasi Mode Workspace"
    >
      <div class="flex flex-wrap items-center gap-1.5">
        <button
          v-for="tab in workspaceTabs"
          :key="tab.role"
          type="button"
          class="inline-flex items-center gap-2 rounded-2xl px-4 py-2 text-xs font-medium transition-all"
          :class="
            activeRole === tab.role
              ? 'bg-ink text-white shadow-sm'
              : 'bg-transparent text-muted hover:bg-frame hover:text-ink'
          "
          @click="setRole(tab.role)"
        >
          <span>{{ tab.label }}</span>
          <span
            class="rounded-full px-2 py-0.5 text-[10px]"
            :class="
              activeRole === tab.role
                ? 'bg-lime text-ink'
                : 'bg-frame text-muted'
            "
          >
            {{ tab.badge }}
          </span>
        </button>
      </div>
      <span class="px-2 text-[11px] text-muted">
        Header aktif: <code>X-User-Role: {{ activeRole }}</code>
      </span>
    </nav>

    <!-- HEADER STATUS PERAN -->
    <section class="mt-3">
      <article
        class="card c-peri in p-6 md:p-7 flex flex-col justify-between gap-3"
      >
        <div class="flex flex-wrap items-center justify-between gap-2">
          <span class="tag bg-white/75">Peran Aktif · {{ activeRoleMeta.code }}</span>
          <span class="text-xs font-medium text-ink/75">
            {{ activeRoleMeta.endpoints.join(' · ') }}
          </span>
        </div>
        <div>
          <h1 class="m-0 text-2xl font-medium tracking-tight md:text-3xl">
            Workspace {{ activeRoleMeta.label }}
          </h1>
          <p class="mt-1.5 max-w-2xl text-sm leading-relaxed text-ink/80">
            {{ activeRoleMeta.description }}
          </p>
        </div>
      </article>
    </section>

    <!-- KONTEN SESUAI PERAN AKTIF -->
    <UnitUsagePanel v-if="activeRole === 'ADMIN_UNIT'" />

    <section v-else class="mt-3 grid grid-cols-1 gap-3 md:grid-cols-2">
      <article
        v-for="mod in placeholderModules"
        :key="mod.title"
        class="card in p-7 flex flex-col justify-between gap-6 min-h-[220px]"
        :class="mod.tone"
      >
        <div class="flex items-center justify-between gap-2">
          <span class="tag bg-white/80 text-ink">{{ mod.tag }}</span>
          <span class="text-xs font-medium opacity-70">Placeholder Modul</span>
        </div>
        <div>
          <h2 class="m-0 text-xl font-medium tracking-tight">{{ mod.title }}</h2>
          <p class="mt-2 text-sm leading-relaxed opacity-85">{{ mod.detail }}</p>
        </div>
      </article>
    </section>

    <!-- FOOTER MINI -->
    <footer
      class="mt-4 flex flex-wrap items-center justify-between gap-3 px-3.5 py-4 text-xs text-muted"
    >
      <span>SIUDES · Design System Bento Grid (Albert Sans)</span>
      <span>Peran tersimpan di localStorage (<code>siudes_active_role</code>)</span>
    </footer>
  </div>
</template>
