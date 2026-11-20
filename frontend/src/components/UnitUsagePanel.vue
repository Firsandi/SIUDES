<script setup>
import { computed, onMounted, ref } from 'vue'
import { getUnitMaster, postUnitUsage } from '../services/api'

const MOCK_MASTER = {
  tariffs: [
    { unit_type: 'AIR', unit_name: 'Air Bersih', tariff_rate: 2500, unit_measure: 'm3' },
    { unit_type: 'SAMPAH', unit_name: 'Pengelolaan Sampah', tariff_rate: 15000, unit_measure: 'bulan' },
    { unit_type: 'ALSINTAN', unit_name: 'Sewa Alsintan', tariff_rate: 50000, unit_measure: 'jam' },
  ],
  customers: [
    { customer_code: 'PLG-001', name: 'Budi Santoso', address: 'Dusun Krajan RT 01' },
    { customer_code: 'PLG-002', name: 'Siti Aminah', address: 'Dusun Krajan RT 02' },
    { customer_code: 'PLG-003', name: 'Ahmad Fauzi', address: 'Dusun Timur RT 01' },
    { customer_code: 'PLG-004', name: 'Dewi Lestari', address: 'Dusun Barat RT 03' },
    { customer_code: 'PLG-005', name: 'Rudi Hartono', address: 'Dusun Selatan RT 02' },
  ],
}

const UNIT_STYLES = {
  AIR: { bg: 'bg-air', text: 'text-white', label: 'Air Bersih' },
  SAMPAH: { bg: 'bg-sampah', text: 'text-white', label: 'Sampah' },
  ALSINTAN: { bg: 'bg-alsintan', text: 'text-white', label: 'Alsintan' },
}

const loadingMaster = ref(true)
const usingMock = ref(false)
const tariffs = ref([])
const customers = ref([])

const selectedCustomer = ref('')
const selectedUnit = ref('AIR')
const usageAmount = ref('')

const submitting = ref(false)
const feedback = ref(null) // { type: 'success' | 'error', title: string, detail: string }
const sessionHistory = ref([])

const activeTariff = computed(() =>
  tariffs.value.find((t) => t.unit_type === selectedUnit.value) || null
)

const displayMeasure = computed(() => {
  const m = activeTariff.value?.unit_measure || ''
  return m === 'm3' ? 'm³' : m
})

const estimatedTotal = computed(() => {
  const amount = Number(usageAmount.value)
  const rate = Number(activeTariff.value?.tariff_rate || 0)
  if (!Number.isFinite(amount) || amount <= 0 || !Number.isFinite(rate)) return 0
  return Math.round(amount * 100) * Math.round(rate * 100) / 10000
})

function formatRupiah(value) {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(Number(value || 0))
}

async function loadMasterData() {
  loadingMaster.value = true
  try {
    const data = await getUnitMaster()
    tariffs.value = data?.tariffs?.length ? data.tariffs : MOCK_MASTER.tariffs
    customers.value = data?.customers?.length ? data.customers : MOCK_MASTER.customers
    usingMock.value = false
  } catch {
    tariffs.value = MOCK_MASTER.tariffs
    customers.value = MOCK_MASTER.customers
    usingMock.value = true
  } finally {
    if (!selectedCustomer.value && customers.value.length) {
      selectedCustomer.value = customers.value[0].customer_code
    }
    if (!tariffs.value.some((t) => t.unit_type === selectedUnit.value) && tariffs.value.length) {
      selectedUnit.value = tariffs.value[0].unit_type
    }
    loadingMaster.value = false
  }
}

