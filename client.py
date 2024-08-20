import os
import sys
import snw_transport
import tcp_transport
from socket import *
from datetime import datetime

BUFFER_SIZE = 1024

def client(serverIP, serverPort, cacheIP, cachePort, command, protocol):
    try:
        cmd, fileName, filePath = tcp_transport.splitCommand(command)  
        # Invoke tcp protocol
        if protocol.upper() == "TCP":
            clientSocket = socket(AF_INET, SOCK_STREAM)
            # Upload file to server
            if cmd.upper() == "PUT":  
                # Connect to server
                clientSocket.connect((serverIP, serverPort))
                clientSocket.send(command.encode())   
                # Send file contents to server 
                try:  
                    tcp_transport.sendFile(clientSocket, filePath)
                    clientSocket.shutdown(SHUT_WR) 
                    print("Awaiting server response.")     
                    msg = clientSocket.recv(BUFFER_SIZE)  
                    print("Server response: ", msg.decode())
                # If file not found send error message to server    
                except IOError:
                    clientSocket.send("error:File not found at client. Terminating".encode())
                    print("File not found. Terminating. \nPlease specify complete path")     
            # Download file from server/cache    
            elif cmd.upper() == "GET":   
                # Connect to cache
                clientSocket.connect((cacheIP, cachePort))
                clientSocket.send(command.encode())  
                path = os.path.join(os.getcwd(), "client_files", filePath)
                tcp_transport.receiveFile(clientSocket, filePath)  
            else:
                print("Invalid command")    
            clientSocket.close()
        # Invoke udp protocol    
        elif protocol.upper() == "SNW":
            clientSocket = socket(AF_INET, SOCK_DGRAM)
            # Upload file to server
            if cmd.upper() == "PUT":  
                # Send command to server
                clientSocket.sendto(command.encode(),(serverIP, serverPort))
                # If file exists at client_files
                try:  
                    # Send file to server
                    snw_transport.sendFile(clientSocket, filePath, serverIP, serverPort, None, "client")   
                # If file doesn't exists at client_files    
                except IOError:
                    clientSocket.sendto("LEN:0".encode(),(serverIP,serverPort))
                    print("File not found at client. Terminating. \nPlease specify complete path") 
                # If timeout occurs              
                except socket.timeout:
                    pass  
            # Download file from cache/server         
            elif cmd.upper() == "GET":
                # Send command to cache
                clientSocket.sendto(command.encode(),(cacheIP, cachePort)) 
                try:   
                    msg, address = clientSocket.recvfrom(BUFFER_SIZE)
                    msg = msg.decode().split(":")[1]
                    length = int(msg)
                    filePath = os.path.join(os.getcwd(), "client_files", fileName)
                    if length !=0 :
                        # Receive file from server/cache
                        snw_transport.receiveFile(clientSocket, filePath, length) 
                except socket.timeout:
                    print("Did not receive data. Terminating.") 
                msg, address = clientSocket.recvfrom(BUFFER_SIZE)
                print(msg.decode())    
            else:
                print("Invalid command")     
            clientSocket.settimeout(None)    
            clientSocket.close()    
        else:
            print("Invalid protocol")   
    except Exception:
        print("Invalid command")           
# Read commandline inputs
serverIP = sys.argv[1]
serverPort = int(sys.argv[2])
cacheIP = sys.argv[3]
cachePort = int(sys.argv[4])
protocol = sys.argv[5]

# Create folder 'client_files' to store the files at client end
if not os.path.exists("client_files"):
    os.makedirs("client_files")

while True:
    # Read input commands  
    command = input("Enter command: ")
    # Terminate the program on quit    
    if command.upper() == 'QUIT':
        sys.exit(1) 

    client(serverIP, serverPort, cacheIP, cachePort, command, protocol)
    
   

