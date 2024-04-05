import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import os
import sys
import ssl

g=0
c=0
HOST = '127.0.0.1'
PORT = 1234
r = None


DARK_GREY = '#121212'
MEDIUM_GREY = '#1F1B24'
OCEAN_BLUE = '#464EB8'
WHITE = "white"
FONT = ("Helvetica", 17)
BUTTON_FONT = ("Helvetica", 15)
SMALL_FONT = ("Helvetica", 13)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
client = context.wrap_socket(client, server_hostname=HOST)

def add_message(message):
    message_box.config(state=tk.NORMAL)
    message_box.insert(tk.END, message + '\n')
    message_box.config(state=tk.DISABLED)
    

def connect():
    username = username_textbox.get()
    roomname = room_textbox.get()
    if username != '' and roomname != '':
        try:
            
            client.connect((HOST, PORT))
            print("Successfully connected to server")
            add_message("[SERVER] you joined to the chatroom")
            global r
            r = username
            client.sendall(username.encode())
            client.sendall(roomname.encode())
            username_textbox.config(state=tk.DISABLED)
            room_textbox.config(state=tk.DISABLED)
            username_button.config(state=tk.DISABLED)
            message_textbox.config(state=tk.NORMAL)
            message_button.config(state=tk.NORMAL)
            image_button.config(state=tk.NORMAL)
            threading.Thread(target=listen_for_messages_from_server, args=(client, )).start() 
        except:
            messagebox.showerror("Unable to connect to server", f"Unable to connect to server {HOST} {PORT}")
        
    elif username == '':
            messagebox.showerror("Invalid username", "Username cannot be empty, please enter valid name")
    else:
            messagebox.showerror("Invalid room_name", "room_name cannot be empty, please enter valid name")

def send_message():
    message = message_textbox.get()
    if message != '':
        client.sendall(message.encode())
        message_textbox.delete(0, len(message))
    else:
        messagebox.showerror("Empty message", "Message cannot be empty")

def send_image():
    image_path = message_textbox.get()
    if image_path !='':
        message_textbox.delete(0, len(image_path))
        extension = image_path.split(".")[-1]
        t="file"
        client.sendall(t.encode())
        if os.path.exists(image_path):
        # Read image file
             with open(image_path, 'rb') as f:
                  image_data = f.read()

            # Send image data size first
                  client.sendall(len(image_data).to_bytes(4, byteorder='big'))
                  
                
                # Send image data to the server
                  client.sendall(image_data)
                  client.sendall(extension.encode())
                  message_box.config(state=tk.NORMAL)
                  p="[you] sent a file "
                  message_box.insert(tk.END, p+ '\n')
                  message_box.config(state=tk.DISABLED)
        else:
            print("Invalid path! Please try again.")
            messagebox.showerror("Invalid path! Please try again.")
    else:
        messagebox.showerror("Empty message", "Message cannot be empty")
        
       
root = tk.Tk()
root.geometry("800x600")
root.title("CHAT ROOM")
root.resizable(False, False)

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=4)
root.grid_rowconfigure(2, weight=1)

top_frame = tk.Frame(root, width=600, height=100, bg=DARK_GREY)
top_frame.grid(row=0, column=0, sticky=tk.NSEW)

middle_frame = tk.Frame(root, width=600, height=400, bg=MEDIUM_GREY)
middle_frame.grid(row=1, column=0, sticky=tk.NSEW)

bottom_frame = tk.Frame(root, width=600, height=100, bg=DARK_GREY)
bottom_frame.grid(row=2, column=0, sticky=tk.NSEW)

username_label = tk.Label(top_frame, text="username:", font=FONT, bg=DARK_GREY, fg=WHITE)
username_label.pack(side=tk.LEFT, padx=10)

        
username_textbox = tk.Entry(top_frame, font=FONT, bg=MEDIUM_GREY, fg=WHITE , width=15)
username_textbox.pack(side=tk.LEFT)

room_label = tk.Label(top_frame, text="room_name:", font=FONT, bg=DARK_GREY, fg=WHITE)
room_label.pack(side=tk.LEFT, padx=10)

room_textbox = tk.Entry(top_frame, font=FONT, bg=MEDIUM_GREY, fg=WHITE , width=10)
room_textbox.pack(side=tk.LEFT)

username_button = tk.Button(top_frame, text="Join", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE,command=connect)
username_button.pack(side=tk.LEFT, padx=15)

message_textbox = tk.Entry(bottom_frame, font=FONT, bg=MEDIUM_GREY, fg=WHITE, width=38)
message_textbox.pack(side=tk.LEFT, padx=10)

message_button = tk.Button(bottom_frame, text="Send", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=send_message)
message_button.pack(side=tk.LEFT, padx=10)

message_box = scrolledtext.ScrolledText(middle_frame, font=SMALL_FONT, bg=MEDIUM_GREY, fg=WHITE, width=67, height=26.5)
message_box.config(state=tk.DISABLED)
message_box.pack(side=tk.TOP)

message_box.config(state=tk.NORMAL)
p="To send any files, enter the file_path in the message_box and click on Send_file button\nDon't forget to enter the file_path with the file extention\nTo exit from the chat send 'bye' through message box\nroom_names: TinyTalk, MiniChat, PetiteChats\nYou can join this room or create your own room "
message_box.insert(tk.END, p+ '\n')
message_box.config(state=tk.DISABLED)


image_button= tk.Button(bottom_frame, text="Send_file", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=send_image)
image_button.pack(side=tk.LEFT, padx=10)
message_textbox.config(state=tk.DISABLED)
message_button.config(state=tk.DISABLED)
image_button.config(state=tk.DISABLED)

def listen_for_messages_from_server(client):

    while 1:

        message = client.recv(2048).decode('utf-8')
        if message == "file":
            try:
                image_size = int.from_bytes(client.recv(4), byteorder='big')
                if image_size > 0:
                    image_data = client.recv(image_size)
                    ext = client.recv(2048).decode('utf-8')
                    p=client.recv(2048).decode('utf-8')
                    
                    username = p.split("~")[0]
                    content = p.split('~')[1]
                    global g
                    g=g+1
                    add_message(f"[{username}] {content} as {g}")
                    save_path = f"{g}.{ext}"
                    with open(save_path, 'wb') as f:
                      f.write(image_data)

            except Exception as e:
                print("[ERROR] Error receiving image:", e)
                pass
        elif message != '':
            global c
            if message == 'remove':
                c=1
                print("you got removed from the server")
                print("disconnected from the server")
                root.destroy()
            if message == "can't join":
                c=1
                print("you can't join the chatroom")
                print("disconnected from the server")
                root.destroy()
            if message == 'bye':
                c=1
                print("you left the chatroom")
                print("disconnected from the server")
                root.destroy()
            if c == 1:
               #client.sendall("close".encode())
               client.close()
               sys.exit()
            else:
                username = message.split("~")[0]
                content = message.split('~')[1]
                global r
                if r == username:
                   add_message(f"[you] {content}")
                else:    
                   add_message(f"[{username}] {content}")


def main():
    root.protocol("WM_DELETE_WINDOW", lambda: None)

    root.mainloop()
    
if __name__ == '__main__':
    main()