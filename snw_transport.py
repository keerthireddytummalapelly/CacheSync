from socket import *

BUFFER_SIZE = 1024   
                            
# Send file contents 
def sendFile(socket, filePath, ip, port, address, source):
    try:
        with open(filePath, 'rb') as file:
            data = file.read()
        file.close()    
        msg = "LEN:" + str(len(data))
        if source == "client":         
            socket.sendto(msg.encode(),(ip, port))
        else:
            socket.sendto(msg.encode(),address)    
        with open(filePath, 'rb') as file:
            while True:
                data = file.read(1000)
                if not data:
                    break   
                if source == "client":
                    socket.sendto(data, (ip, port))
                else:
                    socket.sendto(data, address)
                try:
                    # Set socket timeout to 1s
                    socket.settimeout(1)  
                    acknowledgment, address = socket.recvfrom(BUFFER_SIZE)
                    acknowledgment = acknowledgment.decode()
                    if acknowledgment.upper() == "FIN" and source == "client":
                        print("Server response: File successfully uploaded")  
                    # Unset socket timeout    
                    socket.settimeout(None)      
                except socket.timeout:
                    # Unset socket timeout
                    socket.settimeout(None) 
                    print("Did not receive ACK. Terminating.") 
                    raise socket.timeout()        
        file.close()
    # If file not found     
    except IOError:
        raise IOError       

# Receive file content 
def receiveFile(socket, filePath, length):
    length_of_data_received = 0
    received_data = ""
    try:
        # Set socket timeout to 1s
        socket.settimeout(1)
        data, address = socket.recvfrom(BUFFER_SIZE)
        received_data += data.decode()
        length_of_data_received += len(data)
        socket.sendto("ACK".encode(), address)
        # Unset socket timeout
        socket.settimeout(None) 
    # If timeout occurs    
    except socket.timeout:
        # Unset socket timeout
        socket.settimeout(None)
        print("Did not receive data. Terminating.")
        raise socket.timeout()     
    while True:
        try:
            # Set socket timeout to 1s
            socket.settimeout(1)
            data, address = socket.recvfrom(BUFFER_SIZE)
            received_data += data.decode()   
            length_of_data_received += len(data)
            if length == length_of_data_received:
                acknowledgment = "FIN"
                acknowledgment = acknowledgment.encode()
                socket.sendto(acknowledgment, address)
                break 
            else:
                acknowledgment = "ACK"
                acknowledgment = acknowledgment.encode()
                socket.sendto(acknowledgment, address) 
            # Unset socket timeout    
            socket.settimeout(None)
        # If timeout occurs         
        except socket.timeout:
            # Unset socket timeout
            socket.settimeout(None)
            print("Data transmission terminated prematurely")
            raise socket.timeout() 
    with open(filePath, 'wb') as file:  
        file.write(received_data.encode())                           
    file.close()