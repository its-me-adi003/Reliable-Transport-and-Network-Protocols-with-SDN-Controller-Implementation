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

using namespace std;

string get_substring(string &s,int i,int j){
    string ans="";
    for(int l=i;l<=j;l++){
        ans+=s[l];
    }
    return ans;
}


int main() {
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

    int serverport, n, k, p;
    n = stoi(json_mp["n"]);
    k = stoi(json_mp["k"]);
    p = stoi(json_mp["p"]);
    serverport = stoi(json_mp["server_port"]);
    const char* server_ip = json_mp["server_ip"].c_str();

    int client_socket = socket(AF_INET, SOCK_STREAM, 0);
    

    sockaddr_in server_id;
    server_id.sin_family = AF_INET;
    server_id.sin_port = htons(serverport);

    int ip_status = inet_pton(AF_INET, server_ip, &server_id.sin_addr);
        

    int connection_status = connect(client_socket, (struct sockaddr*)&server_id, sizeof(server_id)) ;
    int offset = 0;
    map<string,int>counter;
    bool indicator=false;
    bool end_of_file = 0;
    while(true){
        
        string request = to_string(offset) +"\n";
        int send_status=send(client_socket, request.c_str(), request.length(), 0);

        bool end_of_iteration = 0;
        while (true) {
            
            char message[1024] = {0};
            int length = recv(client_socket, message, sizeof(message) - 1, 0);
            string for_check (message);

            cout << "Received from server: " << message << endl;
            for(int i=0;i<(length-2);i++){
                
                if(get_substring(for_check,i,i+2) == "EOI") {
                    end_of_iteration = 1;
                }
            }
            string temp = "";
            for(int i=0;i<length;i++){
                if(message[i] == EOF){
                    end_of_file = 1;
                }
                if(message[i] == '\n' || message[i] == EOF) continue;
                else if(message[i] == ','){
                    counter[temp]++;
                    temp = "";
                }
                else{
                    temp += message[i];
                }
            }
            
            if(end_of_file || end_of_iteration){
                break;
            }


        }

        //     if(length <= 0 ) break;
        //     cout<<length<<endl;
        //     if(message=="end_of_parsing\n"){
        //         break;
        //     }
        //     string temp="";
        //     for(int i=0;i<length;i++){
        //         if (message[i]==EOF){
        //             counter[temp]+=1;
        //             temp="";
        //             indicator=true;
        //             break;
        //         }
        //         else if (message[i]==','){
        //             counter[temp]+=1;
        //             temp="";
        //         }
        //         else{
        //             temp+=message[i];
        //         }
        //     }
        //     if(indicator==false and (temp!="")){
        //         counter[temp]+=1;
        //     }
        //     if(indicator){
        //         break;
        //     }
        //     cout << "Received from server: " << message << endl;
        //     if(to_break){
        //         break;
        //     } 
        // }
        // if (indicator){
        //     break;
        // } 


        if(end_of_file){
            break;
        } 

        offset+=k; 
        cout<<"offset after loop :"<<offset<<endl;
    }
    

    cout<<endl<<endl<<endl<<endl;
    cout<<counter.size()<<endl;
    for(auto it = counter.begin();it!=counter.end();it++){
        cout<<it->first<<", "<<it->second<<endl;
    }
    close(client_socket);

    return 0;
}
