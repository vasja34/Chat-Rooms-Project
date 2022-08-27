# Chat Rooms Project

> Chat Rooms is an exercise for Python Software Development workshop. (Based on [PySimpleGUI](https://github.com/PySimpleGUI) framework)

## Description

Chat Rooms is basic asynchronous TCP/IP app. The  chat server creates a server socket, binds it to a port and listens for incoming connections. The chat server allows multiple clients to connect to it and chat with each other in different rooms.

* The server receives a message from a client, broadcasts it to all clients, and then sends an event to the GUI.
* The server accepts new clients and starts a new thread for each one. It also stores the client's information in a dictionary called status_dict.
* The server has two loops, one for accepting new clients and another for brodcasting the messages. The first loop continuously accepts new clients until MAX_CLIENTS is reached.
* Initialy all clients are joined to the room called "Lobby".  A server broadcasts the message to everyone else in the room.

## Installation

There is none :) just download the files from a release and run it.

## Requirements

```shell
pip install PySimpleGUI
```

## Run

```shell
$ python chat_server_ui.py

$ python chat_client_ui.py
$ python chat_client_ui.py
...
```

## Screenshots

- Chat Client

  ![Chat Client](screenshots/Client.png?raw=true)


- Chat Server

  ![Chat Server](screenshots/Server.png)


- Clients Status

  ![Chat Status](screenshots/Status.png)

## Author

Vadim M - vasja34@gmail.com

## Credits

- GitHub: [PySimpleGUI](https://github.com/PySimpleGUI)
- Website: [PySimpleGUI.org](https://PySimpleGUI.org)

## License

This software is licensed under the [MIT](LICENSE) License.
