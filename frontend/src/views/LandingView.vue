<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useNavigation } from '../composables/useNavigation'

const { goToWorkspace } = useNavigation()

const rootRef = ref(null)
const email = ref('')
const emailSent = ref(false)

// 3 Real Wikimedia Commons landmarks of Kabupaten Jember
const jemberSlides = [
  {
    id: 'argopuro',
    label: 'Argopuro',
    caption: 'Pegunungan Argopuro · Hulu Air Bersih Jember',
    src: '/images/argopuro-jember.jpg',
    alt: 'Bentang Alam Taman Hidup, Pegunungan Argopuro Jember',
  },
  {
    id: 'tembakau',
    label: 'Tembakau',
    caption: 'Warisan Tembakau · Agraris Kabupaten Jember',
    src: '/images/tembakau-jember.jpg',
    alt: 'Warisan Pengolahan Tembakau Kabupaten Jember',
  },
  {
    id: 'papuma',
    label: 'Papuma',
    caption: 'Pantai Papuma · Pesisir Selatan Jember',
    src: '/images/papuma-jember.jpg',
    alt: 'Pantai Papuma, Kabupaten Jember',
  },
]
const activeSlideIdx = ref(0)
const activeSlide = computed(() => jemberSlides[activeSlideIdx.value])

// Ticker events aligned with docs/contract.md (PLG-001..PLG-005, m³, bulan, jam)
const tickerEvents = [
  'PLG-001 · AIR · 15,5 m³',
  'PLG-002 · SAMPAH · 1 bulan',
  'PLG-003 · ALSINTAN · 3 jam',
  'PLG-004 · AIR · 8,6 m³',
  'PLG-005 · SAMPAH · 1 bulan',
]
const tickerIdx = ref(0)
const tickerVisible = ref(true)
const currentTicker = computed(() => tickerEvents[tickerIdx.value])

// Marquee invoice cards aligned with docs/contract.md
const unitColors = {
  AIR: '#0369A1',
  SAMPAH: '#6B7280',
  ALSINTAN: '#A16207',
}

const invoiceSamples = [
  { unit: 'AIR', amount: 'Rp 38.750', label: 'PLG-001 · Air 15,5 m³', status: 'PAID' },
  { unit: 'SAMPAH', amount: 'Rp 15.000', label: 'PLG-002 · Sampah 1 bulan', status: 'UNPAID' },
  { unit: 'ALSINTAN', amount: 'Rp 150.000', label: 'PLG-003 · Alsintan 3 jam', status: 'UNPAID' },
  { unit: 'AIR', amount: 'Rp 21.500', label: 'PLG-004 · Air 8,6 m³', status: 'PAID' },
  { unit: 'SAMPAH', amount: 'Rp 15.000', label: 'PLG-005 · Sampah 1 bulan', status: 'PAID' },
]
const marqueeItems = [...invoiceSamples, ...invoiceSamples]

let tickerTimer = null
let tickerFadeTimer = null
let slideTimer = null
let revealObserver = null
let bgObserver = null

function handleEmailSubmit() {
  if (!email.value.trim()) return
  emailSent.value = true
}

function selectSlide(idx) {
  activeSlideIdx.value = idx
}

function initWordReveal(container) {
  container.querySelectorAll('[data-reveal]').forEach((el) => {
    const nodes = [...el.childNodes]
    el.textContent = ''
    let i = 0
    nodes.forEach((n) => {
      if (n.nodeType === 3) {
        n.textContent.split(/(\s+)/).forEach((t) => {
          if (!t) return
          if (!t.trim()) {
            el.append(t)
            return
          }
          const s = document.createElement('span')
          s.className = 'w'
          s.style.setProperty('--i', i++)
          s.textContent = t
          el.append(s)
        })
      } else {
        const c = n.cloneNode(true)
        c.classList.add('w')
        c.style.setProperty('--i', i)
        const dr = c.querySelector('.draw')
        if (dr) dr.style.setProperty('--hd', `${(i * 0.07 + 0.7).toFixed(2)}s`)
        i++
        el.append(c)
      }
    })
  })
}

