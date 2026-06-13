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

    SEND_FILE = "SEND_FILE"
    SEND_PRIVATE_FILE = "SEND_PRIVATE_FILE"
    DOWNLOAD_FILE = "DOWNLOAD_FILE" 

    REACT_MESSAGE = "REACT_MESSAGE"   

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

    SEND_FILE = "SEND_FILE"
    SEND_PRIVATE_FILE = "SEND_PRIVATE_FILE"
    DOWNLOAD_FILE = "DOWNLOAD_FILE"
    REACT_MESSAGE = "REACT_MESSAGE"


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

def make_file_message(
    sender: str,
    room: str,
    file_id: int,
    filename: str,
    filesize: int,
    filetype: str
):
    return info(
        action=Event.FILE_MESSAGE,
        sender=sender,
        room=room,
        file_id=file_id,
        filename=filename,
        filesize=filesize,
        filetype=filetype,
        timestamp=now(),
    )

def make_private_file(
    sender: str,
    recipient: str,
    file_id: int,
    filename: str,
    filesize: int,
    filetype: str
):
    return info(
        action=Event.PRIVATE_FILE,
        sender=sender,
        recipient=recipient,
        file_id=file_id,
        filename=filename,
        filesize=filesize,
        filetype=filetype,
        timestamp=now(),
    )

def make_reaction_update(
    message_id: int,
    reactions: dict
):
    return info(
        action=Event.REACTION_UPDATE,
        message_id=message_id,
        reactions=reactions
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

def req_send_file(
    room_name: str,
    filename: str,
    filetype: str,
    filesize: int,
    filedata: str
):
    return req(
        Action.SEND_FILE,
        room_name=room_name,
        filename=filename,
        filetype=filetype,
        filesize=filesize,
        filedata=filedata
    )

def req_send_private_file(
    recipient: str,
    filename: str,
    filetype: str,
    filesize: int,
    filedata: str
):
    return req(
        Action.SEND_PRIVATE_FILE,
        recipient=recipient,
        filename=filename,
        filetype=filetype,
        filesize=filesize,
        filedata=filedata
    )

def req_download_file(file_id: int):
    return req(
        Action.DOWNLOAD_FILE,
        file_id=file_id
    )

def req_react_message(
    message_id: int,
    reaction: str
):
    return req(
        Action.REACT_MESSAGE,
        message_id=message_id,
        reaction=reaction
    )
