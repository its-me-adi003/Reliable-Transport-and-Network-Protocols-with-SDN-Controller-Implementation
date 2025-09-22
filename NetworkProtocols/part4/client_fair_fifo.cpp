#include <iostream>
#include <fstream>
#include <sstream>
#include <unordered_map>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <vector>
#include <chrono>
#include <map>

using namespace std;

// Structure to hold socket data for threading
struct socket_thread_data {
    int client_id;       // Client ID
    int socket_id;       // Socket ID (from 1 to 5)
    string server_ip;    // Server IP address
    int serverport;      // Server port number
    int k;               // Number of words in one chunk
    int p;               // Number of words in one packet
    int offset;          // Offset to start from
};

vector<double> client_runtimes;
pthread_mutex_t runtime_mutex = PTHREAD_MUTEX_INITIALIZER;
// Function to extract substrings
string get_substring(string &s, int i, int j) {
    string ans = "";
    for (int l = i; l <= j; l++) {
        ans += s[l];
    }
    return ans;
}

// Function to handle each socket in a separate thread for the same client
void* handle_socket(void* arg) {
    socket_thread_data* data = (socket_thread_data*)arg;
    int client_id = data->client_id;
    int socket_id = data->socket_id;
    string server_ip = data->server_ip;
    int serverport = data->serverport;
    int k = data->k;
    int p = data->p;
    int offset = data->offset;

    // Create socket for this thread
    int client_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (client_socket < 0) {
        cerr << "Client " << client_id << ", Socket " << socket_id << ": Failed to create socket" << endl;
        pthread_exit(nullptr);
    }

    // Server address setup
    sockaddr_in server_address;
    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(serverport);

    // Convert IP address
    int ip_status = inet_pton(AF_INET, server_ip.c_str(), &server_address.sin_addr);
    if (ip_status <= 0) {
        cerr << "Client " << client_id << ", Socket " << socket_id << ": Invalid IP address" << endl;
        close(client_socket);
        pthread_exit(nullptr);
    }

    // Connect to server
    int connection_status = connect(client_socket, (struct sockaddr*)&server_address, sizeof(server_address));
    if (connection_status < 0) {
        cerr << "Client " << client_id << ", Socket " << socket_id << ": Failed to connect to server" << endl;
        close(client_socket);
        pthread_exit(nullptr);
    }

    cout << "Client " << client_id << ", Socket " << socket_id << ": Connected to server" << endl;

    map<string, int> counter;
    bool end_of_file = false;

    while (true) {
        string request = to_string(offset) + "\n";
        send(client_socket, request.c_str(), request.length(), 0);

        int num_of_words = 0;
        while (true) {
            char message[1024] = {0};
            int length = recv(client_socket, message, sizeof(message) - 1, 0);

            message[length] = '\0'; // Null terminate the string
            string response(message);
            if(response == "$$\n"){
                end_of_file = true;
                break;
            }
            // Parse and count words
            string temp = "";
            for (int i = 0; i < length; i++) {
                if (message[i] == EOF) {
                    end_of_file = true;
                }
                if (message[i] == '\n' || message[i] == EOF) continue;
                else if (message[i] == ',') {
                    counter[temp]++;
                    temp = "";
                    num_of_words++;
                } else {
                    temp += message[i];
                }
            }

            if (num_of_words >= k || end_of_file) {
                break;
            }
        }

        if (end_of_file) {
            break;
        }

        offset += 5*k;
    }

    // Output results for this socket
    string new_filename = "output_client" + to_string(client_id) + "_socket" + to_string(socket_id) + ".txt";
    ofstream dout;
    dout.open(new_filename);
    for (const auto& entry : counter) {
        dout << entry.first << ": " << entry.second << endl;
    }
    dout.close();

    close(client_socket);
    pthread_exit(nullptr);
}

// Structure to hold client data for threading
struct client_thread_data {
    int client_id;       // Client ID
    string server_ip;    // Server IP address
    int serverport;      // Server port number
    int k;               // Number of words in one chunk
    int p;               // Number of words in one packet
};

