import os
import sys
import tcp_transport
import snw_transport    
from socket import *

BUFFER_SIZE = 1024

def cache(serverIP, serverPort, cachePort, protocol): 
    # Invoke tcp protocol 
    if protocol.upper() == "TCP":
        cacheSocket = socket(AF_INET, SOCK_STREAM)
        cacheSocket.bind(('', cachePort))
        cacheSocket.listen(1)
        print("Cache listening on port", cachePort)
        print("Awaiting connection...")
        while True:
            clientSocket, address = cacheSocket.accept()
            command = clientSocket.recv(BUFFER_SIZE)
            cmd, filePath, fileName = tcp_transport.splitCommand(command.decode()) 
            filePath = os.path.join(os.getcwd(), "cache_files", fileName)
            # If file found at cache_files, send file content from cache
            try:
                tcp_transport.sendFile(clientSocket, filePath)
                msg = "msg:Server response: File delivered from cache" 
                clientSocket.send(msg.encode())
            # Send file content from server    
            except IOError:    
                serverSocket = socket(AF_INET, SOCK_STREAM)
                # Connect to server
                serverSocket.connect((serverIP, serverPort))
                serverSocket.send(command)
                try:
                    path = os.path.join(os.getcwd(), "cache_files", fileName) 
                    tcp_transport.receiveFile(serverSocket, path)  
                    tcp_transport.sendFile(clientSocket, filePath)
                    msg = "msg:Server response: File delivered from origin"   
                    clientSocket.send(msg.encode()) 
                except IOError:
                    clientSocket.send("error:Server response: File not found at server. Terminating.".encode())
                serverSocket.close()       
            clientSocket.close()
    # Invoke udp protocol    
    elif protocol.upper() == "SNW":
        cacheSocket = socket(AF_INET, SOCK_DGRAM)
        cacheSocket.bind(('', cachePort))
        print("Cache listening on port:", cachePort)
        while True:
            # Receive command from client
            command, cache_address = cacheSocket.recvfrom(BUFFER_SIZE)
            cmd, fileName, filePath = tcp_transport.splitCommand(command.decode())
            filePath = os.path.join(os.getcwd(), "cache_files", fileName)  
            # If file exists at cache_files
            try:
                # cacheSocket.settimeout(1)
                # Send file to client
                snw_transport.sendFile(cacheSocket, filePath, None, None, cache_address, "cache")
                # cacheSocket.settimeout(None)
                msg = "Server response: File delivered from cache" 
                cacheSocket.sendto(msg.encode(), cache_address)  
            # If file doesn't exists at cache_files     
            except IOError: 
                serverSocket = socket(AF_INET, SOCK_DGRAM)  
                serverSocket.sendto(command,(serverIP, serverPort)) 
                path = os.path.join(os.getcwd(), "cache_files", fileName) 
                try:
                    msg, address = serverSocket.recvfrom(BUFFER_SIZE)
                    msg = msg.decode().split(":")[1]
                    length = int(msg)
                    if length != 0:
                        # Receive file from server
                        snw_transport.receiveFile(serverSocket, path ,length) 
                except socket.timeout:
                    continue
                serverSocket.settimeout(None)
                serverSocket.close()     
                try :    
                    # Send file to client
                    snw_transport.sendFile(cacheSocket, filePath, None, None, cache_address, "cache")
                    msg = "Server response: File delivered from origin"   
                    cacheSocket.sendto(msg.encode(), cache_address)
                 # If file doesn't exists at server_files 
                except IOError:
                    cacheSocket.sendto("LEN:0".encode(), cache_address)
                    cacheSocket.sendto("Server response: File not found at server. Terminating.".encode(), cache_address)     
                except socket.timeout:
                    continue  
                cacheSocket.settimeout(None)
             # If timeout occurs         
            except socket.timeout:
                cacheSocket.settimeout(None)
                print("Did not receive ACK. Terminating.")        
            cacheSocket.settimeout(None)      
    else:
        print("Invalid protocol")
# Read commandline inputs
cachePort = int(sys.argv[1])
serverIP = sys.argv[2]
serverPort = int(sys.argv[3])
protocol = sys.argv[4]

# Create folder 'cache_files' to store files the at cache end
if not os.path.exists("cache_files"):
    os.makedirs("cache_files")

cache(serverIP, serverPort, cachePort, protocol)

