# Runia Kode Unik Bayar 🪙
**Automatic Unique Payment Code for Odoo Sales & eCommerce**

---

## 📝 Ringkasan / Summary

**[ID]** Modul ini menambahkan kode unik pembulatan ke atas (1-500) pada setiap Sales Order dan Invoice untuk mempermudah identifikasi pembayaran manual. Solusi ini ditujukan bagi bisnis yang menggunakan metode pembayaran transfer bank manual atau QRIS statis yang memerlukan verifikasi cepat berdasarkan nominal presisi.

**[EN]** This module adds a unique rounding-up code (1-500) to every Sales Order and Invoice to facilitate manual payment identification. This solution is designed for businesses using manual bank transfers or static QRIS payment methods that require fast verification based on precise amounts.

---

## 📜 Latar Belakang / Background

**[ID]** Dalam ekosistem bisnis di Indonesia, pembayaran melalui transfer bank manual masih sangat populer. Namun, hal ini seringkali menimbulkan masalah rekonsiliasi bagi tim finance ketika terdapat banyak transaksi dengan nominal yang sama (misal: Rp 100.000). Tanpa pembeda, admin sulit menentukan transfer mana milik pelanggan siapa tanpa meminta bukti transfer manual yang memakan waktu. Modul ini memperpanjang logika identifikasi dengan menyisipkan nominal kecil di akhir total belanja. Dengan adanya pembeda ini, admin cukup melihat mutasi rekening; jika muncul angka Rp 100.153, maka sistem sudah pasti tahu itu adalah milik Order #00153 tanpa keraguan.

**[EN]** In many business ecosystems, manual bank transfers remain a primary payment method. However, this often leads to reconciliation issues for finance teams when multiple transactions occur with identical amounts (e.g., $100.00). Without a unique identifier, it is difficult for administrators to determine which transfer belongs to which customer without requesting manual proof of payment, which is time-consuming. This module extends the identification logic by inserting a small nominal amount at the end of the total. With this differentiator, the admin can simply check the bank statement; if an amount like $100.53 appears, the system (and admin) knows with certainty it belongs to Order #0053 without any doubt.

---

## ✨ Fitur Utama / Key Features

- **Automated Generation**: Kode unik otomatis dihasilkan saat Sales Order dikonfirmasi atau saat checkout di eCommerce.
- **eCommerce Integration**: Mendukung alur kerja `website_sale`, kode unik akan muncul di keranjang belanja dan halaman pembayaran.
- **Dedicated Line Item**: Kode unik ditambahkan sebagai baris produk khusus agar tidak merusak perhitungan pajak produk utama.
- **Tax-Free Nominal**: Nominal kode unik secara default diset bebas pajak (Non-Taxable).
- **Flexible Sequence**: Sistem nomor urut (1 - Limit) yang akan berulang kembali ke angka 1 setelah mencapai batas tertentu.
- **Clear UI**: Menampilkan subtotal sebelum dan sesudah kode unik pada tampilan Sales Order dan Invoice.

---

## 🏗️ Arsitektur Singkat / Brief Architecture

Modul ini melakukan *inheritance* pada model inti Odoo:
1. `sale.order` & `sale.order.line`: Untuk menyisipkan baris kode unik.
2. `account.move`: Untuk memastikan kode unik terbawa hingga ke Invoice.
3. `res.company` & `res.config.settings`: Untuk menyimpan konfigurasi batas nominal unik.
4. `WebsiteSale` Controller: Untuk memicu penambahan kode saat user berbelanja online.

---

## 🔄 Alur Kerja / Workflow

1. **User Checkout**: Pelanggan memilih barang dan menuju halaman pembayaran (atau admin membuat SO).
2. **Code Injection**: Sistem memanggil fungsi `_add_unique_code_line()` yang mengambil nomor urut berikutnya dari database.
3. **Total Update**: Total tagihan berubah, misalnya dari **Rp 1.500.000** menjadi **Rp 1.500.123**.
4. **Payment**: Pelanggan membayar nominal presisi tersebut ke rekening perusahaan.
5. **Verification**: Admin/Finance melihat mutasi masuk dengan angka ekor `123` dan langsung memvalidasi invoice terkait.

---

## ⚙️ Instalasi & Setup / Installation

### Prasyarat / Prerequisites
- Odoo Version: **17.0** (Community or Enterprise).
- Dependency: `sale`, `account`, `website_sale`.

### Langkah Instalasi / Steps
1. Salin folder `runia_kode_unik_bayar` ke direktori `addons` Anda.
2. Restart server Odoo.
3. Aktifkan **Developer Mode**.
4. Pergi ke Apps -> Click **Update Apps List**.
5. Cari "Runia Kode Unik Bayar" dan klik **Install**.

---

## 🛠️ Konfigurasi / Configuration

Buka menu **Sales** atau **Accounting** -> **Configuration** -> **Settings**.
Cari bagian **Kode Unik Pembayaran**:
- **Unique Code Limit**: Tentukan batas maksimal kode (Contoh: 500). Kode akan berulang ke 1 jika transaksi ke-501 tercipta.
- **Unique Code Product**: Modul secara otomatis membuat produk "Kode Unik Pembayaran". Pastikan akun akun pendapatan (Income Account) sudah terset dengan benar pada produk ini.

---

## ⚠️ Batasan & Catatan Teknis / Limitations

- **Recycling Logic**: Jika limit diset terlalu kecil (misal hanya 10) dan transaksi sangat padat, ada kemungkinan dua transaksi aktif memiliki kode unik yang sama dalam waktu bersamaan.
- **Manual Reconciliation**: Modul ini membantu identifikasi, namun proses rekonsiliasi (pencocokan mutasi ke invoice) tetap dilakukan secara manual kecuali Anda memiliki modul integrasi bank pihak ketiga.
- **Tax Handling**: Kode unik dianggap sebagai penyesuaian nominal dan tidak dikenakan pajak dalam implementasi standar ini.
- **Product Dependency**: Jangan menghapus produk "Kode Unik Pembayaran" secara manual karena akan menyebabkan error pada pencarian referensi data.

---
Developed with ❤️ by **Runia**
