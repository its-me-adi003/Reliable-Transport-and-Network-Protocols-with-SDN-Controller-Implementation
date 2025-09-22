
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import arp
from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link
from collections import defaultdict
import time 
from ryu.lib.packet import lldp
import struct 
import heapq 

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port={}
        self.mac_to_switch = {}  # Switch forwarding table
        self.host_to_switch = {}  # Host to switch mapping
        self.topology_api_app = self
        self.first_time=False 
        self.topology_disc=False 
        self.switches = []
        self.links = []
        self.spanning_tree_edges = []
        self.delayed_switches = [] 
        self.lldp_timestamps={}
        self.lldp_timestamps2={}
        self.counter=0
        self.is_done_filling_latency=False 
        self.datapaths = {}  # Add this line to store datapath objects
        self.blocked_ports = defaultdict(list)  # Blocked ports for each switch
        self.echo_timestamps={}
        self.shortest_paths = {}  # To store shortest paths between switches


    @set_ev_cls(event.EventSwitchEnter)
    def get_topology_data(self, ev):
        if self.first_time==False:
            time.sleep(10)
        # Clear existing topology
            self.switches.clear()
            self.links.clear()

            # Get switches and links
            switch_list = get_switch(self.topology_api_app, None)
            self.switches = [switch.dp.id for switch in switch_list]
            self.switches1=[switch.dp for switch in switch_list]
            links_list = get_link(self.topology_api_app, None)
            self.links = [(link.src.dpid, link.dst.dpid, {'port': link.src.port_no}) for link in links_list]
            self.build_spanning_tree()
            self.setup_blocked_ports()
            self.host_ports={}
            for e in self.switches1:
                ports = [p.port_no for p in e.ports.values()]
                set_port=set()
                for e1 in self.links:
                    x,y,z=e1 
                    if x==e.id or y==e.id :
                        set_port.add(z['port'])
                po=set(ports)-set_port
                self.host_ports[e.id]=po 
                
            print("Switches:", self.switches)
            print("Links:", self.links)
            print("Spanning Tree Edges:", self.spanning_tree_edges)
            print("Blocked Ports:", dict(self.blocked_ports))
            print("Switches:", self.switches)
            print("Links:", self.links)
            self.first_time=True 
            self.topology_disc=True
            self.send_packet_all()
             
             
        #    time.sleep(5)
             
            for datapath in self.delayed_switches:
                self.install_flows_for_switch(datapath)
            self.delayed_switches.clear()
            
    
    def build_spanning_tree(self):
        # Create a graph from the links
        graph = defaultdict(list)
        for src, dst, port in self.links:
            graph[src].append((dst, port['port']))
        #    graph[dst].append((src, port['port']))  # Undirected graph

        # Use a simple DFS to find the spanning tree edges
        visited = set()
        self.spanning_tree_edges = []

        def dfs(node):
            visited.add(node)
            for neighbor, port in graph[node]:
                if neighbor not in visited:
                    self.spanning_tree_edges.append((node, neighbor, port))
                    dfs(neighbor)

        # Start DFS from the first switch
        if self.switches:
            dfs(self.switches[0])

    def setup_blocked_ports(self):
        """Block all ports that are not part of the spanning tree."""
        all_ports = defaultdict(set)

        # Gather all ports used for each switch
        for src, dst, port in self.links:
            all_ports[src].add(port['port'])
            all_ports[dst].add(port['port'])
     #   self.blocked_ports.clear()
        # Determine blocked ports (those not in the spanning tree)
     #   print(self.links)
      #  print(self.spanning_tree_edges)
      #  print(self.blocked_ports)
        self.blocked_ports=defaultdict(list)
     #   print(self.blocked_ports)
        for src, dst, port in self.links:
            is_present=False 
            for e in self.spanning_tree_edges:
                
                if (src==e[0] and dst==e[1]) or (src==e[1] and dst==e[0]):
                    is_present=True 
                    break 
      #      print(src,dst,port,is_present)
            if is_present==False:
         #       print(src,dst,port)
                self.blocked_ports[src].append(port['port'])      
            
    def send_packet_all(self):
        """Send LLDP packets to all ports of all switches."""
        i=0
        for dpid in self.switches:
            datapath = self.switches1[i]
            i+=1 
        #    print(dpid,datapath,"sdsss")
            if datapath:
                # Iterate over all ports for the current switch
                for port in datapath.ports.values():
                    lldp_pkt = self.build_lldp_packet(datapath, port.port_no)
            #        print(datapath.id,port.port_no)
                    # Create actions to send the LLDP packet out on the port
                    actions = [datapath.ofproto_parser.OFPActionOutput(port.port_no)]
                    
                    # Prepare and send the packet
                    out = datapath.ofproto_parser.OFPPacketOut(
                        datapath=datapath,
                        buffer_id=datapath.ofproto.OFP_NO_BUFFER,
                        in_port=datapath.ofproto.OFPP_CONTROLLER,
                        actions=actions,
                        data=lldp_pkt.data
                    )
                    datapath.send_msg(out)


    def build_lldp_packet(self, datapath, port_no):
        # Manually create the custom TLV for latency measurement or controller RTT measurement
        timestamp = time.time()
        # Create Ethernet frame
        eth = ethernet.ethernet(
            dst=lldp.LLDP_MAC_NEAREST_BRIDGE,  # Destination MAC for LLDP
            src=datapath.ports[port_no].hw_addr,  # Source MAC is switch port's MAC
            ethertype=ethernet.ether.ETH_TYPE_LLDP  # LLDP EtherType
        )   
        
        custom_tlv_value = b"latency_measurement"
        

        chassis_id = lldp.ChassisID(
            subtype=lldp.ChassisID.SUB_LOCALLY_ASSIGNED,
            chassis_id=str(datapath.id).encode()  # Convert to bytes
        )
        port_id = lldp.PortID(
            subtype=lldp.PortID.SUB_PORT_COMPONENT,
            port_id=str(port_no).encode()  # Convert to bytes
        )
        ttl = lldp.TTL(ttl=120)  # Time-to-live for LLDP packet


        custom_tlv_type = 127  # TLV type for custom TLV
        custom_tlv_header = (custom_tlv_type << 9) | len(custom_tlv_value)  # TLV type + length
        custom_tlv_header_bytes = custom_tlv_header.to_bytes(2, byteorder='big')  # Convert to bytes

        # Combine the custom TLV header and value
        custom_tlv = custom_tlv_header_bytes + custom_tlv_value

        # Build the LLDP packet with Ethernet and LLDP protocols
        lldp_pkt = packet.Packet()
        lldp_pkt.add_protocol(eth)
        lldp_pkt.add_protocol(lldp.lldp(tlvs=[chassis_id, port_id, ttl]))  # Add standard TLVs
        lldp_pkt.serialize()

        # Append custom TLV to the serialized packet
        lldp_pkt.data += custom_tlv

        # Store the timestamp for RTT calculation
        self.lldp_timestamps[(str(datapath.id).encode(), str(port_no).encode())] = timestamp
        return lldp_pkt
    def install_flows_for_switch(self, datapath):
        """Install flows for a switch if topology is discovered"""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
     #   print(f"Flows installed for Switch {datapath.id}")



    
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        if self.topology_disc:
            self.install_flows_for_switch(datapath)
        else:
            # Delay flow installation until after topology is discovered
     #       print(f"Delaying flow installation for Switch {datapath.id}")
            self.delayed_switches.append(datapath)

        self.send_echo_request(datapath)
    def send_echo_request(self, datapath):
        """Send an OFP Echo Request to measure RTT"""
        ofp_parser = datapath.ofproto_parser
        echo_req = ofp_parser.OFPEchoRequest(datapath, data=b'rtt_measurement')
        #print(datapath.id)
        # Record the timestamp when the echo request is sent
        self.echo_timestamps[datapath.id] = time.time()
        datapath.send_msg(echo_req)
    @set_ev_cls(ofp_event.EventOFPEchoReply, MAIN_DISPATCHER)
    def echo_reply_handler(self, ev):
        """Handle the Echo Reply message and calculate RTT"""
        datapath = ev.msg.datapath
     #   print(datapath.id,"this is id")
        if datapath.id in self.echo_timestamps:
            # Calculate RTT by subtracting the sent timestamp from the current time
            rtt = time.time() - self.echo_timestamps[datapath.id]
       #     print(f"Controller-Switch RTT for Switch {datapath.id}: {rtt:.6f} seconds")
    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
 #       print("adding ", datapath.id,actions)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id, priority=priority, match=match, instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # Extract details from the event message
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        # Parse the packet received
        pkt = packet.Packet(msg.data)
        eth= pkt.get_protocols(ethernet.ethernet)[0]
        eth_pkt=eth 
        
        if eth_pkt.ethertype == 0x88CC:  # LLDP EtherType
            lldp_pkt = pkt.get_protocol(lldp.lldp)
            custom_tlv = msg.data[-len("latency_measurement") - 2:] 
            custom_tlv_type = (custom_tlv[0] >> 1) 
            custom_tlv_value = custom_tlv[2:].decode() 

            if custom_tlv_type == 127:
                if custom_tlv_value == "latency_measurement":
                    src_dpid = lldp_pkt.tlvs[0].chassis_id  # Source switch ID from LLDP packet
                    src_port = lldp_pkt.tlvs[1].port_id     # Source port from LLDP packet

                    # Convert source ID and port to bytes for comparison (same as the key used during packet creation)
                    src_key = (src_dpid, src_port)

                    # Get the original timestamp when the packet was sent
                    if src_key in self.lldp_timestamps:
                        send_timestamp = self.lldp_timestamps[src_key]
                        # Calculate the round-trip time (RTT)
                        current_time = time.time()
                        rtt = current_time - send_timestamp
                    self.handle_latency_measurement_lldp(datapath, pkt, lldp_pkt,rtt)
            return 
        
        
        
        
        
        
        ports = [p.port_no for p in datapath.ports.values()]
        dst = eth.dst
        src = eth.src
        dpid = datapath.id

        self.mac_to_port.setdefault(dpid, {})
      #  self.mac_to_switch.setdefault(src, 0)
        # Log the packet reception
    #    self.logger.info(f"Packet in: Switch {dpid}, SRC: {src}, DST: {dst}, In Port: {in_port}")

        # Initialize the switch's MAC to port mapping table if not already done
   #     self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port
        if src not in self.mac_to_switch:
            self.mac_to_switch[src] = dpid
    #    self.logger.info(f"Learned MAC {src} is associated with Switch {dpid}")

        # Learn the source MAC address: associate it with the input port
      #  self.mac_to_port[dpid][src] = in_port
        self.is_not_shortest_present=True 
        actions=[]
        ports = [p.port_no for p in datapath.ports.values()]
        print(dpid,dst)
        print(self.mac_to_port[dpid],"hi")
        print(self.mac_to_switch)
                
        if dst not in self.mac_to_port[dpid]:
            available_ports = set(ports)  # Adjust this if your switches have fewer ports
          #  print(available_ports)
            blocked_ports = set(self.blocked_ports[dpid])
            flood_ports = available_ports - blocked_ports - {in_port}
        #    print(flood_ports)
            actions = [parser.OFPActionOutput(port) for port in flood_ports]
            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data

            # Prepare and send the packet out
            out = parser.OFPPacketOut(
                datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
                actions=actions, data=data)
            datapath.send_msg(out)
            return 
        # Define the action: either flood or forward to the known output port
        else:
            dst_switch=self.mac_to_switch[dst]
            if dpid==dst_switch:
                print(dpid,dst_switch)
                out_port = self.mac_to_port[dpid][dst]
                actions=[parser.OFPActionOutput(out_port)]
                match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
                self.add_flow(datapath, 1, match, actions)
            else:  
                print(dpid,dst_switch) 
                path = self.shortest_paths[dpid][dst_switch]
                next_hop=path[1]
                print(next_hop)
                out=-1 
                for e in self.links:
                    x,y,z=e 
                    if x==dpid and y==next_hop:
                        out=z['port']
                print(out,"gfg")
                actions=[parser.OFPActionOutput(out)]
                match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
                self.add_flow(datapath, 1, match, actions)
                        
    #    actions = [parser.OFPActionOutput(out_port)]
            
        # If the packet is not buffered in the switch, send the data along with the PacketOut message
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        # Prepare and send the packet out
        out = parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
            actions=actions, data=data)
        datapath.send_msg(out)
        
        
    def learn_host(self, datapath, eth, in_port):
        """Learn the host MAC address and map it to the switch and port"""
        dpid = datapath.id
        mac = eth.src

        # Add the host to the mapping
        self.host_to_switch[mac] = (dpid, in_port)
        self.logger.info(f"Host {mac} is connected to Switch {dpid} on port {in_port}")
    def get_datapath(self, dpid):
        """Retrieve the datapath object for a given switch ID (dpid)."""
        return self.mac_to_port.get(dpid, None)
    
    
    
    def handle_latency_measurement_lldp(self, datapath, pkt, lldp_pkt,rtt1):
        """Handles the latency measurement LLDP packet received."""
        
        # Extract source switch and port from LLDP packet
        src_dpid = lldp_pkt.tlvs[0].chassis_id  # Source switch ID from LLDP packet
        src_port = lldp_pkt.tlvs[1].port_id     # Source port from LLDP packet

        # Convert source ID and port to bytes for comparison (same as the key used during packet creation)
        src_key = (src_dpid, src_port)

        # Get the original timestamp when the packet was sent
        if src_key in self.lldp_timestamps:
            send_timestamp = self.lldp_timestamps[src_key]
            # Calculate the round-trip time (RTT)
            current_time = time.time()
            rtt = rtt1 
            print(f"RTT between Switch {datapath.id} and Switch {src_dpid.decode()} on port {src_port.decode()} is: {rtt} seconds")

        
        #    print(f"Estimated Controller-Switch RTT: {controller_switch_rtt} seconds")
            
            # Now calculate switch-switch latency (subtract the controller-switch RTT)
            switch_switch_rtt = rtt
       #     print(f"Switch-Switch RTT: {switch_switch_rtt} seconds")
            dst_switch_id = datapath.id
            src_switch_id = int(src_dpid.decode())  # Convert bytes to integer

            cst1 = self.get_controller_switch_rtt(dst_switch_id)
            cst2 = self.get_controller_switch_rtt(src_switch_id)
            if cst1 is not None and cst2 is not None:
                switch_switch_delay = (switch_switch_rtt - cst1 - cst2) / 2
            # Optionally: You can store the latency for further analysis or decision-making
            self.lldp_timestamps2[(datapath.id,int(src_dpid.decode()))] = rtt  # Store the measured RTT
            self.counter+=1 
       #     print(self.counter,len(self.switches))
            if self.counter==len(self.links):
                print(self.lldp_timestamps2)
                self.continuation()
        else:
            print(f"Error: No timestamp found for Switch {src_dpid.decode()} on port {src_port.decode()}")
    def get_controller_switch_rtt(self, switch_id):
        """
        Get the controller-switch RTT for a given switch.
        """
        if switch_id in self.echo_timestamps:
            return time.time() - self.echo_timestamps[switch_id]
        else:
            return None
    def continuation(self):
        """Calculate the shortest path using Dijkstra's algorithm based on the latencies."""
        # Step 1: Build the graph from self.lldp_timestamps2
        graph = defaultdict(dict)
        for e in self.links:
            x,y,z=e 
            if (x,y) in self.lldp_timestamps2:
                graph[x].update({y:self.lldp_timestamps2[(x,y)]})
            
    #    for (src_dpid, src_port), rtt in self.lldp_timestamps2.items():
     #       print(src_dpid,src_port)
      #      for (dst_dpid, dst_port), dst_rtt in self.lldp_timestamps2.items():
       #         
        #        if src_dpid != dst_dpid:  # Avoid self-loops
         #           # Assume symmetric latency for simplicity
          #          latency = rtt + dst_rtt  # You may adjust this based on your requirements
           #         graph[src_dpid.decode()].update({dst_dpid.decode(): latency})

        print("Constructed Graph:", dict(graph))
        def dijkstra(source, destination):
            # Initialize the priority queue and distances
            queue = []
            heapq.heappush(queue, (0, source))  # (latency, node)
            distances = {source: 0}
            previous_nodes = {source: None}

            while queue:
                current_distance, current_node = heapq.heappop(queue)

                # If we reach the destination, we can stop
                if current_node == destination:
                    break

                # If the current distance is greater than the recorded distance, skip
                if current_distance > distances.get(current_node, float('inf')):
                    continue

                # Explore neighbors
                for neighbor, weight in graph[current_node].items():
                    distance = current_distance + weight

                    # Only consider this new path if it's better
                    if distance < distances.get(neighbor, float('inf')):
                        distances[neighbor] = distance
                        previous_nodes[neighbor] = current_node
                        heapq.heappush(queue, (distance, neighbor))

            # Step 3: Backtrack to find the shortest path
            path, current = [], destination
            while current is not None:
                path.append(current)
                current = previous_nodes[current]
            path.reverse()

            return path, distances.get(destination, float('inf'))
        for src in self.switches:
            self.shortest_paths[src] = {}
            for dst in self.switches:
                if src != dst:
                    path, _ = dijkstra(src, dst)
                    self.shortest_paths[src][dst] = path
                    print(f"Shortest path from {src} to {dst}: {path}")

            
        
    

