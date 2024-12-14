#ClientAS.py

#By Alyousef Soliman 100883692
#This program is strictly my own work. Any material
#beyond course learning materials that is taken from
#the Web or other sources is properly cited, giving
#credit to the original author(s).


"""
Client Script for Raspberry Pi
- Connects to the server running on Raspberry Pi.
- Receives and displays system information sent in JSON format.

"""

import socket  #Import the socket library for network communication
import json  #Import the JSON library for formatting and parsing JSON data
import os  #Import the os library to execute shell commands
import time  #Import the time library for adding delays
from pathlib import Path  #Import the Path class to work with file paths
import PySimpleGUI as sg  #Import the PySimpleGUI library for creating the graphical user interface

#Check if running on Raspberry Pi
IS_RPI = Path("/etc/rpi-issue").exists()  #Check if the Pi-specific file exists to confirm the environment
if(not IS_RPI):
    print("This script is designed to run only on a Raspberry Pi.")  #Notify user if not running on a Pi
    exit(0)  #Exit the program if the environment is not a Raspberry Pi

#Function to collect vcgencmd data
def collect_vcgencmd_data(iteration):
    """
    Collect system data using vcgencmd.
    Includes core voltage, core temperature, and other Pi metrics.
    """
    core_voltage = os.popen('vcgencmd measure_volts core').readline().strip()  #Get the core voltage
    core_temp = os.popen('vcgencmd measure_temp').readline().strip()  #Get the core temperature
    arm_clock = os.popen('vcgencmd measure_clock arm').readline().strip()  #Get the ARM clock speed
    gpu_clock = os.popen('vcgencmd measure_clock core').readline().strip()  #Get the GPU clock speed
    throttled = os.popen('vcgencmd get_throttled').readline().strip()  #Get the throttled status

    return {
        "Iteration": iteration,  #Add the current iteration number
        "Core Voltage": core_voltage,  #Add the core voltage
        "Core Temperature": core_temp,  #Add the core temperature
        "ARM Clock Speed": arm_clock,  #Add the ARM clock speed
        "GPU Clock Speed": gpu_clock,  #Add the GPU clock speed
        "Throttled Status": throttled  #Add the throttled status
    }

#GUI Setup
sg.theme('DarkBlue')  #Set the theme for the GUI
layout = [
    [sg.Text("Client Status", font=("Helvetica", 16))],  #Add a title to the GUI
    [sg.Text("Connection Status:", size=(20, 1)), sg.Text("Disconnected", key="-STATUS-")],  #Add status placeholders
    [sg.Button("Exit", size=(10, 1))]  #Add an Exit button to close the GUI
]
window = sg.Window("Client GUI", layout, finalize=True)  #Create the GUI window

#Server connection details
host = "10.102.13.67"  #IP address of the server
port = 5000  #Port number for the server connection

try:
    #Initialize socket
    sock = socket.socket()  #Create a socket object
    sock.connect((host, port))  #Connect to the server using the host and port
    print(f"Connected to server at {host}:{port}")  #Log the successful connection
    window["-STATUS-"].update("Connected")  #Update GUI status to "Connected"

    #Event loop for GUI and sending data
    iteration = 1  #Start with the first iteration
    while(True):
        event, values = window.read(timeout=100)  #Non-blocking read from the GUI

        #Handle Exit button
        if(event == sg.WIN_CLOSED or event == "Exit"):  #Check if the Exit button is clicked or window is closed
            print("Exiting client.")  #Log the exit
            window["-STATUS-"].update("Disconnected")  #Update status before exiting
            break  #Exit the loop

        #Send data in iterations
        if(iteration <= 50):  #Limit the number of iterations to 50
            try:
                #Collect vcgencmd data
                data = collect_vcgencmd_data(iteration)  #Call the function to get Pi metrics

                #Convert data to JSON byte array
                json_result = json.dumps(data)  #Convert the data dictionary to a JSON string
                json_bytes = bytearray(json_result, "UTF-8")  #Encode the JSON string to bytes
                print(f"Sending data: {json_bytes}")  #Log the data being sent

                #Send data to server
                sock.send(json_bytes)  #Send the byte array to the server

                #Update GUI with iteration status
                window["-STATUS-"].update(f"Iteration {iteration} sent")  #Update the GUI with the iteration status

                #Increment iteration counter
                iteration += 1  #Increment the iteration counter
                time.sleep(5)  #Wait for 5 seconds before the next iteration
            except socket.error as e:
                print(f"Socket error while sending data: {e}")  #Log socket errors
                window["-STATUS-"].update("Disconnected")  #Update GUI status to "Disconnected"
                break  #Exit the loop on socket error

    print("Data successfully sent or process exited. Closing connection.")  # Log the closure of the connection
    sock.close()  #Close the socket
except socket.gaierror as e:
    print(f"Error resolving the host: {e}")  #Log errors in resolving the server address
    window["-STATUS-"].update("Host resolution error")  #Update GUI status to host resolution error
except socket.error as e:
    print(f"Socket error: {e}")  #Log general socket errors
    window["-STATUS-"].update("Socket error")  #Update GUI status to socket error
finally:
    window.close()  #Close the GUI window




