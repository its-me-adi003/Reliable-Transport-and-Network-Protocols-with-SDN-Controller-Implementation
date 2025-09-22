build:
	g++ -o server_beb server_beb.cpp
	g++ -o client_beb client_beb.cpp
	g++ -o server_cscd server_cscd.cpp
	g++ -o client_cscd client_cscd.cpp
	g++ -o server_aloha server_aloha.cpp
	g++ -o client_aloha client_aloha.cpp

run-aloha:
	python3 jsonread.py
	./server_aloha &
	sleep 1
	./client_aloha
	sleep 1
	python3 terminate.py 
	sleep 1

run-beb:
	python3 jsonread.py
	./server_beb &
	sleep 1
	./client_beb
	sleep 1
	python3 terminate.py 
	sleep 1
run-cscd:
	python3 jsonread.py
	./server_cscd &
	sleep 1
	./client_cscd
	sleep 1
	python3 terminate.py 
	sleep 1
plot:
	python3 plot.py


