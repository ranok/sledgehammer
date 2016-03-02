libsledge: libsledge.o
	gcc -shared -Wl,-soname,libsledge.so -o libsledge.so libsledge.o -ldl

libsledge.o: libsledge.c
	gcc -c -fPIC libsledge.c -ldl

clean:
	-rm libsledge.so libsledge.o