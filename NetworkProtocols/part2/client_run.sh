#!/bin/bash

# Compile the client source files
g++ client1.cpp -o client1
g++ client2.cpp -o client2
g++ client.cpp -o client

# Check if compilation was successful
if [ $? -ne 0 ]; then
    echo "Compilation failed!"
    exit 1
fi

# Run each executable in a new terminal
gnome-terminal -- bash -c "./client1; exec bash" &  # Opens a new terminal for client1
gnome-terminal -- bash -c "./client2; exec bash" &  # Opens a new terminal for client2
gnome-terminal -- bash -c "./client; exec bash" &  # Opens a new terminal for client3

# Wait for all clients to finish (if needed)
wait
