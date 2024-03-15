# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 11:58:53 2023

@author: 21714
"""

import socket

A_address = ('localhost', 12001)
A_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
A_socket.settimeout(3)
A_socket.connect(A_address)
B_address = ('localhost', 12002)
B_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
B_socket.settimeout(3)
B_socket.connect(B_address)
C_address = ('localhost', 12003)
C_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
C_socket.settimeout(3)
C_socket.connect(C_address)

C_socket.bind(C_address)
C_socket.listen(5)

TC_now = True
TC_address = C_address

print(f"C is listening on {C_address}")

while True:
    # Wait for client
    print("")
    print("Waiting for client...")
    client_socket, client_address = C_socket.accept()
    print(f"C Accepted connection from {client_address}")
    # Receive and print the data
    data = client_socket.recv(1024)
    print(f"C received data: {data.decode('utf-8')}.")
    
    if TC_now:
        print('C is TC now , start two phase commit.')
        can_A_commit = 'Can A commit?'
        can_B_commit = 'Can B commit?'
        try:
            A_socket.send(can_A_commit.encode('utf-8'))
            A_response = A_socket.recv(1024)
            A_response = A_response.decode('utf-8')
            B_socket.send(can_B_commit.encode('utf-8'))
            B_response = B_socket.recv(1024)
            B_response = B_response.decode('utf-8')
        
            if A_response == 'A is ok.' and B_response == 'B is ok.':
                A_socket.send(str(data).encode('utf-8'))
                A_response = A_socket.recv(1024)
                A_response = A_response.decode('utf-8')
                B_socket.send(str(data).encode('utf-8'))
                B_response = B_socket.recv(1024)
                B_response = B_response.decode('utf-8')
                print(f"A response: {A_response}")
                print(f"B response: {B_response}")
                # Send a response back to the client
                response = f"{str(data)} commit ok"
                print(response)
                client_socket.send(response.encode('utf-8'))
            else:
                response = f"{str(data)} commit failed: not ok."
                print(response)
                client_socket.send(response.encode('utf-8'))
        except Exception:
            response = f"{str(data)} commit failed: time out"
            print(response)
            client_socket.send(response.encode('utf-8'))
            
    else:
        print('C is not TC , send message to TC.')
        A_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        A_socket.settimeout(3)
    
    
    
    
    
    
    
    

    # Receive and print the data
    data = client_socket.recv(1024)
    print(f"TC received data: {data.decode('utf-8')}, start two phase commit.")
    
    can_A_commit = 'Can A commit?'
    can_B_commit = 'Can B commit?'
    
    try:
        A_socket.send(can_A_commit.encode('utf-8'))
        A_response = A_socket.recv(1024)
        A_response = A_response.decode('utf-8')
        B_socket.send(can_B_commit.encode('utf-8'))
        B_response = B_socket.recv(1024)
        B_response = B_response.decode('utf-8')
    
        if A_response == 'A is ok.' and B_response == 'B is ok.':
            A_socket.send(str(data).encode('utf-8'))
            A_response = A_socket.recv(1024)
            A_response = A_response.decode('utf-8')
            B_socket.send(str(data).encode('utf-8'))
            B_response = B_socket.recv(1024)
            B_response = B_response.decode('utf-8')
            print(f"A response: {A_response}")
            print(f"B response: {B_response}")
            # Send a response back to the client
            response = f"{str(data)} commit ok"
            print(response)
            client_socket.send(response.encode('utf-8'))
        else:
            response = f"{str(data)} commit failed: not ok."
            print(response)
            client_socket.send(response.encode('utf-8'))
    except Exception:
        response = f"{str(data)} commit failed: time out"
        print(response)
        client_socket.send(response.encode('utf-8'))

    # Close the connection
    # client_socket.close()
    

