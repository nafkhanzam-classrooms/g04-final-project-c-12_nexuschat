import threading

clients: dict[str, dict] = {}
clients_lock = threading.Lock()

rooms: dict[str, dict] = {}
rooms_lock = threading.Lock()

chat_history: dict[str, list] = {}
chat_history_lock = threading.Lock()

MAX_HISTORY = 50  


# ─── Helper Functions ─────────────────────────────────────────────────────────

def add_history(room_name: str, sender: str, content: str, timestamp: str):
    """Tambah pesan ke chat history sebuah room."""
    with chat_history_lock:
        if room_name not in chat_history:
            chat_history[room_name] = []
        chat_history[room_name].append({
            "sender":    sender,
            "content":   content,
            "timestamp": timestamp,
        })
        if len(chat_history[room_name]) > MAX_HISTORY:
            chat_history[room_name] = chat_history[room_name][-MAX_HISTORY:]


def get_history(room_name: str) -> list:
    """Ambil riwayat pesan sebuah room. Return list kosong kalau room belum ada."""
    with chat_history_lock:
        return list(chat_history.get(room_name, []))


def get_online_users() -> list[str]:
    """Return daftar username yang sedang online."""
    with clients_lock:
        return list(clients.keys())


def get_room_members(room_name: str) -> list[str]:
    """Return daftar member di sebuah room. Return list kosong kalau room tidak ada."""
    with rooms_lock:
        return list(rooms.get(room_name, {}).get("members", []))


def is_online(username: str) -> bool:
    """Cek apakah user sedang online."""
    with clients_lock:
        return username in clients


def get_client_socket(username: str):
    """Ambil socket milik username. Return None kalau tidak ditemukan."""
    with clients_lock:
        info = clients.get(username)
        return info["socket"] if info else None


def get_client_room(username: str) -> str | None:
    """Ambil room aktif milik username. Return None kalau tidak di room manapun."""
    with clients_lock:
        info = clients.get(username)
        return info["room"] if info else None


def set_client_room(username: str, room_name: str | None):
    """Set room aktif milik username."""
    with clients_lock:
        if username in clients:
            clients[username]["room"] = room_name


registered_users: dict[str, str] = {}
registered_users_lock = threading.Lock()

messages = {}
messages_lock = threading.Lock()

message_counter = 1
message_counter_lock = threading.Lock()


def next_message_id():
    global message_counter

    with message_counter_lock:
        current = message_counter
        message_counter += 1
        return current
    
files = {}
files_lock = threading.Lock()

file_counter = 1
file_counter_lock = threading.Lock()


def next_file_id():
    global file_counter

    with file_counter_lock:
        current = file_counter
        file_counter += 1
        return current
    
private_files = {}
private_files_lock = threading.Lock()

import os

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)
