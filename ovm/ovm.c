#include <stdio.h>
#include <math.h>
#include <stdarg.h>
#include <string.h>

#define SIZE 16384
#define MASK 16383

/* so runtime */
int status = 0;
unsigned int mem_code[SIZE];
double mem_data[SIZE];
double port[SIZE];

/* guess what it is */
unsigned int strswitch( const char* s, ... ) {
	va_list op;
	unsigned int ret = 1;
	va_start( op, s );
	char *t = va_arg( op, char* );
	for(; t != 0; t = va_arg(op,char*), ret++ )
		if( !strcmp(s,t) )
			break;
	va_end( op );
	return (t==0)?0:ret;
}

/* вытирайте ноги */
int main( int argc, char *argv[] )
{
	if( argc < 2 )
	{
		printf( "BAKA YARO!\n" );
		return -1;
	}

	char* image_file = 0;
	char* port_read = 0, *port_write = 0; 
	int dump = 0, debug = 0;

	/* run through parameters for.. WHAT FOR AM I WRITING THIS???! */
	int i;
	for( i = 1; i < argc; i++ )
	{
		/* if this is an option */
		if( argv[i][0] == '-' )
			switch( strswitch((argv[i])+1,"u","pr","pw","d") )
			{
				case 1: /* do full dump (instructions and memory) */
					dump = 1;
					break;
				case 2: /* file where ports walues are */
					i++;
					if( i < argc )
						port_read = argv[i];
					break;
				case 3: /* where to write final port values */
					i++;
					if( i < argc )
						port_write = argv[i];
					break;
				case 4: /* debug everything */
					debug = 1;
					break;
				default:
					printf( "option \"%s\" is invalid\n", argv[i] );
			}
		else
			image_file = argv[i];
	}

	/* read image */
	FILE* f = fopen( image_file, "rb" );
	if( f == 0 )
	{
		printf( "file failure\n" );
		return -2;
	}
	unsigned int frame_addr = 0;
	unsigned char frame[12];
	unsigned int rd;
	while( (12 == (rd=fread(frame,1,12,f))) && (frame_addr < SIZE) )
	{
		if( (frame_addr&0x01) == 0 )
		{
			mem_data[frame_addr] = *(double*)frame;
			mem_code[frame_addr] = *(unsigned int*)(frame+8);
		} else
		{
			mem_data[frame_addr] = *(double*)(frame+4);
			mem_code[frame_addr] = *(unsigned int*)frame;
		}
		frame_addr++;
	}

	fclose( f );

	if( rd != 0 )
	{
		printf( "this is so unexpected, (read %d bytes) at %u\n", rd, frame_addr );
		return -3;
	}

	if( dump )
		printf( "read %u frames\n", frame_addr );

	/* dump */
	if( dump )
	{
		printf( "memory image:\n" );
		register unsigned int ptr;
		for( ptr = 0; ptr < frame_addr; ptr++ )
			printf( "%04X\t%f\n", ptr, mem_data[ptr] );
		printf( "data image:\n" );
	}

	/* the interpreter */
	unsigned short pc;
	for( pc = 0; pc < frame_addr; pc++ )
	{
		unsigned short r1, r2;
		unsigned int instr = mem_code[pc];
		unsigned char opcode = instr>>24;
		/* this is slow and retarded */
		if( (opcode&0xF0) == 0 ) /* S-type */
		{
			r2 = 0x0F&(instr>>20);
			r1 = MASK&instr;
		} else
		{						/* D-type */
			r1 = MASK&(instr>>14);
			r2 = MASK&instr;
		}
		switch( opcode ) {
			case 0x00: /* NOOP */
				printf( "%04X\tNoop\n", pc ); 
				continue;
			/* D-type */
			case 0x10: /* Add r1 r2 */
				printf( "%04X\tAdd    %04X %04X\n", pc, r1, r2 );
				mem_data[pc] = mem_data[r1] + mem_data[r2];
				break;
			case 0x20: /* Sub */
				printf( "%04X\tSub    %04X %04X\n", pc, r1, r2 );
				mem_data[pc] = mem_data[r1] - mem_data[r2];
				break;
			case 0x30: /* Mult */
				printf( "%04X\tMult   %04X %04X\n", pc, r1, r2 );
				mem_data[pc] = mem_data[r1] * mem_data[r2];
				break;
			case 0x40: /* Div */
				printf( "%04X\tDiv    %04X %04X\n", pc, r1, r2 );
				if( mem_data[r2] == 0.0 )
					mem_data[pc] = 0.0;
				else
					mem_data[pc] = mem_data[r1] / mem_data[r2];
				break;
			case 0x50: /* Output */
				printf( "%04X\tOutput %04X %04X\n", pc, r1, r2 );
				port[r1] = mem_data[r2];
				break;
			case 0x60: /* Phi */
				printf( "%04X\tPhi    %04X %04X\n", pc, r1, r2 );
				mem_data[pc] = mem_data[(status==1)?r1:r2];
				break;
			/* S-type */
			case 0x01: /* Cmpz */
				printf( "%04X\tCmpz   %04X    ", pc, r1 ); 
				switch( r2 )
				{
					case 0x00: /* < */
						printf( "<\n" );
						status = (mem_data[r1]<0.0)?1:0;
						break;
					case 0x01: /* <= */
						printf( "<=\n" );
						status = (mem_data[r1]<=0.0)?1:0;
						break;
					case 0x02: /* == */
						printf( "==\n" );
						status = (mem_data[r1]==0.0)?1:0;
						break;
					case 0x03: /* >= */
						printf( ">=\n" );
						status = (mem_data[r1]>=0.0)?1:0;
						break;
					case 0x04: /* > */
						printf( ">\n" );
						status = (mem_data[r1]>0.0)?1:0;
						break;
					default:
						printf( "invalid imm %X @ %u\n", r2, pc );
				}
				break;
			case 0x02: /* Sqrt */
				printf( "%04X\tSqrt %04X\n", pc, r1 );
				mem_data[pc] = sqrt( mem_data[r1] );
				break;
			case 0x03: /* Copy */
				printf( "%04X\tCopy %04X\n", pc, r1 );
				mem_data[pc] = mem_data[r1];
				break;
			case 0x04: /* Input */
				printf( "%04X\tInput %04X\n", pc, r1 );
				mem_data[pc] = port[r1];
				break;
			default: /* WHAT */
				printf( "opcode %02X @ %u is a failure\n", opcode, pc );
				return -4;
		}
	}

	return 0;
}
