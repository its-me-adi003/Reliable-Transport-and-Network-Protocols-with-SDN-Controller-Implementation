build:
	g++ -o client_rr client_rr.cpp
	g++ -o client_fifo client_fifo.cpp
	g++ -o server_rr server_rr.cpp
	g++ -o server_fifo server_fifo.cpp
	g++ -o server_fair_fifo server_fair_fifo.cpp
	g++ -o server_fair_rr server_fair_rr.cpp
	g++ -o client_fair_rr client_fair_rr.cpp
	g++ -o client_fair_fifo client_fair_fifo.cpp
	

run-rr:
	python3 jsonread.py
	./server_rr &
	sleep 1
	./client_rr
	sleep 1
	python3 terminate.py
run-fifo:
	python3 jsonread.py
	./server_fifo &
	sleep 1
	./client_fifo
	sleep 1
	python3 terminate.py

run:
	python3 jsonread.py
	./server_rr &
	sleep 1
	./client_rr
	sleep 1
	python3 terminate.py
	sleep 1
	python3 jsonread.py
	./server_fifo &
	sleep 1
	./client_fifo
	sleep 1
	python3 terminate.py
plot:
	python3 plot.py
fairness:
	python3 jsonread.py
	./server_fair_fifo &
	sleep 1
	./client_fair_fifo
	sleep 1
	python3 terminate.py
	sleep 1
	./server_fair_rr &
	sleep 1
	./client_fair_rr
	sleep 1
	python3 terminate.py