import socket
import ipaddress
import sys
import curses

def disconnect_client(client, stdscr):
    # Close connection to server
    client.close()

    # Kill all curses process's
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

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

# Clients fully connected to server and allows data transfer
def data_transfer(client, data):
            client.send(data.encode())
            response = client.recv(1024).decode()
            print(response)
        
# Initializing curses for TUI
def init_curses():
    stdscr = curses.initscr()
    # Prevents user input section from appearing automatically
    curses.noecho()

    # Respons to key presses immedietly
    curses.cbreak()

    # Enables special keys
    stdscr.keypad(True)

    # Get terminal size
    height, width = stdscr.getmaxyx()

    # Create chat window and input window
    chat_win = curses.newwin(height - 4, width, 0, 0)
    input_win = curses.newwin(3, width, height - 3, 0)

    # Enable scrolling for the chat section
    chat_win.scrollok(True)
    chat_win.idlok(True)

    # Divider line
    stdscr.hline(height - 4, 0, '-', width)
    stdscr.refresh()

    return stdscr, chat_win, input_win

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

    # Initialize curses
    stdscr, chat_win, input_win = init_curses()
    
    # Attempts to connect to server, if connection fails, aborts program
    connection_successful, client = connect_to_server(host, port)
    if connection_successful:
        pass
    else:
        curses.endwin()  # Resets terminal if connection fails
        sys.exit("🟥 Exiting program due to error above.")

    # Gets a username from client 
    client_username = input("Enter a username: ")

    # Max username length
    while len(client_username) > 16:
        print("Username too long (Max 16 characters), please try again.")
        client_username = input("Enter a username: ")

    # Welcome message when user connects
    chat_win.addstr(f"🟩 Welcome {client_username}! Type /cmds for a list of commands\n", curses.A_BOLD)
    chat_win.refresh()

    # Send messages and receive responses
    try:
        while True:
            # User inputted message
            data = f"{client_username}: " + input("")
            if not data:
                break

            # Send and recieve data
            data_transfer(client, data)

    except KeyboardInterrupt:
        print("🟨 Disconnecting client...")

    finally:
        disconnect_client()


if __name__ == "__main__":
    print("AI Chat Room, enter ctrl + c to disconnect at any time")
    main()