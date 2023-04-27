CC = clang
CFLAGS = -Wall -std=c99 -pedantic

PYTHON_INC_PATH = -I/usr/include/python3.10 -I/usr/include/python3.10
PYTHON_LIB_PATH = -lcrypt -ldl  -lm -lm 
PY_VERSION = python3.10

all: libmol.so _molecule.so

libmol.so: mol.o
	$(CC) $(CFLAGS) mol.o -shared -o libmol.so -lm

molecule_wrap.o: molecule_wrap.c mol.c
	$(CC) $(CFLAGS) -c molecule_wrap.c -I$(PYTHON_INC_PATH) -fPIC -o molecule_wrap.o

_molecule.so: molecule_wrap.o libmol.so
	$(CC) $(CFLAGS) molecule_wrap.o -shared -o _molecule.so libmol.so -L$(PYTHON_LIB_PATH) -l$(PY_VERSION) -lm

molecule_wrap.c: mol.h molecule.i
	swig -python molecule.i

mol.o: mol.c mol.h
	$(CC) $(CFLAGS) -c mol.c -fPIC -o mol.o

clean:
	rm -f *.o *.so molecule.py molecule_wrap.c