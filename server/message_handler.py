import logging
from shared.crypto import encrypt_message, decrypt_message

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

    Message flow:
        1. Client kirim plaintext ke server
        2. Server encrypt untuk disimpan di history/log
        3. Server broadcast PLAINTEXT ke semua member di room
        4. Semua client menerima dan menampilkan teks asli (readable)

    Payload yang diharapkan:
        {
            "room_name": "nama_room",
            "content":   "isi pesan (plaintext)"
        }
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

    # Step 1: content dari client adalah plaintext — simpan encrypted di server
    plaintext             = content
    encrypted_for_storage = encrypt_message(plaintext)

    # Step 2: Cek apakah user ada di room tersebut
    members = state.get_room_members(room_name)
    if username not in members:
        return error(f"Kamu tidak berada di room '{room_name}'.")

    timestamp = now()

    # Step 3: Simpan versi terenkripsi di server-side history
    state.add_history(room_name, username, encrypted_for_storage, timestamp)
    logger.info(f"[BROADCAST] '{username}' @ '{room_name}': {encrypted_for_storage[:60]}")

    # Step 4: Broadcast PLAINTEXT ke semua member (termasuk pengirim)
    msg_payload = make_chat_message(
        sender  = username,
        room    = room_name,
        content = plaintext,      # ← plaintext, bukan encrypted
    )
    msg_payload["timestamp"] = timestamp

    _broadcast_room(room_name, msg_payload)

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

    msg_payload = make_private_message(
        sender    = username,
        recipient = recipient,
        content   = content,      # plaintext
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
