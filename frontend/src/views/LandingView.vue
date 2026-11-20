<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useNavigation } from '../composables/useNavigation'

const { goToWorkspace } = useNavigation()

const rootRef = ref(null)
const contoursRef = ref(null)
const email = ref('')
const emailSent = ref(false)

// Equalizer bars (16 bars with randomized heights and durations)
const eqBars = Array.from({ length: 16 }, () => ({
  h: `${(35 + Math.random() * 55).toFixed(1)}%`,
  t: `${(0.7 + Math.random() * 1.1).toFixed(2)}s`,
  delay: `${(-Math.random() * 1.5).toFixed(2)}s`,
}))

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
let revealObserver = null
let bgObserver = null

function handleEmailSubmit() {
  if (!email.value.trim()) return
  emailSent.value = true
}

function buildContours() {
  const svg = contoursRef.value
  if (!svg) return
  let out = ''
  for (let i = 0; i < 28; i++) {
    const base = i * 24 - 90
    let d = ''
    for (let x = -20; x <= 820; x += 16) {
      const y =
        base +
        x * 0.22 +
        40 * Math.sin(x / 120 + i * 0.2) +
        20 * Math.sin(x / 55 - i * 0.17)
      d += `${d ? 'L' : 'M'}${x} ${y.toFixed(1)}`
    }
    out += `<path d="${d}"/>`
  }
  svg.innerHTML = `<g>${out}</g>`
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
  buildContours()

  const container = rootRef.value
  if (!container) return

  initWordReveal(container)

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

    <!-- 1 · HERO -->
    <main id="top" class="hero" data-bg="#beccdd,#9bb8a3">
      <section class="card c-peri hero-left" style="--d: 0.05s">
        <svg
          id="contours"
          ref="contoursRef"
          viewBox="0 0 800 600"
          preserveAspectRatio="xMidYMid slice"
          aria-hidden="true"
        ></svg>
        <div class="pill" aria-hidden="true">
          <div class="bars">
            <span
              v-for="(bar, idx) in eqBars"
              :key="idx"
              :style="{
                '--h': bar.h,
                '--t': bar.t,
                animationDelay: bar.delay,
              }"
            ></span>
          </div>
          <div class="play">
            <svg width="22" height="22" viewBox="0 0 24 24">
              <path d="M8 5.5v13l11-6.5z" fill="#0a0a0a" />
            </svg>
          </div>
          <div class="ticker" :style="{ opacity: tickerVisible ? 1 : 0 }">
            {{ currentTicker }}
          </div>
        </div>

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
      </section>

      <div class="hero-right">
        <section class="card c-lime lime-card" style="--d: 0.18s">
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

        <section class="card c-forest green-card" style="--d: 0.3s">
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

        <article class="card b-b" style="--d: 0.08s" aria-hidden="true">
          <svg viewBox="0 0 200 220" preserveAspectRatio="xMidYMid slice">
            <path
              d="M-10 230C20 120 80 40 210 -10c10 90-30 190-120 230z"
              fill="rgba(255,255,255,.12)"
            />
            <path
              d="M20 230C60 140 110 70 200 10"
              stroke="rgba(255,255,255,.7)"
              stroke-width="2.2"
              fill="none"
              stroke-linecap="round"
            />
            <g
              stroke="rgba(255,255,255,.45)"
              stroke-width="1.2"
              fill="none"
              stroke-linecap="round"
            >
              <path
                d="M44 190c14-4 26-12 34-24M62 160c14-2 26-10 34-22M82 132c12-2 22-8 30-18M104 108c10-2 20-8 26-16M30 200c8 2 20 0 30-6M52 176c4 10 12 18 22 22M72 146c4 8 10 16 20 20M94 122c4 8 8 14 16 18"
              />
            </g>
          </svg>
        </article>

        <article class="card c-peri b-c" style="--d: 0.14s">
          <svg class="line-ico" viewBox="0 0 120 80">
            <path d="M6 70C34 60 62 42 108 12" />
            <path
              d="M40 52c-2-12 4-22 16-26 2 12-4 22-16 26zM62 38c0-12 8-20 20-22-1 12-8 20-20 22zM28 60c-8-8-10-18-6-28 10 4 14 14 6 28zM86 22c2-10 10-16 20-16-1 10-8 16-20 16z"
            />
          </svg>
          Perlu laporan konsolidasi tiap unit? Datanya sudah terkumpul dan
          terhitung, tinggal dibaca.
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
            <span class="chip">event_id unik</span>
            <span class="chip">SELECT … FOR UPDATE</span>
            <span class="chip">manual ack</span>
            <span class="chip">prefetch 1</span>
            <span class="chip">409 jika lunas ganda</span>
          </div>
          <span>Tahan duplikat dan tabrakan kasir</span>
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
            Layanan unit hanya mencatat dan mengirim event. Layanan keuangan
            menghitung di belakang layar, jadi form tetap terasa cepat.
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
        <article class="card sky" style="--d: 0.12s" aria-hidden="true">
          <span
            class="cloud"
            style="width: 230px; height: 110px; left: -40px; bottom: 30px"
          ></span>
          <span
            class="cloud"
            style="
              width: 300px;
              height: 150px;
              right: -60px;
              bottom: -20px;
              animation-delay: -3s;
            "
          ></span>
          <span
            class="cloud"
            style="
              width: 160px;
              height: 70px;
              left: 30%;
              top: 14%;
              animation-delay: -5s;
            "
          ></span>
          <div class="float-label">
            <span>Event terkirim<br />dan terverifikasi</span>
            <i>
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#fff"
                stroke-width="2.2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="m5 12 4.5 4.5L19 7" />
              </svg>
            </i>
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
            Petugas unit mencatat pemakaian air, sampah, atau sewa alsintan
            lewat satu form.
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
            Event <code>usage.recorded</code> dikirim ke RabbitMQ tanpa menunggu
            hitungan selesai.
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
            Billing worker memeriksa <code>event_id</code>, menghitung total,
            lalu menerbitkan tagihan.
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
            Kasir melunasi dengan kunci basis data, dan dashboard kepala desa
            langsung ikut berubah.
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
      <h2 class="h2" data-reveal>Banyak unit, satu cara mengelolanya</h2>
      <div class="tiles rv">
        <div class="tile t1" style="--d: 0s">
          Air Bersih<small>satuan: m³</small>
        </div>
        <div class="tile t2" style="--d: 0.05s">
          Sampah<small>satuan: bulan</small>
        </div>
        <div class="tile t3" style="--d: 0.1s">
          Sewa Alsintan<small>satuan: jam</small>
        </div>
        <div class="tile t4" style="--d: 0.15s">
          3<small>unit usaha</small>
        </div>
        <div class="tile t5" style="--d: 0.2s">
          Master data<small>pelanggan dan tarif</small>
        </div>
        <div class="tile t6" style="--d: 0.25s">
          pemakaian × tarif = total<small
            >dihitung otomatis oleh billing worker</small
          >
        </div>
        <div class="tile t7" style="--d: 0.3s">
          UTC<small>waktu ISO-8601</small>
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
          <span>Proyek Sistem Terdistribusi</span>
          <span>Universitas Jember</span>
        </div>
      </div>
      <div class="r">
        <h3>Tinggalkan e-mail, kami kabari perkembangan SIUDES.</h3>
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
