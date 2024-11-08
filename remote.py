import threading
import secrets
import sys
import socket
import shlex
import subprocess
import sys
import secrets
from pathlib import Path
from datetime import date

from unet.flag import FlagParser, PositionalFlag, OptionFlag, Group

__all__ = ["remote-simple"]

PROTOCOL = {
    "udp" : socket.SOCK_DGRAM,
    "tcp" : socket.SOCK_STREAM
}

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd),
        stderr=subprocess.STDOUT)
    return output.decode()

class Remote:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, 
                               socket.SO_REUSEADDR, 1)

    def __init__(
            self,
            host: str | None = None,
            port: int = secrets.randbelow(0xffff),
            ip6: bool = False,
            listen: bool = False,
            protocol: str = "tcp",
            bufsize: int = 8912,
            command: bool = False,
            execute: str | None = None,
            send: bool = False,
            receive: bool = False,
            name: str | None = None,
            buffer: str = '',
    ) -> None:
        self.usage = listen
        self.protocol = protocol
        self.host = host
        self.port = port
        self.bufsize = bufsize
        self.ip6 = ip6
        self.command = command
        self.execute = execute
        self.name = name
        self.send = send
        self.receive = receive
        self.buffer = buffer

        self.socket = socket.socket(socket.AF_INET6 if self.ip6 else socket.AF_INET,
                                    PROTOCOL[self.protocol])
        
        self.socket.setsockopt(socket.SOL_SOCKET,
                               socket.SO_REUSEADDR, 1)

        

    def start(self):
        print(self.usage)
        if self.usage:
            self.listen()
        else:
            self.connect()
    
    def connect(self) -> None:
        self.socket.connect((self.host, self.port))

        if self.buffer:
            self.socket.send(self.buffer)
        print(self.send)
        if self.send:
            offset = self.sendfile(self.name)
            message = f'Sended file with {offset} bytes'
            print(message)
        elif self.receive:
            offset = self.receivefile(self.name)
            message = f'Received file with {offset} bytes'
            print(message)

        try:
            while True:
                recv_len = 1
                response = ''

                while recv_len:
                    data = self.socket.recv(self.bufsize)
                    recv_len = len(data)
                    response += data.decode()

                    if recv_len < self.bufsize:
                        break
                if response:
                    print(response)
                    buff = input('> ')
                    # buff += '\n'
                    self.socket.send(buff.encode())
        except KeyboardInterrupt:
            print('remote: User terminated')
    
    def listen(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print("Is ok?")
        while True:
            client_socket, client_address = self.socket.accept()
            print(f"[*] Accepted connection from {client_address[0]}: {client_address[1]}")
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()
            print("smth")
    
    def handle(self, client_socket):
        print("connected")
        if self.execute:
            output = execute(self.execute)
            client_socket.send(output.encode())
        elif self.send:
            offset = self.sendfile(self.name)
            message = f'Sended file with {offset} bytes'
            client_socket.send(message.encode())
        elif self.receive:
            offset = self.receivefile(self.name)
            message = f'Received file with {offset} bytes'
            client_socket.send(message.encode())
        elif self.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'unet: #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()

    def sendfile(self, file: str) -> int:
        # Make the path absolute
        path = Path(file).expanduser().resolve()
        print(path)
        # The size of a file to send
        size = path.stat().st_size
        
        # The number of bytes sent
        offset = 0
       
        with path.open("rb") as f:
            while size > 0:
                bytes_read = f.read(min(size, self.bufsize))
                self.socket.send(bytes_read)
                
                size -= len(bytes_read)
                offset += len(bytes_read)

        return offset

    def receivefile(self, file: str) -> int:
        if file:
            # Make the path absolute
            path = Path(file).expanduser().resolve()
        else:
            name = "unet_receive_" + f"{date.today()}" + "_" + self.host
            path = Path(name).expanduser().resolve()
        
        # The size of a file to receive
        size = 1
        
        # The number of bytes received
        offset = 0

        with path.open("wb") as f:
            while size > 0:
                data = self.socket.recv(self.bufsize)
                bytes_read = f.write(data)
                size = len(bytes_read)
                offset += len(bytes_read)

        return offset

REMOTE_FLAGS = {
    "host": PositionalFlag(
        help="host to connect to (default: 0.0.0.0)",
        nargs="?",
        type=str,
        default="0.0.0.0",
    ),
    "port": PositionalFlag(
        help="port to connect to (default: random)",
        nargs="?",
        type=int,
        default=secrets.randbelow(0xffff),
    ),
    "ipv6": OptionFlag(
        short="-6",
        long="--ip6",
        help="use IPv6",
        action="store_true",
        required=False,
        default=False,
    ),
    "listen": OptionFlag(
        short="-l",
        long="--listen",
        help="listen for incoming connections (default: connect)",
        action="store_true",
        required=False,
        default=False,
    ),
    "udp": OptionFlag(
        short="-u",
        long="--udp",
        help="use UDP (default: TCP)",
        action="store_true",
        required=False,
        default=False,
    ),
    "command": OptionFlag(
        short="-c",
        long="--command",
        help="command shell",
        action="store_true",
        required=False,
        default=False,
    ),
    "execute": OptionFlag(
        short="-e",
        long="--execute",
        help="execute the supplied command",
        type=str,
        required=False,
        default=None,
        metavar="<cmd>",
    ),
    "bufsize": OptionFlag(
        short="-b",
        long="--bufsize",
        help="changes bufsize (default: 8912)",
        type=int,
        required=False,
        default=8912,
        metavar="<bufsize>",
    ),
    "send": OptionFlag(
        short="-s",
        long="--send",
        help="send file, to specify name use -n/--name",
        action="store_true",
        required=False,
        default=False
    ),
    "receive": OptionFlag(
        short="-r",
        long="--receive",
        help="receive file, to specify name use -n/--name",
        action="store_true",
        required=False,
        default=False
    ),
    "name": OptionFlag(
        short="-n",
        long="--name",
        help="stores name for sending/receiving files (default: auto naming)",
        type=str,
        required=False,
        default=None,
        metavar="<file>",
    ),
    "examples": Group(
        description="\n".join([
            "unet remote-simple 192.168.1.108 5555 -l -c    # command shell",
            "unet remote-simple 192.168.1.108 5555 -l -u file.txt   # upload to file",
            "unet remote-simple 192.168.1.108 5555 -l -e cat /etc/passwd    # execute a command",
            "echo 'ABC' | unet remote-simple 192.168.1.108 135      # echo text to server port 135",
            "unet remote-simple # connect to 0.0.0.0 with random port",
        ]),
        arguments={},
    ),
}


def main(args: list[str]) -> None:
    parser = FlagParser(
        prog='remote-simple', description='make or wait for remote connections')
    parser.add_arguments(REMOTE_FLAGS)
    flags = parser.parse_args(args)

    if flags.listen:
        print(f"listening on {flags.host}:{flags.port}")
        buffer = ''
    else:
        print(f"connect to {flags.host}:{flags.port}")
        buffer = sys.stdin.read()
    
    protocol = "udp" if flags.udp else "tcp"

    remote = Remote(
        flags.host,
        flags.port,
        flags.ipv6,
        flags.listen,
        protocol,
        flags.bufsize,
        flags.command,
        flags.execute,
        flags.send,
        flags.receive,
        flags.name,
        buffer.encode(),
        )
    remote.start()