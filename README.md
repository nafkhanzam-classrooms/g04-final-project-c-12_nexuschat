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

### Deskripsi NexusChat

NexusChat terinspirasi dari kata "Nexus" yang berarti titik pusat penghubung atau jaringan koneksi, dan "Chat" yang merepresentasikan komunikasi real-time. Secara keseluruhan, NexusChat menggambarkan sebuah platform yang menjadi pusat komunikasi bagi banyak pengguna yang terhubung secara bersamaan.

Aplikasi ini dibangun sebagai sistem Multi-Chat Rooms berbasis TCP Socket yang memungkinkan banyak client terhubung ke satu server secara bersamaan, berdiskusi dalam berbagai room, dan berkomunikasi secara privat antar pengguna.

### Garis besar Program

`fpclient.py`

File fpclient.py berfungsi sebagai sisi client atau program yang dijalankan oleh pengguna. Tugas utamanya adalah menghubungkan pengguna ke server, menerima input perintah dari terminal, mengirim permintaan ke server, dan menampilkan hasil yang dikirim balik oleh server. Di dalamnya terdapat fitur autentikasi (login dan register), pembuatan serta bergabung ke room chat, pengiriman pesan ke room maupun pesan pribadi, pengiriman file, pengunduhan file, pemberian reaksi emoji pada pesan, hingga melihat riwayat chat. File ini juga menangani proses enkripsi dan dekripsi pesan private melalui modul kriptografi yang diimpor dari shared.crypto. Selain itu, client menjalankan thread terpisah untuk terus mendengarkan pesan dari server sehingga pengguna dapat menerima pesan secara real-time tanpa mengganggu proses input perintah.

`fpserver.py`

File fpserver.py berfungsi sebagai titik masuk (entry point) dari sisi server. Meskipun ukurannya kecil, file ini sangat penting karena bertugas menginisialisasi seluruh sistem server. Saat dijalankan, file ini pertama-tama memanggil fungsi init_db() untuk memastikan database dan tabel yang diperlukan sudah tersedia. Setelah itu server mulai berjalan melalui fungsi start_server(), yang kemungkinan besar berada pada modul server.tcp_server. Dengan kata lain, file ini berperan sebagai penghubung antara komponen database dan komponen server jaringan, sehingga seluruh layanan chat dapat aktif dan menerima koneksi dari client.

`nexuschat.db`

File nexuschat.db merupakan database SQLite yang digunakan untuk menyimpan data aplikasi secara permanen. Database ini kemungkinan berisi informasi akun pengguna, data room chat, anggota room, pesan yang dikirim, riwayat private message, data file yang dibagikan, serta informasi reaksi terhadap pesan. Kehadiran database ini memungkinkan data tetap tersimpan meskipun server dimatikan dan dijalankan kembali. Dengan kata lain, file ini menjadi pusat penyimpanan seluruh aktivitas yang terjadi pada aplikasi chat.

### Fitur yang Tersedia

`Sistem Autentikasi Pengguna`

NexusChat menyediakan fitur registrasi dan login akun sehingga setiap pengguna memiliki identitas yang unik dalam sistem. Saat pertama kali masuk, pengguna dapat membuat akun baru atau login menggunakan akun yang sudah terdaftar. Dengan adanya autentikasi ini, seluruh aktivitas chat dapat dikaitkan dengan pengguna tertentu.

`Room Chat`

Pengguna dapat membuat room baru menggunakan perintah /create dan bergabung ke room yang sudah ada melalui /join. Setiap room berfungsi sebagai ruang diskusi terpisah yang dapat diikuti oleh banyak pengguna secara bersamaan. Sistem juga menyediakan fitur untuk keluar dari room (/leave) serta melihat daftar room yang tersedia (/list) beserta informasi anggota yang berada di dalamnya.

`Pesan Grup (Broadcast Message)`

Dalam sebuah room, pengguna dapat mengirim pesan yang akan diterima oleh seluruh anggota room menggunakan perintah /msg. Fitur ini memungkinkan komunikasi kelompok secara real-time, sehingga setiap anggota dapat melihat pesan yang dikirim oleh pengguna lain secara langsung.

`Pesan Pribadi (Direct Message)`

Selain chat grup, NexusChat juga mendukung private messaging melalui perintah /pm. Fitur ini memungkinkan dua pengguna berkomunikasi secara langsung tanpa melibatkan anggota room lainnya. Dari kode yang ada, pesan pribadi juga telah menggunakan mekanisme enkripsi sehingga isi pesan menjadi lebih aman saat dikirim.

`Daftar Pengguna Online`

Sistem menyediakan fitur untuk melihat pengguna yang sedang aktif atau online melalui perintah /user. Dengan fitur ini, pengguna dapat mengetahui siapa saja yang sedang terhubung ke server dan siap diajak berkomunikasi.

`Pengiriman File ke Room`

NexusChat mendukung berbagi file dalam room menggunakan perintah /sendfile. File yang dipilih akan dibaca, dikonversi menjadi format Base64, kemudian dikirim ke server untuk diteruskan kepada anggota room lainnya. Saat menerima file, pengguna dapat melihat informasi seperti nama file, ukuran file, dan tipe file.

`Pengiriman File Pribadi`

Selain berbagi file dalam room, pengguna juga dapat mengirim file secara langsung kepada pengguna lain menggunakan /sendfilepm. Fitur ini sangat berguna untuk berbagi dokumen atau media secara privat tanpa harus mengirimkannya ke seluruh anggota room.

`Download File`

Setiap file yang dikirim memperoleh identitas khusus berupa file ID. Pengguna dapat mengunduh file tersebut menggunakan perintah /download. File yang berhasil diunduh akan otomatis disimpan ke folder lokal bernama downloads.

`Reaksi Emoji pada Pesan`

NexusChat memiliki fitur message reaction yang memungkinkan pengguna memberikan reaksi emoji pada pesan tertentu menggunakan /react. Sistem akan menyimpan dan menampilkan jumlah reaksi untuk setiap emoji sehingga interaksi menjadi lebih menarik dan mirip dengan aplikasi chat modern seperti Discord atau WhatsApp.

`Riwayat Percakapan (Chat History)`

Aplikasi menyediakan fitur untuk melihat kembali pesan-pesan yang telah dikirim sebelumnya. Pengguna dapat melihat riwayat percakapan dalam room menggunakan /history <nama_room> maupun riwayat direct message melalui /history dm <username>. Fitur ini menunjukkan bahwa pesan disimpan ke database dan dapat diakses kembali kapan saja.

`Notifikasi Aktivitas Pengguna`

Saat ada pengguna yang masuk atau keluar dari room, sistem akan menampilkan notifikasi kepada anggota room lainnya. Dengan demikian, pengguna dapat mengetahui perubahan anggota yang terjadi secara real-time.

`Komunikasi Real-Time Berbasis TCP Socket`

Seluruh fitur chat berjalan menggunakan koneksi TCP Socket yang bersifat persisten. Client menjalankan thread khusus untuk menerima pesan secara terus-menerus dari server sehingga pesan baru, file, maupun notifikasi dapat muncul secara langsung tanpa perlu melakukan refresh.

## Screenshot Hasil
