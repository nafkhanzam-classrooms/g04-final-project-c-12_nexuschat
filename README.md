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
https://its.id/m/2026FPprogjarK12
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

#### Autentikasi Pengguna

Setiap pengguna harus memiliki akun untuk menggunakan sistem.
```
Fitur:

Registrasi akun baru
Login pengguna
Identifikasi pengguna secara unik
```

#### Multi Room Chat

Pengguna dapat membuat dan bergabung ke berbagai room diskusi.
```
Fitur:

Membuat room baru
Bergabung ke room
Keluar dari room
Melihat daftar room yang tersedia
Melihat anggota yang berada di dalam room
```

#### Pesan Grup (Broadcast Message)

Memungkinkan pengguna mengirim pesan ke seluruh anggota room secara real-time.

#### Pesan Pribadi (Direct Message)

Pengguna dapat berkomunikasi secara langsung dengan pengguna lain tanpa melalui room.
```
Keunggulan:

Komunikasi satu lawan satu
Pesan dienkripsi sebelum dikirim
```

#### Daftar Pengguna Online

Menampilkan seluruh pengguna yang sedang terhubung ke server.

#### Pengiriman File ke Room

Memungkinkan pengguna membagikan file kepada seluruh anggota room.
```
Informasi yang ditampilkan:

Nama file
Ukuran file
Tipe file
ID file
```

#### Pengiriman File Pribadi

Mengirim file langsung kepada pengguna tertentu.

#### Download File

Setiap file yang dikirim memiliki ID unik yang dapat digunakan untuk mengunduh file kembali.

#### Reaksi Emoji pada Pesan

Pengguna dapat memberikan reaksi emoji pada pesan tertentu.
```
Fitur:

Menambahkan reaksi ke pesan
Menghitung jumlah reaksi
Menampilkan update reaksi secara real-time
```

#### Riwayat Percakapan (Chat History)

Pesan yang tersimpan dalam database dapat diakses kembali kapan saja.

#### Notifikasi Aktivitas Pengguna

Server secara otomatis mengirimkan notifikasi ketika:
```
Pengguna masuk ke room
Pengguna keluar dari room
```

#### Komunikasi Real-Time Berbasis TCP Socket

NexusChat menggunakan koneksi TCP Socket yang persisten sehingga:
```
Pesan diterima secara langsung.
Tidak memerlukan refresh.
Mendukung banyak client secara bersamaan.
Mendukung komunikasi dua arah secara terus-menerus.
```

### Daftar Perintah

| Perintah                    | Fungsi                       | 
| ---                         | ---                          | 
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

<img width="637" height="415" alt="Screenshot 2026-06-14 164947" src="https://github.com/user-attachments/assets/f002f3a1-e2bb-4d76-b97c-a280073a4b43" />

<img width="419" height="366" alt="Screenshot 2026-06-14 164824" src="https://github.com/user-attachments/assets/05f8d7cb-06b8-4d4c-b834-44f6b0f1e6c5" />

<img width="857" height="253" alt="Screenshot 2026-06-14 164747" src="https://github.com/user-attachments/assets/851efd49-42e9-4a75-8eec-18b0e8eef686" />

<img width="770" height="194" alt="Screenshot 2026-06-14 164714" src="https://github.com/user-attachments/assets/d2d6df26-b6c7-41b0-b668-5cb3005042cb" />

<img width="790" height="240" alt="Screenshot 2026-06-14 164653" src="https://github.com/user-attachments/assets/88e71f9a-ca2d-4c7d-abc3-d815af39c74d" />

<img width="797" height="178" alt="Screenshot 2026-06-14 164621" src="https://github.com/user-attachments/assets/9c58f370-619b-4fd7-bbc6-b1d2c70c5df5" />

<img width="783" height="412" alt="Screenshot 2026-06-14 164529" src="https://github.com/user-attachments/assets/83d0c354-258a-4e4b-9da6-903851fc4931" />

<img width="763" height="408" alt="Screenshot 2026-06-14 164517" src="https://github.com/user-attachments/assets/4d24cd6c-75fa-4c8a-81f0-a3dec68b6f0e" />

<img width="697" height="394" alt="Screenshot 2026-06-14 164436" src="https://github.com/user-attachments/assets/613f393e-530d-4144-8763-66d77ae6f7e8" />
