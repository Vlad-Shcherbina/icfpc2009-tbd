CC=cc
CFLAGS=-Wall -O2
#-DDEBUG
LDFLAGS=-lm
OBJS=ovm.o solver.o

ovm: ${OBJS}
	${CC} ${LDFLAGS} ${OBJS} -o ovm

%.o: %.c
	${CC} ${CFLAGS} -c $<

clean:
	rm ovm.o ovm
