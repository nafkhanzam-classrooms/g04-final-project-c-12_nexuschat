import socket
import logging
 
from shared.protocol import (
    serialize,
    ok, error,
    Event, Status,
    now_full,
)
from server import state
 
logger = logging.getLogger("AuthManager")
 
  
# ─── Login ────────────────────────────────────────────────────────────────────
 
def handle_login(conn: socket.socket, addr, payload: dict) -> str | None:
    """
    Proses permintaan LOGIN dari client.
 
    Payload yang diharapkan:
        { "username": "Budi" }
 
    Return:
        username (str) jika berhasil
        None jika gagal
    """
    username = payload.get("username", "").strip()
 
    # Validasi username tidak kosong
    if not username:
        conn.sendall(serialize(error("Username tidak boleh kosong.")))
        return None
 
    # Validasi username tidak mengandung karakter aneh
    if not username.replace("_", "").replace("-", "").isalnum():
        conn.sendall(serialize(error("Username hanya boleh huruf, angka, - dan _")))
        return None
 
    # Validasi username belum dipakai
    if state.is_online(username):
        conn.sendall(serialize(error(f"Username '{username}' sedang dipakai orang lain.")))
        return None
 
    # Daftarkan client ke state
    with state.clients_lock:
        state.clients[username] = {
            "socket": conn,
            "room":   None,
        }
 
    # Kirim respon sukses ke client
    conn.sendall(serialize(ok(
        action   = Event.LOGGED_IN,
        message  = f"Selamat datang, {username}! 👋",
        username = username,
        time     = now_full(),
    )))
 
    logger.info(f"[LOGIN] '{username}' terhubung dari {addr}")
    return username
 
 
# ─── Logout ───────────────────────────────────────────────────────────────────
 
def handle_logout(username: str):
    """
    Proses permintaan LOGOUT atau disconnect dari client.
 
    - Keluarkan user dari semua room yang diikuti
    - Hapus dari daftar clients
    - Broadcast notifikasi ke room yang ditinggalkan
    """
    if not username:
        return
 
    # Import di sini untuk hindari circular import
    from server.room_manager import handle_leave_room
 
    # Cari semua room yang diikuti user ini
    with state.rooms_lock:
        rooms_joined = [
            room_name for room_name, info in state.rooms.items()
            if username in info["members"]
        ]
 
    # Keluarkan dari semua room (otomatis broadcast notifikasi ke member lain)
    for room_name in rooms_joined:
        handle_leave_room(username, {"room_name": room_name})
 
    # Hapus dari daftar clients
    with state.clients_lock:
        state.clients.pop(username, None)
 
    logger.info(f"[LOGOUT] '{username}' telah keluar.")
 
 
# ─── Online User List ─────────────────────────────────────────────────────────
 
def handle_list_users(username: str, payload: dict) -> dict:
    """
    Kirim daftar semua user yang sedang online.
 
    Payload: {} (kosong)
    """
    online_users = state.get_online_users()
 
    return ok(
        action = Event.USER_LIST,
        users  = online_users,
        total  = len(online_users),
    )