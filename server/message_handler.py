import logging
 
from shared.protocol import (
    serialize,
    ok, error,
    make_chat_message,
    make_private_message,
    now,
)
from server import state
 
logger = logging.getLogger("MessageHandler")
 
 
# ─── Send Helper ──────────────────────────────────────────────────────────────
 
def _send_to(username: str, data: dict):
    """Kirim pesan ke satu user berdasarkan username."""
    sock = state.get_client_socket(username)
    if sock:
        try:
            sock.sendall(serialize(data))
        except Exception as e:
            logger.warning(f"Gagal kirim ke '{username}': {e}")
 
 
def _broadcast_room(room_name: str, data: dict, exclude: str = None):
    """Kirim pesan ke semua member di room, kecuali exclude."""
    members = state.get_room_members(room_name)
    for member in members:
        if member == exclude:
            continue
        _send_to(member, data)
 
 
# ─── Broadcast ────────────────────────────────────────────────────────────────
 
def handle_broadcast(username: str, payload: dict) -> dict:
    """
    Kirim pesan ke semua member di room yang sama.
 
    Payload yang diharapkan:
        {
            "room_name": "nama_room",
            "content":   "isi pesan"
        }
 
    Aturan:
        - User harus sudah join di room tersebut
        - Pesan tidak boleh kosong
        - Pesan disimpan ke chat history
    """
    room_name = payload.get("room_name", "").strip()
    content   = payload.get("content", "").strip()
 
    # Fallback ke room aktif kalau room_name tidak disertakan
    if not room_name:
        room_name = state.get_client_room(username) or ""
 
    if not room_name:
        return error("Kamu tidak sedang berada di room manapun.")
 
    if not content:
        return error("Pesan tidak boleh kosong.")
 
    # Cek apakah user ada di room tersebut
    members = state.get_room_members(room_name)
    if username not in members:
        return error(f"Kamu tidak berada di room '{room_name}'.")
 
    timestamp = now()
 
    # Buat payload pesan
    msg_payload = make_chat_message(
        sender  = username,
        room    = room_name,
        content = content,
    )
    msg_payload["timestamp"] = timestamp
 
    # Simpan ke chat history
    state.add_history(room_name, username, content, timestamp)
 
    # Kirim ke semua member di room (termasuk pengirim supaya muncul di chat mereka)
    _broadcast_room(room_name, msg_payload)
 
    logger.info(f"[BROADCAST] '{username}' @ '{room_name}': {content[:50]}")
 
    # Return konfirmasi ke pengirim (sudah terkirim via broadcast di atas)
    return ok(
        action    = "message_sent",
        message   = "Pesan terkirim.",
        room_name = room_name,
        timestamp = timestamp,
    )
 
 
# ─── Private Message ──────────────────────────────────────────────────────────
 
def handle_private_msg(username: str, payload: dict) -> dict:
    """
    Kirim pesan private ke satu user tertentu.
 
    Payload yang diharapkan:
        {
            "recipient": "username_tujuan",
            "content":   "isi pesan"
        }
 
    Aturan:
        - Recipient harus sedang online
        - Tidak bisa kirim pesan ke diri sendiri
        - Pesan tidak boleh kosong
    """
    recipient = payload.get("recipient", "").strip()
    content   = payload.get("content", "").strip()
 
    if not recipient:
        return error("Nama penerima tidak boleh kosong.")
 
    if not content:
        return error("Pesan tidak boleh kosong.")
 
    if recipient == username:
        return error("Tidak bisa mengirim pesan ke diri sendiri.")
 
    if not state.is_online(recipient):
        return error(f"User '{recipient}' tidak ditemukan atau sedang offline.")
 
    timestamp = now()
 
    # Buat payload pesan private
    msg_payload = make_private_message(
        sender    = username,
        recipient = recipient,
        content   = content,
    )
    msg_payload["timestamp"] = timestamp
 
    # Kirim ke penerima
    _send_to(recipient, msg_payload)
 
    logger.info(f"[PRIVATE] '{username}' → '{recipient}': {content[:50]}")
 
    # Konfirmasi ke pengirim
    return ok(
        action    = "message_sent",
        message   = f"Pesan private terkirim ke '{recipient}'.",
        recipient = recipient,
        timestamp = timestamp,
    )