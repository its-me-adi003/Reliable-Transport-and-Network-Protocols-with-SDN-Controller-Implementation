import socket
import time
import argparse
import json 

def estimate_initial_rtt(server_socket, client_address):
    initial_rtt = 0.1  # Initial dummy RTT in seconds
    rtt = initial_rtt
    max_attempts = 5
    seq_num = 0
    recive_dict = {}
    
    for attempt in range(max_attempts):
        try:
            # Create and send the RTT test packet
            packet = create_packet(seq_num, "RTT_TEST".encode())  # Send as bytes
            server_socket.sendto(packet, client_address)
            recive_dict[seq_num] = time.time()
            
            # Wait for acknowledgment from client
            server_socket.settimeout(rtt)
            ack_packet, _ = server_socket.recvfrom(5000)
         #   print(len(ack_packet),ack_packet)
            if ack_packet==b"START":
                continue 
            # Decode and interpret the ACK packet
            packet_str = ack_packet.decode()
            packet_dict = json.loads(packet_str)
            ack_seq_num = packet_dict["seq_num"]
            ack_data = packet_dict["data"]
            
            # Check if the ACK packet matches expected sequence and data
            if ack_seq_num == seq_num and ack_data == "RTT_ACK":
                measured_rtt = time.time() - recive_dict[ack_seq_num]
          #      print(f"RTT successfully measured: {measured_rtt:.8f} seconds")
                return measured_rtt  # Return the measured RTT if successful

        except socket.timeout:
            # Double the RTT estimate if timeout occurs
            rtt *= 2
        #    print(f"Timeout occurred. Doubling RTT estimate to {rtt:.8f} seconds")

  #  print("Max attempts reached. Setting RTT to a default high value.")
    return rtt  # Return the final doubled RTT if no ACK received


