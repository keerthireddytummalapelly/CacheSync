import os
from socket import *

BUFFER_SIZE = 1024

# Send file content
def sendFile(socket, filePath):
    try:
        # Read file content
        with open(filePath, 'rb', 0) as file:
            data = file.read()
            # Send file content
            socket.sendall(data)      
        file.close()
    # If file not found    
    except IOError:
        raise IOError    

# Receive file content
def receiveFile(socket, filePath):
    errorOccured = False
    fileData = ""
    while True:
        # Receive file content
        data = socket.recv(BUFFER_SIZE).decode()
        if not data:
            break
        if "msg:" in data:
            data, msg = data.split("msg:", -1)
            print(msg.replace("msg:","")) 
        elif "error:" in data:
            print(data.replace("error:",""))
            errorOccured = True
            break
        fileData += data 
    if not errorOccured:       
        with open(filePath, 'wb') as file:            
            file.write(fileData.encode())
        file.close()

# Process the user input 
def splitCommand(command):
    cmd, filePath = command.split(' ', 1)  
    filePath = filePath.replace("\"", '')
    filePath = filePath.replace("\'", '')
    path = filePath    
    if '\\' in path:
        fileName = path.split('\\')[-1]
    elif "\\" in path:
        fileName = path.split('\\')[-1]  
    elif '/' in path:
        fileName = path.split('/')[-1] 
    elif "//" in path:
        fileName = path.split("//")[-1]
    else:
        if cmd.upper() == "PUT":
            fileName = filePath
            filePath = os.path.join(os.getcwd(), "client_files", fileName) 
        else:
            fileName = filePath                 
    return cmd, fileName, filePath    

    
         