onMounted(() => {
  const container = rootRef.value
  if (!container) return

  initWordReveal(container)

  // Hero Jember landscape rotation
  slideTimer = window.setInterval(() => {
    activeSlideIdx.value = (activeSlideIdx.value + 1) % jemberSlides.length
  }, 5000)

  // Ticker rotation
  tickerTimer = window.setInterval(() => {
    tickerVisible.value = false
    tickerFadeTimer = window.setTimeout(() => {
      tickerIdx.value = (tickerIdx.value + 1) % tickerEvents.length
      tickerVisible.value = true
    }, 350)
  }, 2200)

  // Scroll reveal observer
  revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add('in')
          revealObserver.unobserve(e.target)
        }
      })
    },
    { threshold: 0.18, rootMargin: '0px 0px -6% 0px' }
  )

  container
    .querySelectorAll('.card,[data-reveal],.draw,.rv,.wave')
    .forEach((el) => revealObserver.observe(el))

  // Hero appears immediately
  window.requestAnimationFrame(() => {
    container
      .querySelectorAll('.hero .card,.hero [data-reveal]')
      .forEach((el) => el.classList.add('in'))
  })

  // Dynamic background gradient per section
  bgObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting && e.target.dataset.bg) {
          const [a, b] = e.target.dataset.bg.split(',')
          document.body.style.setProperty('--g1', a)
          document.body.style.setProperty('--g2', b)
        }
      })
    },
    { threshold: 0.35 }
  )

  container.querySelectorAll('[data-bg]').forEach((s) => bgObserver.observe(s))
})

onUnmounted(() => {
  if (slideTimer) window.clearInterval(slideTimer)
  if (tickerTimer) window.clearInterval(tickerTimer)
  if (tickerFadeTimer) window.clearTimeout(tickerFadeTimer)
  if (revealObserver) revealObserver.disconnect()
  if (bgObserver) bgObserver.disconnect()
})
</script>

