import socket
import threading
import json
import sys
import os
import base64
import mimetypes

MESSAGE_CACHE = {}

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
    action = data.get("action", "")

    # ── /list ──────────────────────────────────────────────────────────────────
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

    # ── /user ──────────────────────────────────────────────────────────────────
    if action == "user_list":
        users = data.get("users", [])
        print(f"\n{'─'*40}")
        print(f"  User Online ({data.get('total', 0)} user)")
        print(f"{'─'*40}")
        if not users:
            print("  (Tidak ada user online)")
        for u in users:
            print(f"  • {u}")
        print(f"{'─'*40}\n")
        return

    # ── join room ──────────────────────────────────────────────────────────────
    if action == "joined_room":
        members = ", ".join(data.get("members", []))
        print(f"\n  {data.get('message')}")
        print(f"     Members saat ini: {members}")

        # Tampilkan history pesan kalau ada
        history = data.get("history", [])
        if history:
            print(f"\n  ── Riwayat pesan terakhir ──")
            for entry in history:
                print(f"  [{entry.get('timestamp','')}] {entry.get('sender','?')}: {entry.get('content','')}")
            print(f"  ────────────────────────────")
        print()
        return

    # ── chat message (broadcast) ───────────────────────────────────────────────    
    if action == "new_message":

        message_id = data.get("message_id")
        sender = data.get("sender", "?")
        room = data.get("room", "")
        content = data.get("message", "")
        timestamp = data.get("timestamp", "")

        MESSAGE_CACHE[message_id] = data

        print(
            f"\n#{message_id} "
            f"[{timestamp}] "
            f"[{room}] "
            f"{sender}: {content}\n"
        )
        return

    # ── private message ────────────────────────────────────────────────────────
    if action == "private_message":
        sender    = data.get("sender", "?")
        content   = data.get("message", "")
        timestamp = data.get("timestamp", "")
        print(f"\n  [{timestamp}] (DM dari {sender}): {content}\n")

        print(
            f"\n📎 FILE #{data.get('file_id')}"
            f"\nPengirim : {data.get('sender')}"
            f"\nNama     : {data.get('filename')}"
            f"\nUkuran   : {data.get('filesize')} byte"
            f"\nTipe     : {data.get('filetype')}\n"
        )
        return

    # ── user joined / left room ────────────────────────────────────────────────
    if action in ("user_joined", "user_left"):
        print(f"\n  *** {data.get('message', '')} ***\n")
        return

    # ── file ────────────────────────────────────────────────
    if action == "file_message":

        print(
            f"\n📎 FILE #{data.get('file_id')}"
            f"\nPengirim : {data.get('sender')}"
            f"\nNama     : {data.get('filename')}"
            f"\nUkuran   : {data.get('filesize')} byte"
            f"\nTipe     : {data.get('filetype')}\n"
        )

        return
    
    # ── reaction ────────────────────────────────────────────────
    if action == "reaction_update":

        message_id = data.get("message_id")
        reactions = data.get("reactions", {})

        text = " ".join(
            f"{emoji} {count}"
            for emoji, count in reactions.items()
        )

        print(
            f"\nPesan #{message_id} "
            f"mendapat reaction: {text}\n"
        )
        return

    # ── file download ────────────────────────────────────────────────
    if action == "file_download":

        filename = data["filename"]
        filedata = data["filedata"]

        save_dir = "downloads"
        os.makedirs(save_dir, exist_ok=True)

        filepath = os.path.join(save_dir, filename)

        with open(filepath, "wb") as f:
            f.write(base64.b64decode(filedata))

        print(f"\nFile disimpan ke {filepath}\n")
        return

    # ── fallback ───────────────────────────────────────────────────────────────
    msg = data.get("message", json.dumps(data))
    print(f"\n  {msg}\n")


# ─── Background Receiver ──────────────────────────────────────────────────────

def receiver_thread(sock: socket.socket):
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
                        print(">> ", end="", flush=True)
                    except json.JSONDecodeError:
                        print(f"  [Respon tidak valid: {line}]")
    except Exception:
        pass


# ─── Command Parser ───────────────────────────────────────────────────────────

def print_help():
    print("""
╔══════════════════════════════════════════════╗
║           Perintah yang tersedia             ║
╠══════════════════════════════════════════════╣
║  /create  <nama_room>   Buat room baru       ║
║  /join    <nama_room>   Masuk ke room        ║
║  /leave   <nama_room>   Keluar dari room     ║
║  /list                  Lihat semua room     ║
║  /msg  <room> <pesan>   Kirim pesan ke room  ║
║  /pm   <user> <pesan>   Pesan private        ║
║  /user                  Lihat user online    ║
║  /help                  Tampilkan bantuan    ║
║  /quit                  Keluar dari program  ║
║  /sendfile <room> <path>                     ║
║  /sendfilepm <user> <path>                   ║
║  /react <message_id> <emoji>                 ║
║  /download <file_id>                         ║
╚══════════════════════════════════════════════╝
""")


