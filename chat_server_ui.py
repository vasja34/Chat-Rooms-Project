# -*- coding: utf-8 -*-
"""
Dependencies: PySimpleGUI:  https://pypi.org/project/PySimpleGUI/
                            pip install PySimpleGUI

Example:
        $ python "C:/Users/User/Documents/Python/Chat-Rooms-Project/chat_server_ui.py"

@Author: Vadim Moldavsky   vasja34@gmail.com
@Date:   17/08/2022
"""

import datetime
import socket
import sys
import threading
from pathlib import Path

import PySimpleGUI as sg

from chat_protocol import *


def broadcast(message, clients):
    """
    It takes a message and a list of clients, and sends the message to each client in the list

    :param message: The message to be sent to all clients. The message is already encoded
    :param clients: A list of all the clients connected to the server
    """
    for client in clients:
        client.send(message)


def handle(client, clients, nicknames, addresses, status_dict, window):
    """
    It receives a message from a client, broadcasts it to all clients, and then sends an event to the
    GUI.

    :param client: the client socket
    :param clients: list of clients
    :param nicknames: list of nicknames
    :param addresses: list of tuples of (ip, port)
    :param status_dict: a dictionary that stores the status of each client
    :param window: the tkinter window
    """
    while True:
        idx = clients.index(client)
        nick = nicknames[idx]
        time_stamp = str(datetime.datetime.now())[:19]
        try:
            message = client.recv(BUFSIZE)  # encoded
            broadcast(message, clients)
            # sent event to gui
            window.write_event_value(
                "-BROADCAST_EVENT-",
                (
                    time_stamp,
                    threading.current_thread().name,
                    nick,
                    message.decode("utf-8"),
                ),
            )
        except Exception:
            clients.remove(client)
            client.close()
            nick = nicknames.pop(idx)
            addr = addresses[idx]
            del status_dict[addr]
            addresses.remove(addr)

            msg = "removed from chat"
            # sent event to gui
            window.write_event_value(
                "-Exception_Event-",
                (
                    time_stamp,
                    threading.current_thread().name,
                    nick,
                    msg,
                ),
            )
            break


def accept_new_client(server, clients, nicknames, addresses, status_dict, window):
    """
    It accepts new clients and starts a new thread for each one

    :param server: the socket object
    :param clients: a list of all the clients connected to the server
    :param nicknames: a list of nicknames of all clients
    :param addresses: a list of all the addresses of the clients
    :param status_dict: a dictionary that contains the client's nickname and the room they're in
    :param window: the window object
    """
    while True:
        if len(clients) < MAX_CLIENTS:
            time_stamp = str(datetime.datetime.now())[:19]
            client, address = server.accept()

            nick_request_msg = msg_composer(msg_type=GET_NICKNAME).encode("utf-8")
            client.send(nick_request_msg)
            response_msg = client.recv(BUFSIZE).decode("utf-8")
            _, msg_nickname, msg_room_name, _ = msg_parser(response_msg)

            nicknames.append(msg_nickname)
            clients.append(client)
            addresses.append(address)  # client.getsockname()
            status_dict[address] = [msg_nickname, msg_room_name]

            # ===========================================
            threading.Thread(  # Init 'handle' thread
                target=handle,
                args=(client, clients, nicknames, addresses, status_dict, window),
                daemon=True,
            ).start()
            # ===========================================
            message = msg_composer(
                msg_type=ENTER_ROOM,
                nickname=msg_nickname,
                room_id=rooms_id["Lobby"],
                payload=f"{msg_nickname} joined to the 'Lobby' !",
            ).encode("utf-8")
            broadcast(message, clients)

            window.write_event_value(
                "-ACCEPT_NEW_CLIENT-",
                (time_stamp, threading.current_thread().name, address, msg_nickname),
            )
        else:
            sg.cprint("WARNING   ", c="red on yellow", end="")
            sg.cprint(
                f"Num clients in chat achieved the max allowed: {MAX_CLIENTS}. The new clients will be refused !"
            )


