import socket
import threading
        
        
def UsernameValidator(username, client_names):
    for name in client_names.values():
        if name == username:
            return False
    return True

def create_group(group_name, members, client_names, client_socket):
    # Validate group name
    if not group_name.isalnum() or len(group_name.split()) > 1:
        client_socket.sendall("[Invalid group name. Group name must contain only alphanumeric characters and be a single word.]".encode('utf-8'))
        return

    # Add group to the dictionary of client groups
    client_names[group_name] = members
    client_socket.sendall(f"[Group {group_name} created with members: {', '.join(members)}]".encode('utf-8'))

        
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
            if message.startswith("@group set"):
                # Extract group name and members from the message
                parts = message.split("group set ")[1].split()
                group_name = parts[0]
                members = [name.strip() for name in parts[1].split(",")]

                # Validate that all members exist
                for member in members:
                    if member not in client_names.values():
                        client_socket.sendall(f"[Error: {member} does not exist. Cannot create group.]".encode('utf-8'))
                        break
                else:
                    # Create the group
                    create_group(group_name, members, client_names, client_socket) 
            # Receive @quit message from client
            elif message == "@quit":
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
                if message.startswith('@'):
                    recipient_username, personal_message = message[1:].split(' ', 1)
                    # Iterate through clients to find the recipient
                    for client, username in client_names.items():
                        if username == recipient_username:
                            client.sendall(
                                f"[{client_names[client_socket]} (private)]: {personal_message}".encode('utf-8'))
                            break
                else:
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