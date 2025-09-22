#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <cstring>
#include <queue>
#include <unordered_map>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <mutex>
#include <condition_variable>

using namespace std;

// Global mutex and condition variable to synchronize access to the queue
mutex queue_mutex;
condition_variable queue_cv;

struct client_data;

// Struct for server data
struct server_data {
    queue<pair<client_data*, string>> q;  // Queue of pairs of client_data pointer and input message
    int rem;  // Number of remaining clients to be served

    server_data(int n) : rem(n) {}  // Constructor to initialize rem
};

// Struct for client data
struct client_data {
    int client_sock;
    vector<string> all_words;
    int k;
    int p;
    int client_id;
    int socket_id;
    bool is_done = false;
    server_data* server_state;  // Pointer to the server state

    client_data(server_data* state, int id, int sock_id) : server_state(state), client_id(id), socket_id(sock_id){}  // Constructor to initialize server_state
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
    for (auto& i : v) {
        ans += i;
    }
    return ans;
}

// Queue solver function
void* queue_solver(void* arg) {
    server_data* server = (server_data*) arg;
    while (true) {
        unique_lock<mutex> lock(queue_mutex);
        queue_cv.wait(lock, [&server]() { return !server->q.empty(); });  // Wait until the queue is not empty

        pair<client_data*, string> p1 = (server->q).front();
        (server->q).pop();
        lock.unlock();

        client_data* data = p1.first;
        string message_to_send = "";
        int client_sock = data->client_sock;
        vector<string> all_words = data->all_words;
        int k = data->k;
        int p = data->p;
        int m = all_words.size();
        int j = 0;
        int offset = 0;
        string message = p1.second;

        // Parse offset from the received message
        while (message[j] != '\n') {
            offset = offset * 10 + (message[j] - '0');
            j++;
        }
        cout<<client_sock<<" "<<offset<<endl;
        bool is_this_last_offset = false;
        if (offset >= m) {
            message_to_send = "$$\n";  // All words have been sent
            send(client_sock, message_to_send.c_str(), message_to_send.length(), 0);
            data->is_done = true;
            server->rem = max(server->rem - 1, 0);
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
                for (int i = start; i < min(t, start + p); i++) {
                    message_to_send += to_send[i];
                }
                start = start + p;
                if(start >= t && is_this_last_offset){
                    message_to_send += EOF;
                }
                message_to_send += "\n";
                
                cout << "Packet: " << message_to_send << " to client socket: " << client_sock << endl;
                send(client_sock, message_to_send.c_str(), message_to_send.length(), 0);
            }

            if (is_this_last_offset) {
                
                data->is_done = true;
                close(client_sock);
                delete data;  // Clean up memory for the client
                server->rem -= 1;
            }
        }
    }
}

// Client handling function for each thread
void* handle_client(void* arg) {
    client_data* data = (client_data*)arg;
    int client_sock = data->client_sock;

    while (true) {
        if (data->is_done) {
            return NULL;  // Exit when the client is done
        } else {
            char message[1024] = {0};
            int bytes_received = recv(client_sock, message, sizeof(message) - 1, 0);
            if (bytes_received <= 0) {
                close(client_sock);
                break;  // Exit on error or disconnect
            }

            string temp_message(message);

            {
                lock_guard<mutex> lock(queue_mutex);
                data->server_state->q.push({data, temp_message});
            }
            queue_cv.notify_one();  // Notify solver thread that new data is available
        }
    }

    return NULL;
}

int main() {
    unordered_map<string, string> json_mp;
    ifstream bin("output.txt");
    string key;
    while (bin >> key) {
        string val;
        bin >> val;
        json_mp[key] = val;
    }
    bin.close();

    int serverport = stoi(json_mp["server_port"]);
    int n = stoi(json_mp["n"]);
    int k = stoi(json_mp["k"]);
    int p = stoi(json_mp["p"]);
    string filename = json_mp["filename"];
    vector<string> all_words = read_from_txt_file(filename);

    int server_socket = socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in server_address;
    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = INADDR_ANY;
    server_address.sin_port = htons(serverport);

    ::bind(server_socket, (struct sockaddr*)&server_address, sizeof(server_address));
    listen(server_socket, n+4);

    cout << "Waiting for connections..." << endl;

    server_data server_state(n+4);
    pthread_t server_thread;
    pthread_create(&server_thread, nullptr, queue_solver, (void*)&server_state);

    vector<pthread_t> client_threads;
    int client_count = 0; 

    while (true) {
        sockaddr_in client_address;
        socklen_t client_address_len = sizeof(client_address);
        int client_sock = accept(server_socket, (struct sockaddr*)&client_address, &client_address_len);

        cout << "Client connected!" << endl;

        client_data* data;
        if(client_count < 5){
            data = new client_data(&server_state, 0, client_count % 5);
        }
        else{
            data = new client_data(&server_state, client_count - 4, 0);  
        } // Allocate memory for the client data
        data->client_sock = client_sock;
        data->all_words = all_words;
        data->k = k;
        data->p = p;

        pthread_t client_thread;
        pthread_create(&client_thread, nullptr, handle_client, (void*)data);
        client_threads.push_back(client_thread);
        client_count++;
    }

    for (pthread_t thread : client_threads) {
        pthread_join(thread, nullptr);
    }

    pthread_join(server_thread, nullptr);
    close(server_socket);

    return 0;
}