# Constants
MSS = 1400  # Maximum Segment Size for each packet
WINDOW_SIZE = 10  # Number of packets in flight
DUP_ACK_THRESHOLD = 3  # Threshold for duplicate ACKs to trigger fast recovery
FILE_PATH = "file.txt"
TIMEOUT = 1.0  # Initialize timeout to some value but update it as ACK packets arrive
def send_file(server_ip, server_port, enable_fast_recovery):
    global TIMEOUT
    """
    Send a predefined file to the client, ensuring reliability over UDP.
    """
    # Initialize UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((server_ip, server_port))

 #   print(f"Server listening on {server_ip}:{server_port}")

    # Wait for client to initiate connection
    
    client_address = None
    file_path = FILE_PATH  # Predefined file name

    while client_address is None:
   #     print("Waiting for client connection...")
        start_message, client_address = server_socket.recvfrom(5000)
        
        if start_message == b"START":
   #         print(f"Connection established with client {client_address}")
            server_socket.sendto(b"ACK_START", client_address)  # Acknowledge connection

    
    
    initial_rtt = estimate_initial_rtt(server_socket, client_address)
    WINDOW_SIZE=((initial_rtt)*(5*10**7))//(8*MSS)+1 
 #   print(WINDOW_SIZE)
  #  return None 
    Estimate_rtt=initial_rtt
    Devrtt=0.0 
    TIMEOUT=Estimate_rtt+4*Devrtt
    Estimate_rtt
    is_end=False 
    throughput_time=time.time()
    initial_time=time.time()
    ack_throughput=-1 
    with open(file_path, 'rb') as file:
        seq_num = 0
        window_base = 0
        unacked_packets = {}
        duplicate_ack_count = 0
        last_ack_received = -1
        spec_pack=0
        to_update_time=False 
        end=False 
        #last_ack_recieved is the last acknowledgemnt recieved 
        # ack_seq_num is the packet which is to be recieved by client  
        slow_start=True 
        congestion_avoidance=False
        in_fast_recovery=False 
        cwnd=MSS 
        ssthresh=(64*1024)
        
    
        while True:
            if time.time()-throughput_time>=1:
                print((last_ack_received-ack_throughput)/(time.time()-throughput_time),time.time()-initial_time,"instantaneous rtt")
                throughput_time=time.time()
                ack_throughput=last_ack_received
            if cwnd>=ssthresh and slow_start:
                slow_start=False 
                congestion_avoidance=True 
            while seq_num-last_ack_received<cwnd: ## Use window-based sending
                chunk = file.read(MSS)
       #         print(len(chunk),seq_num,"special_print")
                if not chunk:
                    
                    end=True 
                    # End of file
                    # Send end signal to the client 
                    break

                # Create and send the packet
                packet = create_packet(seq_num, chunk)
                if client_address:
                    server_socket.sendto(packet, client_address)
            #    else:
             #       print("Waiting for client connection...")
              #      data, client_address = server_socket.recvfrom(1024)
               #     print(f"Connection established with client {client_address}")
                

                ## 
                if to_update_time==False:
                    spec_pack=seq_num
                    to_update_time=True 
                unacked_packets[seq_num] = (packet, time.time())  # Track sent packets
             #   print(f"Sent packet {seq_num}")
                seq_num += MSS
       #     print(end,"end is here")
            # Wait for ACKs and retransmit if needed
            server_socket.settimeout(TIMEOUT)
        #    print(TIMEOUT,spec_pack,to_update_time,last_ack_received,time.time())
            try:
            	## Handle ACKs, Timeout, Fast retransmit
                server_socket.settimeout(TIMEOUT)
                ack_packet, _ = server_socket.recvfrom(1024)
                if ack_packet==b"END_ACK":
                    is_end=True 
                    break 
                packet_str=ack_packet.decode()
                packet_dict =json.loads(packet_str)
                ack_seq_num=packet_dict["seq_num"]
              #  ack_seq_num = get_seq_no_from_ack_pkt()
            #    print(ack_seq_num,last_ack_received,seq_num,"first")
         #       print(ack_seq_num>last_ack_received)
          #      print(TIMEOUT,"here1")
                TIMEOUT=Estimate_rtt+4*Devrtt
           #     print(TIMEOUT,"here2")
                
                if ack_seq_num > last_ack_received:
          #          print(f"Received cumulative ACK for packet {ack_seq_num}")
                    duplicate_ack_count=0
                    s_no=last_ack_received
                    if s_no==-1:
                        s_no=0 
                    last_ack_received = ack_seq_num 
                    # Slide the window forward
                    if ack_seq_num==spec_pack and to_update_time:
                        curr_time=time.time()
                        send_time=unacked_packets[spec_pack][1]
                        Samplertt=curr_time-send_time
                        
                        Estimate_rtt=(1-0.125)*Estimate_rtt+0.125*Samplertt
                        Devrtt=(0.75)*Devrtt+0.25*abs(Samplertt-Estimate_rtt)
           #             print("SampleRtt ",Samplertt,Estimate_rtt,Devrtt)
                        to_update_time=False 
                    if slow_start:    
                        for s_no in range(s_no, ack_seq_num, MSS):
                            if s_no in unacked_packets:
                                cwnd+=MSS 
                    if congestion_avoidance:
                        for s_no in range(s_no, ack_seq_num, MSS):
                            if s_no in unacked_packets:
                                cwnd+=MSS*(MSS/cwnd)
                    if in_fast_recovery:
                        cwnd=ssthresh
                        in_fast_recovery=False
                        congestion_avoidance=True 
                        
                    
                    # Remove acknowledged packets from the buffer 
                elif ack_seq_num<last_ack_received:
                    continue 
                else:
         #           print(TIMEOUT,spec_pack,to_update_time,last_ack_received,"hi1")
                    # Duplicate ACK received
          #          print(f"Received duplicate ACK for packet {ack_seq_num}, count={duplicate_ack_count}")
                    duplicate_ack_count+=1
                    if in_fast_recovery:
                        cwnd+=MSS  
                    if enable_fast_recovery and duplicate_ack_count == DUP_ACK_THRESHOLD:
          #              print("Entering fast recovery mode")
                        if ack_seq_num>spec_pack:
                            to_update_time=False 
                        if congestion_avoidance:
                            ssthresh=cwnd/2 
                            cwnd=ssthresh+3*MSS
                            congestion_avoidance=False 
                            in_fast_recovery=True 
                        if slow_start:
                            ssthresh=cwnd/2 
                            cwnd=ssthresh+3*MSS
                            slow_start=False 
                            in_fast_recovery=True 
                        fast_recovery(server_socket, client_address, unacked_packets,ack_seq_num)
         #           print(TIMEOUT,spec_pack,to_update_time,last_ack_received,time.time(),"hi2")

            except socket.timeout:
                # Timeout handling: retransmit all unacknowledged packets
         ##       print("Timeout occurred, retransmitting unacknowledged packets")
                TIMEOUT*=2 
                if slow_start:
                    ssthresh=cwnd/2 
                    cwnd=MSS 
                if congestion_avoidance:
                    ssthresh=cwnd/2 
                    cwnd=MSS
                    slow_start=True 
                    congestion_avoidance=False 
                if in_fast_recovery:
                    ssthresh=cwnd/2 
                    cwnd=MSS 
                    slow_start=True 
                    in_fast_recovery=False 
                duplicate_ack_count=0
                pack_to_retransmit=last_ack_received
                to_update_time=False 
                if pack_to_retransmit==-1:
                    pack_to_retransmit=0
                retransmit_unacked_packets(server_socket, client_address, unacked_packets,pack_to_retransmit)

            # Check if we are done sending the file
            if end:
         #       print("end_is_received")
                while seq_num-last_ack_received>MSS+1:
                    try:
                        ## Handle ACKs, Timeout, Fast retransmit
                        server_socket.settimeout(TIMEOUT)
                        ack_packet, _ = server_socket.recvfrom(1024)
                        packet_str=ack_packet.decode()
                        packet_dict =json.loads(packet_str)
                        ack_seq_num=packet_dict["seq_num"]
                    #  ack_seq_num = get_seq_no_from_ack_pkt()
               #         print(ack_seq_num,last_ack_received,seq_num)
          #              print(ack_seq_num>last_ack_received)
                        TIMEOUT=Estimate_rtt+4*Devrtt
                        if ack_seq_num > last_ack_received:
         #                   print(f"Received cumulative ACK for packet {ack_seq_num} here")
                            duplicate_ack_count=0
                            s_no=last_ack_received
                            if s_no==-1:
                                s_no=0 
                            last_ack_received = ack_seq_num
                            if ack_seq_num==spec_pack and to_update_time:
                                curr_time=time.time()
                                send_time=unacked_packets[spec_pack][1]
                                Samplertt=curr_time-send_time
                                
                                Estimate_rtt=(1-0.125)*Estimate_rtt+0.125*Samplertt
                                Devrtt=(0.75)*Devrtt+0.25*abs(Samplertt-Estimate_rtt)
          #                      print("SampleRtt ",Samplertt,Estimate_rtt,Devrtt)
                                to_update_time=False 
                                
                       #     for s_no in range(last_ack_received, ack_seq_num, MSS):
                        #        if s_no in unacked_packets:
                         #           del unacked_packets[s_no]
                        elif ack_seq_num<last_ack_received:
                            continue 
                        else:
                            # Duplicate ACK received
            #                print(f"Received duplicate ACK for packet {ack_seq_num}, count={duplicate_ack_count}")
                            duplicate_ack_count+=1 
                            if enable_fast_recovery and duplicate_ack_count == DUP_ACK_THRESHOLD:
           #                     print("Entering fast recovery mode")
                                if ack_seq_num==spec_pack:
                                    to_update_time=False 
                                fast_recovery(server_socket, client_address, unacked_packets,ack_seq_num)
                    except socket.timeout:
                        # Timeout handling: retransmit all unacknowledged packets
          #              print("Timeout occurred, retransmitting unacknowledged packets")
                        TIMEOUT*=2 
                        duplicate_ack_count=0
                        pack_to_retransmit=last_ack_received
                        to_update_time=False 
                        if pack_to_retransmit==-1:
                            pack_to_retransmit=0
                        retransmit_unacked_packets(server_socket, client_address, unacked_packets,pack_to_retransmit)
                            
                        
                        
                        
                for e in range(20):        
                    server_socket.sendto(b"END_OF_FILE", client_address)
           #     print("hi")
                must_end=False 
                while True:
                    try:
                        ## Handle ACKs, Timeout, Fast retransmit
                        server_socket.settimeout(TIMEOUT)
                        ack_packet, _ = server_socket.recvfrom(1024)
                        if ack_packet==b"END_ACK":
                            must_end=True 
                            break 
                    except socket.timeout:
                        TIMEOUT*=2 
                        server_socket.sendto(b"END_OF_FILE", client_address)
                if must_end:
                    print("File transfer complete by must_end")
                    break 
                    
            if not chunk and len(unacked_packets) == 0:
                print("File transfer complete")
                break
            if is_end:
                
                break
       #     print(cwnd,ssthresh,slow_start,congestion_avoidance,in_fast_recovery,"hi")
            

def create_packet(seq_num,data):
    packet={
        "seq_num" : seq_num,
        "data" :data.decode('latin-1')
    }
    return json.dumps(packet).encode()
    

def retransmit_unacked_packets(server_socket, client_address, unacked_packets,pack_to_retransmit):
    
    """
    Retransmit all unacknowledged packets.
    """
    earliest_seq_num = pack_to_retransmit
#    print("sending/retransmitting ",pack_to_retransmit)
    server_socket.sendto(unacked_packets[earliest_seq_num][0], client_address)
    
    

def fast_recovery(server_socket, client_address, unacked_packets,ack_seq_num):
    """
    Retransmit the earliest unacknowledged packet (fast recovery).
    """
    earliest_seq_num = ack_seq_num
 #   print("sending fast retransmission of ack_seq_num: ",ack_seq_num)
    server_socket.sendto(unacked_packets[earliest_seq_num][0], client_address)
    

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Reliable file transfer server over UDP.')
parser.add_argument('server_ip', help='IP address of the server')
parser.add_argument('server_port', type=int, help='Port number of the server')

args = parser.parse_args()

# Run the server
send_file(args.server_ip, args.server_port, True)