def parse_and_send(sock: socket.socket, line: str) -> bool:
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
            print("  Penggunaan: /create <nama_room>")
        else:
            sock.sendall(serialize({"action": "CREATE_ROOM", "payload": {"room_name": arg}}))

    elif cmd == "/join":
        if not arg:
            print("  Penggunaan: /join <nama_room>")
        else:
            sock.sendall(serialize({"action": "JOIN_ROOM", "payload": {"room_name": arg}}))

    elif cmd == "/leave":
        sock.sendall(serialize({"action": "LEAVE_ROOM", "payload": {"room_name": arg}}))

    elif cmd == "/list":
        sock.sendall(serialize({"action": "LIST_ROOMS", "payload": {}}))

    elif cmd == "/user":
        # FIX: was "/user" → "LIST_USERS" mapping, now wired correctly
        sock.sendall(serialize({"action": "LIST_USERS", "payload": {}}))

    elif cmd == "/msg":
        parts2 = arg.split(maxsplit=1)
        if len(parts2) < 2:
            print("  Penggunaan: /msg <nama_room> <pesan>")
        else:
            room, content = parts2[0], parts2[1]
            sock.sendall(serialize({
                "action": "BROADCAST",
                "payload": {"room_name": room, "content": content}
            }))

    elif cmd == "/pm":
        parts2 = arg.split(maxsplit=1)
        if len(parts2) < 2:
            print("  Penggunaan: /pm <username> <pesan>")
        else:
            recipient, content = parts2[0], parts2[1]
            sock.sendall(serialize({
                "action":  "PRIVATE_MSG",
                "payload": {"recipient": recipient, "content": content}
            }))

    elif cmd == "/sendfile":

        parts2 = arg.split(maxsplit=1)

        if len(parts2) < 2:
            print(
                "Penggunaan: "
                "/sendfile <room> <path_file>"
            )

        else:

            room_name, filepath = parts2

            try:

                with open(filepath, "rb") as f:
                    content = f.read()

                encoded = base64.b64encode(
                    content
                ).decode()

                mime_type, _ = mimetypes.guess_type(
                    filepath
                )

                sock.sendall(
                    serialize({
                        "action": "SEND_FILE",
                        "payload": {
                            "room_name": room_name,
                            "filename": os.path.basename(filepath),
                            "filetype": mime_type,
                            "filesize": len(content),
                            "filedata": encoded
                        }
                    })
                )

            except Exception as e:
                print(
                    f"Gagal mengirim file: {e}"
                )

    elif cmd == "/sendfilepm":

        parts2 = arg.split(maxsplit=1)

        if len(parts2) < 2:
            print("Penggunaan: /sendfilepm <user> <path>")
        else:

            recipient, filepath = parts2

            try:
                with open(filepath, "rb") as f:
                    content = f.read()

                encoded = base64.b64encode(content).decode()

                mime_type, _ = mimetypes.guess_type(filepath)

                sock.sendall(
                    serialize({
                        "action": "SEND_PRIVATE_FILE",
                        "payload": {
                            "recipient": recipient,
                            "filename": os.path.basename(filepath),
                            "filetype": mime_type,
                            "filesize": len(content),
                            "filedata": encoded
                        }
                    })
                )

            except Exception as e:
                print(f"Gagal mengirim file: {e}")

    elif cmd == "/react":

        parts2 = arg.split(maxsplit=1)

        if len(parts2) < 2:
            print(
                "Penggunaan: "
                "/react <message_id> <emoji>"
            )

        else:

            message_id = int(parts2[0])
            reaction = parts2[1]

            sock.sendall(
                serialize({
                    "action": "REACT_MESSAGE",
                    "payload": {
                        "message_id": message_id,
                        "reaction": reaction
                    }
                })
            )

    elif cmd == "/download":

        try:
            file_id = int(arg)

            sock.sendall(
                serialize({
                    "action": "DOWNLOAD_FILE",
                    "payload": {
                        "file_id": file_id
                    }
                })
            )

        except ValueError:
            print("File ID harus berupa angka.")

    else:
        print(f"  Perintah '{cmd}' tidak dikenal. Ketik /help untuk bantuan.")

    return True


# ─── Authenticate ─────────────────────────────────────────────────────────────

def authenticate(sock):
    # Buang pesan sambutan dari server
    sock.recv(BUFFER_SIZE)

    while True:
        print("\n  1. Login")
        print("  2. Register")

        pilihan  = input("  Pilih (1/2): ").strip()
        username = input("  Username   : ").strip()
        password = input("  Password   : ").strip()

        if not username or not password:
            print("  Username dan password tidak boleh kosong.")
            continue

        action = "REGISTER" if pilihan == "2" else "LOGIN"

        sock.sendall(serialize({
            "action": action,
            "payload": {
                "username": username,
                "password": password,
            }
        }))

        response = sock.recv(BUFFER_SIZE).decode("utf-8")
        for line in response.split("\n"):
            if not line.strip():
                continue
            try:
                data = deserialize(line)
                print(f"\n  {data.get('message')}")
                if data.get("status") == "ok":
                    return
            except Exception:
                pass

        print("  Silakan coba lagi.\n")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("╔══════════════════════════════════╗")
    print("║   Multi-Chat Rooms — Client      ║")
    print("╚══════════════════════════════════╝")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        print(f"  Terhubung ke server {HOST}:{PORT}\n")
    except ConnectionRefusedError:
        print(f"  Tidak bisa terhubung ke {HOST}:{PORT}. Pastikan server sudah berjalan.")
        sys.exit(1)

    authenticate(sock)

    t = threading.Thread(target=receiver_thread, args=(sock,), daemon=True)
    t.start()

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
