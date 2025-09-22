#include <iostream>
#include <fstream>
#include <sstream>
#include <bits/stdc++.h>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h> 


using namespace std;


vector<string> read_from_txt_file(string filename){

    vector<string>ans;
    ifstream din;
    din.open(filename);
    string line;
    // Read the single line from the file
    if (getline(din, line)) {
        stringstream ss(line);
        string word;

        // Split the line by commas and store each word in the vector
        while (getline(ss, word, ',')) {
            ans.push_back(word+",");
        }
    }

    
    return ans;
}
string helper(vector<string>&v){
    string ans="";
    for(auto i:v){
        ans+=i;
    }
    return ans;
}

int main(){
    unordered_map<string,string> json_mp;
    ifstream bin;
    bin.open("json.txt");
    string key;
    while(bin>>key){
        string val;
        bin>>val;
        json_mp[key] = val;
    }
    bin.close();
    int serverport,n,k,p;
    n = stoi(json_mp["n"]);
    k = stoi(json_mp["k"]);
    p = stoi(json_mp["p"]);
    string filename = json_mp["filename"];
    serverport = stoi(json_mp["server_port"]);
    const char* server_ip = json_mp["server_ip"].c_str();
    vector<string>all_words = read_from_txt_file(filename);
    int m = all_words.size();

    int server_socket = socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in server_address;
    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = INADDR_ANY;  
    server_address.sin_port = htons(serverport);
    int connection_status = ::bind(server_socket, (struct sockaddr*)&server_address, sizeof(server_address));
    listen(server_socket, 1);
    std::cout << "Waiting for connections..." << std::endl;

    // Accept a connection
    cout<<"hi";
    // int client_sock = accept(server_socket, nullptr, nullptr);
    sockaddr_in client_address;
    socklen_t client_address_len = sizeof(client_address);
    int client_sock = accept(server_socket, (struct sockaddr*)&client_address, &client_address_len);
    cout<<client_sock<<endl;
    std::cout << "Client connected!" << std::endl;
    
    bool ind =false;
    while(true){
        
        char message[1024] = {0};
        int bytes_received = recv(client_sock, message, sizeof(message) - 1, 0);
        message[bytes_received] = '\0'; 
        if(bytes_received == 0){
            break;
        }
        cout << "Received message: " << message << endl;
        int j=0;
        int offset = 0;
        while(message[j] != '\n'){
            offset = offset*10 + (message[j]-'0');
            j++;
        }
        // cout<<ind<<" "<<offset<<endl;
        string message_to_send = "";
        
        
        bool is_this_last_offset = 0;
        if(offset>=m){
            message_to_send = "$$\n";
            send(client_sock, message_to_send.c_str(), message_to_send.length(), 0);
        }
        else{
            if(offset + k >= m) {
                is_this_last_offset = 1;
            }
            vector<string>to_send;
            for(int i=offset;i<min(m,offset+k);i++){
                to_send.push_back(all_words[i]);
            }
            int t = to_send.size();
            int start = 0;
            while(start < t)
            {
                message_to_send = "";
                
                for(int i=start;i< min(t,(start+p));i++){
                    message_to_send += to_send[i];
                }
                start = start + p;
                if(start >= t && is_this_last_offset){
                    message_to_send += EOF;
                }
                message_to_send += "\n";
                cout<<"packet : "<<message_to_send<<endl;
                send(client_sock, message_to_send.c_str(), message_to_send.length(), 0);
            }
            
            
        }
        
    }
    close(server_socket);

}
