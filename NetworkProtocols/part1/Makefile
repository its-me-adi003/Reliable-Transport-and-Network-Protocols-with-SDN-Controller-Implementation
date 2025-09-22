
build:
	g++ -o server server.cpp
	g++ -o client client.cpp

run: 
	python3 jsonread.py
	./server &
	sleep 1
	./client

plot: 
	python3 plot.py
