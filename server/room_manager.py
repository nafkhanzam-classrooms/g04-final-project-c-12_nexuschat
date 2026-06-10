import logging
 
from shared.protocol import (
    serialize,
    ok, error, info,
    Event,
    now,
)
from server import state
 
logger = logging.getLogger("RoomManager")
 
 
# ─── Broadcast Helper (lokal) ─────────────────────────────────────────────────
 
def _broadcast_room(room_name: str, data: dict, exclude: str = None):
    """
    Kirim pesan ke semua member di sebuah room.
    exclude: username yang tidak perlu menerima (biasanya pengirimnya sendiri)
    """
    members = state.get_room_members(room_name)
    for member in members:
        if member == exclude:
            continue
        sock = state.get_client_socket(member)
        if sock:
            try:
                sock.sendall(serialize(data))
            except Exception as e:
                logger.warning(f"Gagal kirim ke '{member}': {e}")
 
 
# ─── Create Room ──────────────────────────────────────────────────────────────
 
def handle_create_room(username: str, payload: dict) -> dict:
    """
    Buat room baru.
 
    Payload yang diharapkan:
        { "room_name": "nama_room" }
 
    Aturan:
        - Nama room tidak boleh kosong
        - Nama room belum ada
        - Creator otomatis join ke room yang dibuat
    """
    room_name = payload.get("room_name", "").strip()
 
    if not room_name:
        return error("Nama room tidak boleh kosong.")
 
    if not room_name.replace("_", "").replace("-", "").isalnum():
        return error("Nama room hanya boleh huruf, angka, - dan _")
 
    with state.rooms_lock:
        if room_name in state.rooms:
            return error(f"Room '{room_name}' sudah ada.")
 
        # Buat room baru, creator langsung jadi member pertama
        state.rooms[room_name] = {
            "creator": username,
            "members": [username],
        }
 
    # Update room aktif si creator
    state.set_client_room(username, room_name)
 
    # Inisialisasi chat history untuk room ini
    with state.chat_history_lock:
        state.chat_history[room_name] = []
 
    logger.info(f"[ROOM] '{username}' membuat room '{room_name}'.")
 
    return ok(
        action    = Event.ROOM_CREATED,
        message   = f"Room '{room_name}' berhasil dibuat. Kamu otomatis bergabung!",
        room_name = room_name,
        members   = [username],
    )
 
 
# ─── Join Room ────────────────────────────────────────────────────────────────
 
def handle_join_room(username: str, payload: dict) -> dict:
    """
    Bergabung ke room yang sudah ada.
 
    Payload yang diharapkan:
        { "room_name": "nama_room" }
 
    Saat berhasil join:
        - User ditambahkan ke member list
        - Member lain mendapat notifikasi
        - User menerima chat history room tersebut
    """
    room_name = payload.get("room_name", "").strip()
 
    if not room_name:
        return error("Nama room tidak boleh kosong.")
 
    with state.rooms_lock:
        if room_name not in state.rooms:
            return error(f"Room '{room_name}' tidak ditemukan.")
 
        if username in state.rooms[room_name]["members"]:
            return error(f"Kamu sudah berada di room '{room_name}'.")
 
        state.rooms[room_name]["members"].append(username)
        members = list(state.rooms[room_name]["members"])
 
    # Update room aktif user
    state.set_client_room(username, room_name)
 
    logger.info(f"[ROOM] '{username}' bergabung ke room '{room_name}'.")
 
    # Notifikasi ke member lain
    _broadcast_room(
        room_name,
        info(
            action    = Event.USER_JOINED,
            message   = f"{username} bergabung ke room.",
            username  = username,
            room_name = room_name,
            timestamp = now(),
        ),
        exclude=username,
    )
 
    # Kirim chat history ke user yang baru join
    history = state.get_history(room_name)
 
    return ok(
        action    = Event.JOINED_ROOM,
        message   = f"Berhasil bergabung ke room '{room_name}'.",
        room_name = room_name,
        members   = members,
        history   = history,      # riwayat pesan terakhir
    )
 
 
# ─── Leave Room ───────────────────────────────────────────────────────────────
 
def handle_leave_room(username: str, payload: dict) -> dict:
    """
    Keluar dari room.
 
    Payload yang diharapkan:
        { "room_name": "nama_room" }   ← opsional, default pakai room aktif
 
    Aturan:
        - Kalau room jadi kosong setelah user keluar, room otomatis dihapus
    """
    room_name = payload.get("room_name", "").strip()
 
    # Fallback ke room aktif kalau tidak disertakan
    if not room_name:
        room_name = state.get_client_room(username) or ""
 
    if not room_name:
        return error("Kamu tidak sedang berada di room manapun.")
 
    with state.rooms_lock:
        if room_name not in state.rooms:
            return error(f"Room '{room_name}' tidak ditemukan.")
 
        if username not in state.rooms[room_name]["members"]:
            return error(f"Kamu tidak berada di room '{room_name}'.")
 
        state.rooms[room_name]["members"].remove(username)
        remaining = list(state.rooms[room_name]["members"])
 
        # Hapus room kalau sudah kosong
        room_deleted = False
        if not remaining:
            del state.rooms[room_name]
            room_deleted = True
 
    # Reset room aktif user
    if state.get_client_room(username) == room_name:
        state.set_client_room(username, None)
 
    logger.info(
        f"[ROOM] '{username}' keluar dari '{room_name}'. "
        f"{'Room dihapus (kosong).' if room_deleted else f'Sisa member: {remaining}'}"
    )
 
    # Notifikasi ke member yang tersisa
    if not room_deleted:
        _broadcast_room(
            room_name,
            info(
                action    = Event.USER_LEFT,
                message   = f"{username} meninggalkan room.",
                username  = username,
                room_name = room_name,
                timestamp = now(),
            ),
        )
 
    return ok(
        action       = Event.LEFT_ROOM,
        message      = f"Kamu telah keluar dari room '{room_name}'."
                       + (" Room dihapus karena kosong." if room_deleted else ""),
        room_name    = room_name,
        room_deleted = room_deleted,
    )
 
 
# ─── List Rooms ───────────────────────────────────────────────────────────────
 
def handle_list_rooms(username: str, payload: dict) -> dict:
    """
    Kirim daftar semua room yang aktif beserta info member.
 
    Payload: {} (kosong)
    """
    with state.rooms_lock:
        room_list = [
            {
                "room_name":    name,
                "creator":      info_data["creator"],
                "member_count": len(info_data["members"]),
                "members":      list(info_data["members"]),
            }
            for name, info_data in state.rooms.items()
        ]
 
    return ok(
        action = Event.ROOM_LIST,
        rooms  = room_list,
        total  = len(room_list),
    )