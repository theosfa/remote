# import socket

# target_host = "0.0.0.0"
# target_port = 9998

# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# client.connect((target_host, target_port))

# client.send(b"GET / HTTP/1.1\r\nHost: google.1com\r\n\r\n")
with open("text.txt", "w") as f:
    i = 0
    while i < 10:
        f.write("hi")
        i+=1


# response = client.recv(4096)

# print(response.decode())
# client.close()