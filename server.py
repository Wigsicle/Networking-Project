import socket
import threading
        
        
def UsernameValidator(username, client_names):
    for name in client_names.values():
        if name == username:
            return False
    return True

        
# Function to handle client connections
def handle_client(client_socket, clients, client_names):
    # send welcome msg to new chatter, broadcast newcomer msg to all other chatters
    for client in clients:
        if client != client_socket:
            client.sendall(f"[{client_names[client_socket]} joined]".encode('utf-8'))
        if client == client_socket:
            client.sendall(f"[Welcome {client_names[client_socket]}!]".encode('utf-8'))
            
    # loops to check for new message input from clients
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            # Receive @quit message from client
            if message == "@quit":
                for client in clients:
                    if client != client_socket:
                        client.sendall(f"[{client_names[client_socket]} exited]".encode('utf-8'))
                break
            # Receive @names message from client
            if message == "@names":
                namesMessage = "[Connected users: "
                firstName = True
                for client in clients:
                    if firstName == True:
                        namesMessage = namesMessage.__add__(f"{client_names[client]}")
                        firstName = False
                    else:
                        namesMessage = namesMessage.__add__(f", {client_names[client]}")
                namesMessage = namesMessage.__add__("]")
                client_socket.sendall(namesMessage.encode('utf-8'))
            # Receive normal message from client
            elif message:
                # Broadcast message to all clients
                for client in clients:
                    if client != client_socket:
                        client.sendall(f"[{client_names[client_socket]}]: {message}".encode('utf-8'))
        except Exception as e:
            print(f"Error: {e}")
            break

    # Remove client from list and close connection
    clients.remove(client_socket)
    client_socket.close()
    del client_names[client_socket]
    

# Main function
def main():
    # Server configuration
    host = 'localhost'
    port = 8888

    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"[*] Listening on {host}:{port}")

    clients = []
    client_names = {}

    while True:
        # Accept client connection
        client_socket, addr = server_socket.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")

        isUsernameUnique = False
        while isUsernameUnique == False:
            # Prompt client for username
            client_socket.sendall("Enter your name: ".encode('utf-8'))
            username = client_socket.recv(1024).decode('utf-8').strip()
            isUsernameUnique = UsernameValidator(username, client_names)
            if isUsernameUnique == False:
                client_socket.sendall("[Username has already been used. Please enter another name.]".encode('utf-8'))

        # add new client username to list of clients names if valid
        client_names[client_socket] = username
        # Add client to list
        clients.append(client_socket)

        # Create thread to handle client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, clients, client_names))
        client_thread.start()

    server_socket.close()


if __name__ == "__main__":
    main()