def get_status(status_dict):
    """
    It creates a window with a tabbed layout.  The first tab is a tree element that shows the chat rooms
    and the users in each room.  The second tab is a table element that shows the users and the room
    they are in.

    :param status_dict: a dictionary of dictionaries.  The outer dictionary is keyed by the address of
    the client.  The inner dictionary is keyed by the name of the field.
    :return: A window object.
    """
    # treedata.Insert(parent, fullname, f, values=[], icon=folder_icon)
    tree_data = sg.TreeData()
    tree_data.Insert("", "Lobby", "🗫 Lobby", [""])
    tree_data.Insert("", "Private Room 1", "🗪 Private Room 1", [""])
    tree_data.Insert("", "Private Room 2", "🗪 Private Room 2", [""])
    tree_data.Insert("", "Private Room 3", "🗪 Private Room 3", [""])
    tree_data.Insert("", "Private Room 4", "🗪 Private Room 4", [""])
    tree_data.Insert("", "Private Room 5", "🗪 Private Room 5", [""])
    tree_data.Insert("", "Private Room 6", "🗪 Private Room 6", [""])
    tree_data.Insert("", "Private Room 7", "🗪 Private Room 7", [""])
    tree_data.Insert("", "Private Room 8", "🗪 Private Room 8", [""])
    tree_data.Insert("", "Private Room 9", "🗪 Private Room 9", [""])

    table_data = []
    user_idx = 0
    room_idx = 1
    tab = 4
    # status_dict[addresses[idx]] = [msg_nickname, msg_room_name]
    for addr, val in status_dict.items():
        nick = val[user_idx]
        room = val[room_idx]
        icon = "🗫" if room == "Lobby" else "🗪"
        table_data.append([f"😎 {nick}", f"{icon}  {room}"])
        tree_data.Insert(room, nick, f"{' '*tab}😎 {nick}", [f"🖥 {addr}"])

    sg.theme("DarkAmber")
    users_layout = [
        [sg.Text("Users joined to the chat rooms:")],
        [
            sg.Table(
                values=table_data,
                font="Franklin, 14",
                headings=["User", "Room"],
                max_col_width=15,
                auto_size_columns=True,
                # vertical_scroll_only=False,
                display_row_numbers=True,
                justification="left",
                right_click_selects=True,
                num_rows=30,
                key="-STATUS_USERS-",
                # selected_row_colors="red on yellow",
                enable_events=True,
                expand_x=True,
                expand_y=True,
                enable_click_events=False,
                tooltip="",
            ),
        ],
    ]

    rooms_layout = [
        [sg.Text("Chat rooms populated by users:")],
        [
            sg.Tree(
                data=tree_data,
                font="Franklin, 14",
                headings=["Address"],
                justification="left",
                auto_size_columns=True,
                select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                num_rows=20,
                col0_width=40,
                key="-STATUS_ROOMS-",
                show_expanded=False,
                enable_events=True,
                expand_x=True,
                expand_y=True,
            ),
        ],
    ]

    layout = [
        [sg.Titlebar("Clients Status")],
        [sg.TabGroup([[sg.Tab("Rooms", rooms_layout), sg.Tab("Users", users_layout)]])],
        [
            sg.Push(),
            sg.Button("Exit", size=(12, 1), key="-EXIT-"),
            sg.Push(),
        ],
    ]

    status_window = sg.Window(
        "", layout, modal=False, relative_location=(0, -100), finalize=True
    )
    return status_window


