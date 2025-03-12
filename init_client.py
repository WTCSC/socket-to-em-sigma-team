import socket
import ipaddress
import sys
import threading
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime

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

class ChatUI:
    def __init__(self, client, username):
        self.client = client
        self.username = username
        self.running = True
        
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Chat Room")
        self.root.configure(bg="#1e1e1e")
        self.root.geometry("600x400")
        
        font_style = ("Helvetica", 12)
        
        # Frame for chat area
        chat_frame = tk.Frame(self.root, bg="#1e1e1e")
        chat_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # ScrolledText widget for chat messages (read-only)
        self.chat_area = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state=tk.DISABLED,
            bg="#1e1e1e", fg="#d4d4d4",
            font=font_style, borderwidth=0, highlightthickness=0)
        self.chat_area.pack(expand=True, fill="both")
        
        # Frame for entry and disconnect button
        bottom_frame = tk.Frame(self.root, bg="#1e1e1e")
        bottom_frame.pack(fill="x", padx=10, pady=(0,10))
        
        # Entry widget for typing messages
        self.entry = tk.Entry(bottom_frame, bg="#333333", fg="#ffffff",
            font=font_style, insertbackground="#ffffff")
        self.entry.pack(side=tk.LEFT, fill="x", expand=True)
        self.entry.focus()
        
        # Disconnect button
        disconnect_btn = tk.Button(bottom_frame, text="Disconnect", bg="#aa3333", fg="white",
                                  command=self.disconnect)
        disconnect_btn.pack(side=tk.RIGHT, padx=(5,0))
        
        # Bind the Enter key to the send_message function
        self.entry.bind("<Return>", self.send_message)
        
        # Protocol for window close
        self.root.protocol("WM_DELETE_WINDOW", self.disconnect)
        
        # Display welcome message
        self.add_system_message(f"Connected as {username}")
        
        # Announce this user has joined to the server
        try:
            client.send(f"JOIN:{username}".encode())
        except Exception as e:
            print(f"🟥 Error sending join notification: {e}")
        
    def send_message(self, event=None):
        msg = self.entry.get().strip()
        if msg:
            # Format the message with username and send to server
            formatted_msg = f"{self.username}: {msg}"
            try:
                self.client.send(formatted_msg.encode())
                self.entry.delete(0, tk.END)
            except Exception as e:
                print(f"🟥 Error sending message: {e}")
                self.disconnect()
    
    def add_message(self, message):
        timestamp = datetime.now().strftime("[%H:%M]")
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"{timestamp} {message}\n")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.yview(tk.END)
    
    def add_system_message(self, message):
        timestamp = datetime.now().strftime("[%H:%M]")
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"{timestamp} [System] {message}\n")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.yview(tk.END)
    
    def disconnect(self):
        self.running = False
        # Send leave notification before disconnecting
        try:
            self.client.send(f"LEAVE:{self.username}".encode())
        except:
            pass
        self.root.destroy()
        print("🟨 Disconnecting client...")
        disconnect_client(self.client)

# Function ran by thread to receive data and update UI
def receive_data(client, chat_ui):
    try:
        while chat_ui.running:
            response = client.recv(1024).decode()
            if not response:
                break
                
            # Check for special join/leave messages
            if response.startswith("JOIN:"):
                username = response[5:]
                chat_ui.add_system_message(f"{username} has joined the chat")
            elif response.startswith("LEAVE:"):
                username = response[6:]
                chat_ui.add_system_message(f"{username} has left the chat")
            else:
                chat_ui.add_message(response)
                
    except Exception as e:
        if chat_ui.running:  # Only print error if not intentionally disconnected
            print(f"🟥 Error receiving data: {e}")

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
    print(f"🟩 Welcome {client_username}! Launching chat interface...")

    # Create and start UI
    chat_ui = ChatUI(client, client_username)
    
    # Start receive thread
    recv_thread = threading.Thread(target=receive_data, args=(client, chat_ui), daemon=True)
    recv_thread.start()
    
    # Start UI main loop
    chat_ui.root.mainloop()

if __name__ == "__main__":
    print("Chat Room, enter ctrl + c to disconnect at any time")
    main()