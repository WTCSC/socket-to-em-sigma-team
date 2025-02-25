import socket
import ipaddress
import sys
import threading

# Close connection to server
def disconnect_client(client):
    client.close()
    print("🟧 Client disconnected.")

# Validates inputted IP for IPv4 format
def validate_ip(ip_input):
    try:
        ipaddress.IPv4Address(ip_input)
        return True

    except ipaddress.AddressValueError:
        print("Invalid IPv4 address. Please try again.")
        return False

# Validates inputted port:
def validate_port(port_string_input):
    # Checks that all characters in the string are numbers
    if not port_string_input.isnumeric():
        print("🟥 Please enter a valid integer for the port.")
        return False

    # Checks if public port
    elif int(port_string_input) < 1024 or int(port_string_input) > 65535:
        print("🟥 Please enter a valid, public port (1024-65535).")
        return False        

    else:
        return True

# Initialize client and attempt to connect to server
def connect_to_server(host, port):
    # Create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to server
    try:
        client.connect((host, port))
        print(f"🟩 Connected to server {host}:{port}")
        return True, client

    except ConnectionRefusedError:
        print("🟥 Could not connect to server. Make sure the server is running and the address/port is correct.")
        return False, None

    except Exception as e:
        print(f"🟥 An error occurred: {e}")
        return False, None

# Function ran by thread to recieve data + additional error handling
def recieve_data(client):
    try:
        while True:
            response = client.recv(1024).decode()
            print(response)
    except Exception as e:
        print(f"{e}")

# Sending and recieving data
def data_transfer(client, user_input, client_username):
    user_input = (f"{client_username}: {user_input}")
    client.send(user_input.encode())
    
# Main loop
def main():
    # Localhost address
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)

    # Gets user inputted IP and validates it for correct IPv4 format
    while True:
        ip_input = input(f"Enter desired IP address to connect to OR leave blank for localhost connection ({host}): ")
        
        # If user chooses localhost connection
        if ip_input == '':
            break

        # Breaks out of loop if IP is valid
        valid_ip = validate_ip(ip_input)
        if valid_ip:
            host = ip_input
            break

    # Input and validation for port
    while True:
        port_string_input = input("Enter port: ")

        # Breaks out of loop if port is valid
        valid_port = validate_port(port_string_input)
        if valid_port:
            port = int(port_string_input)
            break

    # Gets a username from client 
    client_username = input("Enter a username: ")

    # Max username length
    while len(client_username) > 16:
        print("Username too long (Max 16 characters), please try again.")
        client_username = input("Enter a username: ")
    
    # Attempts to connect to server 
    connection_successful, client = connect_to_server(host, port)

    # If connection fails, aborts program
    if not connection_successful:
        sys.exit("🟥 Exiting program due to error above.")

    # Welcome message once user connects
    print(f"🟩 Welcome {client_username}! Type /cmds for a list of commands")

    # Dedicated background thread to constantly receive data.
    recv_thread = threading.Thread(target=recieve_data, args=(client,), daemon=True)
    recv_thread.start()

    # Sending data
    try:
        while True:
            user_input = input("Message: ")
            
            if user_input == "/cmds":
                print("""Command List:
Ctrl + c          Disconnect Client""")

            if not user_input:
                print("Message must have context!")

            else:
                data_transfer(client, user_input, client_username)

    except KeyboardInterrupt:
        print("🟨 Disconnecting client...")

    finally:
        disconnect_client(client)

if __name__ == "__main__":
    print("AI Chat Room, enter ctrl + c to disconnect at any time")
    main()