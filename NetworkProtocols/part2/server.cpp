#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <cstring>
#include <bits/stdc++.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>

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

string helper(vector<string>& v) {
    string ans = "";
    for (auto i : v) {
        ans += i;
    }
    return ans;
}
struct client_data {
    int client_sock;
    vector<string> all_words;
    int k;
    int p;
};
void* handle_client(void* arg) {
    client_data* data = (client_data*)arg;
    int client_sock = data->client_sock;
    vector<string> all_words = data->all_words;
    int k = data->k;
    int p = data->p;
    int m = all_words.size();

    bool ind = false;
    while (true) {
        char message[1024] = {0};
        int bytes_received = recv(client_sock, message, sizeof(message) - 1, 0);
        if (bytes_received <= 0) {
            cout << "Client disconnected." << endl;
            close(client_sock);
            break;
        }
        message[bytes_received] = '\0';
        cout << "Received message: " << message << endl;

        int j = 0;
        int offset = 0;
        while (message[j] != '\n') {
            offset = offset * 10 + (message[j] - '0');
            j++;
        }

        string message_to_send = "";
        bool is_this_last_offset = false;
        if (offset >= m) {
            message_to_send = "$$\n";
            send(client_sock, message_to_send.c_str(), message_to_send.length(), 0);
        } 
        else {
            if (offset + k >= m) {
                is_this_last_offset = true;
            }
            vector<string> to_send;
            for (int i = offset; i < min(m, offset + k); i++) {
                to_send.push_back(all_words[i]);
            }
            int t = to_send.size();
            for(auto str:to_send){
                cout<<str;
            }
            int start = 0;
            while (start < t) {
                message_to_send = "";
                for (int i = start; i < min(t, (start + p)); i++) {
                    message_to_send += to_send[i];
                }
                start = start + p;
                if(start >= t && is_this_last_offset){
                    message_to_send += EOF;
                }
                message_to_send += "\n";
                cout << "packet : " << message_to_send << endl;
                send(client_sock, message_to_send.c_str(), message_to_send.length(), 0);
            }
            // if (is_this_last_offset) {
            //     message_to_send = EOF;
            //     send(client_sock, message_to_send.c_str(), message_to_send.length(), 0);

            // } 
        }
    }
    close(client_sock);
    delete data;
    pthread_exit(nullptr);
}

int main() {
    unordered_map<string, string> json_mp;
    ifstream bin;
    bin.open("output.txt");
    string key;
    while (bin >> key) {
        string val;
        bin >> val;
        json_mp[key] = val;
    }
    bin.close();

    int serverport, n, k, p;
    n = stoi(json_mp["n"]);
    k = stoi(json_mp["k"]);
    p = stoi(json_mp["p"]);
    string filename = json_mp["filename"];
    serverport = stoi(json_mp["server_port"]);
    const char* server_ip = json_mp["server_ip"].c_str();

    vector<string> all_words = read_from_txt_file(filename);


    int server_socket = socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in server_address;
    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = INADDR_ANY;
    server_address.sin_port = htons(serverport);

    int connection_status = ::bind(server_socket, (struct sockaddr*)&server_address, sizeof(server_address));

    listen(server_socket, 10);
    cout << "Waiting for connections..." << endl;
    
    while (true) {
        sockaddr_in client_address;
        socklen_t client_address_len = sizeof(client_address);
        int client_sock = accept(server_socket, (struct sockaddr*)&client_address, &client_address_len);
        

        cout << "Client connected!" << endl;

        
        client_data* data = new client_data;  // Use new to allocate memory
        data->client_sock = client_sock;
        data->all_words = all_words;
        data->k = k;
        data->p = p;
        pthread_t thread_id;
        int connection =pthread_create(&thread_id, nullptr, handle_client, (void*)data);
        pthread_detach(thread_id);  // Detach thread to let it clean up after itself
        
    }
    

    close(server_socket);
    return 0;
}
