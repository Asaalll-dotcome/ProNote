import socket

def client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(("127.0.0.1", 12345))

        print("Welcome to the Task Management System!")
        print("Commands:")
        print("  - To Register: 'register:<name>,<lastname>,<username>,<email>,<postalcode>,<password>'")
        print("  - To Login: 'login:<username>,<password>'")
        print("  - To Reset Password: 'reset_password:<email>,<newPassword>,<re-typeNewPassword>'")
        print("  - To Add Task: 'add_task:<username>,<listName>,<task>,<important>,<deadline>'")
        print("  - To see list of tasks: 'show_list:<username>'")
        print("  - To Change status: 'change_task_status:<userName>,<list_name>,<task>'")
        print("  - To Change deadline: 'change_task_deadline:<userName>,<list_name>,<deadline>'")
        print("  - Type 'exit' to quit")

        while True:
            message = input("Enter command: ")
            if message.lower() == 'exit':
                break

            # Sending the message to the server
            client_socket.send(message.encode('utf-8'))

            # Receiving and printing the response from the server
            response = client_socket.recv(4096).decode('utf-8')
            print(f"Server replied: {response}")

if __name__ == "__main__":
    client()

