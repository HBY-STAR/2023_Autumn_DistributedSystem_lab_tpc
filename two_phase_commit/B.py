import socket

# Define the server's address and port
server_address = ('localhost', 12002)

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the server address
server_socket.bind(server_address)

# Listen for incoming connections (max 5 connections in the queue)
server_socket.listen(5)

print(f"B is listening on {server_address}")

first = True

while True:
    # Wait for a connection
    print("")
    print("Waiting for TC...")
    
    if first:
        client_socket, client_address = server_socket.accept()
        print(f"B accepted connection from {client_address}")
        first=False

    # Receive and print the data
    data = client_socket.recv(1024)
    data = data.decode('utf-8')
    
    if data == 'Can B commit?':
        print("B is ok.")
        response = "B is ok."
        client_socket.send(response.encode('utf-8'))
        continue
    else:
        print(f"Received data: {str(data)}")
        response = f"B received : {str(data)}"
        client_socket.send(response.encode('utf-8'))
    
    

    # Close the connection
    # client_socket.close()
    
def clear_socket_buffer(sock):
    # 设置非阻塞模式，用于清空接收缓存
    sock.setblocking(0)
    while True:
        try:
            # 尝试接收数据，设置一个较小的缓冲区大小
            data = sock.recv(1024)
            if not data:
                break
        except socket.error:
            break
