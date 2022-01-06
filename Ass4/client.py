import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 80
MSG_MAX_SIZE = 256


def send_to_server(message: str) -> None:
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((SERVER_IP, SERVER_PORT))

        request = bytearray(message.encode())
        client_socket.sendall(request)

        response = client_socket.recv(MSG_MAX_SIZE)
        print(response)

        # This line is not strictly necessary due to the with statement, but
        # has been left here to illustrate the complete socket lifespan
        client_socket.close()


if __name__ == "__main__":
    send_to_server(input())