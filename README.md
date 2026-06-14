# Network Programming - Final Project [G04]

## Anggota Kelompok
| Nama           | NRP        | Kelas     |
| ---            | ---        | ----------|
| Fathiya Nayla Husna Wibowo | 5025241204 | Pemrograman Jaringan C |
| Shafira Nauraishma Zahida  | 5025241235 | Pemrograman Jaringan C |
| Najma Lail Arazy           | 5025241243 | Pemrograman Jaringan C |

## Link Youtube (Unlisted)
Link ditaruh di bawah ini
```
```

## Penjelasan Program

NexusChat terinspirasi dari kata "Nexus" yang berarti titik pusat penghubung atau jaringan koneksi, dan "Chat" yang merepresentasikan komunikasi real-time. Secara keseluruhan, NexusChat menggambarkan sebuah platform yang menjadi pusat komunikasi bagi banyak pengguna yang terhubung secara bersamaan.

Aplikasi ini dibangun sebagai sistem Multi-Chat Rooms berbasis TCP Socket yang memungkinkan banyak client terhubung ke satu server secara bersamaan, berdiskusi dalam berbagai room, dan berkomunikasi secara privat antar pengguna.

1. fpclient.py

File fpclient.py berfungsi sebagai sisi client atau program yang dijalankan oleh pengguna. Tugas utamanya adalah menghubungkan pengguna ke server, menerima input perintah dari terminal, mengirim permintaan ke server, dan menampilkan hasil yang dikirim balik oleh server. Di dalamnya terdapat fitur autentikasi (login dan register), pembuatan serta bergabung ke room chat, pengiriman pesan ke room maupun pesan pribadi, pengiriman file, pengunduhan file, pemberian reaksi emoji pada pesan, hingga melihat riwayat chat. File ini juga menangani proses enkripsi dan dekripsi pesan private melalui modul kriptografi yang diimpor dari shared.crypto. Selain itu, client menjalankan thread terpisah untuk terus mendengarkan pesan dari server sehingga pengguna dapat menerima pesan secara real-time tanpa mengganggu proses input perintah.

2. fpserver.py

File fpserver.py berfungsi sebagai titik masuk (entry point) dari sisi server. Meskipun ukurannya kecil, file ini sangat penting karena bertugas menginisialisasi seluruh sistem server. Saat dijalankan, file ini pertama-tama memanggil fungsi init_db() untuk memastikan database dan tabel yang diperlukan sudah tersedia. Setelah itu server mulai berjalan melalui fungsi start_server(), yang kemungkinan besar berada pada modul server.tcp_server. Dengan kata lain, file ini berperan sebagai penghubung antara komponen database dan komponen server jaringan, sehingga seluruh layanan chat dapat aktif dan menerima koneksi dari client.

3. nexuschat.db

File nexuschat.db merupakan database SQLite yang digunakan untuk menyimpan data aplikasi secara permanen. Database ini kemungkinan berisi informasi akun pengguna, data room chat, anggota room, pesan yang dikirim, riwayat private message, data file yang dibagikan, serta informasi reaksi terhadap pesan. Kehadiran database ini memungkinkan data tetap tersimpan meskipun server dimatikan dan dijalankan kembali. Dengan kata lain, file ini menjadi pusat penyimpanan seluruh aktivitas yang terjadi pada aplikasi chat.

## Screenshot Hasil
