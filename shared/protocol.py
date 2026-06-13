import json
import datetime


# ─── Action Constants ─────────────────────────────────────────────────────────

class Action:
    REGISTER    = "REGISTER"
    LOGIN       = "LOGIN"
    LOGOUT      = "LOGOUT"

    CREATE_ROOM = "CREATE_ROOM"
    JOIN_ROOM   = "JOIN_ROOM"
    LEAVE_ROOM  = "LEAVE_ROOM"
    LIST_ROOMS  = "LIST_ROOMS"

    BROADCAST   = "BROADCAST"      
    PRIVATE_MSG = "PRIVATE_MSG"    

    LIST_USERS  = "LIST_USERS"      

# ─── Server Response Action Constants ────────────────────────────────────────

class Event:
    LOGGED_IN       = "logged_in"
    LOGGED_OUT      = "logged_out"

    ROOM_CREATED    = "room_created"
    JOINED_ROOM     = "joined_room"
    LEFT_ROOM       = "left_room"
    ROOM_LIST       = "room_list"
    USER_JOINED     = "user_joined"     
    USER_LEFT       = "user_left"       

    NEW_MESSAGE     = "new_message"     
    PRIVATE_MESSAGE = "private_message" 

    USER_LIST       = "user_list"       


# ─── Status Constants ─────────────────────────────────────────────────────────

class Status:
    OK    = "ok"
    ERROR = "error"
    INFO  = "info"


# ─── Serialization Helpers ────────────────────────────────────────────────────

def serialize(data: dict) -> bytes:
    """
    Dict → bytes JSON dengan newline delimiter.
    Newline dipakai agar penerima tahu kapan 1 pesan selesai.
    """
    return (json.dumps(data) + "\n").encode("utf-8")


def deserialize(raw: str) -> dict:
    """
    String JSON → dict.
    Terima str (bukan bytes) karena biasanya sudah di-decode sebelumnya.
    """
    return json.loads(raw.strip())


# ─── Timestamp Helper ─────────────────────────────────────────────────────────

def now() -> str:
    """Return timestamp sekarang dalam format HH:MM:SS."""
    return datetime.datetime.now().strftime("%H:%M:%S")


def now_full() -> str:
    """Return timestamp lengkap: YYYY-MM-DD HH:MM:SS."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ─── Message Builders ─────────────────────────────────────────────────────────

def ok(action: str, message: str = "", **kwargs) -> dict:
    """Buat response sukses."""
    return {"status": Status.OK, "action": action, "message": message, **kwargs}


def error(message: str) -> dict:
    """Buat response error."""
    return {"status": Status.ERROR, "message": message}


def info(action: str, message: str = "", **kwargs) -> dict:
    """Buat response informatif (notifikasi, bukan hasil aksi langsung)."""
    return {"status": Status.INFO, "action": action, "message": message, **kwargs}


def make_chat_message(sender: str, room: str, content: str) -> dict:
    """Buat payload pesan broadcast."""
    return info(
        action    = Event.NEW_MESSAGE,
        message   = content,
        sender    = sender,
        room      = room,
        timestamp = now(),
    )


def make_private_message(sender: str, recipient: str, content: str) -> dict:
    """Buat payload pesan private."""
    return info(
        action    = Event.PRIVATE_MESSAGE,
        message   = content,
        sender    = sender,
        recipient = recipient,
        timestamp = now(),
    )


# ─── Request Builders ─────────────────────────────────────────────────────────

def req(action: str, **payload) -> dict:
    """Buat pesan request generik dari client."""
    return {"action": action, "payload": payload}

def req_login(username: str) -> dict:
    return req(Action.LOGIN, username=username)

def req_create_room(room_name: str) -> dict:
    return req(Action.CREATE_ROOM, room_name=room_name)

def req_join_room(room_name: str) -> dict:
    return req(Action.JOIN_ROOM, room_name=room_name)

def req_leave_room(room_name: str = "") -> dict:
    return req(Action.LEAVE_ROOM, room_name=room_name)

def req_list_rooms() -> dict:
    return req(Action.LIST_ROOMS)

def req_broadcast(room_name: str, content: str) -> dict:
    return req(Action.BROADCAST, room_name=room_name, content=content)

def req_private_msg(recipient: str, content: str) -> dict:
    return req(Action.PRIVATE_MSG, recipient=recipient, content=content)

def req_list_users() -> dict:
    return req(Action.LIST_USERS)

def req_register(username: str, password: str) -> dict:
    return req(Action.REGISTER, username=username, password=password)

def req_login_with_password(username: str, password: str) -> dict:
    return req(Action.LOGIN, username=username, password=password)
