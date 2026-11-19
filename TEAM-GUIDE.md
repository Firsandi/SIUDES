# SIUDES: Panduan Tim (Baca 5 Menit)

Panduan singkat cara kerja tim SIUDES (Firsandi, Ahmad Rafif, Ridho Rizky) selama pengembangan 19 November – 10 Desember 2026. Tujuannya satu: tiga orang bekerja paralel tanpa saling bentrok, dan hasil kerja agent AI tetap konsisten.

---

## 1. Aturan Emas

1. **Satu tiket = satu branch = satu percakapan agent.** Jangan menumpuk beberapa tiket dalam satu percakapan; konteks yang terlalu panjang membuat agent lupa aturan.
2. **Kerjakan hanya folder milikmu.** Kalau butuh perubahan di folder orang lain, minta lewat issue atau chat.
3. **Kontrak tidak boleh diubah sendiri.** Perubahan pada `docs/contract.md` dan Bagian 2 file rules harus disepakati bertiga lewat PR.
4. **Rencana dulu, eksekusi kemudian.** Agent wajib menampilkan rencana dan berhenti. Kamu baca dulu, baru setujui.
5. **Selesai berarti terbukti.** Lampirkan output verifikasi (hasil `make up`, `curl`, atau tes) di PR, bukan hanya kata "sudah jalan".
6. **Jangan pernah commit `.env` atau secret.** Hanya `.env.example` yang boleh masuk repo.

---

## 2. Pemilik Folder

| Folder | Pemilik | Isi |
|---|---|---|
| `/unit-service` | Ahmad Rafif | Laravel 13, `db_siudes_unit`, publisher RabbitMQ |
| `/finance-service` | Firsandi | FastAPI, `db_siudes_finance`, consumer, SSE |
| `/frontend` | Ridho Rizky | Vue 3, Vite, Tailwind |
| `/nginx`, `docker-compose.yml`, `Makefile` | Firsandi | Infrastruktur |
| `/tests` | Rafif & Ridho (Black-Box), Firsandi (Locust) | Pengujian |

Catatan: tiket #4 (endpoint usage + publisher) dikerjakan Firsandi di `/unit-service`. Bagian itu sudah disepakati sebagai pengecualian.

---

## 3. Alur Kerja Satu Tiket

1. **Ambil kode terbaru.** `git checkout main && git pull`
2. **Buat branch** dari `main`, dengan format `feat/m<fase>-<nomor>-<nama-singkat>`. Contoh: `feat/m1-02-seeder`, `feat/m3-01-ui`.
3. **Buka percakapan baru** di Antigravity, lalu tempel prompt tiket (lihat bagian 4).
4. **Review rencana agent.** Pastikan file yang akan diubah hanya yang ada di lingkup tiket. Kalau ada yang di luar lingkup, minta dibuang.
5. **Setujui, lalu biarkan agent mengerjakan.**
6. **Verifikasi sendiri.** Jalankan perintah verifikasi dan lihat hasilnya dengan matamu.
7. **Baca diff** (`git diff`) sebelum commit. Jangan commit apa pun yang tidak kamu pahami.
8. **Tambahkan 3-5 baris ke `docs/devlog.md`** (keputusan, masalah, solusi). Ini bahan laporan akhir.
9. **Buka Pull Request** dengan kata kunci `closes #<nomor-tiket>`, lalu minta satu orang me-review.
10. **Merge ke `main`** setelah disetujui. Anggota lain tarik `main` terbaru sebelum memulai tiket berikutnya.

---

## 4. Template Prompt untuk Agent

Tempel ini di awal percakapan baru, dan isi bagian dalam kurung:

```
Kerjakan Tiket #<nomor> [<kode>] dari GitHub Issue SIUDES.
Patuhi .agents/rules/siudes-architecture.md dan docs/contract.md.

Lingkup (hanya boleh menyentuh):
- <folder / file>

Tugas:
- <butir tugas dari issue>

Langkah:
1. Baca struktur repo saat ini, lalu tulis rencana (file yang dibuat/diubah). BERHENTI dan tunggu persetujuan saya.
2. Setelah saya setuju, implementasikan hanya lingkup di atas.
3. Verifikasi dengan: <perintah verifikasi>. Tampilkan outputnya.
4. Tambahkan catatan singkat ke docs/devlog.md.

Larangan: jangan menyentuh folder lain, jangan mengubah kontrak, jangan menambah dependency baru tanpa izin.
```

Tips model: tiket boilerplate (#1, #2, #7) cukup dengan **Gemini 4 Hydrogen**. Tiket yang lebih berat (#4, #5, #8) boleh pakai **Orchestrator** kalau akunmu punya akses (Orchestrator belum tersedia di paket gratis). Tiket konkurensi (#6, #10) lebih baik pakai model besar langsung dengan effort tinggi.

---

## 5. Cek Cepat: Apakah Agent Sudah Membaca Rules?

Di awal percakapan, ketik:

> Rangkum rules yang kamu patuhi di proyek ini.

Kalau ringkasannya tidak menyebut RabbitMQ `siudes.events`, `prefetch_count=1`, dan isolasi database, berarti rules belum terbaca. Periksa apakah file ada di `.agents/rules/` dan aktivasinya "selalu aktif".

---

## 6. Checklist Pull Request

Sebelum meminta review, pastikan semuanya tercentang:

- [ ] Hanya mengubah folder yang ada di lingkup tiket
- [ ] Kontrak (Bagian 2 rules dan `docs/contract.md`) tidak berubah
- [ ] Output verifikasi dilampirkan di deskripsi PR
- [ ] `docs/devlog.md` sudah diperbarui
- [ ] Deskripsi PR memuat `closes #<nomor-tiket>`
- [ ] Tidak ada `.env` atau secret yang ikut ter-commit

Reviewer cukup memeriksa enam butir di atas, tidak perlu membaca ulang seluruh kode.

---

## 7. Kalau Tersangkut

- **Stuck lebih dari 1-2 jam? Kabari Firsandi.** Lebih baik 15 menit dibantu daripada berhari-hari diam.
- Agent berputar-putar atau mulai mengacak berkas? **Hentikan, `git restore .`, buka percakapan baru**, dan perjelas prompt-nya.
- Agent menyarankan mengubah kontrak? Jangan setuju. Catat dan tanyakan ke tim.
- Docker bermasalah? Coba `make down && make up` dulu, lalu `make logs` untuk melihat penyebabnya.

---

## 8. Peran Role (Auth Sederhana)

Autentikasi memakai header statis `X-User-Role`, dan **dicek di backend**, bukan hanya di UI.

| Role | Boleh |
|---|---|
| `ADMIN_UNIT` | Input pemakaian unit, kelola master data |
| `KASIR` | Lihat daftar tagihan, lakukan pelunasan |
| `KEPALA_DESA` | Hanya melihat dashboard dan laporan |

Role yang salah harus dijawab dengan **403**; header kosong dengan **401**.

---

## 9. Jadwal Singkat

| Fase | Tanggal | Fokus |
|---|---|---|
| 1 | 19 - 23 Nov | Arsitektur & database |
| 2 | 24 - 30 Nov | Jalur asinkron & transaksi inti |
| 3 | 1 - 7 Des | Frontend & pengujian fungsional |
| 4 | 7 - 10 Des | Validasi sistem & laporan |

Target selesai: **10 Desember 2026**.
