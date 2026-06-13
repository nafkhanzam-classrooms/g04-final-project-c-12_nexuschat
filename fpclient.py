import socket
import threading
import json
import sys
from shared.crypto import encrypt_message
from shared.crypto import decrypt_message

HOST = "127.0.0.1"
PORT = 9090
BUFFER_SIZE = 4096


# ─── Serialization Helpers ────────────────────────────────────────────────────

def serialize(data: dict) -> bytes:
    return (json.dumps(data) + "\n").encode("utf-8")


def deserialize(raw: str) -> dict:
    return json.loads(raw.strip())


# ─── Pretty Printer ───────────────────────────────────────────────────────────

def print_response(data: dict):
    """Tampilkan respon dari server dengan format yang mudah dibaca."""
    action = data.get("action", "")
    status = data.get("status", "")

    if action == "room_list":
        rooms = data.get("rooms", [])
        print(f"\n{'─'*40}")
        print(f"  Daftar Room ({data.get('total', 0)} room)")
        print(f"{'─'*40}")
        if not rooms:
            print("  (Belum ada room)")
        for r in rooms:
            members_str = ", ".join(r["members"]) if r["members"] else "-"
            print(f"  {r['room_name']}  |  {r['member_count']} member  |  creator: {r['creator']}")
            print(f"     Members: {members_str}")
        print(f"{'─'*40}\n")
        return

    if action == "user_list":
        users = data.get("users", [])

        print(f"\n{'─'*40}")
        print(f"  User Online ({data.get('total', 0)} user)")
        print(f"{'─'*40}")

        if not users:
            print("  (Tidak ada user online)")
        else:
            for user in users:
                print(f"  • {user}")

        print(f"{'─'*40}\n")
        return

    if action == "joined_room":
        members = ", ".join(data.get("members", []))
        print(f"\n  {data.get('message')}")
        print(f"     Members saat ini: {members}\n")
        return

    if action == "broadcast":
        encrypted = data.get("content", "")

        try:
            content = decrypt_message(encrypted)
        except Exception:
            content = encrypted

        print(f"[{data['sender']}] {content}")

    msg = data.get("message", json.dumps(data))
    print(f"\n{msg}\n")


# ─── Background Receiver ──────────────────────────────────────────────────────

def receiver_thread(sock: socket.socket):
    """Terima pesan dari server di thread terpisah (non-blocking input)."""
    buffer = ""
    try:
        while True:
            chunk = sock.recv(BUFFER_SIZE).decode("utf-8")
            if not chunk:
                print("\n  [Koneksi ke server terputus]")
                break
            buffer += chunk
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if line.strip():
                    try:
                        data = deserialize(line)
                        print_response(data)
                        # Cetak ulang prompt agar tidak mengganggu input user
                        print(">> ", end="", flush=True)
                    except json.JSONDecodeError:
                        print(f"  [Respon tidak valid: {line}]")
    except Exception:
        pass


# ─── Command Parser ───────────────────────────────────────────────────────────

def print_help():
    print("""
╔═════════════════════════════════════════════════╗
║           Perintah yang tersedia                ║
╠═════════════════════════════════════════════════╣
║  /create  <nama_room>     Buat room baru        ║
║  /join    <nama_room>     Masuk ke room         ║
║  /msg     <room> <pesan>  Kirim pesan ke room   ║
║  /pm      <user> <pesan>  Kirim pesan pribadi   ║
║  /leave   <nama_room>     Keluar dari room      ║
║  /list                    Lihat semua room      ║
║  /user                    Lihat user online     ║
║  /help                    Tampilkan bantuan     ║
║  /quit                    Keluar dari program   ║
╚═════════════════════════════════════════════════╝
""")


def parse_and_send(sock: socket.socket, line: str) -> bool:
    """
    Parse input user, buat pesan JSON, kirim ke server.
    Return False jika user ingin keluar.
    """
    parts = line.strip().split(maxsplit=1)
    if not parts:
        return True

    cmd = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""

    if cmd == "/quit":
        sock.sendall(serialize({"action": "LOGOUT", "payload": {}}))
        return False

    elif cmd == "/help":
        print_help()

    elif cmd == "/create":
        if not arg:
            print(" Penggunaan: /create <nama_room>")
        else:
            sock.sendall(serialize({"action": "CREATE_ROOM", "payload": {"room_name": arg}}))

    elif cmd == "/join":
        if not arg:
            print("Penggunaan: /join <nama_room>")
        else:
            sock.sendall(serialize({"action": "JOIN_ROOM", "payload": {"room_name": arg}}))

    elif cmd == "/leave":
        # Boleh tanpa argumen — server akan pakai room aktif
        sock.sendall(serialize({"action": "LEAVE_ROOM", "payload": {"room_name": arg}}))

    elif cmd == "/list":
        sock.sendall(serialize({"action": "LIST_ROOMS", "payload": {}}))

    elif cmd == "/user":
        sock.sendall(serialize({
            "action": "LIST_USERS",
            "payload": {}
        }))

    elif cmd == "/msg":
        # Format: /msg <room> <pesan>
        parts2 = arg.split(maxsplit=1)
        if len(parts2) < 2:
            print("Penggunaan: /msg <nama_room> <pesan>")
        else:
            room, content = parts2[0], parts2[1]
            encrypted = encrypt_message(content)
            sock.sendall(serialize({
                "action": "BROADCAST",
                "payload": { "room_name": room, "content": encrypted}
            }))
        
    elif cmd == "/pm":
        # Format: /pm <username> <pesan>
        parts2 = arg.split(maxsplit=1)
        if len(parts2) < 2:
            print("Penggunaan: /pm <username> <pesan>")
        else:
            recipient, content = parts2[0], parts2[1]
            sock.sendall(serialize({
                "action":  "PRIVATE_MSG",
                "payload": {"recipient": recipient, "content": content}
            
            }))

    else:
        print(f"Perintah '{cmd}' tidak dikenal. Ketik /help untuk bantuan.")

    return True


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("╔══════════════════════════════════╗")
    print("║   Multi-Chat Rooms — Client      ║")
    print("╚══════════════════════════════════╝")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        print(f"Terhubung ke server {HOST}:{PORT}\n")
    except ConnectionRefusedError:
        print(f"Tidak bisa terhubung ke {HOST}:{PORT}. Pastikan server sudah berjalan.")
        sys.exit(1)

    # Minta username
    username = input("  Masukkan username: ").strip()
    if not username:
        print("Username tidak boleh kosong.")
        sock.close()
        sys.exit(1)

    # Kirim LOGIN
    sock.sendall(serialize({"action": "LOGIN", "payload": {"username": username}}))

    # Mulai thread penerima
    t = threading.Thread(target=receiver_thread, args=(sock,), daemon=True)
    t.start()

    import time
    time.sleep(0.3)  # Beri waktu server merespon login

    print_help()

    try:
        while True:
            line = input(">> ").strip()
            if not line:
                continue
            if not parse_and_send(sock, line):
                break
    except (KeyboardInterrupt, EOFError):
        print("\n  Menutup koneksi...")
        try:
            sock.sendall(serialize({"action": "LOGOUT", "payload": {}}))
        except Exception:
            pass

    sock.close()
    print("  Sampai jumpa!")


if __name__ == "__main__":
    main()
