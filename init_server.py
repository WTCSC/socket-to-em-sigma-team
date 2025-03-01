import socket
import threading
import ipaddress

# List of clients used to echo data back to all clients
client_list = []

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

def init_server(host, port):
    # Create socket object
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the server
    server.bind((host, port))

    # Listens for connections (Currently 5)
    server.listen(5)
    print(f"🟩 Server listening on {host}:{port}")

    try:
        while True:
            client, addr = server.accept()
            client_list.append(client)

            # Thread to handle new clients
            thread = threading.Thread(target=handle_client, args=(client, addr))
            thread.start()

    except KeyboardInterrupt:
        print("🟨 Shutting down server...")

    finally:
        server.close()
        print("🟧 Server shut down.")

# Recieves data from clients and echos back
def handle_client(client, addr):
    print(f"🟩 Accepted connection from {addr}")
    try:
        while True:
            data = client.recv(1024)
            if not data:
                break

            print(f"Received: {data.decode()} from {addr}")

            # Broadcast the message to all connected clients
            for c in client_list[:]:  # iterate over a copy
                try:
                    c.send(data)

                except Exception as e:
                    print(f"Error sending message to {c}: {e}")

    except Exception as e:
         print(f"🟥 Error handling client {addr}: {e}")

    finally:
        print("🟨 A client is disconnecting...")
        client.close()

        # Removes any clients that disconnects from the client list
        if client in client_list:
            client_list.remove(client)
            
        print(f"🟧 Client {addr} closed")

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

    init_server(host, port)

if __name__ == "__main__":
    print("AI Chat Room, hit ctrl + c to shutdown server at any time")
    main()