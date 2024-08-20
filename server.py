import os
import sys
import snw_transport
import tcp_transport
from socket import *

BUFFER_SIZE = 1024

def server(serverPort, protocol): 
    # Invoke tcp protocol
    if protocol.upper() == 'TCP': 
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind(('', serverPort))
        serverSocket.listen(1)
        print("Server listening on port", serverPort)
        print("Awaiting connection...")
        while True:
            # Accept connection from client/cache 
            clientSocket, address = serverSocket.accept()
            command = clientSocket.recv(BUFFER_SIZE).decode()
            cmd, fileName, filePath = tcp_transport.splitCommand(command)
            # Upload file content
            if cmd.upper() == "PUT":
                filePath = os.path.join(os.getcwd(), "server_files", fileName)
                # filePath = filePath+ "\\" + fileName
                tcp_transport.receiveFile(clientSocket, filePath)
                msg = "File successfully uploaded" 
                clientSocket.send(msg.encode()) 
            # Download file content    
            elif cmd.upper() == "GET":
                filePath = os.path.join(os.getcwd(), "server_files", fileName)
                try:
                    tcp_transport.sendFile(clientSocket, filePath) 
                except IOError:
                    clientSocket.send("error:Server response: File not found at server. Terminating.".encode())
            clientSocket.close()
    # Invoke udp protocol        
    elif protocol.upper() == "SNW":
        serverSocket = socket(AF_INET, SOCK_DGRAM)
        serverSocket.bind(('', serverPort))
        print("Server listening on port:", serverPort)
        while True:
            # Receive command
            command, address = serverSocket.recvfrom(BUFFER_SIZE)
            cmd, fileName, filePath = tcp_transport.splitCommand(command.decode())
            # Upload file to server
            if cmd.upper() == "PUT":
                try:
                    msg, address = serverSocket.recvfrom(BUFFER_SIZE)
                    msg = msg.decode().split(":")[1]
                    length = int(msg)
                    if length != 0: 
                        filePath = os.path.join(os.getcwd(), "server_files", fileName)
                        # Receive file from client
                        snw_transport.receiveFile(serverSocket, filePath, length)
                except socket.timeout:
                    continue
            #  Download file from server        
            elif cmd.upper() == "GET":
                # If requested file exists at server_files
                try:
                    # Send file to cache 
                    filePath = os.path.join(os.getcwd(), "server_files", fileName)
                    snw_transport.sendFile(serverSocket, filePath, None, None, address, "server") 
                # If requested file doesn't exists at server_files
                except IOError:
                    serverSocket.sendto("LEN:0".encode(),address)
                    print("File not found at server. Terminating.") 
                # If timeout occurs      
                except socket.timeout: 
                    print("Did not receive ACK. Terminating.")         
               
            serverSocket.settimeout(None)
           
    else:
        print("Invalid protocol")
       

# Read commandline inputs
serverPort = int(sys.argv[1])
protocol = sys.argv[2]

# Create folder 'server_files' to store the files at server end
if not os.path.exists("server_files"):
    os.makedirs("server_files") 

server(serverPort, protocol)


