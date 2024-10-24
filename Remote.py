import socket
import shlex
import subprocess
import sys
import threading
import secrets

__all__ = ["Remote"]

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
            upload: str | None = None,
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
        self.upload = upload
        self.buffer = buffer

        self.socket = socket.socket(socket.AF_INET6 if self.ip6 else socket.AF_INET,
                                    PROTOCOL[self.protocol])
        
        self.socket.setsockopt(socket.SOL_SOCKET,
                               socket.SO_REUSEADDR, 1)

        

    def start(self):
        if self.usage:
            self.listen()
        else:
            self.connect()
    
    def connect(self) -> None:
        self.socket.connect(self.host, self.port)

        if self.buffer:
            self.socket.send(self.buffer)
        
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
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()
    
    def handle(self, client_socket):
        if self.execute:
            output = execute(self.execute)
            client_socket.send(output.encode())
        elif self.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(self.bufsize)
                if data:
                    file_buffer += data
                else:
                    break
                with open(self.upload, 'wb') as f:
                    f.write(file_buffer)
                    client_socket.sendfile(f)
                message = f'Saved file {self.upload}'
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