// Modify handle_client to spawn 5 threads (for 5 sockets) per client
void* rogue_handle_client(void* arg) {
    client_thread_data* data = (client_thread_data*)arg;
    int client_id = data->client_id;
    string server_ip = data->server_ip;
    int serverport = data->serverport;
    int k = data->k;
    int p = data->p;
    auto start_time = chrono::high_resolution_clock::now();

    pthread_t socket_threads[5];  // 5 threads for each socket
    socket_thread_data socket_data[5];

    for (int i = 0; i < 5; i++) {
        socket_data[i].client_id = client_id;
        socket_data[i].socket_id = i + 1;  // Socket ID from 1 to 5
        socket_data[i].server_ip = server_ip;
        socket_data[i].serverport = serverport;
        socket_data[i].k = k;
        socket_data[i].p = p;
        socket_data[i].offset = i * k;  // Offset for each socket to start from different chunks

        int status = pthread_create(&socket_threads[i], nullptr, handle_socket, (void*)&socket_data[i]);
        if (status != 0) {
            cerr << "Failed to create thread for client " << client_id << ", socket " << i + 1 << endl;
        }
    }

    for (int i = 0; i < 5; i++) {
        pthread_join(socket_threads[i], nullptr);
    }

    auto end_time = chrono::high_resolution_clock::now();
    chrono::milliseconds runtime = chrono::duration_cast<chrono::milliseconds>(end_time - start_time);
    pthread_mutex_lock(&runtime_mutex);  // Lock the mutex to safely add runtime
    client_runtimes.push_back(runtime.count());
    pthread_mutex_unlock(&runtime_mutex);  

    pthread_exit(nullptr);
}
void* handle_client(void* arg) {
    client_thread_data* data = (client_thread_data*)arg;
    int client_id = data->client_id;
    string server_ip = data->server_ip;
    int serverport = data->serverport;
    int k = data->k;
    int p = data->p;

    auto start_time = chrono::high_resolution_clock::now();
    // Create client socket
    int client_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (client_socket < 0) {
        cerr << "Client " << client_id << ": Failed to create socket" << endl;
        pthread_exit(nullptr);
    }

    // Server address setup
    sockaddr_in server_address;
    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(serverport);

    // Convert IP address
    int ip_status = inet_pton(AF_INET, server_ip.c_str(), &server_address.sin_addr);
    if (ip_status <= 0) {
        cerr << "Client " << client_id << ": Invalid IP address" << endl;
        close(client_socket);
        pthread_exit(nullptr);
    }

    // Connect to server
    int connection_status = connect(client_socket, (struct sockaddr*)&server_address, sizeof(server_address));
    if (connection_status < 0) {
        cerr << "Client " << client_id << ": Failed to connect to server" << endl;
        close(client_socket);
        pthread_exit(nullptr);
    }

    cout << "Client " << client_id << ": Connected to server" << endl;

    // Keep track of the offset for this client
    int offset = 0;
    map<string, int> counter;
    bool end_of_file = false;

    while (true) {
        string request = to_string(offset) + "\n";
        send(client_socket, request.c_str(), request.length(), 0);
        int num_of_words = 0;
        // bool end_of_iteration = false;
        
        while (true) {
            char message[1024] = {0};
            int length = recv(client_socket, message, sizeof(message) - 1, 0);

            message[length] = '\0'; // Null terminate the string
            string response(message);

            
            // Parse and count words
            string temp = "";
            for (int i = 0; i < length; i++) {
                if (message[i] == EOF) {
                    end_of_file = true;
                }
                if (message[i] == '\n' || message[i] == EOF) continue;
                else if (message[i] == ',') {
                    counter[temp]++;
                    temp = "";
                    num_of_words++;
                }
                else {
                    temp += message[i];
                }
            }

            // Break inner loop if EOI or EOF is received
            if (num_of_words >= k || end_of_file) {
                break;
            }
        }

        // If EOF, stop the client
        if (end_of_file) {
            break;
        }

        offset += k;
    }

    // Output results for this client
    // cout << "Client " << client_id << ": Word counts" << endl;

    string new_filename = "output_"+to_string(client_id)+".txt";
    ofstream dout;
    dout.open(new_filename);
    for (const auto& entry : counter) {
        dout << entry.first << ": " << entry.second << endl;
    }
    dout.close();

    // Close the client socket
    close(client_socket);

    auto end_time = chrono::high_resolution_clock::now();
    chrono::milliseconds runtime = chrono::duration_cast<chrono::milliseconds>(end_time - start_time);
    pthread_mutex_lock(&runtime_mutex);  // Lock the mutex to safely add runtime
    client_runtimes.push_back(runtime.count());
    pthread_mutex_unlock(&runtime_mutex);  

    pthread_exit(nullptr);
}

int main() {
    // Read parameters from output.txt file
    unordered_map<string, string> json_mp;
    ifstream bin("output.txt");
    if (!bin.is_open()) {
        cerr << "Failed to open file 'output.txt'" << endl;
        return -1;
    }

    string key;
    while (bin >> key) {
        string val;
        bin >> val;
        json_mp[key] = val;
    }
    bin.close();

    // Parse the parameters from the file
    int n = stoi(json_mp["n"]);             // Number of clients
    int k = stoi(json_mp["k"]);             // Number of words in one chunk
    int p = stoi(json_mp["p"]);             // Number of words in one packet
    int serverport = stoi(json_mp["server_port"]);
    string server_ip = json_mp["server_ip"];

    // Create threads for each client
    vector<pthread_t> client_threads(n);
    vector<client_thread_data> client_data(n);

    auto start = chrono::high_resolution_clock::now();
    client_data[0].client_id = 1;
    client_data[0].server_ip = server_ip;
    client_data[0].serverport = serverport;
    client_data[0].k = k;
    client_data[0].p = p;
    int status = pthread_create(&client_threads[0], nullptr, rogue_handle_client, (void*)&client_data[0]);
    if (status != 0) {
        cerr << "Failed to create thread for client " <<  1 << endl;
    }
    for (int i = 1; i < n; i++) {
        client_data[i].client_id = i + 1;
        client_data[i].server_ip = server_ip;
        client_data[i].serverport = serverport;
        client_data[i].k = k;
        client_data[i].p = p;

        // Create a thread for each client
        int status = pthread_create(&client_threads[i], nullptr, handle_client, (void*)&client_data[i]);
        if (status != 0) {
            cerr << "Failed to create thread for client " << i + 1 << endl;
        }
    }

    // Join all client threads
    for (int i = 0; i < n; i++) {
        pthread_join(client_threads[i], nullptr);
    }

    auto end = chrono::high_resolution_clock::now();
    auto duration = chrono::duration_cast<chrono::milliseconds>(end - start).count();
    ofstream eout;
    eout.open("res.txt");
    eout << duration << " ";
    eout.close();

    double sum1 = 0;
    double sum2 = 0;
    for(auto &v:client_runtimes){
        v = 1/v;
    }
    for(auto val:client_runtimes){
        sum1 += val;
        sum2 += (val*val);
        cout<<val<<" ";
    }
    double fairness_idx = (sum1*sum1)/(sum2 * n);
    cout<<"\nFairness index :"<<fairness_idx<<endl;

    ofstream fout;
    fout.open("fairness.txt");
    fout<<fairness_idx<<" ";
    fout.close();


    

    return 0;
}
