CC=cc
CFLAGS=-Wall -O2
LDFLAGS=-lm

ovm: ovm.o
	${CC} ${LDFLAGS} -o ovm ovm.o

%.o: %.c
	${CC} ${CFLAGS} -c $<
