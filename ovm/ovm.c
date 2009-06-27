#include <stdio.h>
#include <math.h>
#include <stdarg.h>
#include <string.h>
#include <stdlib.h>

#define SIZE 16384
#define MASK 16383

/* so runtime */
int status = 0;
unsigned int mem_code[SIZE];
double mem_data[SIZE];
double ports_in[SIZE];
double ports_out[SIZE];
unsigned short frames = 0;
double task = 1001;
char* image_file = 0;
char* solution_file = 0;
char* ports_file = 0;
char* memory_file = 0;
int dump = 0, debug = 0;
int full_dump = 0, solve = 0;
unsigned int iterations = 1;

int process();
int run_solution( char* file, double *score );

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

/* read size doubles from file */
int file_read( char *filename, double *p, unsigned int size )
{
	FILE *f = fopen( filename, "rb" );
	if( f == 0 )
		return -1;
	unsigned int rd = fread( p, sizeof(double), size, f );
	fclose( f );
	if( rd != size )
		return -2;
	return 0;
}

/* write size doubles to file */
int file_write( char *filename, double *p, unsigned int size )
{
	FILE *f = fopen( filename, "wb" );
	if( f == 0 )
		return -1;
	unsigned int wr = fwrite( p, sizeof(double), size, f );
	fclose( f );
	if( wr != size )
		return -2;
	return 0;
}

/* вытирайте ноги */
int main( int argc, char *argv[] )
{
	if( argc < 2 )
	{
		printf( "BAKA YARO!\n" );
		return -1;
	}

	/* run through parameters for.. WHAT FOR AM I WRITING THIS???! */
	int i;
	for( i = 1; i < argc; i++ )
	{
		/* if this is an option */
		if( argv[i][0] == '-' )
			switch( strswitch((argv[i])+1,"u","p","d","m","t","f","s","i","r") )
			{
				case 1: /* do full dump (instructions and memory) */
					dump = 1;
					break;
				case 2: /* file where ports walues are */
					i++;
					if( i < argc )
						ports_file = argv[i];
					break;
				case 3: /* debug everything */
					debug = 1;
					break;
				case 4: /* memory rw file (for state preserving) */
					i++;
					if( i < argc )
						memory_file = argv[i];
					break;
				case 5: /* task number */
					i++;
					if( i < argc )
						task = atoi( argv[i] );
					break;
				case 6: /* full dumps */
					full_dump = 1;
					break;
				case 7: /* use internal solver */
					solve = 1;
					break;
				case 8: /* number of machine iterations */
					i++;
					if( i < argc )
						iterations = atoi( argv[i] );
					break;
				case 9: /* run solution */
					i++;
					if( i < argc )
						solution_file = argv[i];
				default:
					printf( "option \"%s\" is invalid\n", argv[i] );
			}
		else
			image_file = argv[i];
	}

	/* read code and initial memory */
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
	frames = frame_addr;

	if( dump )
		printf( "read %u frames\n", frame_addr );

	/* run clean simulation of a solution */
	if( solution_file )
	{
		double score;
		if( run_solution(solution_file,&score) == 1 )
		{
			fprintf( stderr, "simulation succeeded with score %f\n", score );
			return 0;
		} 
		fprintf( stderr, "simulation failed with score %f\n", score );
		return 0;
	}

	/* read memory image */
	if( memory_file )
		file_read( memory_file, mem_data, SIZE );

	/* read ports image */
	if( ports_file )
		file_read( ports_file, ports_in, SIZE );
	else
		ports_in[0x3E80] = task;
	
	/* well, this is it */
	for(;iterations > 0; iterations-- )
	{
		process();
//		if( dump )
//			printf( "%f %f\n", ports_out[0x02], ports_out[0x03] ); 
	}

#ifdef DEBUG
	if( full_dump )
	{
		register unsigned int ptr;
		for( ptr = 0; ptr < SIZE; ptr++ )
			printf( "%04X %f\n", ptr, mem_data[ptr] );
	}
#endif

	/* write memory image */
	if( memory_file )
		file_write( memory_file, mem_data, SIZE );

	/* write ports image */
	if( ports_file )
		file_write( ports_file, ports_out, SIZE );

	return 0;
}

