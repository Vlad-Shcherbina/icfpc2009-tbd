#include <stdio.h>
#include <math.h>

#define SIZE 16384
#define MASK 16383

/* so runtime */
int status = 0;
unsigned int mem_code[SIZE];
double mem_data[SIZE];
double port[SIZE];

/* вытирайте ноги */
int main( int argc, char *argv[] )
{
	if( argc < 1 )
	{
		printf( "BAKA YARO!\n" );
		return -1;
	}

	FILE* f = fopen( argv[1], "rb" );
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

	printf( "read %u frames\n", frame_addr );

	/* the interpreter */
	unsigned short pc;
	for( pc = 0; pc < SIZE; pc++ )
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
				printf( "%04X\tAdd %04X %04X\n", pc, r1, r2 );
				mem_data[pc] = mem_data[r1] + mem_data[r2];
				break;
			case 0x20: /* Sub */
				printf( "%04X\tSub %04X %04X\n", pc, r1, r2 );
				mem_data[pc] = mem_data[r1] - mem_data[r2];
				break;
			case 0x30: /* Mult */
				printf( "%04X\tMult %04X %04X\n", pc, r1, r2 );
				mem_data[pc] = mem_data[r1] * mem_data[r2];
				break;
			case 0x40: /* Div */
				printf( "%04X\tDiv %04X %04X\n", pc, r1, r2 );
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
				printf( "%04X\tPhi %04X %04X\n", pc, r1, r2 );
				mem_data[pc] = mem_data[(status==1)?r1:r2];
				break;
			/* S-type */
			case 0x01: /* Cmpz */
				printf( "%04X\tCmpz %04X ", pc, r1 ); 
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
				printf( "opcode %02X @ %u is failure\n", opcode, pc );
				return -4;
		}
	}

	return 0;
}
