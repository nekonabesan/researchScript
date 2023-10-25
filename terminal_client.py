import socket
target_host="ev3dev.local"
target_port=50000
client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((target_host, target_port))
while True:
    com=input("command: ")
    client.send(com.encode('utf-8'))
    response = client.recv(4096)
    print(response.decode('utf-8'))