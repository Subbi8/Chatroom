import socket
import threading
import time
import ssl
g=0
HOST = '127.0.0.1'
PORT = 1234 
LISTENER_LIMIT = 5
removed_clients = []
TinyTalk = []
MiniChat = []
PetiteChats = []
all_list = [TinyTalk, MiniChat, PetiteChats]
all_dict = {}

def listen_for_messages(client, username,i):

    while 1:
        message = client.recv(2048).decode('utf-8')
        if message == "file":
            try:
                image_size_bytes = client.recv(4)
                if not image_size_bytes:
                  break
                image_size = int.from_bytes(image_size_bytes, byteorder='big')

                image_data = client.recv(image_size)
                extension = client.recv(2048).decode('utf-8')

                if image_data:
                     print(f"Received file from {username}\n")
                     for t in i:
                        if t[0] == username:
                             continue
                        h="file"
                        t[1].sendall(h.encode())
                        t[1].sendall(image_size_bytes)
                        t[1].sendall(image_data)
                        t[1].sendall(extension.encode())
                        final_msg =username+ '~' +f"sent a file, check in your directory that will be saved  "
                        t[1].sendall(final_msg.encode())
            except Exception as e:
                print(f"[ERROR] {username} disconnected\n")
                for t in i:
                        i.remove(t)
                client.close(t)
                break
        #elif message == 'close':
            #print(f"{username}disconnected\n")
            
        elif message != '':
            if message == "bye":
                client.sendall("bye".encode())
                print(f"{username} disconnected")
                for t in i:
                    if t[1]==client:
                        i.remove(t)
                final_msg = "SERVER" + '~' + f" {username} exited from the chat room"
                send_messages_to_all(final_msg,i)
            else:
                final_msg = username + '~' + message
                send_messages_to_all(final_msg,i)

        #else:
            #print(f"The message send from client {username} is empty\n")
            #break


def send_message_to_client(client, message):

    client.sendall(message.encode())

def send_messages_to_all(message,m):
    
    for user in m:

        send_message_to_client(user[1], message)

def client_handler(client):
 
    while 1:
        c=0
        w=0
        r=0
        username = client.recv(2048).decode('utf-8')
        roomname = client.recv(2048).decode('utf-8')
        #p = roomname
        #l = roomname
        if username != '' and roomname != '':
            for i in removed_clients:
                if(i[0]==username):
                    c=1
                    print(f"server can't allow {username} to join\n")
                    message="can't join"
                    send_message_to_client(client, message)
                    
            if c!=1:
               for i in all_list:
                   if i == roomname:
                      w=1
                      i.append((username, client))
                      break
                
                      
               if w!=1:
                    for i in all_dict:
                        if i == roomname:
                            r=1
                            all_dict[i].append((username, client))
                            break
                            
               if r!=1 and w!=1:  
                    all_dict[roomname] = []
                    all_dict[roomname].append((username, client))
               prompt_message = "SERVER~" + f"{username} added to the chat"
               if w == 1:
                 for o in all_list[i]:
                    if(o[0]==username):
                        break
                    send_message_to_client(o[1],prompt_message)
                 threading.Thread(target=listen_for_messages, args=(client, username,all_list[i], )).start()
                 threading.Thread(target=remove_client, args=(all_list[i], )).start()
               else:
                 for o in all_dict[roomname]:
                    if(o[0]==username):
                        break
                    send_message_to_client(o[1],prompt_message)
                 threading.Thread(target=listen_for_messages, args=(client, username,all_dict[roomname], )).start()
                 threading.Thread(target=remove_client, args=(all_dict[roomname], )).start()
                       
            break
        else:
            print("Client username or roomname is empty")
    
    
def remove_client(k):
    while 1:
        o=1
        m=input("Do you want to remove any client(y/n): \n")
        if m=='y' or m=='Y':
            n=input("enter the name of the client you want to remove: \n")
            for i in k:
                if i[0]==n:
                    o=0
                    removed_clients.append(i)
                    k.remove(i)
                    p="remove"
                    send_message_to_client(i[1], p)
                    message = "SERVER~" + f" removed {n} from the chat"
                    send_messages_to_all(message,k)
                    print(f"removed {n}")
                if o==0:
                    break
            if o==1:
                print("client is not connected\n")
            time.sleep(5)

def main():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((HOST, PORT))
        print(f"Running the server on {HOST} {PORT}")
    except:
        print(f"Unable to bind to host {HOST} and port {PORT}")

    server.listen(LISTENER_LIMIT)

    while 1:

        client, address = server.accept()
        client = ssl.wrap_socket(client,server_side=True, certfile="cert.pem", keyfile="key.pem",ssl_version=ssl.PROTOCOL_TLS)
        print(f"Successfully connected to client {address[0]} {address[1]}")

        threading.Thread(target=client_handler, args=(client, )).start()

if __name__ == '__main__':
    main()