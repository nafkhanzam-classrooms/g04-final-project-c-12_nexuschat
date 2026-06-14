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

### Alur Kerja

```
1. Client melakukan koneksi ke server menggunakan TCP Socket.
2. Pengguna melakukan login atau registrasi akun.
3. Setelah berhasil masuk, pengguna dapat membuat room, bergabung ke room, mengirim pesan, atau melakukan komunikasi privat.
4. Server memproses seluruh permintaan client dan menyimpan data ke database.
5. Pesan, file, notifikasi, dan reaksi didistribusikan secara real-time kepada pengguna terkait.
```

### Struktur Utama Program

`fpclient.py`

Merupakan aplikasi client yang dijalankan oleh pengguna.
```
Tanggung jawab utama:

Menghubungkan pengguna ke server.
Menangani proses login dan registrasi.
Mengirim perintah dan data ke server.
Menampilkan respon dari server.
Menjalankan thread listener untuk menerima pesan secara real-time.
Melakukan enkripsi dan dekripsi pada pesan pribadi.
Mengelola pengiriman dan pengunduhan file.
```

`fpserver.py`

Merupakan entry point aplikasi server.
```
Tanggung jawab utama:

Menginisialisasi database.
Menjalankan layanan TCP Server.
Menerima koneksi dari banyak client.
Menjadi pusat koordinasi seluruh komunikasi antar pengguna.
```

`nexuschat.db`

Database SQLite yang digunakan untuk menyimpan data aplikasi secara permanen.
```
Data yang disimpan meliputi:

Akun pengguna
Room chat
Keanggotaan room
Riwayat pesan room
Riwayat direct message
Metadata file
Reaksi pesan
```

### Fitur Utama

Autentikasi Pengguna

Setiap pengguna harus memiliki akun untuk menggunakan sistem.
```
Fitur:

Registrasi akun baru
Login pengguna
Identifikasi pengguna secara unik
```

Multi Room Chat

Pengguna dapat membuat dan bergabung ke berbagai room diskusi.
```
Fitur:

Membuat room baru
Bergabung ke room
Keluar dari room
Melihat daftar room yang tersedia
Melihat anggota yang berada di dalam room
```

Pesan Grup (Broadcast Message)

Memungkinkan pengguna mengirim pesan ke seluruh anggota room secara real-time.

Pesan Pribadi (Direct Message)

Pengguna dapat berkomunikasi secara langsung dengan pengguna lain tanpa melalui room.
```
Keunggulan:

Komunikasi satu lawan satu
Pesan dienkripsi sebelum dikirim
```

Daftar Pengguna Online

Menampilkan seluruh pengguna yang sedang terhubung ke server.

Pengiriman File ke Room

Memungkinkan pengguna membagikan file kepada seluruh anggota room.
```
Informasi yang ditampilkan:

Nama file
Ukuran file
Tipe file
ID file
```

Pengiriman File Pribadi

Mengirim file langsung kepada pengguna tertentu.

Download File

Setiap file yang dikirim memiliki ID unik yang dapat digunakan untuk mengunduh file kembali.

Reaksi Emoji pada Pesan

Pengguna dapat memberikan reaksi emoji pada pesan tertentu.
```
Fitur:

Menambahkan reaksi ke pesan
Menghitung jumlah reaksi
Menampilkan update reaksi secara real-time
```

Riwayat Percakapan (Chat History)

Pesan yang tersimpan dalam database dapat diakses kembali kapan saja.

Notifikasi Aktivitas Pengguna

Server secara otomatis mengirimkan notifikasi ketika:
```
Pengguna masuk ke room
Pengguna keluar dari room
```

Komunikasi Real-Time Berbasis TCP Socket

NexusChat menggunakan koneksi TCP Socket yang persisten sehingga:
```
Pesan diterima secara langsung.
Tidak memerlukan refresh.
Mendukung banyak client secara bersamaan.
Mendukung komunikasi dua arah secara terus-menerus.
```

### Daftar Perintah

| /create <room>              | Membuat room baru            |
| /join <room>	              | Bergabung ke room            |
| /leave <room>	              | Keluar dari room             |
| /list	                      | Melihat daftar room          |
| /msg <room> <pesan>	        | Mengirim pesan ke room       |
| /pm <user> <pesan>	        | Mengirim pesan pribadi       |
| /user	                      | Melihat pengguna online      |
| /sendfile <room> <path>	    | Mengirim file ke room        |
| /sendfilepm <user> <path>	  | Mengirim file pribadi        |
| /download <file_id>	        |  Mengunduh file              |
| /react <message_id> <emoji> | Memberi reaksi pada pesan    |
| /history <room>	            | Melihat riwayat room         |
| /history dm <user>	        | Melihat riwayat DM           |
| /help	                      | Menampilkan bantuan          |
| /quit	                      | Keluar dari aplikasi         |

## Screenshot Hasil
