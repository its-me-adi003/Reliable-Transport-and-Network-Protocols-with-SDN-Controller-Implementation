import socket
import argparse
import json
import time 
# Constants
MSS = 1400  # Maximum Segment Size

def receive_file(server_ip, server_port):
    """
    Receive the file from the server with reliability, handling packet loss
    and reordering.
    """
    # Initialize UDP socket
    
    ## Add logic for handling packet loss while establishing connection
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(2)  # Set timeout for server response

    server_address = (server_ip, server_port)
    expected_seq_num = 0
    output_file_path = "received_file.txt"  # Default file name

    recive_dict={}

    while True:
        try:
            # Send initial connection request to server
       #     print("Attempting to connect to server...")
            client_socket.sendto(b"START", server_address)
            
            # Wait for server acknowledgment
            ack_packet, _ = client_socket.recvfrom(5000)
            if ack_packet == b"ACK_START":
      #          print("Connection established with server.")
                break  # Exit loop if connection is successful

        except socket.timeout:
     #       print("No response from server, retrying connection...")
            continue 
    while True:
        try:
            # Wait for RTT test packet from server
            ack_packet, _ = client_socket.recvfrom(5000)
            packet_str = ack_packet.decode()
            packet_dict = json.loads(packet_str)
            ack_seq_num = packet_dict["seq_num"]
            ack_data = packet_dict["data"]

            if ack_data == "RTT_TEST":
      #          print("Received RTT test packet from server")
                
                # Create RTT_ACK packet to send back to server
                ack_response = json.dumps({"seq_num": ack_seq_num, "data": "RTT_ACK"}).encode()
                client_socket.sendto(ack_response, server_address)
                break  # Exit loop after responding to RTT test

        except socket.timeout:
            continue
       #     print("No response from server, retrying RTT test...")
  #  return None 
    with open(output_file_path, 'wb') as file:
        while True:
            try:
                # Receive the packet
                packet, _ = client_socket.recvfrom(MSS + 1500)  # Allow room for headers
                
                # Logic to handle end of file
                if packet==b"END_OF_FILE":
             #       print("Received END signal from server, file transfer complete")
                    for e in range(10):
                        client_socket.sendto(b"END_ACK", server_address)
                    time.sleep(1)
                    break
             #   try:
                    
                seq_num, data = parse_packet(packet)
               # except (json.JSONDecodeError,ValueError) as e:
                #    print(f"Packet decode error: {e}")
                 #   continue 
                
                # If the packet is in order, write it to the file
                if seq_num == expected_seq_num:
                    file.write(data)
             #       print(f"Received packet {seq_num}, writing to file")
                    s_no=expected_seq_num
                    x=s_no+MSS 
                    recive_dict[s_no]=data 
                    while x in recive_dict:
                        d=recive_dict[x]
                        file.write(d)
              #          print(f"Received packet {seq_num}, writing to file")
                        x+=MSS 
                   #     del recive_dict[x]
                    expected_seq_num=x 
                    seq_num=x 
                    # Update expected seq number and send cumulative ACK for the received packet
                    send_ack(client_socket, server_address, seq_num)
                elif seq_num < expected_seq_num:
                    # Duplicate or old packet, send ACK again
         #           print("recieved duplicate")
                    send_ack(client_socket, server_address, expected_seq_num)
                else:
          #          print("recieved out of order packet")
                    recive_dict[seq_num]=data 
                    
                    send_ack(client_socket, server_address, expected_seq_num)
                    pass 
                    # packet arrived out of order
                    # handle_pkt()
            except socket.timeout:
        #        print("Timeout waiting for data")
                continue

def parse_packet(packet):
    """
    Parse the packet to extract the sequence number and data.
    """
 #   print("Attempting to parse packet")
    
    try:
        packet_str = packet.decode()
        packet_dict = json.loads(packet_str)
        seq_num = packet_dict['seq_num']
     #   print(len(packet),seq_num)
        data = packet_dict['data'].encode()  # Convert back to bytes
        return seq_num, data
    except (json.JSONDecodeError, KeyError) as e:
    #    print(f"Error parsing packet: {e} - Raw packet data: {packet}")
        return None, None


def send_ack(client_socket, server_address, seq_num):
    """
    Send a cumulative acknowledgment for the received packet.
    """
    ack_packet = json.dumps({"seq_num": seq_num, "type": "ACK"}).encode()
    client_socket.sendto(ack_packet, server_address)
    
 #   print(f"Sent cumulative ACK for packet {seq_num}")

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Reliable file receiver over UDP.')
parser.add_argument('server_ip', help='IP address of the server')
parser.add_argument('server_port', type=int, help='Port number of the server')

args = parser.parse_args()

# Run the client
receive_file(args.server_ip, args.server_port)

