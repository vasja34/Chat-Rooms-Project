"""
byte[1]: msg_type
byte[2,3]: nickname_len
byte[4,5]: room_id_len
byte[6,7]: payload_len
byte[8:] (nickname, room_id, payload)
"""
BUFSIZE = 1024
GET_NICKNAME = 1
EXIT_ROOM = 2
ENTER_ROOM = 3
CHAT_CONVERSATION = 4
# CLIENT_EXIT = 5
MAX_PAYLOAD = 90
MAX_PRIVATE_ROOMS = 9
MAX_CLIENTS = 100

rooms_name = {
    0: "Lobby",
    1: "Private Room 1",
    2: "Private Room 2",
    3: "Private Room 3",
    4: "Private Room 4",
    5: "Private Room 5",
    6: "Private Room 6",
    7: "Private Room 7",
    8: "Private Room 8",
    9: "Private Room 9",
}

rooms_id = {
    "Lobby": 0,
    "Private Room 1": 1,
    "Private Room 2": 2,
    "Private Room 3": 3,
    "Private Room 4": 4,
    "Private Room 5": 5,
    "Private Room 6": 6,
    "Private Room 7": 7,
    "Private Room 8": 8,
    "Private Room 9": 9,
}

rooms_color = {
    "Lobby": "#FFFFFF",  # bg_color
    "Private Room 1": "#94B49F",
    "Private Room 2": "#FFF9CA",
    "Private Room 3": "#D9F8C4",
    "Private Room 4": "#F2D7D9",
    "Private Room 5": "#FFE699",
    "Private Room 6": "#92B4E3",
    "Private Room 7": "#97DBAE",
    "Private Room 8": "#BFFFF0",
    "Private Room 9": "#FDBAF8",
}  # just for message coloring


def msg_parser(message):
    msg_type = int(message[0])
    msg_nickname_len = int(message[1:3])
    room_id_len = int(message[3:5])
    payload_len = int(message[5:7])
    if msg_type > 6:
        raise ValueError("Unknown msg_type")
    if payload_len > 90:
        raise ValueError("msg_len > 90")
    if msg_nickname_len > 10:
        raise ValueError("nickname_len > 10")

    OFFSET = 7  # 1+2+2+2
    c1 = OFFSET
    c2 = c1 + msg_nickname_len
    msg_nickname = message[c1:c2]
    c1 = c2
    c2 = c1 + room_id_len
    room_id = int(message[c1:c2])
    msg_room_name = rooms_name[room_id]
    c1 = c2
    c2 = c1 + payload_len
    msg_payload = message[c1:c2]
    return msg_type, msg_nickname, msg_room_name, msg_payload


def msg_composer(msg_type, nickname="#Empty", room_id=0, payload="#Empty"):
    msg_type = str(msg_type)
    tmp = len(nickname)
    nickname_len = str(tmp) if tmp > 9 else f"0{tmp}"
    tmp = len(str(room_id))
    room_id_len = str(tmp) if tmp > 9 else f"0{tmp}"
    tmp = len(payload)
    payload_len = str(tmp) if tmp > 9 else f"0{tmp}"
    return "".join(
        [
            msg_type,
            nickname_len,
            room_id_len,
            payload_len,
            nickname,
            str(room_id),
            payload,
        ]
    )
