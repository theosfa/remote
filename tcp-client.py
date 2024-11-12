import socket
from pathlib import Path
target_host = "0.0.0.0"
target_port = 9998

def sendfile(client, file: str) -> int:
    # Make the path absolute
    path = Path(file).expanduser().resolve()
    print(path)
    # The size of a file to send
    size = path.stat().st_size
    
    # The number of bytes sent
    offset = 0
    
    with path.open("rb") as f:
        while size > 0:
            bytes_read = f.read(min(size, 4096))
            client.send(bytes_read)
            
            size -= len(bytes_read)
            offset += len(bytes_read)

    return offset

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((target_host, target_port))

client.send(b"GET / HTTP/1.1\r\nHost: google.1com\r\n\r\n")
# with open("text.txt", "w") as f:
#     i = 0
#     while i < 10:
#         f.write("hi")
#         i+=1
path = Path("text.txt").expanduser().resolve()
print(path)
size = path.stat().st_size
print(size)
f = open(path, "rb")
while size > 0:
    bytes_read = f.read(min(size, 4096))
    client.send(bytes_read)
    
    size -= len(bytes_read)
# client.sendfile(f)

# offset = sendfile(client, "text.txt")

response = client.recv(4096)

print(response.decode())
client.close()