def main():
    """
    The main function of the chat server. It creates a server socket, binds it to a port and listens for
    incoming connections.
    """
    ############################################################
    # Server Socket  init
    ############################################################
    HOST = "127.0.0.1"  # 'localhost'
    PORT = 9090
    ADDR = (HOST, PORT)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen(MAX_CLIENTS)  # listens for MAX_CLIENTS active connections
    print("Server is running. Waiting for a connection...")

    ############################################################
    # Vars  init
    ############################################################
    clients, nicknames, addresses = [], [], []
    status_dict = {}

    ############################################################
    # PySimpleGUI  init
    ############################################################
    sg.theme("Black")

    layout = [
        [sg.Titlebar("Chat Server")],
        [sg.Text("Network Log")],
        [
            sg.Multiline(
                "Server Side Network Sniffing!\n\n",
                font="Franklin 11",
                no_scrollbar=True,
                size=(120, 30),
                horizontal_scroll=True,
                echo_stdout_stderr=True,
                reroute_stdout=True,
                # write_only=True,
                reroute_cprint=True,
                disabled=True,
                autoscroll=True,
                key="-OUTPUT-",
            ),
        ],
        [
            sg.Button("Status", key="-GET_STATUS-"),
            sg.Push(),
            sg.Button("Save Log As...", key="-SAVE_LOG-"),
            sg.Text(" "),
            sg.Button("Exit", size=(12, 1), key="-EXIT-"),
        ],
    ]

    main_window = sg.Window("", layout, finalize=True)
    status_window = None  # start with main_window open
    sg.cprint_set_output_destination(main_window, "-OUTPUT-")

    ############################################################
    # Init 'accept_new_client' thread
    ############################################################
    threading.Thread(
        target=accept_new_client,
        args=(
            server,
            clients,
            nicknames,
            addresses,
            status_dict,
            main_window,
        ),
        daemon=True,
    ).start()

    ############################################################
    # main loop
    ############################################################
    while True:
        # ===========================================
        window, event, values = sg.read_all_windows()
        # ===========================================
        if event in [sg.WIN_CLOSED, "-EXIT-"]:
            if window == status_window:  # if closing status_window, mark as closed
                window.close()
                status_window = None
            elif window == main_window:  # if closing main_window, exit program
                break

            # ============================
        if event == "-ACCEPT_NEW_CLIENT-":
            # ============================
            val = values[event]
            time_stamp = val[0]
            thread_ = val[1]
            address = val[2]
            nick = val[3]
            sg.cprint("accept_client()", c=("#FFFFFF", "#546393"), end="")
            sg.cprint(f"[{time_stamp}]", c=("#FFFFFF", "#7186c7"), end="")
            sg.cprint(f"[{thread_}]", c=("#FFFFFF", "#546393"), end="")
            sg.cprint(
                f"[New client connected with address: {address}]",
                c=("#FFFFFF", "#7186c7"),
                end="",
            )
            sg.cprint(f"[Nickname of the client is: {nick}]", c=("#FFFFFF", "#546393"))

            # ============================
        if event == "-BROADCAST_EVENT-":
            # ============================
            val = values[event]
            time_stamp = val[0]
            thread_ = val[1]
            nick = val[2]
            msg_type, msg_nickname, msg_room_name, msg_payload = msg_parser(val[3])
            sg.cprint("broadcast()     ", colors="white on green", end="")
            if msg_type in [EXIT_ROOM, ENTER_ROOM]:
                bg_color1 = "#ffd258"
                bg_color2 = "#cca746"
                txt_color = "#000000"
            else:
                bg_color1 = "#4d4d4d"
                bg_color2 = "#737373"
                txt_color = "#FFFFFF"
            # end if
            sg.cprint(f"[{time_stamp}]", c=(txt_color, bg_color1), end="")
            sg.cprint(f"[{thread_}]", c=(txt_color, bg_color2), end="")
            sg.cprint(
                f"[<{msg_type}><{msg_nickname}><{msg_room_name}><{msg_payload}>]",
                c=(txt_color, bg_color1),
            )

            # update status_dict
            idx = nicknames.index(msg_nickname)
            status_dict[addresses[idx]] = [msg_nickname, msg_room_name]

            # ============================
        if event == "-GET_STATUS-" and not status_window:
            # ============================
            status_window = get_status(status_dict)

        # ============================
        if event == "-Exception_Event-":
            # ============================
            val = values[event]
            time_stamp = val[0]
            thread_ = val[1]
            nick = val[2]
            msg = val[3]
            sg.cprint("Exception_Event ", c=("#FFFFFF", "#800080"), end="")
            sg.cprint(f"[{time_stamp}]", c=("#FFFFFF", "#cc00cc"), end="")
            sg.cprint(f"[{thread_}]", c=("#FFFFFF", "#800080"), end="")
            sg.cprint(f"[{nick} {msg}]", c=("#FFFFFF", "#cc00cc"))

            # ============================
        if event == "-SAVE_LOG-":
            # ============================
            if fname := sg.popup_get_file(
                "Please enter a log-file name",
                save_as=True,
                default_extension="txt",
                file_types=(("Text Files", "*.txt"),),
                no_window=True,
            ):
                Path(fname).write_text(values["-OUTPUT-"])

    ############################################################
    # finalize Server Socket & GUI
    ############################################################
    # server.close()
    window.close()
    sys.exit()


if __name__ == "__main__":
    main()