<template>
  <div ref="rootRef" class="frame">
    <!-- NAV -->
    <header class="nav">
      <a class="logo" href="#top"><i></i>SIUDES</a>
      <nav class="links">
        <a class="hide-m" href="#unit-usaha">Unit Usaha</a>
        <a class="hide-m" href="#alur">Alur</a>
        <button type="button" class="btn-black" @click="goToWorkspace()">
          Buka Dashboard
        </button>
      </nav>
    </header>

    <!-- 1 · HERO (OPSI 2 · FULL BANNER JEMBER + 3-COL BENTO) -->
    <main id="top" class="hero" data-bg="#beccdd,#9bb8a3">
      <section class="card hero-banner" style="--d: 0.05s">
        <img
          v-for="(slide, idx) in jemberSlides"
          :key="slide.id"
          class="hero-slide"
          :class="{ 'is-active': idx === activeSlideIdx }"
          :src="slide.src"
          :alt="slide.alt"
        />
        <div class="hero-scrim" aria-hidden="true"></div>

        <div class="hero-top">
          <span class="hero-badge">✦ BUMDes Kabupaten Jember</span>
          <div class="jember-chips" role="tablist" aria-label="Lanskap Kabupaten Jember">
            <button
              v-for="(slide, idx) in jemberSlides"
              :key="slide.id"
              type="button"
              class="jember-chip"
              :class="{ 'is-active': idx === activeSlideIdx }"
              @click="selectSlide(idx)"
            >
              {{ slide.label }}
            </button>
          </div>
        </div>

        <div class="hero-copy">
          <h1 data-reveal>
            Satu sistem untuk
            <span class="hl">
              semua
              <svg viewBox="0 0 120 50" preserveAspectRatio="none">
                <path
                  class="draw"
                  pathLength="1"
                  d="M10 28C8 10 40 4 68 5c32 1 50 9 46 23-4 14-36 19-62 18C26 45 6 38 12 22 16 12 30 8 44 6"
                />
              </svg>
            </span>
            unit usaha desa
          </h1>
          <p class="hero-sub">
            {{ activeSlide.caption }} — kelola air bersih dusun, sampah desa, dan
            sewa alsintan secara terintegrasi.
          </p>
          <div class="hero-actions">
            <a class="btn-white" href="#keunggulan">
              Lihat keunggulan
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.2"
              >
                <path d="M7 17 17 7M8 7h9v9" />
              </svg>
            </a>
            <button
              type="button"
              class="btn-black"
              @click="goToWorkspace()"
            >
              Buka Dashboard
            </button>
          </div>
        </div>
      </section>

      <div class="hero-bento">
        <section class="card c-peri unit-mini" style="--d: 0.14s">
          <span class="tag bg-white/60">3 Unit Usaha</span>
          <div>
            <h3>Air bersih, sampah, dan alsintan dalam satu data</h3>
            <div class="unit-pills mt-3">
              <span>AIR · m³</span>
              <span>SAMPAH · bulan</span>
              <span>ALSINTAN · jam</span>
            </div>
          </div>
          <div class="live-ticker-pill" :style="{ opacity: tickerVisible ? 1 : 0 }">
            <i></i>
            <span>{{ currentTicker }}</span>
          </div>
        </section>

        <section class="card c-lime lime-card" style="--d: 0.2s">
          <span class="tag">Kasir real-time</span>
          <h3>Catat pemakaian, tagihan terbit otomatis</h3>
          <div class="rail">
            <div class="track">
              <div
                v-for="(item, idx) in marqueeItems"
                :key="`${item.label}-${idx}`"
                class="inv"
              >
                <div class="thumb" :style="{ background: unitColors[item.unit] }">
                  <span class="badge">{{ item.status }}</span>
                  <svg
                    v-if="item.unit === 'AIR'"
                    width="26"
                    height="26"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="#fff"
                    stroke-width="1.8"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M12 3s6 6.4 6 11a6 6 0 0 1-12 0c0-4.6 6-11 6-11z" />
                  </svg>
                  <svg
                    v-else-if="item.unit === 'SAMPAH'"
                    width="26"
                    height="26"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="#fff"
                    stroke-width="1.8"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path
                      d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v6M14 11v6"
                    />
                  </svg>
                  <svg
                    v-else
                    width="26"
                    height="26"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="#fff"
                    stroke-width="1.8"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <circle cx="7" cy="17" r="3.5" />
                    <circle cx="18" cy="18" r="2" />
                    <path d="M10.5 17H16M7 13.5V8h6l2 5h4v3" />
                  </svg>
                </div>
                <div class="row">
                  <b>{{ item.amount }}</b>
                  <span class="ok">
                    <svg
                      width="12"
                      height="12"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="#fff"
                      stroke-width="2.6"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    >
                      <path d="m5 12 4.5 4.5L19 7" />
                    </svg>
                  </span>
                </div>
                <small>{{ item.label }}</small>
              </div>
            </div>
          </div>
          <a class="circle-btn" href="#alur" aria-label="Lihat alur">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.2"
            >
              <path d="M7 17 17 7M8 7h9v9" />
            </svg>
          </a>
        </section>

        <section class="card c-forest green-card" style="--d: 0.26s">
          <span class="tag bg-lime text-ink self-start">Arsitektur</span>
          <p>
            Tiap pencatatan dikirim lewat RabbitMQ, dihitung otomatis, dan tidak
            pernah tertagih dua kali.
          </p>
          <a class="circle-btn" href="#keunggulan" aria-label="Pelajari">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#000"
              stroke-width="2.2"
            >
              <path d="M7 17 17 7M8 7h9v9" />
            </svg>
          </a>
        </section>
      </div>
    </main>

    <!-- 2 · KEUNGGULAN -->
    <section class="sec" id="keunggulan" data-bg="#dee7da,#c9d6ee">
      <span class="tag">2 / Keunggulan</span>
      <h2 class="h2" data-reveal>
        Tiga
        <span class="hl">
          unit
          <svg viewBox="0 0 120 50" preserveAspectRatio="none">
            <path
              class="draw"
              pathLength="1"
              d="M8 26C6 10 36 4 62 5c32 1 52 9 50 22-3 14-34 19-60 18C26 44 4 37 10 22 14 12 28 8 42 6"
            />
          </svg>
        </span>
        usaha, satu laporan keuangan yang rapi dan real-time
      </h2>

      <div class="bento">
        <article class="card c-white b-a" style="--d: 0s">
          <div class="avatars">
            <span class="av" style="background: #cfe3ff">AU</span>
            <span class="av" style="background: #ffe2c2">KS</span>
            <span class="av" style="background: #e5d4ff">KD</span>
            <span class="av" style="background: #000; color: #fff">+</span>
            <small>Satu data<br />untuk tiga peran</small>
          </div>
          <p>
            Petugas unit, kasir, dan kepala desa bekerja di data yang sama tanpa
            saling menunggu.
          </p>
        </article>

        <article class="card b-b" style="--d: 0.08s">
          <span class="argopuro-cap">Pantai Papuma · Jember</span>
        </article>

        <article class="card b-c" style="--d: 0.14s">
          <div class="mini-report" aria-hidden="true">
            <div class="mini-report-hd">
              <span>Konsolidasi Unit</span>
              <em>Rp 4,2 jt</em>
            </div>
            <div class="mini-report-bars">
              <div>
                <span style="--h: 82%; background: var(--air)"></span>
                <small>AIR</small>
              </div>
              <div>
                <span style="--h: 54%; background: var(--sampah)"></span>
                <small>SAMPAH</small>
              </div>
              <div>
                <span style="--h: 68%; background: var(--alsintan)"></span>
                <small>ALSINTAN</small>
              </div>
            </div>
          </div>
          <span>
            Perlu laporan konsolidasi tiap unit? Datanya sudah terkumpul dan
            terhitung, tinggal dibaca Kepala Desa.
          </span>
        </article>

        <article class="card c-lime b-d" style="--d: 0.2s">
          <svg class="line-ico" viewBox="0 0 48 48">
            <circle cx="24" cy="20" r="9" />
            <path
              d="M19 32h10M20 37h8M24 4v4M8 20H4M44 20h-4M11 7l3 3M37 7l-3 3"
            />
          </svg>
          Tagihan otomatis
        </article>

        <article class="card c-white b-e" style="--d: 0.26s">
          <div class="chips">
            <span class="chip">Anti tagihan ganda</span>
            <span class="chip">Kasir aman &amp; cepat</span>
            <span class="chip">Laporan real-time</span>
            <span class="chip">Tercatat otomatis</span>
            <span class="chip">Siap diaudit desa</span>
          </div>
          <span>Bebas catat ulang dan salah hitung</span>
        </article>
      </div>
    </section>

    <!-- 3 · ARSITEKTUR -->
    <section class="sec" id="unit" data-bg="#a9cdd0,#cfe6ee">
      <span class="tag">3 / Arsitektur</span>
      <h2 class="h2" data-reveal>Hitung dan konsolidasikan tagihan tanpa antre</h2>
      <div class="duo">
        <article class="card c-forest" style="--d: 0s">
          <p>
            Layanan unit hanya mencatat dan mengirim event ke RabbitMQ. Layanan
            keuangan menghitung di belakang layar, jadi form tetap terasa cepat.
          </p>
          <a class="btn-white" href="#alur">
            Lihat alur event
            <svg
              width="13"
              height="13"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.2"
            >
              <path d="M7 17 17 7M8 7h9v9" />
            </svg>
          </a>
        </article>
        <article class="card arch-diagram" style="--d: 0.12s">
          <span class="tag bg-white/80 self-start">Alur Terdistribusi</span>
          <div class="arch-nodes">
            <div class="arch-node">
              <small>1 · Unit Service</small>
              <b>Catat Pemakaian</b>
              <span>Air, sampah, dan alsintan</span>
            </div>
            <div class="arch-node is-broker">
              <small>2 · RabbitMQ</small>
              <b>Antrean Event</b>
              <span>Kirim cepat tanpa blokir</span>
            </div>
            <div class="arch-node is-finance">
              <small>3 · Finance</small>
              <b>Tagihan &amp; Kasir</b>
              <span>Hitung &amp; kunci lunas</span>
            </div>
          </div>
          <div class="arch-status">
            <i>
              <svg
                width="13"
                height="13"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#fff"
                stroke-width="2.4"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="m5 12 4.5 4.5L19 7" />
              </svg>
            </i>
            <span>Layanan unit &amp; keuangan terhubung otomatis tanpa antre</span>
          </div>
        </article>
      </div>
    </section>

    <!-- 3b · ALUR -->
    <section
      class="sec"
      id="alur"
      data-bg="#e3ecdc,#f1f5e4"
      style="padding-top: 70px"
    >
      <h2 class="h2 flow-title" data-reveal>
        Alur SIUDES dari catatan sampai lunas
      </h2>
      <svg
        class="bracket rv"
        viewBox="0 0 100 10"
        preserveAspectRatio="none"
        aria-hidden="true"
      >
        <path
          pathLength="1"
          d="M12.5 10V4H87.5V10M37.5 10V4M62.5 10V4M50 4V0"
        />
      </svg>
      <div class="steps">
        <article class="card step" style="--d: 0s">
          <div class="top">
            <span class="ic">
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#222"
                stroke-width="1.8"
                stroke-linecap="round"
              >
                <circle cx="12" cy="8" r="4" />
                <path d="M4 21c1-5 15-5 16 0" />
              </svg>
            </span>
            1 / langkah
          </div>
          <p>
            Petugas BUMDes mencatat pemakaian air bersih dusun, pengelolaan
            sampah desa, atau sewa alsintan pertanian lewat satu form.
          </p>
        </article>

        <article class="card step" style="--d: 0.08s">
          <div class="top">
            <span class="ic">
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#222"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M12 3 4 7.5v9L12 21l8-4.5v-9z" />
                <path d="m4 7.5 8 4.5 8-4.5M12 12v9" />
              </svg>
            </span>
            2 / langkah
          </div>
          <p>
            Catatan pemakaian langsung dikirim ke antrean sistem tanpa membuat
            petugas menunggu proses hitung.
          </p>
        </article>

        <article class="card step" style="--d: 0.16s">
          <div class="top">
            <span class="ic">
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#222"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <rect x="5" y="3" width="14" height="18" rx="2" />
                <path d="M9 8h6M9 12h6M9 16h3" />
              </svg>
            </span>
            3 / langkah
          </div>
          <p>
            Sistem keuangan menghitung total tarif × pemakaian secara otomatis
            dan menerbitkan tagihan tanpa duplikasi.
          </p>
        </article>

        <article class="card step last" style="--d: 0.24s">
          <div class="top">
            <span class="ic">
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#222"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path
                  d="m12 3 2.6 5.6 6 .7-4.5 4.1 1.2 6L12 16.5 6.7 19.4l1.2-6L3.4 9.3l6-.7z"
                />
              </svg>
            </span>
            4 / langkah
          </div>
          <p>
            Kasir menerima pelunasan dengan aman, dan laporan Kepala Desa
            langsung terbarui saat itu juga.
          </p>
        </article>
      </div>
    </section>

    <!-- 4 · PERAN -->
    <section class="sec" id="peran" data-bg="#d3dfce,#c4d3dc">
      <span class="tag">4 / Peran</span>
      <h2 class="h2" data-reveal>Satu aplikasi, tiga peran yang jelas</h2>
      <div class="roles">
        <div class="role-stack">
          <article class="card c-white role" style="--d: 0s">
            <div>
              <h3>Untuk petugas unit (ADMIN_UNIT)</h3>
              <svg class="wave" viewBox="0 0 92 10">
                <path
                  class="draw"
                  pathLength="1"
                  d="M2 5q5.75-7 11.5 0t11.5 0 11.5 0 11.5 0 11.5 0 11.5 0 11.5 0"
                />
              </svg>
            </div>
            <div class="row">
              <p>Catat pemakaian dan pantau riwayat pencatatan terakhir.</p>
              <button
                type="button"
                class="circle-btn dark"
                aria-label="Masuk sebagai ADMIN_UNIT"
                @click="goToWorkspace('ADMIN_UNIT')"
              >
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.2"
                >
                  <path d="M7 17 17 7M8 7h9v9" />
                </svg>
              </button>
            </div>
          </article>

          <article class="card c-lime role" style="--d: 0.1s">
            <div>
              <h3>Untuk kasir &amp; kepala desa</h3>
              <svg class="wave" viewBox="0 0 92 10">
                <path
                  class="draw"
                  pathLength="1"
                  d="M2 5q5.75-7 11.5 0t11.5 0 11.5 0 11.5 0 11.5 0 11.5 0 11.5 0"
                />
              </svg>
            </div>
            <div class="row">
              <p>
                Lunasi tagihan tanpa tabrakan, lalu lihat konsolidasi secara
                langsung.
              </p>
              <button
                type="button"
                class="circle-btn"
                aria-label="Masuk sebagai KASIR"
                @click="goToWorkspace('KASIR')"
              >
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.2"
                >
                  <path d="M7 17 17 7M8 7h9v9" />
                </svg>
              </button>
            </div>
          </article>
        </div>

        <article class="card c-peri device-card" style="--d: 0.15s">
          <svg class="sprig line-ico" viewBox="0 0 80 50" aria-hidden="true">
            <path d="M4 44C22 38 44 26 74 6" />
            <path
              d="M26 32c-2-9 3-16 12-19 1 9-3 16-12 19zM44 22c0-9 6-14 15-15-1 9-6 14-15 15z"
            />
          </svg>
          <div class="device" aria-hidden="true">
            <div class="hd">SIUDES <em>KEPALA_DESA</em></div>
            <div class="mini-stats">
              <div style="background: var(--lime)">
                <span>Total terbayar</span><b>Rp 4,2 jt</b>
              </div>
              <div style="background: var(--forest); color: #fff">
                <span>Piutang</span><b>Rp 1,1 jt</b>
              </div>
            </div>
            <div class="mini-chart">
              <span style="--h: 78%; background: var(--air)"></span>
              <span style="--h: 46%; background: var(--sampah)"></span>
              <span style="--h: 62%; background: var(--alsintan)"></span>
              <span style="--h: 90%; background: var(--air)"></span>
              <span style="--h: 38%; background: var(--sampah)"></span>
            </div>
            <div class="mini-list">
              <div>
                <span>PLG-001 · Air</span>
                <i style="background: #dcfce7; color: #15803d">PAID</i>
              </div>
              <div>
                <span>PLG-002 · Sampah</span>
                <i style="background: #fef3c7; color: #b45309">UNPAID</i>
              </div>
              <div>
                <span>PLG-003 · Alsintan</span>
                <i style="background: #fef3c7; color: #b45309">UNPAID</i>
              </div>
            </div>
          </div>
          <div class="store">
            <button type="button" @click="goToWorkspace('ADMIN_UNIT')">
              Role: ADMIN_UNIT
            </button>
            <button type="button" @click="goToWorkspace('KASIR')">
              Role: KASIR
            </button>
            <button type="button" @click="goToWorkspace('KEPALA_DESA')">
              Role: KEPALA_DESA
            </button>
          </div>
        </article>
      </div>
    </section>

    <!-- 5 · UNIT USAHA -->
    <section class="sec" id="unit-usaha" data-bg="#e8efe6,#dfe6ee">
      <span class="tag">5 / Unit usaha</span>
      <h2 class="h2" data-reveal>Unit usaha agraris BUMDes dalam satu sistem</h2>
      <div class="tiles rv">
        <div class="tile has-photo t1" style="--d: 0s">
          Air Bersih Dusun<small>AIR · satuan: m³</small>
        </div>
        <div class="tile has-photo t2" style="--d: 0.05s">
          Sampah Desa<small>SAMPAH · satuan: bulan</small>
        </div>
        <div class="tile has-photo t3" style="--d: 0.1s">
          Sewa Alsintan Pertanian<small>ALSINTAN · satuan: jam</small>
        </div>
        <div class="tile t4" style="--d: 0.15s">
          3<small>unit BUMDes</small>
        </div>
        <div class="tile t5" style="--d: 0.2s">
          Master data<small>pelanggan dan tarif</small>
        </div>
        <div class="tile t6" style="--d: 0.25s">
          pemakaian × tarif = total<small
            >tagihan terhitung otomatis</small
          >
        </div>
        <div class="tile t7" style="--d: 0.3s">
          Real-time<small>pantau kapan saja</small>
        </div>
      </div>
    </section>

    <!-- 6 · KONTAK -->
    <footer class="foot" id="kontak" data-bg="#e6ede6,#dde5ec">
      <div class="l">
        <span class="tag" style="align-self: flex-start">6 / Kontak</span>
        <a class="logo" href="#top"
          ><i style="transform: rotate(-45deg)"></i>SIUDES</a
        >
        <div class="meta">
          <span>© 2026 SIUDES</span>
          <span>BUMDes Kabupaten Jember · Universitas Jember</span>
          <span>Proyek Sistem Terdistribusi</span>
        </div>
      </div>
      <div class="r">
        <h3>Tinggalkan e-mail untuk info implementasi SIUDES di BUMDes Jember.</h3>
        <form @submit.prevent="handleEmailSubmit">
          <input
            v-model="email"
            type="email"
            placeholder="Alamat e-mail"
            aria-label="Alamat e-mail"
            required
          />
          <button class="btn-black" type="submit">
            {{ emailSent ? 'Terkirim ✓' : 'Kirim' }}
          </button>
        </form>
      </div>
    </footer>
  </div>
</template>
