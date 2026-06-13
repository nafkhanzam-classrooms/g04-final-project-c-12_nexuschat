import socket
import threading
import json
import logging

from shared.protocol import serialize, error, Action
from server.auth_manager import handle_register, handle_login, handle_logout, handle_list_users
from server.room_manager import (
    handle_create_room,
    handle_join_room,
    handle_leave_room,
    handle_list_rooms,
)
from server.message_handler import handle_broadcast, handle_private_msg

HOST        = "127.0.0.1"
PORT        = 9090
BUFFER_SIZE = 4096

logger = logging.getLogger("TCPServer")

ACTION_HANDLERS = {
    Action.CREATE_ROOM: handle_create_room,
    Action.JOIN_ROOM:   handle_join_room,
    Action.LEAVE_ROOM:  handle_leave_room,   # FIX: removed dangling "Action." line
    Action.LIST_ROOMS:  handle_list_rooms,
    Action.BROADCAST:   handle_broadcast,
    Action.PRIVATE_MSG: handle_private_msg,
    Action.LIST_USERS:  handle_list_users,
}


# ─── Per-Client Thread ────────────────────────────────────────────────────────

def client_thread(conn: socket.socket, addr):
    """
    Thread untuk menangani satu client dari awal sampai disconnect.

    Alur:
        1. Tunggu pesan LOGIN / REGISTER
        2. Setelah login, routing action ke handler yang sesuai
        3. Saat disconnect, cleanup otomatis
    """
    logger.info(f"Koneksi baru dari {addr}")
    username = None
    buffer   = ""

    try:
        conn.sendall(serialize({
            "status":  "info",
            "message": "Terhubung ke server. Silakan LOGIN untuk melanjutkan.",
        }))

        while True:
            chunk = conn.recv(BUFFER_SIZE).decode("utf-8")
            if not chunk:
                break

            buffer += chunk

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue

                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    conn.sendall(serialize(error("Format pesan tidak valid (harus JSON).")))
                    continue

                action  = msg.get("action", "").upper()
                payload = msg.get("payload", {})

                if username is None:
                    if action == Action.REGISTER:
                        username = handle_register(conn, addr, payload)
                    elif action == Action.LOGIN:
                        username = handle_login(conn, addr, payload)
                    else:
                        conn.sendall(serialize(error("Harap LOGIN terlebih dahulu.")))
                    continue

                if action == Action.LOGOUT:
                    conn.sendall(serialize({
                        "status":  "ok",
                        "message": "Sampai jumpa! 👋",
                    }))
                    return

                handler = ACTION_HANDLERS.get(action)
                if handler:
                    response = handler(username, payload)
                    conn.sendall(serialize(response))
                else:
                    conn.sendall(serialize(error(f"Action '{action}' tidak dikenal.")))

    except (ConnectionResetError, BrokenPipeError):
        logger.info(f"Koneksi '{username or addr}' terputus secara tiba-tiba.")
    except Exception as e:
        logger.error(f"Error pada client '{username or addr}': {e}")
    finally:
        if username:
            handle_logout(username)
        conn.close()
        logger.info(f"Koneksi '{username or addr}' ditutup.")


# ─── Start Server ─────────────────────────────────────────────────────────────

def start_server():
    """
    Mulai server TCP, listen di HOST:PORT,
    dan spawn thread baru untuk setiap client yang connect.
    """
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(10)

    logger.info(f"Server berjalan di {HOST}:{PORT} — menunggu koneksi...")

    try:
        while True:
            conn, addr = server_sock.accept()
            t = threading.Thread(
                target = client_thread,
                args   = (conn, addr),
                daemon = True,
            )
            t.start()
            logger.info(f"Thread baru untuk {addr} | Total aktif: {threading.active_count() - 1}")

    except KeyboardInterrupt:
        logger.info("Server dihentikan oleh user (Ctrl+C).")
    finally:
        server_sock.close()
        logger.info("Server socket ditutup.")