/* do all the dirty work */
int process()
{
	/* dump */
#ifdef DEBUG
	if( dump )
	{
		printf( "memory image:\n" );
		register unsigned int ptr;
		for( ptr = 0; ptr < frames; ptr++ )
			if( mem_data[ptr] != 0.0 ) printf( "%04X %f\n", ptr, mem_data[ptr] );
		printf( "code image:\n" );
	}
	char dbg_str[128]="";
#endif

	/* the interpreter */
	unsigned short pc;
	for( pc = 0; pc < frames; pc++ )
	{
		unsigned short r1, r2;
		unsigned int instr = mem_code[pc];
		unsigned char opcode = instr>>24;
		/* this is slow and retarded */
		if( (opcode&0xF0) == 0 ) /* S-type */
		{
			r2 = 0x07&(instr>>21);
			r1 = MASK&instr;
		} else
		{						/* D-type */
			r1 = MASK&(instr>>14);
			r2 = MASK&instr;
		}
		switch( opcode ) {
			case 0x00: /* NOOP */
#ifdef DEBUG
				if( debug || dump ) printf( "%04X\tNoop\n", pc ); 
#endif
				continue;
			/* D-type */
			case 0x10: /* Add r1 r2 */
				mem_data[pc] = mem_data[r1] + mem_data[r2];
#ifdef DEBUG
				if( debug )
					sprintf( dbg_str, "\t%f = %f + %f", mem_data[pc], mem_data[r1], mem_data[r2] );
				if( debug || dump ) 
					printf( "%04X\tAdd    %04X %04X%s\n", pc, r1, r2, dbg_str );
#endif
				break;
			case 0x20: /* Sub */
				mem_data[pc] = mem_data[r1] - mem_data[r2];
#ifdef DEBUG
				if( debug )
					sprintf( dbg_str, "\t%f = %f - %f", mem_data[pc], mem_data[r1], mem_data[r2] );
				if( debug || dump )
					printf( "%04X\tSub    %04X %04X%s\n", pc, r1, r2, dbg_str );
#endif
				break;
			case 0x30: /* Mult */
				mem_data[pc] = mem_data[r1] * mem_data[r2];
#ifdef DEBUG
				if( debug )
					sprintf( dbg_str, "\t%f = %f * %f", mem_data[pc], mem_data[r1], mem_data[r2] );
				if( debug || dump )
					printf( "%04X\tMult   %04X %04X%s\n", pc, r1, r2, dbg_str );
#endif
				break;
			case 0x40: /* Div */
				if( mem_data[r2] == 0.0 )
					mem_data[pc] = 0.0;
				else
					mem_data[pc] = mem_data[r1] / mem_data[r2];
#ifdef DEBUG
				if( debug )
					sprintf( dbg_str, "\t%f = %f / %f", mem_data[pc], mem_data[r1], mem_data[r2] );
				if( debug || dump )
					printf( "%04X\tDiv    %04X %04X%s\n", pc, r1, r2, dbg_str );
#endif
				break;
			case 0x50: /* Output */
				ports_out[r1] = mem_data[r2];
#ifdef DEBUG
				if( debug )
					sprintf( dbg_str, "\t%f", mem_data[r2] );
				if( debug || dump )
					printf( "%04X\tOutput %04X %04X%s\n", pc, r1, r2, dbg_str );
#endif
				break;
			case 0x60: /* Phi */
				mem_data[pc] = mem_data[(status==1)?r1:r2];
#ifdef DEBUG
				if( debug )
					sprintf( dbg_str, "\t(status==%d), %f = %s%f ? %s%f", status, mem_data[pc], 
									(status==1)?"*":"", mem_data[r1], (status==1)?"":"*", mem_data[r2] );
				if( debug || dump )
					printf( "%04X\tPhi    %04X %04X%s\n", pc, r1, r2, dbg_str );
#endif
				break;
			/* S-type */
			case 0x01: /* Cmpz */
				{
				char *cmp = "";
				switch( r2 )
				{
					case 0x00: /* < */
						cmp = "<";
						status = (mem_data[r1]<0.0)?1:0;
						break;
					case 0x01: /* <= */
						cmp = "<=";
						status = (mem_data[r1]<=0.0)?1:0;
						break;
					case 0x02: /* == */
						cmp = "==";
						status = (mem_data[r1]==0.0)?1:0;
						break;
					case 0x03: /* >= */
						cmp = ">=";
						status = (mem_data[r1]>=0.0)?1:0;
						break;
					case 0x04: /* > */
						cmp = ">";
						status = (mem_data[r1]>0.0)?1:0;
						break;
					default:
						cmp = "?";
				}
#ifdef DEBUG
				if( debug )
					sprintf( dbg_str, "\t%f %s 0.0  status=%d", mem_data[r1], cmp, status );
				if( debug || dump )
					printf( "%04X\tCmpz   %04X    %s%s\n", pc, r1, cmp, dbg_str );
#endif
				break;
				}
			case 0x02: /* Sqrt */
				mem_data[pc] = sqrt( mem_data[r1] );
#ifdef DEBUG
				if( debug )
					sprintf( dbg_str, "\t\t%f = sqrt(%f)", mem_data[pc], mem_data[r1] );
				if( debug || dump )
					printf( "%04X\tSqrt   %04X%s\n", pc, r1, dbg_str );
#endif
				break;
			case 0x03: /* Copy */
				mem_data[pc] = mem_data[r1];
#ifdef DEBUG
				if( debug )
					sprintf( dbg_str, "\t\t%f", mem_data[pc] );
				if( debug || dump )
					printf( "%04X\tCopy   %04X%s\n", pc, r1, dbg_str );
#endif
				break;
			case 0x04: /* Input */
				mem_data[pc] = ports_in[r1];
#ifdef DEBUG
				if( debug )
					sprintf( dbg_str, "\t\t%f", mem_data[pc] );
				if( debug || dump )
					printf( "%04X\tInput  %04X%s\n", pc, r1, dbg_str );
#endif
				break;
			default: /* WHAT */
				printf( "opcode %02X @ %u is a failure\n", opcode, pc );
				return -4;
		}
	}

#ifdef DEBUG
	if( dump )
	{
		printf( "ports image:\n" );
		register unsigned int ptr;
		for( ptr = 0; ptr < SIZE; ptr++ )
			if( ports_out[ptr] != 0.0 )
				printf( "%04X\t%f\n", ptr, ports_out[ptr] );
	}
#endif

	return 0;
}

