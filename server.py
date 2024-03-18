import socket
import threading

def UsernameValidator(username, client_names):
    if username.strip() == '':
        return False, "Username cannot be empty."
    elif ' ' in username:
        return False, "Username cannot contain spaces."
    elif not username.isalnum():
        return False, "Username must contain only alphanumeric characters."
    elif len(username) < 3 or len(username) > 10:
        return False, "Username must be between 3 and 10 characters long."

    for name in client_names.values():
        if name == username:
            return False, "Username is already taken."
        
    return True, "Username is valid."
 
def send_group_message(group_name, message, client_names, clients):
    # Check if group exists
    if group_name in client_names:
        members = client_names[group_name]
        # Iterate through all clients and send the message to the members of the group
        for client, username in client_names.items():
            if username in members:
                client.sendall(message.encode('utf-8'))

def create_group(group_name, members, client_names, clients, client_socket):
    # Validate group name
    if not group_name.isalnum() or len(group_name.split()) > 1:
        client_socket.sendall("[Invalid group name. Group name must contain only alphanumeric characters and be a single word.]".encode('utf-8'))
        return

    # Check if group already exists
    if group_name in client_names:
        client_socket.sendall(f"[Error: Group {group_name} already exists. Choose a different name.]".encode('utf-8'))
        return

    # Add group to the dictionary of client groups
    client_names[group_name] = members
    client_socket.sendall(f"[Group {group_name} created with members: {', '.join(members)}]".encode('utf-8'))

    # Notify all members of the new group
    send_group_message(group_name, f"[You are enrolled in the {group_name} group]", client_names, clients)


def leave_group(group_name, client_socket, client_names):
    # If client is in group, remove the client
    if client_names[client_socket] in client_names[group_name]:
        left_member = client_names[client_socket]
        client_names[group_name].remove(client_names[client_socket])
        client_socket.sendall(f"[You have left the group {group_name}].".encode('utf-8'))

        # Notify other members that someone has left the group
        for client, username in client_names.items():
            if username in client_names[group_name] and client != client_socket:
                client.sendall(f"[{left_member} has left the group {group_name}].".encode('utf-8'))

    else:
        client_socket.sendall("[Error: You are not a member of this group.]".encode('utf-8'))



def delete_group(group_name, client_names, clients, client_socket):
    # Check if group exists
    if group_name in client_names:
        del client_names[group_name]
        client_socket.sendall(f"[Group {group_name} has been deleted.]".encode('utf-8'))
        send_group_message(group_name, f"[The group {group_name} has been deleted.]", client_names, clients)
    else:
        client_socket.sendall("[Error: Group does not exist.]".encode('utf-8'))

# Function to handle client connections
def handle_client(client_socket, clients, client_names):
    # Send welcome message to new chatter, broadcast newcomer message to all other chatters
    for client in clients:
        if client != client_socket:
            client.sendall(f"[{client_names[client_socket]} joined]".encode('utf-8'))
        if client == client_socket:
            client.sendall(f"[Welcome {client_names[client_socket]}!]".encode('utf-8'))

    # Loops to check for new message input from clients
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
                    create_group(group_name, members, client_names, clients, client_socket)

            # Delete group
            elif message.startswith("@group delete"):
                group_name = message.split("delete ")[1].strip()
                delete_group(group_name, client_names, clients, client_socket)

            #Leave Group
            elif message.startswith("@group leave"):
                # Extract the group name from the message
                group_name = message.split("leave ")[1].strip()
                # Call the leave_group function
                leave_group(group_name, client_socket, client_names)
            

            #Quit for clients
            elif message == "@quit":
                for client in clients:
                    if client != client_socket:
                        client.sendall(f"[{client_names[client_socket]} exited]".encode('utf-8'))
                break
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

            elif message.startswith("@group send"):
                parts = message.split(' ', 3)  # Expected format: @group send groupName message
                if len(parts) < 4:
                    client_socket.sendall("[Error: Invalid group message format.]".encode('utf-8'))
                else:
                    _, _, group_name, group_message = parts
                    # Send the message to all members of the group
                    if group_name in client_names and client_names[client_socket] in client_names[group_name]:
                        for client, username in client_names.items():
                            if username in client_names[group_name]:
                                client.sendall(
                                    f"[{group_name}][{client_names[client_socket]}]: {group_message}".encode('utf-8'))
                    else:
                        client_socket.sendall(
                            "[Error: You are not a member of this group or the group does not exist.]".encode('utf-8'))
            elif message:
                if message.startswith('@'):
                    recipient_username, personal_message = message[1:].split(' ', 1)
                    # Iterate through clients to find the recipient
                    for client, username in client_names.items():
                        if username == recipient_username:
                            client.sendall(f"[{client_names[client_socket]} (private)]: {personal_message}".encode('utf-8'))
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

        isUsernameValid = False
        while not isUsernameValid:
            # Prompt client for username
            client_socket.sendall("Enter your name: ".encode('utf-8'))
            username = client_socket.recv(1024).decode('utf-8').strip()
            isUsernameValid, validation_message = UsernameValidator(username, client_names)
            if not isUsernameValid:
                client_socket.sendall(f"[{validation_message}]\n".encode('utf-8'))

        # Add new client username to list of clients names if valid
        client_names[client_socket] = username
        # Add client to list
        clients.append(client_socket)

        # Create thread to handle client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, clients, client_names))
        client_thread.start()

    server_socket.close()

if __name__ == "__main__":
    main()
