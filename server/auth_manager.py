import socket
import hashlib
import logging

from shared.protocol import (
    serialize,
    ok, error,
    Event,
    now_full,
)
from server import state
from server.database import save_user, get_user

logger = logging.getLogger("AuthManager")


# ─── Password Helper ──────────────────────────────────────────────────────────

def _hash_password(password: str) -> str:
    """Hash password menggunakan SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _validate_username(username: str) -> str | None:
    """
    Validasi format username.
    Return pesan error jika tidak valid, None jika valid.
    """
    if not username:
        return "Username tidak boleh kosong."
    if len(username) < 3:
        return "Username minimal 3 karakter."
    if len(username) > 20:
        return "Username maksimal 20 karakter."
    if not username.replace("_", "").replace("-", "").isalnum():
        return "Username hanya boleh huruf, angka, - dan _"
    return None


def _validate_password(password: str) -> str | None:
    """
    Validasi format password.
    Return pesan error jika tidak valid, None jika valid.
    """
    if not password:
        return "Password tidak boleh kosong."
    if len(password) < 4:
        return "Password minimal 4 karakter."
    return None


# ─── Register ─────────────────────────────────────────────────────────────────

def handle_register(conn: socket.socket, addr, payload: dict) -> str | None:
    """
    Proses permintaan REGISTER dari client.

    Payload yang diharapkan:
        { "username": "Budi", "password": "1234" }

    Return:
        username (str) jika berhasil dan langsung login
        None jika gagal
    """
    username = payload.get("username", "").strip()
    password = payload.get("password", "").strip()

    err = _validate_username(username)
    if err:
        conn.sendall(serialize(error(err)))
        return None

    err = _validate_password(password)
    if err:
        conn.sendall(serialize(error(err)))
        return None

# ─── ini yang aku ubah ────────────────────────────────────────────────────────────────────
#        save_user(username, _hash_password(password))
#        user = get_user(username) 
# ─── ini yang aku ubah ────────────────────────────────────────────────────────────────────

    with state.clients_lock:
        state.clients[username] = {
            "socket": conn,
            "room":   None,
        }

    conn.sendall(serialize(ok(
        action   = Event.LOGGED_IN,
        message  = f"Registrasi berhasil! Selamat datang, {username}! 👋",
        username = username,
        time     = now_full(),
    )))

    logger.info(f"[REGISTER] '{username}' mendaftar dan login dari {addr}")
    return username


# ─── Login ────────────────────────────────────────────────────────────────────

def handle_login(conn: socket.socket, addr, payload: dict) -> str | None:
    """
    Proses permintaan LOGIN dari client.

    Payload yang diharapkan:
        { "username": "Budi", "password": "1234" }

    Return:
        username (str) jika berhasil
        None jika gagal
    """
    username = payload.get("username", "").strip()
    password = payload.get("password", "").strip()

    err = _validate_username(username)
    if err:
        conn.sendall(serialize(error(err)))
        return None

    if not password:
        conn.sendall(serialize(error("Password tidak boleh kosong.")))
        return None

        if state.registered_users[username] != _hash_password(password):
            conn.sendall(serialize(error("Password salah.")))
            return None

    if state.is_online(username):
        conn.sendall(serialize(error(f"'{username}' sudah login di tempat lain.")))
        return None

    with state.clients_lock:
        state.clients[username] = {
            "socket": conn,
            "room":   None,
        }

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

    from server.room_manager import handle_leave_room

    with state.rooms_lock:
        rooms_joined = [
            room_name for room_name, info in state.rooms.items()
            if username in info["members"]
        ]

    for room_name in rooms_joined:
        handle_leave_room(username, {"room_name": room_name})

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
