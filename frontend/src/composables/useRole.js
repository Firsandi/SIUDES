import { computed, ref } from 'vue'

export const STORAGE_KEY = 'siudes_active_role'

export const ROLES = [
  {
    code: 'ADMIN_UNIT',
    label: 'Admin Unit',
    badge: 'AU',
    description:
      'Catat pemakaian air, sampah, dan sewa alsintan serta kelola master data pelanggan dan tarif.',
    endpoints: ['GET /api/unit/master', 'POST /api/unit/usage'],
  },
  {
    code: 'KASIR',
    label: 'Kasir',
    badge: 'KS',
    description:
      'Pantau tagihan UNPAID/PAID dan lunasi pembayaran dengan PostgreSQL SELECT ... FOR UPDATE.',
    endpoints: [
      'GET /api/finance/invoices',
      'POST /api/finance/invoices/{code}/pay',
      'GET /api/finance/summary',
    ],
  },
  {
    code: 'KEPALA_DESA',
    label: 'Kepala Desa',
    badge: 'KD',
    description:
      'Lihat ringkasan pendapatan, piutang, dan konsolidasi real-time via SSE stream.',
    endpoints: [
      'GET /api/finance/invoices',
      'GET /api/finance/summary',
      'GET /api/finance/stream',
    ],
  },
]

const VALID_ROLES = ROLES.map((r) => r.code)

function readStoredRole() {
  if (typeof window === 'undefined') return 'ADMIN_UNIT'
  const saved = window.localStorage.getItem(STORAGE_KEY)
  return VALID_ROLES.includes(saved) ? saved : 'ADMIN_UNIT'
}

const activeRole = ref(readStoredRole())

export function useRole() {
  const activeRoleMeta = computed(
    () => ROLES.find((r) => r.code === activeRole.value) || ROLES[0]
  )

  function setRole(roleCode) {
    if (!VALID_ROLES.includes(roleCode)) return
    activeRole.value = roleCode
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(STORAGE_KEY, roleCode)
    }
  }

  return {
    roles: ROLES,
    activeRole,
    activeRoleMeta,
    setRole,
  }
}
