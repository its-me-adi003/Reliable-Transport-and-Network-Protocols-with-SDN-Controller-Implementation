
build:
	g++ -o server server.cpp
	g++ -o client client.cpp

run: 
	python3 jsonread.py
	./server &
	sleep 1
	./client
	sleep 1
	python3 terminate.py

plot: 
	python3 plot.py
