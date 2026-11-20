<script setup>
import { computed, onMounted } from 'vue'
import RoleSwitcher from '../components/RoleSwitcher.vue'
import { useNavigation } from '../composables/useNavigation'
import { useRole } from '../composables/useRole'

const { goToLanding } = useNavigation()
const { activeRole, activeRoleMeta, roles, setRole } = useRole()

const roleModules = computed(() => {
  if (activeRole.value === 'ADMIN_UNIT') {
    return [
      {
        title: 'Catat Pemakaian Unit',
        tag: 'POST /api/unit/usage',
        tone: 'c-peri',
        detail:
          'Input pemakaian AIR (m³), SAMPAH (bulan), dan ALSINTAN (jam) untuk pelanggan PLG-001 s.d. PLG-005.',
      },
      {
        title: 'Master Tarif & Pelanggan',
        tag: 'GET /api/unit/master',
        tone: 'c-white',
        detail:
          'Daftar tarif aktif unit usaha desa dan data pelanggan terdaftar pada db_siudes_unit.',
      },
    ]
  }
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

    <!-- HEADER WORKSPACE -->
    <section class="mt-2 grid grid-cols-1 gap-3 md:grid-cols-12">
      <article class="card c-peri in p-7 md:col-span-8 flex flex-col justify-between gap-6 min-h-[240px]">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <span class="tag bg-white/70">Peran Aktif · {{ activeRoleMeta.code }}</span>
          <span class="rounded-full bg-black/10 px-3 py-1 text-xs font-medium">
            Header: X-User-Role: {{ activeRole }}
          </span>
        </div>
        <div>
          <h1 class="m-0 text-3xl font-medium tracking-tight md:text-4xl">
            Workspace {{ activeRoleMeta.label }}
          </h1>
          <p class="mt-2 max-w-2xl text-sm leading-relaxed text-ink/80 md:text-base">
            {{ activeRoleMeta.description }}
          </p>
        </div>
      </article>

      <article class="card c-lime in p-6 md:col-span-4 flex flex-col justify-between gap-4 min-h-[240px]">
        <span class="tag bg-white/50">Ganti Peran Cepat</span>
        <div class="flex flex-col gap-2">
          <button
            v-for="r in roles"
            :key="r.code"
            type="button"
            class="flex items-center justify-between rounded-2xl px-3.5 py-2.5 text-left text-xs font-medium transition-all"
            :class="
              activeRole === r.code
                ? 'bg-ink text-white'
                : 'bg-white/75 text-ink hover:bg-white'
            "
            @click="setRole(r.code)"
          >
            <span>{{ r.label }}</span>
            <span class="opacity-75">{{ r.code }}</span>
          </button>
        </div>
      </article>
    </section>

    <!-- MODUL PLACEHOLDER SESUAI PERAN -->
    <section class="mt-3 grid grid-cols-1 gap-3 md:grid-cols-2">
      <article
        v-for="mod in roleModules"
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
    <footer class="mt-4 flex flex-wrap items-center justify-between gap-3 px-3.5 py-4 text-xs text-muted">
      <span>SIUDES · Design System Bento Grid (Albert Sans)</span>
      <span>Peran tersimpan di localStorage (<code>siudes_active_role</code>)</span>
    </footer>
  </div>
</template>