/* test solution */
int run_solution( char *file, double *score )
{
	*score = 0.0;
	FILE *f = fopen( file, "rb" );
	if( f == 0 )
	{
		fprintf( stderr, "cannot open solution file \"%s\"\n", file );
		return 0;
	}
	unsigned int ival;
	double dval;
	if( (fread(&ival,sizeof(ival),1,f) != 1) || (ival != 0xCAFEBABE) )
	{
		fprintf( stderr, "solution file \"%s\" is invalid: wrong header\n", file );
		fclose( f );
		return 0;
	}

	if( fread(&ival,sizeof(ival),1,f) != 1 )
	{
		fprintf( stderr, "solution file \"%s\" is invalid: no team\n", file );
		fclose( f );
		return 0;
	}
	fprintf( stderr, "team id: %u\n", ival );

	if( fread(&ival,sizeof(ival),1,f) != 1 )
	{
		fprintf( stderr, "solution file \"%s\" is invalid: no scenario\n", file );
		fclose( f );
		return 0;
	}
	fprintf( stderr, "scenario id: %u\n", ival );
	task = ival;

	/* now to the simulation */
	ports_in[0x3E80] = task;
	unsigned int time = 0;
	do {
		if( fread(&ival,sizeof(ival),1,f) != 1 )
		{
			fprintf( stderr, "solution file \"%s\" is invalid: no time\n", file );
			fclose( f );
			return 0;
		}
		/* go to that step */
		for(; time<ival; time++ )
			process();
	
		/* read port values */
		if( fread(&ival,sizeof(ival),1,f) != 1 )
		{
			fprintf( stderr, "solution file \"%s\" is invalid: no port count\n", file );
			fclose( f );
			return 0;
		}
		if( ival == 0 ) /* if this is assumed to be the end */
		{
			*score = ports_out[0];
			break;
		}

		/* fill ports */
		unsigned int i;
		for( i = ival; i > 0; i-- )
		{
			if( fread(&ival,sizeof(ival),1,f) != 1 )
			{
				fprintf( stderr, "solution file \"%s\" is invalid: port address\n", file );
				fclose( f );
				return 0;
			}
			if( ival >= SIZE )
			{
				fprintf( stderr, "port address %08X is out of range (%04X)\n", ival, SIZE );
				fclose( f );
				return 0;
			}
			if( fread(&dval,sizeof(double),1,f) != 1 )
			{
				fprintf( stderr, "solution file \"%s\" is invalid: port value\n", file );
				fclose( f );
				return 0;
			}
			ports_in[ival] = dval;
		}
	} while( 1 );

	fclose( f );
	return 1;
}
