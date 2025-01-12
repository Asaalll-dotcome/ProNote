import socket
import threading
import loginOrRegister

def handle_client(client_socket, username):
    while True:
        request = client_socket.recv(1024).decode('utf-8')
        
        if request:
            print(f"Received: {request}")
            print(f"Current username: {username}")
            response = loginOrRegister.process_request(request)  
            if response is not None:
            # Send the response back to the client
                client_socket.send(response.encode('utf-8'))
            else:
                # Handle the case where the response is None
                print("Error processing request. Please contact support.")
                break
        else:
            break

    client_socket.close()

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind(("127.0.0.1", 12345))
    server_socket.listen(5)
    print("Listening on port 12345...")

    while True:
        client, addr = server_socket.accept()
        print(f"Accepted connection from {addr[0]}:{addr[1]}")
        username = None
        client_handler = threading.Thread(target=handle_client, args=(client, username))
        client_handler.start()

if __name__ == "__main__":
    server()
