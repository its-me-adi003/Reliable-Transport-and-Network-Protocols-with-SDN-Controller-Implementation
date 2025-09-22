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
#include <mutex>
#include <chrono>

using namespace std;


struct server_data {
    atomic<bool> busy{false};
    atomic<int> socket_id{-1};  // Socket ID now atomic
    atomic<std::chrono::time_point<std::chrono::system_clock>*> start_time;
    atomic<std::chrono::time_point<std::chrono::system_clock>*> last_concurrent_time;
    atomic<bool> collide{false};  // Now an atomic flag
    atomic<int> active_clients{0};  // Atomic counter for active clients

    server_data() {
        // Initialize the time points with atomic pointers
        auto now = new chrono::time_point<chrono::system_clock>(chrono::system_clock::now());
        start_time.store(now);
        last_concurrent_time.store(now);
    }

    ~server_data() {
        // Clean up atomic pointer memory
        delete start_time.load();
        delete last_concurrent_time.load();
    } 
};

// Function to read words from file
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
// Helper function to combine vector of strings into one string
string helper(vector<string>& v) {
    string ans = "";
    for (auto i : v) {
        ans += i;
    }
    return ans;
}

// Struct to hold client data
struct client_data {
    int client_sock;
    vector<string> all_words;
    int k;
    int p;
    server_data* server_state;  // Pointer to the server state
};

// Client handling function for each thread
void* handle_client(void* arg) {
    client_data* data = (client_data*)arg;
    int client_sock = data->client_sock;
    vector<string> all_words = data->all_words;
    int k = data->k;
    int p = data->p;
    int m = all_words.size();
    server_data* server_state = data->server_state;
    cout<<client_sock<<endl;
    while (true) {
        // Synchronize access to shared state
        bool is_end_of_communication =false;

        while (true){
            char message[1024] = {0};
            auto now = new chrono::time_point<chrono::system_clock>(chrono::system_clock::now());
            auto last_time = server_state->last_concurrent_time.load();
            int bytes_received = recv(client_sock, message, sizeof(message) - 1, 0);
            bool does_collide=false;
            if (bytes_received <= 0) {
             //   cout << "Client disconnected." << endl;
                close(client_sock);
                break;
            }
            
            // Receive message from client
            
            message[bytes_received] = '\0';
            cout << "Received message: " << message << endl;

            // Process the message (as before)
            int j = 0;
            int offset = 0;
            while (message[j] != '\n') {
                offset = offset * 10 + (message[j] - '0');
                j++;
            }

            string message_to_send = "";
            
            if (*now<*last_time){
                if(server_state->socket_id==client_sock){
                    message_to_send="HUH!\n";
                    send(client_sock, message_to_send.c_str(), message_to_send.length(), 0);
                    server_state->active_clients--;
                    server_state->collide =false;
                    server_state->socket_id=-1;
                    break;
                }
                else{
                    message_to_send="HUH!\n";
                    send(client_sock, message_to_send.c_str(), message_to_send.length(), 0);
                    server_state->active_clients--;
                    server_state->collide =true;
                    break;
                }
            }
            if (server_state->active_clients>1){
                if(server_state->socket_id==client_sock){
                    message_to_send="HUH!\n";
                    send(client_sock, message_to_send.c_str(), message_to_send.length(), 0);
                    server_state->active_clients--;
                    server_state->collide =false;
                    server_state->last_concurrent_time.compare_exchange_strong(last_time, now);
                    server_state->socket_id=-1;
                    break;
                }
                else{
                    message_to_send="HUH!\n";
                    send(client_sock, message_to_send.c_str(), message_to_send.length(), 0);
                    server_state->active_clients--;
                    server_state->last_concurrent_time.compare_exchange_strong(last_time, now);
                    server_state->collide =true;
                    break;
                }
            }

            server_state->active_clients++;  // Increase the count of active clients
            server_state->busy=true;
            server_state->socket_id=client_sock;
            bool is_this_last_offset = false;
            if (offset >= m) {
                message_to_send = "$$\n";
                send(client_sock, message_to_send.c_str(), message_to_send.length(), 0);
            } else {
                if (offset + k >= m) {
                    is_this_last_offset = true;
                }
                vector<string> to_send;
                for (int i = offset; i < min(m, offset + k); i++) {
                    to_send.push_back(all_words[i]);
                }
                int t = to_send.size();
                int start = 0;
                while (start < t) {
                    message_to_send = "";
                    if (server_state->active_clients > 1) {
                        if (server_state->socket_id == client_sock) {
                            message_to_send = "HUH!\n";
                            send(client_sock, message_to_send.c_str(), message_to_send.length(), 0);
                            server_state->active_clients--;
                            server_state->collide = false;
                            server_state->last_concurrent_time.compare_exchange_strong(last_time, now);
                            server_state->socket_id = -1;
                            break;
                        } else {
                            message_to_send = "HUH!\n";
                            send(client_sock, message_to_send.c_str(), message_to_send.length(), 0);
                            server_state->active_clients--;
                            server_state->last_concurrent_time.compare_exchange_strong(last_time, now);
                            server_state->collide = true;
                            break;
                        }
                    }
                    message_to_send = "";
                    for (int i = start; i < min(t, (start + p)); i++) {
                        message_to_send += to_send[i];
                    }
                    message_to_send += "\n";
                    start = start + p;
                    cout << "packet : " << message_to_send << endl;
                    send(client_sock, message_to_send.c_str(), message_to_send.length(), 0);
                }
                if(does_collide){break;}
                if (is_this_last_offset) {
                    is_end_of_communication=true;
                    message_to_send = EOF;
                    send(client_sock, message_to_send.c_str(), message_to_send.length(), 0);
                }
            }

            server_state->active_clients--;
            server_state->socket_id=-1;
        }
        if(is_end_of_communication){
            break;
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
    int opt = 1;
    if (setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }
    sockaddr_in server_address;

    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = INADDR_ANY;
    server_address.sin_port = htons(serverport);

    int connection_status = ::bind(server_socket, (struct sockaddr*)&server_address, sizeof(server_address));
    vector<pthread_t> threads; 
    listen(server_socket, n);
    cout << "Waiting for connections..." << endl;

    server_data server_state;
    int num_client_connected = 0;
    while (true) {
        sockaddr_in client_address;
        socklen_t client_address_len = sizeof(client_address);
        int client_sock = accept(server_socket, (struct sockaddr*)&client_address, &client_address_len);
        num_client_connected++;
        cout << "Client connected!" << endl;

        client_data* data = new client_data;  // Use new to allocate memory
        data->client_sock = client_sock;
        data->all_words = all_words;
        data->k = k;
        data->p = p;
        data->server_state = &server_state;

        pthread_t thread_id;
        int connection = pthread_create(&thread_id, nullptr, handle_client, (void*)data);
        threads.push_back(thread_id);
        if(num_client_connected == n){
            break;
        }
    }

    for (pthread_t thread : threads) {
        pthread_join(thread, nullptr);
    }

    close(server_socket);
    return 0;
}