async function handleSubmit() {
  feedback.value = null
  const numericAmount = Number(usageAmount.value)

  if (!selectedCustomer.value) {
    feedback.value = {
      type: 'error',
      title: 'Pelanggan belum dipilih',
      detail: 'Pilih kode pelanggan terlebih dahulu.',
    }
    return
  }

  if (!Number.isFinite(numericAmount) || numericAmount <= 0) {
    feedback.value = {
      type: 'error',
      title: 'Jumlah pemakaian tidak valid',
      detail: 'Masukkan angka pemakaian lebih besar dari 0.',
    }
    return
  }

  submitting.value = true
  try {
    const result = await postUnitUsage({
      customer_code: selectedCustomer.value,
      unit_type: selectedUnit.value,
      usage_amount: numericAmount,
    })

    const totalAmount = result?.total_amount ?? estimatedTotal.value
    const eventId = result?.event_id || '-'

    feedback.value = {
      type: 'success',
      title: 'Pemakaian berhasil dicatat & dikirim ke RabbitMQ',
      detail: `event_id: ${eventId} · Total: ${formatRupiah(totalAmount)}`,
    }

    sessionHistory.value.unshift({
      event_id: eventId,
      customer_code: selectedCustomer.value,
      unit_type: selectedUnit.value,
      usage_amount: numericAmount,
      unit_measure: displayMeasure.value,
      total_amount: totalAmount,
      recorded_at: new Date().toLocaleTimeString('id-ID', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      }),
    })

    usageAmount.value = ''
  } catch (err) {
    feedback.value = {
      type: 'error',
      title: `Gagal mencatat pemakaian (${err.code || 'ERROR'})`,
      detail: err.message || 'Terjadi kesalahan saat mengirim ke /api/unit/usage.',
    }
  } finally {
    submitting.value = false
  }
}

onMounted(loadMasterData)
</script>

