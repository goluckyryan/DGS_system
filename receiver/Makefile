CC=g++
CFLAG= -std=c++98 -O3 -Wall -Wextra
# CFLAG= -g -Wall -Wextra

all: tcp_Receiver

tcp_Receiver: tcp_Receiver.cpp constant.h
	$(CC) $(CFLAG) tcp_Receiver.cpp -o tcp_Receiver 

clean:
	-rm tcp_Receiver
