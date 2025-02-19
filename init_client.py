import socket
import ipaddress

def init_client():
    # User enters ip address and validates format
    while True:
        host = input("Enter desired IP address to connect to OR leave blank for localhost connection: ")
        if host == '':
            hostname = socket.gethostname()
            host = socket.gethostbyname(hostname)
            print(host)
        else:
            pass
        try:
            ipaddress.IPv4Address(host)
            break
        except ipaddress.AddressValueError:
            print("Invalid IPv4 address. Please try again.")

    # Get port to be listened on
    while True:
        try:
            port = int(input("Enter port: "))
            break
        except ValueError:
            print("🟥 Please enter a valid integer for the port.")

    # Create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to server
    try:
        client.connect((host, port))
        print(f"🟩 Connected to server {host}:{port}")

    except ConnectionRefusedError:
            print("🟥 Could not connect to server. Make sure the server is running and the address is correct.")

    except Exception as e:
        print(f"🟥 An error occured: {e}")

    client_username = input("Enter a username: ")

    # Send messages and receive responses
    try:
        while True:
            data = f"{client_username}: " + input("Enter message: ")
            if not data:
                break
            client.send(data.encode())
            response = client.recv(1024).decode()
            print(response)
            
    except KeyboardInterrupt:
        print("🟨 Disconnecting client...")

    finally:
        client.close()

if __name__ == "__main__":
    init_client()