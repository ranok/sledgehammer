libsledge: libsledge.o
	gcc -shared -o libsledge.so libsledge.o

libsledge.o: libsledge.c
	gcc -c -fPIC libsledge.c

clean:
	-rm libsledge.so libsledge.o