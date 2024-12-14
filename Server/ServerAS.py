#ServerAS.py

#By Alyousef Soliman 100883692
#This program is strictly my own work. Any material
#beyond course learning materials that is taken from
#the Web or other sources is properly cited, giving
#credit to the original author(s).


"""
Server Script for Raspberry Pi
- Collects and sends system information using vcgencmd commands.
- Sends data to the client in JSON format.

"""

import socket  #Import the socket library for network communication
import json  #Import the JSON library to parse and format JSON data
import threading  #Import threading to handle multiple client connections
import PySimpleGUI as sg  #Import PySimpleGUI for creating the graphical user interface

def handle_client(client_socket, addr, window):
    """
    Handles the client connection and updates GUI with received data.
    Continuously receives data until the client disconnects.
    """
    print(f"Connection established with {addr}")  #Log the established connection
    try:
        while(True):
            #Receive data from the client
            json_received = client_socket.recv(1024)  #Receive up to 1024 bytes from the client
            if not json_received:  #If no data is received, the client has disconnected
                print(f"Client {addr} disconnected.")  # Log the disconnection
                break  #Exit the loop

            #Decode and parse the JSON data
            parsed_data = json.loads(json_received.decode('utf-8'))  # Decode and parse the JSON data
            print(f"Data received: {parsed_data}")  # Log the received data

            #Update GUI with the received data
            for i, (key, value) in enumerate(parsed_data.items()):  # Loop through key-value pairs in the data
                if(i < 6):  #Display only the first 6 values
                    window.write_event_value(f"-UPDATE-{i}-", f"{key}: {value}")  #Update GUI with the data
    except Exception as e:
        print(f"Error handling client {addr}: {e}")  #Log any errors
    finally:
        client_socket.close()  #Close the client socket
        print(f"Connection closed with {addr}")  #Log the socket closure

def start_server(window):
    """
    Starts the server socket to listen for client connections.
    """
    host = ''  #Listen on all interfaces
    port = 5000  #Define the port for the server to listen on
    server_socket = socket.socket()  #Create a server socket
    server_socket.bind((host, port))  #Bind the socket to the host and port
    server_socket.listen(5)  #Set the socket to listen for up to 5 connections
    print("Server is running...")  #Log that the server is running

    while(True):
        client_socket, addr = server_socket.accept()  #Accept an incoming client connection
        threading.Thread(target=handle_client, args=(client_socket, addr, window)).start()  #Handle the client in a new thread

#Create the GUI
sg.theme('DarkBlue')  #Set the GUI theme
layout = [
    [sg.Text("Server Status", font=("Helvetica", 16))],  #Add a title to the GUI
    [sg.Text("Current Data:", font=("Helvetica", 14))],  #Add a label for the data section
    [sg.Text(key=f"-DATA-{i}-", size=(40, 1)) for i in range(6)],  #Add placeholders for up to 6 pieces of data
    [sg.Button("Exit", size=(10, 1))]  #Add an Exit button to close the GUI
]
window = sg.Window("Server GUI", layout, finalize=True)  #Create the GUI window

#Start the server in a separate thread
threading.Thread(target=start_server, args=(window,), daemon=True).start()  #Start the server in a background thread

#Event loop for the GUI
while(True):
    event, values = window.read(timeout=100)  #Non-blocking GUI loop to handle events
    if(event == sg.WIN_CLOSED or event == "Exit"):  #Check if the window is closed or Exit is clicked
        break  #Exit the loop
    elif(event.startswith("-UPDATE-")):  #Check for data update events
        index = int(event.split("-")[2])  #Extract the index from the event key
        window[f"-DATA-{index}-"].update(values[event])  #Update the corresponding data placeholder in the GUI

window.close()  #Close the GUI window


