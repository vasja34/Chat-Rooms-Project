# -*- coding: utf-8 -*-
"""
Dependencies: PySimpleGUI:  https://pypi.org/project/PySimpleGUI/
                            pip install PySimpleGUI

Example:
        $ python "C:/Users/User/Documents/Python/Chat-Rooms-Project/chat_client_ui.py"

@Author: Vadim Moldavsky   vasja34@gmail.com
@Date:   17/08/2022
"""

import datetime
import random
import socket
import sys
import threading
from pathlib import Path

import PySimpleGUI as sg

from chat_protocol import *


def receive(client, window, nickname):
    """
    It receives messages from the server and prints them to the GUI

    :param client: socket.socket
    :param window: the GUI window
    :param nickname: the nickname of the client
    """
    while True:
        time_stamp = str(datetime.datetime.now())[:19]
        try:
            message = client.recv(BUFSIZE).decode("utf-8")
            msg_type, msg_nickname, msg_room_name, msg_payload = msg_parser(message)
            if msg_type == GET_NICKNAME:
                nick_message = msg_composer(
                    msg_type=GET_NICKNAME,
                    nickname=nickname,
                    room_id=rooms_id[current_room_name],
                ).encode("utf-8")
                client.send(nick_message)
                # send nickname from client to server by request from accept_new_client()
            else:
                window.write_event_value(
                    "-RECEIVE_THREAD-",
                    (
                        time_stamp,
                        threading.current_thread().name,
                        msg_type,
                        msg_nickname,
                        msg_room_name,
                        msg_payload,
                    ),
                )
                # Data sent as a tuple
        except ConnectionAbortedError:
            time_stamp = str(datetime.datetime.now())[:19]
            window.write_event_value(
                "-ConnectionAbortedError-",
                (
                    time_stamp,
                    threading.current_thread().name,
                ),
            )
        except Exception:
            time_stamp = str(datetime.datetime.now())[:19]
            window.write_event_value(
                "-SocketError-",
                (
                    time_stamp,
                    threading.current_thread().name,
                ),
            )


