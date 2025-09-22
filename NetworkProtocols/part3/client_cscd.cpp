#include <iostream>
#include <fstream>
#include <sstream>
#include <unordered_map>
#include <bits/stdc++.h>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <thread>
#include <chrono>
#include <random>

using namespace std;

string get_substring(string &s,int i,int j){
    string ans="";
    for(int l=i;l<=j;l++){
        ans+=s[l];
    }
    return ans;
}
struct client{
    map<string,int>counter;
    int client_socket = 0;
    int offset=0;
    bool end_of_file=false;
    int numcollisions=0;
    client(){
        offset=0;
        client_socket = socket(AF_INET, SOCK_STREAM, 0);
        end_of_file=false;
    }
    

};
void *helper(void *arg){
   // cout<<"hihgh"<<endl;
    unordered_map<string, string> json_mp;
    ifstream bin("output.txt");
    if (!bin.is_open()) {
        cerr << "Failed to open file 'output.txt'" << endl;
        return NULL;
    }
    string key;
    while (bin >> key) {
        string val;
        bin >> val;
        json_mp[key] = val;
    }
    bin.close();
    int serverport, n, k, p,time_slot;
    n = stoi(json_mp["n"]);
    k = stoi(json_mp["k"]);
    p = stoi(json_mp["p"]);
    time_slot = stoi(json_mp["T"]);
    serverport = stoi(json_mp["server_port"]);
    const char* server_ip = json_mp["server_ip"].c_str();
    client* data = (client*)arg;
    int client_socket = data->client_socket;
   // cout<<"this client: "<<client_socket<<endl;
    sockaddr_in server_id;
    server_id.sin_family = AF_INET;
    server_id.sin_port = htons(serverport);
    int ip_status = inet_pton(AF_INET, server_ip, &server_id.sin_addr);
    int connection_status = connect(client_socket, (struct sockaddr*)&server_id, sizeof(server_id)) ;
    
    int* offset = &(data->offset);
    map<string,int>&counter=data->counter;
    bool indicator=false;
    bool end_of_file = data->end_of_file;
    while(true){
        string request = to_string(*offset) +"\n";
        random_device rd;  // Seed
        mt19937 gen(rd());  // Mersenne Twister RNG
        uniform_real_distribution<> dis(0,(int)pow(2,data->numcollisions)-1);
        int random_value = dis(gen);
        auto sleep_duration1 = chrono::milliseconds(random_value*time_slot);
        this_thread::sleep_for(sleep_duration1);
      //  cout<<"hi"<<endl;
        

        auto start_time = chrono::steady_clock::now();
        string send_request="BUSY?\n";
        int send_status1=send(client_socket, send_request.c_str(), send_request.length(), 0);
        
        bool ready_to_send=false;
      //  cout<<"mdwfnissvis"<<endl;
        char message[1024] = {0};
        int length = recv(client_socket, message, sizeof(message) - 1, 0);
        
        string for_check (message);
        cout<<client_socket<<" "<<for_check<<endl;
        if(for_check=="IDLE\n"){
            ready_to_send=true;
        }
        if(for_check=="BUSY\n"){
            ready_to_send=false;
        }
       // cout<<client_socket<<" "<<ready_to_send<<endl;
        if (ready_to_send==false){
            auto end_time = chrono::steady_clock::now();
            auto elapsed_time = chrono::duration_cast<chrono::milliseconds>(end_time - start_time).count();
            auto sleep_duration = chrono::milliseconds(time_slot - elapsed_time);
            if (sleep_duration.count() > 0) {
                this_thread::sleep_for(sleep_duration);
            }
            else{
                cout<<"no time"<<endl;
            }
            continue;
        }


        int send_status=send(client_socket, request.c_str(), request.length(), 0);
        if (send_status == -1) {
            cerr << "Failed to send request to server." << endl;
            close(client_socket);
            return nullptr;
        }
        bool collision =false;
        int num_of_words=0;
        while (true) {
            char message[1024] = {0};
            int length = recv(client_socket, message, sizeof(message) - 1, 0);
            
            string for_check (message);

            cout << "Received from server: " << message << endl;
            for(int i=0;i<(length-4);i++){
                if(get_substring(for_check,i,i+4) == "HUH!\n") {
                    collision = 1;
                }
            }
            if(collision){break;}
            string temp = "";
            for(int i=0;i<length;i++){
                if(message[i] == EOF){
                    end_of_file = 1;
                }
                if(message[i] == '\n' || message[i] == EOF) continue;
                else if(message[i] == ','){
                    counter[temp]++;
                    temp = "";
                    num_of_words++;
                }
                else{
                    temp += message[i];
                }
            }
            
            if(end_of_file || num_of_words>=k){
                break;
            }


        }

        if(end_of_file){
            break;
        } 
        
        if(collision==false){
            *offset+=k; 
            data->numcollisions=0;
        }
        else{
            data->numcollisions++;
            cout<<"collision"<<endl;
        }
        cout<<"offset after loop :"<<*offset<<" "<<client_socket<<" "<<data->numcollisions<<endl;
        
        auto end_time = chrono::steady_clock::now();
        auto elapsed_time = chrono::duration_cast<chrono::milliseconds>(end_time - start_time).count();
        auto sleep_duration = chrono::milliseconds(time_slot - elapsed_time);
        if (sleep_duration.count() > 0) {
            this_thread::sleep_for(sleep_duration);
        }
        else{
            cout<<"no time"<<endl;
        }

    }
    

    string new_filename = "output_"+to_string(client_socket)+".txt";
    ofstream dout;
    dout.open(new_filename);
    for (const auto& entry : counter) {
        dout << entry.first << ", " << entry.second << endl;
    }
    dout.close();
    close(client_socket);
    return NULL;
}

int main() {
    
    vector<pthread_t>vec;
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
    int n;
    
    n = stoi(json_mp["n"]);
    for(int i=0;i<n;i++){
        pthread_t t;
        vec.push_back(t);
    }
    vector<client>client_vec;
    for(int i=0;i<n;i++){
        client client1;
        client_vec.push_back(client1);
    }
 //   cout<<"hi"<<endl;
    auto start = chrono::high_resolution_clock::now();

    for(int i=0;i<n;i++){
        pthread_create(&vec[i],NULL,helper,(void*)&client_vec[i]);
    }
    for(int i=0;i<n;i++){
        pthread_join(vec[i],NULL);
    }
    auto end = chrono::high_resolution_clock::now();
    auto duration = chrono::duration_cast<chrono::milliseconds>(end - start).count();
    ofstream eout;
    eout.open("res_cscd.txt");
    eout<<duration<<" ";
    eout.close();
    return 0;
}
