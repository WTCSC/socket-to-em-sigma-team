import socket
import ipaddress

# Get selected port and ensure valid port
def init_port(host):
    while True:
        try:
            port = int(input("Enter port: "))
            break

        except ValueError:
            print("🟥 Please enter a valid integer for the port.")

    connect_to_server(host, port)

# Initialize client and attempt to connect to server
def connect_to_server(host, port):
    # Create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to server
    try:
        client.connect((host, port))
        print(f"🟩 Connected to server {host}:{port}")
        successful_connection(client)

    except ConnectionRefusedError:
        print("🟥 Could not connect to server. Make sure the server is running and the address/port is correct.")

    except Exception as e:
        print(f"🟥 An error occured: {e}")

# Once connection is successful, allows users to send messages to server
def successful_connection(client):
    client_username = input("Enter a username: ")
    print("You can now send messages! Just type and hit enter")

    # Send messages and receive responses
    try:
        while True:
            data = f"{client_username}: " + input("")
            if not data:
                break
            
            client.send(data.encode())
            response = client.recv(1024).decode()
            print(response)
            
    except KeyboardInterrupt:
        print("🟨 Disconnecting client...")

    finally:
        client.close()
        print("🟧 Client disconnected.")

# Lets user select IP address, then the port
def main():
    # Localhost address
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)

    # User entered address + address validation for IPv4 format
    while True:
        selected_ip_input = input(f"Enter desired IP address to connect to OR leave blank for localhost connection ({host}): ")
        
        if selected_ip_input == '':
            selected_ip_input = host
            pass

        else:
            pass

        try:
            ipaddress.IPv4Address(selected_ip_input)
            break

        except ipaddress.AddressValueError:
            print("Invalid IPv4 address. Please try again.")

    init_port(host)

if __name__ == "__main__":
    print("AI Chat Room, enter ctrl + c to disconnect at any time")
    main()