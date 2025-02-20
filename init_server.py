import socket
import threading
import ipaddress

def handle_client(client, addr):
    print(f"🟩 Accepted connection from {addr}")
    try:
        while True:
            data = client.recv(1024)
            if not data:
                break
            print(f"Received: {data.decode()} from {addr}")
            client.send(data) # Echo back to client

    except Exception as e:
         print(f"🟥 Error handling client {addr}: {e}")

    finally:
        print("🟨 A client is disconnecting...")
        client.close()
        print(f"🟧 Client {addr} closed")

def init_server():
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
            print("🟥 Invalid IPv4 address. Please try again.")
            
    # Get port to be listened on
    while True:
        try:
            port = int(input("Enter port: "))
            break
        except ValueError:
            print("🟥 Please enter a valid integer for the port.")

    # Create socket object
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the server
    server.bind((host, port))

    # Listens for connections
    server.listen(5)
    print(f"🟩 Server listening on {host}:{port}")

    # Accept any clients that connect and enable threading to have multiple clients connect
    try:
        while True:
            client, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(client, addr))
            thread.start()
    except KeyboardInterrupt:
        print("🟨 Shutting down server...")
    finally:
        server.close()
        print("🟧 Server shut down.")

if __name__ == "__main__":
    print("AI Chat Room, hit ctrl + c to shutdown server at any time")
    init_server()