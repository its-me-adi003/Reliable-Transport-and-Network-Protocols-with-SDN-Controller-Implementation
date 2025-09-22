#!/bin/bash

# Run the server in a new terminal window
gnome-terminal -- bash -c "./server; exec bash" &

# Wait for the server to start
sleep 2

# Run the client in a new terminal window
gnome-terminal -- bash -c "./client; exec bash"
