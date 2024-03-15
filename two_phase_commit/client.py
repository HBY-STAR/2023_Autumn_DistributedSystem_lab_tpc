import socket

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.settimeout(5)

print("Client start :")

while True:
    try:
        # Connect to server
        address = input("请输入服务器地址：")
        address_list = address.split()
        serverHost = address_list[0]
        serverPort = int(address_list[1])
        server_address = (serverHost,serverPort)
        client_socket.connect(server_address)
        
        # Send data to the server
        message = input("请输入要提交的消息: ")
        client_socket.send(message.encode('utf-8'))
        
        # Receive and print the response from the server
        response = client_socket.recv(1024)
        print(f"Received response: {response.decode('utf-8')}")
    except Exception:
        print("Commit failed: time out")

    client_socket.close()
