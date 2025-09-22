// #include <iostream>
// #include <fstream>
// #include <sstream>
// #include <unordered_map>
// #include <bits/stdc++.h>
// #include <cstring>
// #include <sys/socket.h>
// #include <netinet/in.h>
// #include <unistd.h>
// #include <arpa/inet.h>

// using namespace std;

// string get_substring(string &s,int i,int j){
//     string ans="";
//     for(int l=i;l<=j;l++){
//         ans+=s[l];
//     }
//     return ans;
// }


// int main() {
//     unordered_map<string, string> json_mp;
//     ifstream bin("output.txt");

//     if (!bin.is_open()) {
//         cerr << "Failed to open file 'output.txt'" << endl;
//         return -1;
//     }

//     string key;
//     while (bin >> key) {
//         string val;
//         bin >> val;
//         json_mp[key] = val;
//     }
//     bin.close();

//     int serverport, n, k, p;
//     n = stoi(json_mp["n"]);
//     k = stoi(json_mp["k"]);
//     p = stoi(json_mp["p"]);
//     serverport = stoi(json_mp["server_port"]);
//     const char* server_ip = json_mp["server_ip"].c_str();

//     int client_socket = socket(AF_INET, SOCK_STREAM, 0);
    

//     sockaddr_in server_id;
//     server_id.sin_family = AF_INET;
//     server_id.sin_port = htons(serverport);

//     int ip_status = inet_pton(AF_INET, server_ip, &server_id.sin_addr);
        

//     int connection_status = connect(client_socket, (struct sockaddr*)&server_id, sizeof(server_id)) ;
//     int offset = 0;
//     map<string,int>counter;
//     bool indicator=false;
//     bool end_of_file = 0;
//     while(true){
        
//         string request = to_string(offset) +"\n";
//         int send_status=send(client_socket, request.c_str(), request.length(), 0);

//         bool end_of_iteration = 0;
//         while (true) {
            
//             char message[1024] = {0};
//             int length = recv(client_socket, message, sizeof(message) - 1, 0);
//             string for_check (message);

//             cout << "Received from server: " << message << endl;
//             for(int i=0;i<(length-2);i++){
                
//                 if(get_substring(for_check,i,i+2) == "EOI") {
//                     end_of_iteration = 1;
//                 }
//             }
//             string temp = "";
//             for(int i=0;i<length;i++){
//                 if(message[i] == EOF){
//                     end_of_file = 1;
//                 }
//                 if(message[i] == '\n' || message[i] == EOF) continue;
//                 else if(message[i] == ','){
//                     counter[temp]++;
//                     temp = "";
//                 }
//                 else{
//                     temp += message[i];
//                 }
//             }
            
//             if(end_of_file || end_of_iteration){
//                 break;
//             }


//         }

//         //     if(length <= 0 ) break;
//         //     cout<<length<<endl;
//         //     if(message=="end_of_parsing\n"){
//         //         break;
//         //     }
//         //     string temp="";
//         //     for(int i=0;i<length;i++){
//         //         if (message[i]==EOF){
//         //             counter[temp]+=1;
//         //             temp="";
//         //             indicator=true;
//         //             break;
//         //         }
//         //         else if (message[i]==','){
//         //             counter[temp]+=1;
//         //             temp="";
//         //         }
//         //         else{
//         //             temp+=message[i];
//         //         }
//         //     }
//         //     if(indicator==false and (temp!="")){
//         //         counter[temp]+=1;
//         //     }
//         //     if(indicator){
//         //         break;
//         //     }
//         //     cout << "Received from server: " << message << endl;
//         //     if(to_break){
//         //         break;
//         //     } 
//         // }
//         // if (indicator){
//         //     break;
//         // } 


//         if(end_of_file){
//             break;
//         } 

//         offset+=k; 
//         cout<<"offset after loop :"<<offset<<endl;
//     }
    

//     cout<<endl<<endl<<endl<<endl;
//     cout<<counter.size()<<endl;
//     for(auto it = counter.begin();it!=counter.end();it++){
//         cout<<it->first<<", "<<it->second<<endl;
//     }
//     close(client_socket);

//     return 0;
// }

#include <iostream>
#include <fstream>
#include <sstream>
#include <unordered_map>
#include <cstring>
#include <chrono>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <vector>
#include <map>

using namespace std;

// Function to extract substrings
string get_substring(string &s, int i, int j) {
    string ans = "";
    for (int l = i; l <= j; l++) {
        ans += s[l];
    }
    return ans;
}

// Structure to hold client data for threading
struct client_thread_data {
    int client_id;       // Client ID
    string server_ip;    // Server IP address
    int serverport;      // Server port number
    int k;               // Number of words in one chunk
    int p;               // Number of words in one packet
};

// Function to handle each client in a separate thread
void* handle_client(void* arg) {
    client_thread_data* data = (client_thread_data*)arg;
    int client_id = data->client_id;
    string server_ip = data->server_ip;
    int serverport = data->serverport;
    int k = data->k;
    int p = data->p;

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
    cout << "Client " << client_id << ": Word counts" << endl;

    string new_filename = "output_"+to_string(client_id)+".txt";
    ofstream dout;
    dout.open(new_filename);
    for (const auto& entry : counter) {
        dout << entry.first << ", " << entry.second << endl;
    }
    dout.close();

    // Close the client socket
    close(client_socket);
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

    for (int i = 0; i < n; i++) {
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
    eout<<duration<<" ";
    eout.close();


    return 0;
}
