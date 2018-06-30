CXX = g++-8
CXXFLAGS = -Wall --pedantic -O3 -std=c++1z `pkg-config --cflags opencv`
LDFLAGS = -lboost_program_options -lboost_system `pkg-config --libs opencv`

all: sentry


main.o: main.cpp
	$(CXX) $(CXXFLAGS) -c main.cpp

sentry.o: sentry.cpp
	$(CXX) $(CXXFLAGS) -c sentry.cpp


sentry: main.o sentry.o
	$(CXX) main.o sentry.o $(LDFLAGS) -o sentry

clean:
	rm *.o sentry

run:
	./sentry | sudo python3.6 sentry_only.py