def main():
    """
    It's a chat client that uses a socket to communicate with a server.
    The server is not included in this code. The chat server is a separate program: 'chat_server_ui.py'.
    The chat server allows multiple clients to connect to it and chat with each other in different rooms.
    """
    ############################################################
    # Client Socket  init
    ############################################################
    HOST = "127.0.0.1"  # 'localhost'
    PORT = 9090
    ADDR = (HOST, PORT)  # server_address
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    # Create a TCP/IP socket
    # client = socket.create_connection(ADDR)

    ############################################################
    # Choose Nickname
    ############################################################
    global current_room_name
    current_room_name = "Lobby"

    # nickname = f"Nick_{random.randint(1,1000)}"
    nick_condition = False
    nickname = ""

    while not nick_condition:
        nickname = sg.popup_get_text(
            "Choose your NICKNAME for this chat-session\nNICKNAME must contain [1..10] letters only\n'Cancel' with choose a random nick for you",
            "Login",
        )
        if nickname is None:  # choose a random nick
            nick_len = random.randint(1, 10)
            rand_chars = [
                chr(random.randint(65, 90)) for _ in range(nick_len)
            ]  # Upper ASCII
            nickname = f"{''.join(rand_chars)}"
            nick_condition = True
        elif nickname.isalpha():
            # NOTE: nickname might be not unique
            nick_condition = True

    ############################################################
    # PySimpleGUI   init
    ############################################################
    sg.theme("BlueMono")
    current_room_id = rooms_id[current_room_name]

    layout = [
        [sg.Titlebar("Chat Client")],
        [
            sg.Text(
                f"Nickname: {nickname}", font="Franklin 12 bold", text_color="blue"
            ),
            sg.Push(),
            sg.Combo(  # sg.Combo sg.OptionMenu
                [
                    "Lobby",
                    "Private Room 1",
                    "Private Room 2",
                    "Private Room 3",
                    "Private Room 4",
                    "Private Room 5",
                    "Private Room 6",
                    "Private Room 7",
                    "Private Room 8",
                    "Private Room 9",
                ],
                font="Franklin 12",
                size=(13, 10),
                default_value="Lobby",
                enable_events=True,
                readonly=True,
                # background_color='#FFFFFF',
                key="-ROOMS_OPTION-",
            ),
        ],
        [
            sg.Multiline(
                f" Hello {nickname}!\n Welcome to the lobby chat!\n\n",
                font="Franklin 11",
                no_scrollbar=True,
                size=(50, 20),
                text_color="black",
                background_color=rooms_color[current_room_name],
                horizontal_scroll=True,
                autoscroll=True,
                echo_stdout_stderr=True,
                reroute_stdout=True,
                # write_only=True,
                reroute_cprint=True,
                disabled=True,
                # enter_submits=True,
                key="-OUTPUT-",
            ),
        ],
        [
            sg.Multiline(
                font="Franklin 11",
                no_scrollbar=True,
                size=(50, 5),
                horizontal_scroll=False,
                autoscroll=True,
                key="-INPUT-",
            )
        ],
        [
            sg.Button("Send", size=(12, 1), key="-SEND-", button_color="#219F94"),
            sg.Push(),
            sg.Button("Save Chat As...", key="-SAVE_LOG-"),
            sg.Button("Exit", size=(12, 1), key="-EXIT-"),
        ],
    ]
    window = sg.Window("", layout, finalize=True)
    sg.cprint_set_output_destination(window, "-OUTPUT-")

    ############################################################
    # Init 'receive' thread
    ############################################################
    threading.Thread(
        target=receive,
        args=(
            client,
            window,
            nickname,
        ),
        daemon=True,
    ).start()

    while True:
        # ============================
        event, values = window.read()
        # ============================
        if event in [sg.WIN_CLOSED, "-EXIT-"]:
            break

            # ============================
        if event == "-ROOMS_OPTION-":
            # ============================
            room_name = values["-ROOMS_OPTION-"]
            if room_name != current_room_name:
                message = msg_composer(
                    msg_type=EXIT_ROOM,
                    nickname=nickname,
                    room_id=rooms_id[current_room_name],  # the prev room
                    payload=f"left '{current_room_name}'",
                ).encode("utf-8")
                client.send(message)

                current_room_name = room_name  # update current_room_name

                bg_color = rooms_color[current_room_name]
                window["-OUTPUT-"].print("\n")  # align prev output
                # change  background_color
                window["-OUTPUT-"].print(
                    "=" * 40,
                    "\n",
                    f"Hello {nickname}!\n Welcome to the '{current_room_name}' chat!\n\n",
                    background_color=bg_color,
                )
                sg.cprint("")

                message = msg_composer(
                    msg_type=ENTER_ROOM,
                    nickname=nickname,
                    room_id=rooms_id[current_room_name],  # the new room
                    payload=f"joined to '{current_room_name}'",
                ).encode("utf-8")
                client.send(message)

            # ============================
        if event == "-RECEIVE_THREAD-":
            # ============================
            val = values[event]
            time_stamp = val[0]
            thread_ = val[1]
            msg_type = val[2]
            msg_nickname = val[3]
            msg_room_name = val[4]
            msg_payload = val[5]
            # print messages from the current_room_name only!
            if msg_room_name == current_room_name:
                bg_color = rooms_color[msg_room_name]
                if msg_type == EXIT_ROOM:
                    bg_color = "#ffd258"
                    sg.cprint(
                        f"[{time_stamp}]  {msg_nickname} left '{msg_room_name}'",
                        c=("#000000", bg_color),
                    )
                elif msg_type == ENTER_ROOM:
                    bg_color = "#ffd258"
                    sg.cprint(
                        f"[{time_stamp}]  {msg_nickname} joined to '{msg_room_name}'",
                        c=("#000000", bg_color),
                    )
                elif msg_type == CHAT_CONVERSATION:
                    bg_color = rooms_color[msg_room_name]
                    just_ = "l" if msg_nickname == nickname else "r"  # left / right
                    sg.cprint(
                        f"[{time_stamp}]  {msg_nickname} wrote:",
                        c=("#000000", bg_color),
                        justification=just_,  # left / right,
                    )
                    sg.cprint(
                        f"{msg_payload}\n",
                        c=("#000000", bg_color),
                        justification=just_,
                    )

        # window["-OUTPUT-"].print(
        #     "\n",
        #     f"Hello {nickname}!\n Welcome to the '{current_room_name}' chat!\n\n",
        #     background_color=bg_color,
        # )

        # ============================
        if event == "-SEND-":
            # ============================
            current_room_id = rooms_id[current_room_name]
            payload_ = f"{values['-INPUT-']}"
            if len(payload_) > MAX_PAYLOAD:
                sg.popup_error(
                    f"Message exceed {MAX_PAYLOAD} characters!",
                    title="Error: Message Length Violation",
                )
                # Shows red error button
            else:
                message = msg_composer(
                    msg_type=CHAT_CONVERSATION,
                    nickname=nickname,
                    room_id=current_room_id,
                    payload=payload_,
                ).encode("utf-8")
                client.send(message)
                window["-INPUT-"].update("")  # clean input prompt

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

            # ============================
        if event in ["-ConnectionAbortedError-", "-SocketError-"]:
            # ============================
            val = values[event]
            time_stamp = val[0]
            thread_ = val[1]
            sg.cprint("Data from Exception ", colors="yellow on red", end="")
            sg.cprint(f"[{time_stamp}]", c=("#FFFFFF", "#b20000"), end="")
            sg.cprint(f"[{thread_}]", c=("#FFFFFF", "#ff0000"), end="")
            sg.cprint(f"[{event}]", c=("#FFFFFF", "#b20000"))
            client.close()
            break

    ############################################################
    # finalize Socket & GUI
    ############################################################
    window.close()
    sys.exit()
    # trd_id._stop.set()


if __name__ == "__main__":
    main()
