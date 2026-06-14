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
from server.database import save_message, get_messages, save_file, get_file
 
logger = logging.getLogger("MessageHandler")
 
 
# ─── Send Helper ──────────────────────────────────────────────────────────────
 
def _send_to(username: str, data: dict):
    """Kirim pesan ke satu user berdasarkan username."""
    sock = state.get_client_socket(username)
    logger.info(f"[DEBUG] _send_to '{username}', sock found: {sock is not None}")
    if sock:
        try:
            sock.sendall(serialize(data))
            logger.info(f"[DEBUG] sendall to '{username}' success")
        except Exception as e:
            logger.warning(f"Gagal kirim ke '{username}': {e}")
 
 
def _broadcast_room(room_name: str, data: dict, exclude: str = None):
    """Kirim pesan ke semua member di room, kecuali exclude."""
    members = state.get_room_members(room_name)
    logger.info(f"[DEBUG] Broadcasting to room '{room_name}', members: {members}, exclude: {exclude}")
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

    if not room_name:
        room_name = state.get_client_room(username) or ""
 
    if not room_name:
        return error("Kamu tidak sedang berada di room manapun.")
 
    if not content:
        return error("Pesan tidak boleh kosong.")

    members = state.get_room_members(room_name)
    if username not in members:
        return error(f"Kamu tidak berada di room '{room_name}'.")
 
    plaintext = content
    encrypted_for_storage = encrypt_message(content)

    timestamp = now()

    message_id = state.next_message_id()

    with state.messages_lock:
        state.messages[message_id] = {
            "sender": username,
            "room": room_name,
            "content": plaintext,
            "timestamp": timestamp,
            "reactions": {}
        }

    state.add_history(room_name, username, encrypted_for_storage, timestamp)
    logger.info(f"[BROADCAST] '{username}' @ '{room_name}': {encrypted_for_storage[:60]}")
 
    msg_payload = make_chat_message(
        sender  = username,
        room    = room_name,
        content = plaintext,
    )
    msg_payload["timestamp"] = timestamp
    msg_payload["message_id"] = message_id

    save_message(room_name, username, content, timestamp)

    _broadcast_room(room_name, msg_payload)
 
    logger.info(f"[BROADCAST] '{username}' @ '{room_name}': {content[:50]}")
 
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
    message_id = state.next_message_id()

    with state.messages_lock:
        state.messages[message_id] = {
            "sender": username,
            "room": None,
            "recipient": recipient,
            "content": content,
            "timestamp": timestamp,
            "reactions": {}
        }

    msg_payload = make_private_message(
        sender    = username,
        recipient = recipient,
        content   = encrypt_message(content),
    )
    msg_payload["timestamp"] = timestamp
    msg_payload["message_id"] = message_id
 
    _send_to(recipient, msg_payload)

    save_message(
    room_name = f"DM:{username}→{recipient}",
    sender    = username,
    content   = content,
    timestamp = timestamp
    )
 
    logger.info(f"[PRIVATE] '{username}' → '{recipient}': {encrypt_message(content)}")
    logger.info(f"[PRIVATE] '{username}' → '{recipient}': {content[:50]}")
 
    return ok(
        action    = "message_sent",
        message   = f"Pesan private terkirim ke '{recipient}'.",
        recipient = recipient,
        timestamp = timestamp,
    )

# ─── File Transfer & Reaction (STUB - belum lengkap) ─────────────────────────

# ─── File Transfer & Reaction ─────────────────────────────────────────────────

def handle_send_file(username, payload):
    room_name = payload.get("room_name", "").strip()
    filename  = payload.get("filename", "")
    filetype  = payload.get("filetype", "")
    filesize  = payload.get("filesize", 0)
    filedata  = payload.get("filedata", "")

    if not room_name or not filedata:
        return error("Data file tidak lengkap.")

    members = state.get_room_members(room_name)
    if username not in members:
        return error(f"Kamu tidak berada di room '{room_name}'.")

    timestamp = now()
    file_id = save_file(room_name, username, None, filename, filetype, filesize, filedata, timestamp)

    msg_payload = {
        "action":   "file_message",
        "file_id":  file_id,
        "sender":   username,
        "filename": filename,
        "filetype": filetype,
        "filesize": filesize,
        "timestamp": timestamp,
    }
    _broadcast_room(room_name, msg_payload)

    return ok(action="file_sent", message="File berhasil dikirim.")


def handle_send_private_file(username, payload):
    recipient = payload.get("recipient", "").strip()
    filename  = payload.get("filename", "")
    filetype  = payload.get("filetype", "")
    filesize  = payload.get("filesize", 0)
    filedata  = payload.get("filedata", "")

    if not recipient or not filedata:
        return error("Data file tidak lengkap.")

    if not state.is_online(recipient):
        return error(f"User '{recipient}' tidak ditemukan atau sedang offline.")

    timestamp = now()
    file_id = save_file(None, username, recipient, filename, filetype, filesize, filedata, timestamp)

    msg_payload = {
        "action":    "private_message",
        "file_id":   file_id,
        "sender":    username,
        "recipient": recipient,
        "filename":  filename,
        "filetype":  filetype,
        "filesize":  filesize,
        "message":   "",
        "timestamp": timestamp,
    }
    _send_to(recipient, msg_payload)

    return ok(action="file_sent", message=f"File berhasil dikirim ke '{recipient}'.")


def handle_download_file(username, payload):
    file_id = payload.get("file_id")

    if not file_id:
        return error("File ID tidak valid.")

    file = get_file(file_id)
    if not file:
        return error(f"File #{file_id} tidak ditemukan.")

    return ok(
        action   = "file_download",
        filename = file["filename"],
        filetype = file["filetype"],
        filesize = file["filesize"],
        filedata = file["filedata"],
    )


def handle_react_message(username, payload):
    message_id = payload.get("message_id")
    reaction   = payload.get("reaction", "").strip()

    if not message_id or not reaction:
        return error("Message ID dan emoji wajib diisi.")

    with state.messages_lock:
        if message_id not in state.messages:
            return error(f"Pesan #{message_id} tidak ditemukan.")

        msg = state.messages[message_id]
        reactions = msg.setdefault("reactions", {})
        reactions[reaction] = reactions.get(reaction, 0) + 1
        room_name = msg.get("room")

    if room_name:
        _broadcast_room(room_name, {
            "action":     "reaction_update",
            "message_id": message_id,
            "reactions":  reactions,
        })

    return ok(action="reacted", message="Reaksi berhasil dikirim.")

# ─── History Chat DM ─────────────────────────

def handle_get_dm_history(username: str, payload: dict) -> dict:
    recipient = payload.get("recipient", "").strip()
    
    history1 = get_messages(f"DM:{username}→{recipient}")
    history2 = get_messages(f"DM:{recipient}→{username}")
    
    all_history = sorted(history1 + history2, key=lambda x: x["timestamp"])
    
    return ok(
        action  = "dm_history",
        history = all_history
    )

# ─── History Chat Room ─────────────────────────
def handle_get_room_history(username: str, payload: dict) -> dict:  # ← hapus indentnya
    room_name = payload.get("room_name", "").strip()

    if not room_name:
        return error("Nama room tidak boleh kosong.")

    members = state.get_room_members(room_name)
    if username not in members:
        return error(f"Kamu tidak berada di room '{room_name}'.")

    history = get_messages(room_name)

    return ok(
        action    = "room_history",
        room_name = room_name,
        history   = history
    )