<template>
  <section class="mt-3 grid grid-cols-1 gap-3 lg:grid-cols-12">
    <!-- FORM INPUT PEMAKAIAN UNIT -->
    <article class="card c-white in p-6 md:p-7 lg:col-span-7 flex flex-col gap-5">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <div class="flex items-center gap-2">
          <span class="tag">Pencatatan Unit</span>
          <span
            class="rounded-full px-2.5 py-1 text-[11px] font-medium"
            :class="
              usingMock
                ? 'bg-amber-100 text-amber-800'
                : 'bg-emerald-100 text-emerald-800'
            "
          >
            {{ usingMock ? 'Master: Mock Fallback' : 'Master: API Terhubung' }}
          </span>
        </div>
        <button
          type="button"
          class="rounded-full bg-frame px-3 py-1 text-xs font-medium text-ink transition hover:bg-peri/40"
          :disabled="loadingMaster"
          @click="loadMasterData"
        >
          {{ loadingMaster ? 'Memuat...' : 'Muat Ulang Master' }}
        </button>
      </div>

      <form class="flex flex-col gap-4" @submit.prevent="handleSubmit">
        <!-- PILIH PELANGGAN -->
        <label class="flex flex-col gap-1.5">
          <span class="text-xs font-medium text-muted">Pelanggan</span>
          <select
            v-model="selectedCustomer"
            class="w-full rounded-2xl border border-black/10 bg-frame px-4 py-3 text-sm font-medium text-ink outline-none transition focus:border-peri-deep focus:bg-white"
            :disabled="loadingMaster"
          >
            <option
              v-for="cust in customers"
              :key="cust.customer_code"
              :value="cust.customer_code"
            >
              {{ cust.customer_code }} — {{ cust.name }}
              {{ cust.address ? `(${cust.address})` : '' }}
            </option>
          </select>
        </label>

        <!-- PILIH JENIS UNIT -->
        <div class="flex flex-col gap-1.5">
          <span class="text-xs font-medium text-muted">Jenis Unit Usaha</span>
          <div class="grid grid-cols-1 gap-2 sm:grid-cols-3">
            <button
              v-for="tariff in tariffs"
              :key="tariff.unit_type"
              type="button"
              class="flex flex-col items-start justify-between gap-2 rounded-2xl border p-3.5 text-left transition-all"
              :class="
                selectedUnit === tariff.unit_type
                  ? 'border-ink bg-lime/60 shadow-sm'
                  : 'border-black/10 bg-frame hover:bg-white'
              "
              @click="selectedUnit = tariff.unit_type"
            >
              <span
                class="rounded-full px-2.5 py-0.5 text-[10px] font-semibold"
                :class="[
                  UNIT_STYLES[tariff.unit_type]?.bg || 'bg-ink',
                  UNIT_STYLES[tariff.unit_type]?.text || 'text-white',
                ]"
              >
                {{ tariff.unit_type }}
              </span>
              <div>
                <div class="text-sm font-medium text-ink">
                  {{ tariff.unit_name }}
                </div>
                <div class="text-xs text-muted">
                  {{ formatRupiah(tariff.tariff_rate) }} /
                  {{ tariff.unit_measure === 'm3' ? 'm³' : tariff.unit_measure }}
                </div>
              </div>
            </button>
          </div>
        </div>

        <!-- JUMLAH PEMAKAIAN -->
        <label class="flex flex-col gap-1.5">
          <span class="text-xs font-medium text-muted">
            Jumlah Pemakaian ({{ displayMeasure || 'satuan' }})
          </span>
          <div class="relative flex items-center">
            <input
              v-model="usageAmount"
              type="number"
              step="0.01"
              min="0.01"
              placeholder="Contoh: 15.5"
              class="w-full rounded-2xl border border-black/10 bg-frame px-4 py-3 pr-20 text-sm font-medium text-ink outline-none transition focus:border-peri-deep focus:bg-white"
              required
            />
            <span
              class="pointer-events-none absolute right-4 rounded-full bg-white px-2.5 py-1 text-xs font-medium text-muted"
            >
              {{ displayMeasure }}
            </span>
          </div>
        </label>

        <!-- NOTIFIKASI FEEDBACK -->
        <div
          v-if="feedback"
          class="rounded-2xl p-4 text-xs leading-relaxed"
          :class="
            feedback.type === 'success'
              ? 'bg-lime/70 text-ink'
              : 'bg-red-50 text-red-800 border border-red-200'
          "
        >
          <div class="font-semibold">{{ feedback.title }}</div>
          <div class="mt-0.5 break-all opacity-90">{{ feedback.detail }}</div>
        </div>

        <!-- TOMBOL SUBMIT -->
        <div class="flex flex-wrap items-center justify-between gap-3 pt-1">
          <span class="text-xs text-muted">
            Dikirim ke <code>POST /api/unit/usage</code>
          </span>
          <button
            type="submit"
            class="btn-black inline-flex items-center gap-2 disabled:opacity-50"
            :disabled="submitting || loadingMaster"
          >
            <span>{{ submitting ? 'Mengirim Event...' : 'Catat & Kirim Event' }}</span>
          </button>
        </div>
      </form>
    </article>

    <!-- KOLOM KANAN: ESTIMASI REAL-TIME + RIWAYAT SESI -->
    <div class="flex flex-col gap-3 lg:col-span-5">
      <!-- KARTU ESTIMASI REAL-TIME -->
      <article class="card c-forest in p-6 flex flex-col justify-between gap-4">
        <div class="flex items-center justify-between gap-2">
          <span class="tag bg-lime text-ink">Estimasi Tagihan</span>
          <span class="text-xs text-white/75">
            pemakaian × tarif
          </span>
        </div>
        <div>
          <div class="text-3xl font-medium tracking-tight text-white">
            {{ formatRupiah(estimatedTotal) }}
          </div>
          <p class="mt-1.5 text-xs text-white/80">
            {{ usageAmount || 0 }} {{ displayMeasure }} ×
            {{ formatRupiah(activeTariff?.tariff_rate || 0) }}
          </p>
        </div>
      </article>

      <!-- RIWAYAT PENCATATAN SESI INI -->
      <article class="card c-lime in p-6 flex flex-1 flex-col gap-3">
        <div class="flex items-center justify-between">
          <span class="tag bg-white/50">Riwayat Sesi Ini</span>
          <span class="text-xs font-medium text-ink/70">
            {{ sessionHistory.length }} catatan
          </span>
        </div>

        <div
          v-if="sessionHistory.length === 0"
          class="flex flex-1 items-center justify-center rounded-2xl bg-white/60 p-5 text-center text-xs text-ink/70"
        >
          Belum ada pencatatan pada sesi ini. Isi form di samping untuk mengirim
          event <code>usage.recorded</code>.
        </div>

        <ul v-else class="m-0 flex list-none flex-col gap-2 p-0">
          <li
            v-for="item in sessionHistory"
            :key="item.event_id"
            class="flex items-center justify-between gap-3 rounded-2xl bg-white px-3.5 py-2.5 text-xs"
          >
            <div class="min-w-0">
              <div class="font-semibold text-ink">
                {{ item.customer_code }} · {{ item.unit_type }}
              </div>
              <div class="truncate text-[11px] text-muted">
                {{ item.usage_amount }} {{ item.unit_measure }} ·
                {{ item.recorded_at }}
              </div>
            </div>
            <div class="text-right font-semibold text-forest">
              {{ formatRupiah(item.total_amount) }}
            </div>
          </li>
        </ul>
      </article>
    </div>
  </section>
</template>
